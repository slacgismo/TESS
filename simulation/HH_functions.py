"""
Defines functions for the HH

Uses direct setting of system mode
"""
#import gridlabd
#import gridlabd_functions
#from gridlabd_functions import p_max # ???????????????
#import mysql_functions
#from HH_global import *
import requests

#import battery_functions as Bfct
#import EV_functions as EVfct
import PV_functions as PVfct

import datetime
import numpy as np
import pandas
from dateutil import parser
from datetime import timedelta
from HH_global import results_folder, db_address, dispatch_mode

#import mysql_functions as myfct

"""NEW FUNCTIONS / MYSQL DATABASE AVAILABLE"""

#HVAC
from HH_global import flexible_houses, C, p_max, interval, prec, start_time_str

def create_agent_house(hh_id,flex_HVAC=False):
	#Create agent
	house = House(hh_id)

	#Create HVAC
	if flex_HVAC:
		hvac = HVAC(house_name)
		hvac.k = df_house_settings['k'].iloc[-1]
		hvac.T_max = df_house_settings['T_max'].iloc[-1]
		hvac.cooling_setpoint = df_house_settings['cooling_setpoint'].iloc[-1]
		hvac.T_min = df_house_settings['T_min'].iloc[-1]
		hvac.heating_setpoint = df_house_settings['heating_setpoint'].iloc[-1]
		hvac.T_des = (df_house_settings['heating_setpoint'].iloc[-1] + df_house_settings['cooling_setpoint'].iloc[-1])/2. #Default
		house.HVAC = hvac
	#Other variables are related to continuously changing state and updated by update state: T_air, mode, cooling_demand, heating_demand

	#Create and assign DER objects if exist
	house = PVfct.get_PV(house,hh_id) # get PV table and checks if PV is associated with HH id
	# house = Bfct.get_battery(house,house_name)
	# house = EVfct.get_CP(house,house_name)

	return house


class House:
	def __init__(self,hh_id):
		#Str
		self.hh_id = hh_id
		#Objects
		self.HVAC = None
		self.PV = None
		self.battery = None
		self.EVCP = None

	def update_state(self,dt_sim_time):
		# if self.HVAC:
		# 	df_state_in = myfct.get_values_td(self.name+'_state_in', begin=dt_sim_time, end=dt_sim_time)
		# 	self.HVAC.update_state(df_state_in)
		if self.PV:
			#import pdb; pdb.set_trace()
			pv_interval = requests.get(db_address+'/meter_intervals?meter_id=1').json()['results']['data'][-1] #Use last measurement
			self.PV.update_state(pv_interval)
		# if self.battery:
		# 	df_batt_state_in = myfct.get_values_td(self.battery.name+'_state_in', begin=dt_sim_time, end=dt_sim_time)
		# 	self.battery.update_state(df_batt_state_in)
		# if self.EVCP:
		# 	df_evcp_state_in = myfct.get_values_td('EV_'+self.EVCP.ID+'_state_in', begin=dt_sim_time, end=dt_sim_time)
		# 	if len(df_evcp_state_in):
		# 		self.EVCP.checkin_newEV(df_evcp_state_in,connected=True)
		# 	self.EVCP.update_state(dt_sim_time)
		return

	#GUSTAVO: If the customer changes the settings through the App or at a device, that needs to be pushed here
	def update_settings(self):
		#HVAC settings
		self.HVAC.update_settings()
		#Battery settings
		#EV settings
		return

	#According to
	#https://github.com/slacgismo/TESS/blob/b99df97815465a964c7e5813ce7b7ef726751abd/agents/Bid%20and%20response%20strategy.ipynb
	def bid(self,dt_sim_time,market):
		# Derive reference prices
		time_delta = 12*24
		try:
			df_prices_lem = requests.get(db_address+'market_intervals').json()['results']['data'][-1]
			# Price expectations, can be specified by household
			P_exp, P_dev = self.get_reference_prices(df_prices_lem)
		except:
			# If price not available (in first period or bec of connection issues)
			P_exp, P_dev = 0.02, 1.0
		
		# Bid household devices
		#self.HVAC.bid(dt_sim_time,market,P_exp,P_dev)
		self.PV.bid(dt_sim_time,market,P_exp,P_dev)
		#self.battery.bid(dt_sim_time,market,P_exp,P_dev)
		#self.EVCP.bid(dt_sim_time,market,P_exp,P_dev)
		return

	#Use centralized expected price average and variance
	def get_reference_prices(self,df_prices_lem):
		return df_prices_lem['p_exp'], df_prices_lem['p_dev']

	def determine_dispatch(self,dt_sim_time):
		#HH reads price from market DB
		df_lem = requests.get(db_address+'market_intervals').json()['results']['data'][-1]
		p_lem = df_lem['p_clear']
		alpha = df_lem['alpha']
		if dispatch_mode:
			#self.HVAC.dispatch(dt_sim_time,p_lem,alpha)
			self.PV.dispatch(dt_sim_time,p_lem,alpha)
		#self.battery.dispatch(dt_sim_time,p_lem,alpha)
		#self.EVCP.dispatch(dt_sim_time,p_lem,alpha)

