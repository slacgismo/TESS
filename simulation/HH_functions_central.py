"""
Defines functions for the HH

Uses direct setting of system mode
"""
import gridlabd
import gridlabd_functions
#from gridlabd_functions import p_max # ???????????????
#import mysql_functions
#from HH_global import *

import datetime
import numpy as np
import pandas
from dateutil import parser
from datetime import timedelta
from HH_global import delta

"""NEW FUNCTIONS / MYSQL DATABASE AVAILABLE"""

#HVAC
from HH_global import flexible_houses, C, p_max, interval, prec

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
def bid_rule_HVAC(house, mean_p, var_p, interval):
	control_type = gridlabd_functions.get(house,'control_type')['value']
	k = float(gridlabd_functions.get(house,'k')['value'][1:])
	
	T_c_set = float(gridlabd_functions.get(house,'T_c_set_0')['value'][1:])
	T_h_set = float(gridlabd_functions.get(house,'T_h_set_0')['value'][1:])
	#T_curr = float(gridlabd_functions.get(house,'air_temperature')['value'][1:-5])
	#calculate energy
	hvac_q = float(gridlabd_functions.get(house,'cooling_demand')['value'][1:-3]) * interval / (60*60)
	heat_q = float(gridlabd_functions.get(house,'heating_demand')['value'][1:-3]) * interval / (60*60)

	#State of appliance in previous period
	status = int(gridlabd_functions.get(house,'state')['value'])
	
	if 'deadband' in control_type:
		# cooling
		if T_curr > T_c_set + k:
			bid_price = 1
			bid_quantity = hvac_q	
			gridlabd_functions.set(house,'bid_mode','COOL')		
			return bid_quantity, bid_price, status
		# heating
		elif T_curr < T_h_set - k:
			bid_price = 1
			bid_quantity = heat_q	
			gridlabd_functions.set(house,'bid_mode','HEAT')			
			return bid_quantity, bid_price, status
		# no activity
		else:
			bid_price = 0
			bid_quantity = 0
			gridlabd_functions.set(house,'bid_mode','NONE')	
			return bid_quantity, bid_price, status
	
	elif 'trans' in control_type:
		# Non-bid region size between cooling and heating [F]
		epsilon = 2
		bid_price = transactive_price(house, T_curr, T_c_set, T_h_set, mean_p, var_p, epsilon)
		if T_curr > T_c_set - (T_c_set - T_h_set)/2 + epsilon/2: #above T_c_zero
			bid_quantity = hvac_q
			gridlabd_functions.set(house,'bid_mode','COOL')
		elif T_curr < T_h_set + (T_c_set - T_h_set)/2 - epsilon/2: #below T_h_zero
			bid_quantity = heat_q
			gridlabd_functions.set(house,'bid_mode','HEAT')
		else:
			bid_quantity = 0
			gridlabd_functions.set(house,'bid_mode','NONE')
		return bid_quantity, bid_price, status
	else:
		print('Bid reserve price could not be calculated')
		return 0,0,0

# with non-bid region of size epsilon between T_h and T_c
def transactive_price(house, T_curr, T_c_set, T_h_set, mean_p, var_p, epsilon):
	T_zero_h = T_h_set + (T_c_set - T_h_set)/2 - epsilon/2
	T_zero_c = T_c_set - (T_c_set - T_h_set)/2 + epsilon/2
	T_max = float(gridlabd_functions.get(house,'T_max')['value'][1:])
	T_min = float(gridlabd_functions.get(house,'T_min')['value'][1:])
	k = float(gridlabd_functions.get(house,'k')['value'][1:])
	if T_curr > T_max or T_curr < T_min:
		return 1 #max price
	# cooling
	elif T_curr > T_zero_c:
		#Remains here if comfort settings are changed during operation
		m = (mean_p + k * np.sqrt(var_p))/(T_max - T_zero_c)
		gridlabd_functions.set(house,'m',m)
		n = - m * T_zero_c
		gridlabd_functions.set(house,'n',n)
		return (m * T_curr + n)
	# heating
	elif T_curr < T_zero_h:
		m = (mean_p + k * np.sqrt(var_p))/(T_min - T_zero_h)
		gridlabd_functions.set(house,'m',m)
		n = - m * T_zero_h
		gridlabd_functions.set(house,'n',n)
		return (m * T_curr + n)
	else:
		return 0

#Set rule: control HVAC by control of system mode
# def set_HVAC_direct(house,control_type,bid_price,Pd):
# 	if bid_price >= Pd and bid_price > 0: #to exclude consumption when price is zero
# 		#Appliance is active
# 		gridlabd_functions.set(house,'state',True)
# 		#switch on HVAC
# 		if 'COOL' in gridlabd_functions.get(house,'bid_mode')['value']:
# 			gridlabd_functions.set(house,'system_mode','COOL')
# 		elif 'HEAT' in gridlabd_functions.get(house,'bid_mode')['value']:
# 			gridlabd_functions.set(house,'system_mode','HEAT')
# 		else:
# 			print 'Check bid mode - there might be an inconsistency in bidding and actual behavior'
# 		return
# 	else:
# 		#Appliance is not active
# 		gridlabd_functions.set(house,'state',False)
# 		#turn off HVAC
# 		gridlabd_functions.set(house,'system_mode','OFF')
# 		return

#Set rule: control HVAC by control of set point
def set_HVAC_setpoint(house,control_type,bid_price,Pd):

	#Set state: Load is active in that period
	if bid_price >= Pd:
		gridlabd_functions.set(house,'state',True)
	else:
		gridlabd_functions.set(house,'state',False)

	if 'deadband' in control_type:
		if bid_price >= Pd and bid_price > 0: #to exclude consumption when price is zero
			#switch on HVAC
			if 'COOL' in gridlabd_functions.get(house,'bid_mode')['value']:
				gridlabd_functions.set(house,'system_mode','COOL')
			elif 'HEAT' in gridlabd_functions.get(house,'bid_mode')['value']:
				gridlabd_functions.set(house,'system_mode','HEAT')
			else:
				print('Check bid mode - there might be an inconsistency in bidding and actual behavior')
			return
		else:
			#turn off HVAC
			gridlabd_functions.set(house,'system_mode','OFF')
			#gridlabd_functions.set('control_1','control','OFF')
			return

	elif ('trans' in control_type): 

		m = float(gridlabd_functions.get(house,'m')['value'])
		n = float(gridlabd_functions.get(house,'n')['value'])
		T_max = float(gridlabd_functions.get(house,'T_max')['value'][1:])
		T_min = float(gridlabd_functions.get(house,'T_min')['value'][1:])

		#change setpoint on HVAC
		if 'COOL' in gridlabd_functions.get(house,'bid_mode')['value']:
			gridlabd_functions.set(house,'system_mode','COOL')
			# calculate new setpoint
			T_c_set_new = (Pd - n)/m
			if T_c_set_new > T_max:
				gridlabd_functions.set(house,'cooling_setpoint',T_max)
			else:
				gridlabd_functions.set(house,'cooling_setpoint',T_c_set_new)
		
		elif 'HEAT' in gridlabd_functions.get(house,'bid_mode')['value']:
			gridlabd_functions.set(house,'system_mode','HEAT')
			#calculate new setpoint
			T_h_set_new = (Pd - n)/m
			if T_h_set_new < T_min:
				gridlabd_functions.set(house,'heating_setpoint',T_min)
			else:
				gridlabd_functions.set(house,'heating_setpoint',T_h_set_new)
		else:
			gridlabd_functions.set(house,'system_mode','OFF')
		return
	else:
		print('HVAC could not be set')
		return