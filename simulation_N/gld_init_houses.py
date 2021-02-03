print('Next module imported')

import os
print('os')
import gridlabd_functions
print('gridlabd_functions')
import mysql_functions
print('mysql_functions')
from HH_global import *
import random
import pandas
#import pycurl
import json
from StringIO import StringIO
import numpy as np
import datetime
from datetime import timedelta
from dateutil import parser



def initialize():
	mysql_functions.clear_databases()

	print('Initialize')
	#Start time of simulation is '2017-07-01 12:00:00' EST+5 - get this from GLOBALS or likewise
	interval = int(gridlabd_functions.get('retail','interval')['value']) #in seconds
	#prev_timedate = datetime.datetime(2015, 6, 30, 23, 60  - (interval/60))
	#prev_timedate = datetime.datetime(2015, 7, 1, 4, 60  - (interval/60))

	dt = parser.parse(os.getenv("clock"))
	prev_timedate = dt - timedelta(minutes=interval/60)

	#Get list of house objects in GLM file and assign to global GLD variable "houselist"
	#houses = gridlabd_functions.find('class=house')
	#houselist = [];

	#Read in wholesale market prices
	df_prices = pandas.read_csv('ercot_2017.csv',parse_dates=[0])
	mysql_functions.set_WSmarket(df_prices)

	#Check if downgrading pycurl changes gridlabd_functions
	# from sqlalchemy import create_engine
	# engine = create_engine("mysql://root:gridlabd@127.0.0.1/gridlabd")
	# con = engine.connect()
	# df_prices.to_sql(name='WS_market',con=con,if_exists='append')
	# con.close()

	for house in houselist :
		#houselist.append(name)	
		#Fills TABLE market_houses (can this be done via GridlabD directly?)	
		mysql_functions.set_values('market_houses', '(house_name)',(house,))
		
		#Fills TABLE market_appliances (can this be done via GridlabD directly?)
		#HVAC
		k = float(gridlabd_functions.get(house,'k')['value'])
		T_min = float(gridlabd_functions.get(house,'T_min')['value'])
		T_max = float(gridlabd_functions.get(house,'T_max')['value'])
		heat_q = float(gridlabd_functions.get(house,'heating_demand')['value'][1:-3]) #heating_demand is in kW
		hvac_q = float(gridlabd_functions.get(house,'cooling_demand')['value'][1:-3]) #cooling_demand is in kW
		#mysql_functions.set_values('market_HVAC', '(house_name,appliance_name,k,T_min,T_max,P_heat,P_cool)',(house['name'],'HVAC_'+str(houses.index(house)+1),k,T_min,T_max,heat_q,hvac_q,))
		mysql_functions.set_values('market_HVAC', '(house_name,appliance_name,k,T_min,T_max,P_heat,P_cool)',(house,'HVAC_'+house[4:],k,T_min,T_max,heat_q,hvac_q,))

		#Fills TABLE market_appliance_meter
		#HVAC
		heating_setpoint = float(gridlabd_functions.get(house,'heating_setpoint')['value'][1:-5])
		cooling_setpoint = float(gridlabd_functions.get(house,'cooling_setpoint')['value'][1:-5])	
		#Set values for previous period, i.e. start - interval
		#mysql_functions.set_values('market_HVAC_meter', '(system_mode,heating_setpoint,cooling_setpoint,active,timedate,appliance_id)',('OFF',heating_setpoint,cooling_setpoint,0,prev_timedate,houses.index(house)+1,))
		mysql_functions.set_values('market_HVAC_meter', '(system_mode,av_power,heating_setpoint,cooling_setpoint,active,timedate,appliance_id)',('OFF',0.0,heating_setpoint,cooling_setpoint,0,prev_timedate,int(house.split('_')[-1]),))

	#gridlabd_functions.set('houselist',';'.join(houselist))

	#batteries = gridlabd_functions.find('class=battery')

	for battery in batterylist:
		house_name = 'GLD_'+battery[8:]
		#Fills TABLE market_appliances
		SOC_max = float(gridlabd_functions.get(battery,'battery_capacity')['value'][:-3])/1000 #Wh in Gridlabd -> kWh
		str_i_max = gridlabd_functions.get(battery,'I_Max')['value'][:-2].replace('-','+')
		i_max = str_i_max.split('+')[1]
		u_max = float(gridlabd_functions.get(battery,'V_Max')['value'][:-2])*float(i_max)/1000 #W -> kW #better inverter?
		eff = float(gridlabd_functions.get(battery,'base_efficiency')['value'][:-5])
		mysql_functions.set_values('market_battery', '(house_name,appliance_name,appliance_id,SOC_max,u_max,eff)',(house_name,battery,int(battery.split('_')[-1]),SOC_max,u_max,eff,))
		#Fills TABLE market_appliance_meter
		SOC_0 = float(gridlabd_functions.get(battery,'state_of_charge')['value'][:-3])*SOC_max
		mysql_functions.set_values('market_battery_meter', '(SOC,active,timedate,appliance_id)',(SOC_0,0,prev_timedate,int(battery.split('_')[-1]),))

	for EV in EVlist:
		house_name = 'GLD_'+EV[3:]
		#Fills TABLE market_appliances
		SOC_max = float(gridlabd_functions.get(EV,'battery_capacity')['value'][:-3])/1000 #Wh in Gridlabd -> kWh
		str_i_max = gridlabd_functions.get(EV,'I_Max')['value'][:-2].replace('-','+')
		i_max = str_i_max.split('+')[1]
		u_max = float(gridlabd_functions.get(EV,'V_Max')['value'][:-2])*float(i_max)/1000 #W -> kW #better inverter?
		eff = float(gridlabd_functions.get(EV,'base_efficiency')['value'][:-5])
		charging_type = gridlabd_functions.get(EV,'charging_type')['value']
		k = gridlabd_functions.get(EV,'k')['value']
		mysql_functions.set_values('market_EV', '(house_name,appliance_name,appliance_id,SOC_max,u_max,eff,charging_type,k)',(house_name,EV,int(EV.split('_')[-1]),SOC_max,u_max,eff,charging_type,k,))
		#Fills TABLE market_appliance_meter
		mysql_functions.set_values('market_EV_meter', '(connected,SOC,active,timedate,appliance_id)',(0,0,0,prev_timedate,int(EV.split('_')[-1]),))
		#Set all cars offline/disconnected in the beginning
		gridlabd_functions.set(EV,'generator_status','OFFLINE')

	df_events = pandas.read_csv('EV_events.csv',index_col=[0])
	df_events.to_csv('EV_events_pop.csv')

	# PVs = gridlabd_functions.find('class=solar')

	for pv in pvlist:
		house_name = 'GLD_'+pv[3:]
		#Fills TABLE market_appliances
		inverter_name = 'PV_inverter_' + pv[3:]
		rated_power = float(gridlabd_functions.get(inverter_name,'rated_power')['value'][:-3])/1000
		mysql_functions.set_values('market_pv', '(house_name,appliance_name,inverter_name,appliance_id,rated_power)',(house_name,pv,inverter_name,int(pv.split('_')[-1]),rated_power,))
		#Fills TABLE market_appliance_meter
		production = float(gridlabd_functions.get(inverter_name,'P_Out')['value'][:-3])/1000
		mysql_functions.set_values('market_pv_meter', '(P_Out,timedate,appliance_id)',(production,prev_timedate,int(pv.split('_')[-1]),))

	return dt