class HVAC:
	def __init__(self,name,T_air=0.0,mode='OFF',k=0.0,T_max=None,cooling_setpoint=None,cooling_demand=None,T_min=None,heating_setpoint=None,heating_demand=None):
		self.name = name
		self.T_air = T_air
		self.k = k
		self.mode = mode
		self.T_max = T_max
		self.cooling_setpoint = cooling_setpoint
		self.cooling_demand = cooling_demand
		self.T_min = T_min
		self.heating_setpoint = heating_setpoint
		self.heating_demand = heating_demand
		if heating_setpoint and cooling_setpoint:
			self.T_des = heating_setpoint + (cooling_setpoint - heating_setpoint)/2. #Default
		#Last bids
		self.P_bid = 0.0
		self.Q_bid = 0.0

	def update_state(self,df_state_in):
		self.T_air = float(df_state_in['T_air'].iloc[0])
		self.mode = df_state_in['mode'].iloc[0]
		self.cooling_demand = float(df_state_in['q_cool'].iloc[0])
		self.heating_demand = float(df_state_in['q_heat'].iloc[0])
		return

	#Needs to get updated
	def update_settings(self):
		# house_obj = gridlabd.get_object(self.name) #GUSTAVO & MAYANK: user input - this comes from the App / hardware settings
		# self.k = k
		# self.T_max = T_max
		# self.cooling_setpoint = float(house_obj['cooling_setpoint'])
		# self.T_min = T_min
		# self.heating_setpoint = float(house_obj['heating_setpoint'])
		# self.T_des = heating_setpoint + (cooling_setpoint - heating_setpoint)/2. #Default

		# self.cooling_demand = float(house_obj['cooling_demand'])
		# self.heating_demand = float(house_obj['heating_demand'])
		# if (self.mode == 'HEAT') and (float(house_obj['air_temperature']) >= self.cooling_setpoint):
		# 	self.mode = 'COOL'
		# elif (self.mode == 'COOL') and (float(house_obj['air_temperature']) <= self.heating_setpoint):
		# 	self.mode = 'HEAT'
		return

	def bid(self,dt_sim_time,market,P_exp,P_dev):
		if self.T_air <= self.T_des:
			T_ref = self.T_min
		else:
			T_ref = self.T_max
		if self.mode == 'COOL':
			m = -1
			Q_bid = self.cooling_demand
		elif self.mode == 'HEAT':
			m = 1
			Q_bid = self.heating_demand
		else:
			m = 0
			Q_bid = 0.0 
		P_bid = P_exp - 3*np.sign(m)*P_dev*(self.T_air - self.T_des)/abs(T_ref - self.T_des)
		self.P_bid = P_bid
		self.Q_bid = Q_bid

		#write P_bid, Q_bid to market DB
		if (Q_bid > 0.0) and not (self.mode == 'OFF'):
			timestamp_arrival = market.send_demand_bid(dt_sim_time, float(P_bid), float(Q_bid), 'HVAC_'+self.name) #Feedback: timestamp of arrival #C determined by market_operator
		return

	def dispatch(self,dt_sim_time,p_lem,alpha):
		if (self.Q_bid > 0.0) and (self.P_bid > p_lem):
			gridlabd.set_value(self.name,'system_mode',self.mode)
			operating_mode = self.mode
		elif (self.Q_bid > 0.0) and (self.P_bid == p_lem):
			print('This HVAC is marginal; no partial implementation yet: '+str(alpha))
			gridlabd.set_value(self.name,'system_mode',self.mode)
			operating_mode = self.mode
		else:
			gridlabd.set_value(self.name,'system_mode','OFF')
			operating_mode = 'OFF'
		myfct.set_values(self.name+'_state_out', '(timedate, operating_mode, p_HVAC)', (dt_sim_time, operating_mode, str(self.P_bid)))
		self.P_bid = 0.0
		self.Q_bid = 0.0


