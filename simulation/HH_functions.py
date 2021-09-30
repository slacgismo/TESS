"""
Defines functions for customers and their home hubs

Bundles all appliances in one home hub
"""

import datetime
import numpy as np
import pandas
from dateutil import parser
from datetime import timedelta
import requests

#import battery_functions as Bfct
#import EV_functions as EVfct
import PV_functions as PVfct

from HH_global import db_address, dispatch_mode, p_max, interval

# Creates one agent per house and includes flexible appliances as children
def create_agent_house(hh_id,flex_HVAC=False):
	#Create agent
	house = House(hh_id)

	#Creates HVAC child if flexible
	if flex_HVAC:
		hvac = HVAC(house_name)
		hvac.k = df_house_settings['k'].iloc[-1]
		hvac.T_max = df_house_settings['T_max'].iloc[-1]
		hvac.cooling_setpoint = df_house_settings['cooling_setpoint'].iloc[-1]
		hvac.T_min = df_house_settings['T_min'].iloc[-1]
		hvac.heating_setpoint = df_house_settings['heating_setpoint'].iloc[-1]
		hvac.T_des = (df_house_settings['heating_setpoint'].iloc[-1] + df_house_settings['cooling_setpoint'].iloc[-1])/2. #Default
		house.HVAC = hvac

	#Create and assign DER objects if exist
	house = PVfct.get_PV(house,hh_id) # get PV table and checks if PV is associated with HH id
	# house = Bfct.get_battery(house,house_name)
	# house = EVfct.get_CP(house,house_name)

	return house

# Python object class for house and its home hub
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
            self.PV.update_state()
		# if self.battery:
		# 	df_batt_state_in = myfct.get_values_td(self.battery.name+'_state_in', begin=dt_sim_time, end=dt_sim_time)
		# 	self.battery.update_state(df_batt_state_in)
		# if self.EVCP:
		# 	df_evcp_state_in = myfct.get_values_td('EV_'+self.EVCP.ID+'_state_in', begin=dt_sim_time, end=dt_sim_time)
		# 	if len(df_evcp_state_in):
		# 		self.EVCP.checkin_newEV(df_evcp_state_in,connected=True)
		# 	self.EVCP.update_state(dt_sim_time)
        return

	# If the customer changes the settings through the App or at a device, that needs to be updated in Python objects
    def update_settings(self):
		#self.HVAC.update_settings()
		#self.PV.update_settings()
		#self.battery.update_settings()
		#self.EV.update_settings()
        return

	#According to
	#https://github.com/slacgismo/TESS/blob/b99df97815465a964c7e5813ce7b7ef726751abd/agents/Bid%20and%20response%20strategy.ipynb
    def bid(self,dt_sim_time,market):
		# Derive reference prices
        try:
            df_prices_lem = requests.get(db_address+'market_intervals').json()['results']['data'][-1]
			# Price expectations, can be specified by household
            P_exp, P_dev = self.get_reference_prices(df_prices_lem)
        except:
			# If price not available (in first period or bec of connection issues)
            P_exp, P_dev = 0.02, 1.0

		# Bid household devices
		#self.HVAC.bid(dt_sim_time,market,P_exp,P_dev)
		#import pdb; pdb.set_trace()
        self.PV.bid(dt_sim_time,market,P_exp,P_dev)
		#self.battery.bid(dt_sim_time,market,P_exp,P_dev)
		#self.EVCP.bid(dt_sim_time,market,P_exp,P_dev)
        return

	#Use centralized expected price average and variance
    def get_reference_prices(self,df_prices_lem):
        return df_prices_lem['p_exp'], df_prices_lem['p_dev']

	# Determine `mode' in response to market result
    def determine_dispatch(self,dt_sim_time):
		#HH reads price from market DB
        df_lem = requests.get(db_address+'market_intervals').json()['results']['data'][-1]
        p_lem = df_lem['p_clear']
        alpha = df_lem['alpha']

        # Dispatch of flexible appliances
		#self.HVAC.dispatch(dt_sim_time,p_lem,alpha)
        try:
            self.PV.dispatch(dt_sim_time,p_lem,alpha)
        except:
            data = requests.get(db_address+'meter_intervals?meter_id='+str(self.PV.meter)).json()['results']['data'][-1]
            #data['mode_market'] = -9999. # mode_dispatch is set to default == full dispatch of PV
            data['mode_dispatch'] = 1.0 # mode_dispatch is set to default == full dispatch of PV
            requests.put(db_address+'meter_interval/'+str(data['meter_interval_id']),json=data)
            pass
		#self.battery.dispatch(dt_sim_time,p_lem,alpha)
		#self.EVCP.dispatch(dt_sim_time,p_lem,alpha)
        return

	# If market signals shouldn't be implemented (e.g. because of testing)
    def default(self,dt_sim_time):
		#HH reads price from market DB
        df_lem = requests.get(db_address+'market_intervals').json()['results']['data'][-1]
        p_lem = df_lem['p_clear']
        alpha = df_lem['alpha']
		#self.HVAC.default(dt_sim_time,p_lem,alpha)
        self.PV.default(dt_sim_time,p_lem,alpha)
		#self.battery.default(dt_sim_time,p_lem,alpha)
		#self.EVCP.default(dt_sim_time,p_lem,alpha)

# Python object class for HVAC
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
        import sys; sys.exit('HVAC table not available yet')
        if (Q_bid > 0.0) and not (self.mode == 'OFF'):
            timestamp_arrival = market.send_demand_bid(dt_sim_time, float(P_bid), float(Q_bid), 'HVAC_'+self.name) #Feedback: timestamp of arrival #C determined by market_operator
        return

    def dispatch(self,dt_sim_time,p_lem,alpha):
        import sys; sys.exit('HVAC dispatch not implemented yet')
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
