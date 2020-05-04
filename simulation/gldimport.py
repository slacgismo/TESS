#import gridlabd_functions
import os
import pandas
#import pycurl
from io import StringIO
import json
import gridlabd

import mysql_functions as myfct

from HH_global import city, market_data, C

#These function descrbe the physical interface: read out of physical environment / API --> provide information / fill into DB

###############
# GENERAL
###############

#Initialization: Find relevant objects and appliances

def find_objects(criteria) :
	finder = criteria.split("=")
	if len(finder) < 2 :
		raise Exception("find(criteria='key=value'): criteria syntax error")
	objects = gridlabd.get("objects")
	result = []
	for name in objects :
		try:
			item = gridlabd.get_object(name)
			if finder[0] in item.keys() and item[finder[0]] == finder[1] :
				result.append(name)
		except:
			pass
	return result

#Get specific object

def get(obj):
	finder = obj.split("=")
	return

###############
# HOUSEHOLDS
###############

#Get house characteristics and write to DB

def get_houseobjects(house_name,time):
	#Get information from physical representation
	house_obj = gridlabd.get_object(house_name) #GUSTAVO: API implementation
	#Switch off default control
	gridlabd.set_value(house_name,'thermostat_control','NONE')
	gridlabd.set_value(house_name,'system_mode','OFF')
	
	#Read out settings
	k = float(house_obj['k'])
	T_max = float(house_obj['T_max'])
	cooling_setpoint = float(house_obj['cooling_setpoint'])
	cooling_demand = float(house_obj['cooling_demand']) #cooling_demand is in kW
	T_min = float(house_obj['T_min'])
	heating_setpoint = float(house_obj['heating_setpoint'])
	heating_demand = float(house_obj['heating_demand']) #heating_demand is in kW

	#Save in long-term memory (in the db) - accessible for market code
	parameter_string = '(timedate, k, T_min, heating_setpoint, T_max, cooling_setpoint)' #timedate TIMESTAMP PRIMARY KEY, 
	value_tuple = (time, k,T_min,heating_setpoint,T_max,cooling_setpoint,)
	myfct.set_values(house_name+'_settings', parameter_string, value_tuple)

	return

def get_batteries(house_name,time):
	battery_name = 'Battery'+house_name[5:]
	battery_obj = gridlabd.get_object(battery_name)

	#Read out settings
	import pdb; pdb.set_trace()
	SOC_max = float(battery_obj['E_Max'])/1000. #kWh
	SOC_min = 0.2*SOC_max #could be part of user settings
	i_max = float(battery_obj['I_Max'].split('+')[1])
	u_max = float(battery_obj['rated_power'])/1000. #kVA
	efficiency = float(battery_obj['base_efficiency'])
	k = float(battery_obj['k'])

	#Save in long-term memory (in the db) - accessible for market code
	parameter_string = '(timedate, SOC_min, SOC_max, i_max, u_max, efficiency, k)'
	value_tuple = (time, SOC_min, SOC_max, i_max, u_max, efficiency, k,)
	myfct.set_values(battery_name+'_settings', parameter_string, value_tuple)
	
#Get house state and write to db

def update_house_state(house_name,dt_sim_time):
	#Get information from physical representation
	house_obj = gridlabd.get_object(house_name)

	#Determine principal mode
	#DAVE: this is a heuristic
	T_air = float(house_obj['air_temperature'])
	if T_air >= (float(house_obj['heating_setpoint']) + float(house_obj['cooling_setpoint']))/2:
		mode = 'COOL'
	else:
		mode = 'HEAT'
	actual_mode = house_obj['system_mode']

	#Save in long-term memory (in the db) - accessible for market code
	parameter_string = '(timedate, mode, actual_mode, T_air, q_heat, q_cool)' #timedate TIMESTAMP PRIMARY KEY, 
	value_tuple = (dt_sim_time, mode, actual_mode, T_air, float(house_obj['heating_demand']),float(house_obj['cooling_demand']),)
	myfct.set_values(house_name+'_state_in', parameter_string, value_tuple)
	return

###############
# Market Operator
###############

#Get supply specifications

def get_slackload(dt_sim_time): #GUSTAVO: this information comes from HCE systems
	load_SLACK = float(gridlabd.get_object('node_149')['measured_real_power'])/1000. #measured_real_power in [W]
	#C - can also come from HCE setting
	myfct.set_values('system_load', '(timedate, C, slack_load)', (dt_sim_time, C, load_SLACK,))
	return

###############
# WHOLESALE SUPPLIER
###############

#This should be coming from HCE's system or other real-time portal

def get_WSprice(dt_sim_time):
	df_WS = pandas.read_csv('glm_generation_'+city+'/'+market_data,parse_dates=[-1],index_col=[0])
	df_WS = pandas.DataFrame(index=pandas.to_datetime(df_WS.index.astype(str)),columns=df_WS.columns,data=df_WS.values.astype(float))
	p_WS = float(df_WS['RT'].loc[dt_sim_time]) 
	myfct.set_values('WS_supply', '(timedate, WS_price)', (dt_sim_time, p_WS,))
	return

###############
# NOT USED
###############

def sort_list(unsorted_list):
	sorted_list = []
	if unsorted_list:
		no = [int(x.split('_')[-1]) for x in unsorted_list]
		d = dict(zip(no,unsorted_list))
		for i in range(1,max(no)+1):
			try:
				sorted_list.append(d[i])
			except:
				pass
	return 

def sort_batteries(batteries):
	batterylist_unsorted = [] #;
	EVlist_unsorted = []

	#Batteries not ordered accoridng to house numbers
	for battery in batteries:
		#name = battery['name']
		#if int(battery['name'].split('_')[-1]) < amount:
		if 'Battery_' in battery:
			batterylist_unsorted.append(battery)
		elif 'EV_' in battery:
			EVlist_unsorted.append(battery)

	batterylist = batterylist_unsorted
	#batterylist = sort_list(batterylist_unsorted)
	EVlist = EVlist_unsorted
	#EVlist = sort_list(EVlist_unsorted)

	return batterylist, EVlist

def sort_pvs(pvs):
	pvlist_unsorted = [];

	#Batteries not ordered accoridng to house numbers
	for pv in pvs:
		pvlist_unsorted.append(pv)

	#Sort PVs
	
	pv_list = []
	if pvlist_unsorted:
		pvlist_no = [int(x.split('_')[-1]) for x in pvlist_unsorted]
		d = dict(zip(pvlist_no,pvlist_unsorted))
		for i in range(1,max(pvlist_no)+1):
			try:
				pv_list.append(d[i])
			except:
				pass

	pvinv_list = []
	for pv in pv_list:
		#inverter_name = gridlabd_functions.get(pv,'parent')
		inverter_name = 'PV_inverter_' + pv[3:]
		pvinv_list += [inverter_name]

	return pv_list, pvinv_list