def get_settings_houses(houselist,interval,mysql=False):
	dt = parser.parse(gridlabd.get_global('clock')) #Better: getstart time!
	prev_timedate = dt - timedelta(minutes=interval/60)
	#Prepare dataframe to save settings and current state
	cols_market_hvac = ['house_name','appliance_name','k','T_min','T_max','P_heat','P_cool','heating_setpoint','cooling_setpoint','air_temperature','active']
	df_market_hvac = pandas.DataFrame(columns=cols_market_hvac)
	#cols_market_hvac_meter = ['system_mode','av_power','active','timedate','appliance_id']
	#df_market_hvac_meter = pandas.DataFrame(columns=cols_market_hvac_meter)
	#Iterate through all houses and collect characteristics relevant for bidding
	for house in houselist:            
		#Table with all relevant settings
		house_obj = gridlabd.get_object(house)
		k = float(house_obj['k'])
		T_min = float(house_obj['T_min'])
		T_max = float(house_obj['T_max'])
		heat_q = float(house_obj['heating_demand']) #heating_demand is in kW
		hvac_q = float(house_obj['cooling_demand']) #cooling_demand is in kW
		heating_setpoint = float(house_obj['heating_setpoint'])
		cooling_setpoint = float(house_obj['cooling_setpoint'])
		T_air = float(house_obj['air_temperature'])
		df_market_hvac = df_market_hvac.append(pandas.Series([house,'HVAC_'+house[4:],k,T_min,T_max,heat_q,hvac_q,heating_setpoint,cooling_setpoint,T_air,0],index=cols_market_hvac),ignore_index=True)          
		#DB structure according to AWS structure
		
		#if mysql:
		#	mysql_functions.set_values('market_houses', '(house_name)',(house,))
		#	mysql_functions.set_values('market_HVAC', '(house_name,appliance_name,k,T_min,T_max,P_heat,P_cool)',(house,'HVAC_'+house[4:],k,T_min,T_max,heat_q,hvac_q,))
		#	mysql_functions.set_values('market_HVAC_meter', '(system_mode,av_power,heating_setpoint,cooling_setpoint,active,timedate,appliance_id)',('OFF',0.0,heating_setpoint,cooling_setpoint,0,prev_timedate,int(house.split('_')[-1]),))           
	
	#df_market_hvac.to_sql('market_HVAC',mycursor,if_exists='append') #, flavor='mysql')
	#Index = house_number
	df_market_hvac.index = df_market_hvac.index + 1
	return df_market_hvac

#Read current temperature of each house
def update_house(dt_sim_time,df_market_hvac):
	#rec_obj = gridlabd.get_object('rec_T')
	for i in df_market_hvac.index: #directly from mysql
		#house_obj = gridlabd.get_object(df_market_hvac['house_name'].loc[i])
		#df_market_hvac.at[i,'air_temperature'] = float(house_obj['air_temperature'])
		df_market_hvac.at[i,'air_temperature'] = float(gridlabd.get_value(df_market_hvac['house_name'].loc[i],'air_temperature')[:-5])
		#Update bidding q to latest demand values
		#if house_obj['system_mode'] == 'HEAT':
		if df_market_hvac.at[i,'active'] == 1: #Only update if it was active before
			if gridlabd.get_value(df_market_hvac['house_name'].loc[i],'system_mode') == 'HEAT':
				df_market_hvac.at[i,'P_heat'] = float(gridlabd.get_value(df_market_hvac['house_name'].loc[i],'hvac_load')[:-3])
			#elif house_obj['system_mode'] == 'COOL':
			elif gridlabd.get_value(df_market_hvac['house_name'].loc[i],'system_mode') == 'COOL':
				#df_market_hvac.at[i,'P_cool'] = float(house_obj['hvac_load'])
				#print(gridlabd.get_value(df_market_hvac['house_name'].loc[i],'hvac_load'))
				df_market_hvac.at[i,'P_cool'] = float(gridlabd.get_value(df_market_hvac['house_name'].loc[i],'hvac_load')[:-3])
	return df_market_hvac

#Calculates bids for HVAC systems under transactive control
def calc_bids_HVAC(dt_sim_time,df_house_state,retail,mean_p,var_p):
	df_house_state['active'] = 0 #Reset from last period
	df_bids = df_house_state.copy()
	#Calculate bid prices
	#intersection with (p - k*sigma)
	#delta = 3.0 #band of HVAC inactivity
	df_bids['T_h0'] = df_bids['T_min'] + (df_bids['T_max'] - df_bids['T_min'])/2 - delta/2
	df_bids['T_c0'] = df_bids['T_min'] + (df_bids['T_max'] - df_bids['T_min'])/2 + delta/2
	df_bids['bid_p'] = 0.0 #default
	df_bids['system_mode'] = 'OFF' #default
	#heating
	df_bids.at[df_bids['air_temperature'] <= df_bids['T_h0'],'system_mode'] = 'HEAT'
	df_bids.at[df_bids['system_mode'] == 'HEAT','bid_p'] = (mean_p + df_bids['k']*var_p) + (df_bids['air_temperature']-df_bids['T_min'])*(-2*df_bids['k']*var_p)/(df_bids['T_h0']-df_bids['T_min']).round(prec)
	df_bids.at[df_bids['air_temperature'] <= df_bids['T_min'],'bid_p'] = retail.Pmax
	#cooling
	df_bids.at[df_bids['air_temperature'] >= df_bids['T_c0'],'system_mode'] = 'COOL'
	df_bids.at[df_bids['system_mode'] == 'COOL','bid_p'] = (mean_p + df_bids['k']*var_p) - (df_bids['T_max']-df_bids['air_temperature'])*(2*df_bids['k']*var_p)/(df_bids['T_max']-df_bids['T_c0']).round(prec)
	df_bids.at[df_bids['air_temperature'] >= df_bids['T_max'],'bid_p'] = retail.Pmax
	"""Should we enable negative prices?"""
	df_bids['lower_bound'] = 0.0
	df_bids['upper_bound'] = retail.Pmax
	df_bids['bid_p'] = df_bids[['bid_p','lower_bound']].max(axis=1)
	df_bids['bid_p'] = df_bids[['bid_p','upper_bound']].min(axis=1) #just below the price cap; set upper bound according to global!
	#DO MERGE INSTEAD!!!
	df_house_state['bid_p'] = df_bids['bid_p']
	df_house_state['system_mode'] = df_bids['system_mode']
	return df_house_state

#Submits HVAC bids to market and saves bids to database
def submit_bids_HVAC(dt_sim_time,retail,df_bids,df_buy_bids):
	#Submit bids (in kW)
	df_bids['bid_q'] = 0.0
	for ind in df_bids.index:
		if df_bids['bid_p'].loc[ind] > 0 and df_bids['P_heat'].loc[ind] > 0.0 and df_bids['system_mode'].loc[ind] == 'HEAT':
			df_bids.at[ind,'bid_q'] = df_bids['P_heat'].loc[ind]
			retail.buy(df_bids['P_heat'].loc[ind],df_bids['bid_p'].loc[ind],active=int(df_bids['active'].loc[ind]),appliance_name=df_bids['house_name'].loc[ind])
			#mysql_functions.set_values('buy_bids', '(bid_price,bid_quantity,timedate,appliance_name)',(float(df_bids['bid_p'].loc[ind]),float(df_bids['P_heat'].loc[ind]),dt_sim_time,df_bids['appliance_name'].loc[ind],))
			df_buy_bids = df_buy_bids.append(pandas.DataFrame(columns=df_buy_bids.columns,data=[[dt_sim_time,df_bids['appliance_name'].loc[ind],float(df_bids['bid_p'].loc[ind]),float(df_bids['P_heat'].loc[ind])]]),ignore_index=True)
		elif df_bids['bid_p'].loc[ind] > 0 and df_bids['P_cool'].loc[ind] > 0.0 and df_bids['system_mode'].loc[ind] == 'COOL':
			df_bids.at[ind,'bid_q'] = df_bids['P_cool'].loc[ind]
			retail.buy(df_bids['P_cool'].loc[ind],df_bids['bid_p'].loc[ind],active=int(df_bids['active'].loc[ind]),appliance_name=df_bids['house_name'].loc[ind])
			#mysql_functions.set_values('buy_bids', '(bid_price,bid_quantity,timedate,appliance_name)',(float(df_bids['bid_p'].loc[ind]),float(df_bids['P_cool'].loc[ind]),dt_sim_time,df_bids['appliance_name'].loc[ind],))
			df_buy_bids = df_buy_bids.append(pandas.DataFrame(columns=df_buy_bids.columns,data=[[dt_sim_time,df_bids['appliance_name'].loc[ind],float(df_bids['bid_p'].loc[ind]),float(df_bids['P_cool'].loc[ind])]]),ignore_index=True)
	return retail, df_buy_bids

def set_HVAC_T(dt_sim_time,df_bids_HVAC,mean_p,var_p, Pd):
	df_bids_HVAC.at[df_bids_HVAC['bid_p'] >= Pd,'active'] = 1
	df_bids_HVAC['p_max'] = mean_p+df_bids_HVAC['k']*var_p

	df_bids_HVAC['temp'] = df_bids_HVAC['T_min'] + (df_bids_HVAC['p_max'] - Pd)*(df_bids_HVAC['T_h0'] - df_bids_HVAC['T_min'])/(2*df_bids_HVAC['k']*var_p)
	df_bids_HVAC['temp'] = df_bids_HVAC[['temp','T_min']].max(axis=1)
	df_bids_HVAC['temp'] = df_bids_HVAC[['temp','T_h0']].min(axis=1)
	df_bids_HVAC.loc[df_bids_HVAC['system_mode'] == 'HEAT','heating_setpoint'] = df_bids_HVAC['temp']
	df_bids_HVAC.loc[df_bids_HVAC['system_mode'] == 'HEAT','cooling_setpoint'] = p_max #where should those be to not harm?
	df_bids_HVAC.loc[df_bids_HVAC['system_mode'] == 'OFF','cooling_setpoint'] = p_max #where should those be to not harm?
	
	df_bids_HVAC['temp'] = df_bids_HVAC['T_max'] + (df_bids_HVAC['p_max'] - Pd)*(df_bids_HVAC['T_c0'] - df_bids_HVAC['T_max'])/(2*df_bids_HVAC['k']*var_p)
	df_bids_HVAC['temp'] = df_bids_HVAC[['temp','T_c0']].max(axis=1)
	df_bids_HVAC['temp'] = df_bids_HVAC[['temp','T_max']].min(axis=1)
	df_bids_HVAC.loc[df_bids_HVAC['system_mode'] == 'COOL','cooling_setpoint'] = df_bids_HVAC['temp']
	df_bids_HVAC.loc[df_bids_HVAC['system_mode'] == 'COOL','heating_setpoint'] = 0.0 #where should those be to not harm?
	df_bids_HVAC.loc[df_bids_HVAC['system_mode'] == 'OFF','heating_setpoint'] = 0.0 #where should those be to not harm?

	#Write to GridlabD objects
	#Read information via database later on!
	for house in houselist:		
		cooling_setpoint = df_bids_HVAC['cooling_setpoint'].loc[df_bids_HVAC['house_name'] == house].values[0]
		heating_setpoint = df_bids_HVAC['heating_setpoint'].loc[df_bids_HVAC['house_name'] == house].values[0]
		active = df_bids_HVAC['active'].loc[df_bids_HVAC['house_name'] == house].values[0]
		#Can I do that for the whole table with a dataframe?
		#mysql_functions.set_values('market_HVAC_meter', '(system_mode,heating_setpoint,cooling_setpoint,active,timedate,appliance_id)',('OFF',float(heating_setpoint),float(cooling_setpoint),int(active),dt_sim_time,houselist.index(house)+1,))
		#Write to gridlabd (to be done from mysql in future)
		gridlabd_functions.set(house,'cooling_setpoint',cooling_setpoint)
		gridlabd_functions.set(house,'heating_setpoint',heating_setpoint)

	return df_bids_HVAC

def set_HVAC_GLD(dt_sim_time,df_house_state,df_awarded_bids):
	for ind in df_house_state.index:		
		house = df_house_state['house_name'].loc[ind]
		if df_house_state['active'].loc[ind] == 1:
			system_mode = df_house_state['system_mode'].loc[ind]
			gridlabd.set_value(house,'system_mode',system_mode) #Cool or heat
			p_bid = df_house_state['bid_p'].loc[ind]
			q_bid = df_house_state['bid_q'].loc[ind]
			#mysql_functions.set_values('awarded_bids','(appliance_name,p_bid,q_bid,timedate)',(house,float(p_bid),float(q_bid),dt_sim_time))
			df_awarded_bids = df_awarded_bids.append(pandas.DataFrame(columns=df_awarded_bids.columns,data=[[dt_sim_time,house,float(p_bid),float(q_bid),'D']]),ignore_index=True)
		else:
			system_mode = 'OFF'
			gridlabd.set_value(house,'system_mode',system_mode)
	return df_house_state,df_awarded_bids

def set_HVAC_by_price(dt_sim_time,df_house_state,mean_p,var_p, Pd,df_awarded_bids):
	df_house_state.at[df_house_state['bid_p'] >= Pd,'active'] = 1
	df_house_state,df_awarded_bids = set_HVAC_GLD(dt_sim_time,df_house_state,df_awarded_bids)
	return df_house_state, df_awarded_bids

def set_HVAC_by_award(dt_sim_time,df_house_state,market,df_awarded_bids):
	try:
		list_awards = market.D_awarded[:,3]
	except:
		list_awards = []
	for bidder in list_awards:
		if 'GLD_' in bidder:
			df_house_state.at[df_house_state['house_name'] == bidder,'active'] = 1
	df_house_state, df_awarded_bids = set_HVAC_GLD(dt_sim_time,df_house_state,df_awarded_bids)
	return df_house_state,df_awarded_bids

"""OLD FUNCTIONS / NO MYSQL DATABASE AVAILABLE"""

#Bid functions
# def bid_rule_HVAC(house, mean_p, var_p, interval):
# 	control_type = gridlabd_functions.get(house,'control_type')['value']
# 	k = float(gridlabd_functions.get(house,'k')['value'][1:])
	
# 	T_c_set = float(gridlabd_functions.get(house,'T_c_set_0')['value'][1:])
# 	T_h_set = float(gridlabd_functions.get(house,'T_h_set_0')['value'][1:])
# 	#T_curr = float(gridlabd_functions.get(house,'air_temperature')['value'][1:-5])
# 	#calculate energy
# 	hvac_q = float(gridlabd_functions.get(house,'cooling_demand')['value'][1:-3]) * interval / (60*60)
# 	heat_q = float(gridlabd_functions.get(house,'heating_demand')['value'][1:-3]) * interval / (60*60)

# 	#State of appliance in previous period
# 	status = int(gridlabd_functions.get(house,'state')['value'])
	
# 	if 'deadband' in control_type:
# 		# cooling
# 		if T_curr > T_c_set + k:
# 			bid_price = 1
# 			bid_quantity = hvac_q	
# 			gridlabd_functions.set(house,'bid_mode','COOL')		
# 			return bid_quantity, bid_price, status
# 		# heating
# 		elif T_curr < T_h_set - k:
# 			bid_price = 1
# 			bid_quantity = heat_q	
# 			gridlabd_functions.set(house,'bid_mode','HEAT')			
# 			return bid_quantity, bid_price, status
# 		# no activity
# 		else:
# 			bid_price = 0
# 			bid_quantity = 0
# 			gridlabd_functions.set(house,'bid_mode','NONE')	
# 			return bid_quantity, bid_price, status
	
# 	elif 'trans' in control_type:
# 		# Non-bid region size between cooling and heating [F]
# 		epsilon = 2
# 		bid_price = transactive_price(house, T_curr, T_c_set, T_h_set, mean_p, var_p, epsilon)
# 		if T_curr > T_c_set - (T_c_set - T_h_set)/2 + epsilon/2: #above T_c_zero
# 			bid_quantity = hvac_q
# 			gridlabd_functions.set(house,'bid_mode','COOL')
# 		elif T_curr < T_h_set + (T_c_set - T_h_set)/2 - epsilon/2: #below T_h_zero
# 			bid_quantity = heat_q
# 			gridlabd_functions.set(house,'bid_mode','HEAT')
# 		else:
# 			bid_quantity = 0
# 			gridlabd_functions.set(house,'bid_mode','NONE')
# 		return bid_quantity, bid_price, status
# 	else:
# 		print('Bid reserve price could not be calculated')
# 		return 0,0,0

# # with non-bid region of size epsilon between T_h and T_c
# def transactive_price(house, T_curr, T_c_set, T_h_set, mean_p, var_p, epsilon):
# 	T_zero_h = T_h_set + (T_c_set - T_h_set)/2 - epsilon/2
# 	T_zero_c = T_c_set - (T_c_set - T_h_set)/2 + epsilon/2
# 	T_max = float(gridlabd_functions.get(house,'T_max')['value'][1:])
# 	T_min = float(gridlabd_functions.get(house,'T_min')['value'][1:])
# 	k = float(gridlabd_functions.get(house,'k')['value'][1:])
# 	if T_curr > T_max or T_curr < T_min:
# 		return 1 #max price
# 	# cooling
# 	elif T_curr > T_zero_c:
# 		#Remains here if comfort settings are changed during operation
# 		m = (mean_p + k * np.sqrt(var_p))/(T_max - T_zero_c)
# 		gridlabd_functions.set(house,'m',m)
# 		n = - m * T_zero_c
# 		gridlabd_functions.set(house,'n',n)
# 		return (m * T_curr + n)
# 	# heating
# 	elif T_curr < T_zero_h:
# 		m = (mean_p + k * np.sqrt(var_p))/(T_min - T_zero_h)
# 		gridlabd_functions.set(house,'m',m)
# 		n = - m * T_zero_h
# 		gridlabd_functions.set(house,'n',n)
# 		return (m * T_curr + n)
# 	else:
# 		return 0

# #Set rule: control HVAC by control of system mode
# # def set_HVAC_direct(house,control_type,bid_price,Pd):
# # 	if bid_price >= Pd and bid_price > 0: #to exclude consumption when price is zero
# # 		#Appliance is active
# # 		gridlabd_functions.set(house,'state',True)
# # 		#switch on HVAC
# # 		if 'COOL' in gridlabd_functions.get(house,'bid_mode')['value']:
# # 			gridlabd_functions.set(house,'system_mode','COOL')
# # 		elif 'HEAT' in gridlabd_functions.get(house,'bid_mode')['value']:
# # 			gridlabd_functions.set(house,'system_mode','HEAT')
# # 		else:
# # 			print 'Check bid mode - there might be an inconsistency in bidding and actual behavior'
# # 		return
# # 	else:
# # 		#Appliance is not active
# # 		gridlabd_functions.set(house,'state',False)
# # 		#turn off HVAC
# # 		gridlabd_functions.set(house,'system_mode','OFF')
# # 		return

# #Set rule: control HVAC by control of set point
# def set_HVAC_setpoint(house,control_type,bid_price,Pd):

# 	#Set state: Load is active in that period
# 	if bid_price >= Pd:
# 		gridlabd_functions.set(house,'state',True)
# 	else:
# 		gridlabd_functions.set(house,'state',False)

# 	if 'deadband' in control_type:
# 		if bid_price >= Pd and bid_price > 0: #to exclude consumption when price is zero
# 			#switch on HVAC
# 			if 'COOL' in gridlabd_functions.get(house,'bid_mode')['value']:
# 				gridlabd_functions.set(house,'system_mode','COOL')
# 			elif 'HEAT' in gridlabd_functions.get(house,'bid_mode')['value']:
# 				gridlabd_functions.set(house,'system_mode','HEAT')
# 			else:
# 				print('Check bid mode - there might be an inconsistency in bidding and actual behavior')
# 			return
# 		else:
# 			#turn off HVAC
# 			gridlabd_functions.set(house,'system_mode','OFF')
# 			#gridlabd_functions.set('control_1','control','OFF')
# 			return

# 	elif ('trans' in control_type): 

# 		m = float(gridlabd_functions.get(house,'m')['value'])
# 		n = float(gridlabd_functions.get(house,'n')['value'])
# 		T_max = float(gridlabd_functions.get(house,'T_max')['value'][1:])
# 		T_min = float(gridlabd_functions.get(house,'T_min')['value'][1:])

# 		#change setpoint on HVAC
# 		if 'COOL' in gridlabd_functions.get(house,'bid_mode')['value']:
# 			gridlabd_functions.set(house,'system_mode','COOL')
# 			# calculate new setpoint
# 			T_c_set_new = (Pd - n)/m
# 			if T_c_set_new > T_max:
# 				gridlabd_functions.set(house,'cooling_setpoint',T_max)
# 			else:
# 				gridlabd_functions.set(house,'cooling_setpoint',T_c_set_new)
		
# 		elif 'HEAT' in gridlabd_functions.get(house,'bid_mode')['value']:
# 			gridlabd_functions.set(house,'system_mode','HEAT')
# 			#calculate new setpoint
# 			T_h_set_new = (Pd - n)/m
# 			if T_h_set_new < T_min:
# 				gridlabd_functions.set(house,'heating_setpoint',T_min)
# 			else:
# 				gridlabd_functions.set(house,'heating_setpoint',T_h_set_new)
# 		else:
# 			gridlabd_functions.set(house,'system_mode','OFF')
# 		return
# 	else:
# 		print('HVAC could not be set')
# 		return