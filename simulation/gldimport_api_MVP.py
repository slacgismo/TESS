#import gridlabd_functions
import os
import pandas
import numpy
import random
#import pycurl
from io import StringIO
import json
import gridlabd

import requests

from HH_global import transformer_id, market_id

from HH_global import city, market_data, C, interval, db_address #, ip_address
from HH_global import results_folder

#These function descrbe the physical interface: read out of physical environment / API --> provide information / fill into DB

###############
# GENERAL functions for interaction of GLD and py
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

#Not needed in deployment - gets entered by utility into db
def get_houseobjects(house_name,time):
	#Get information from physical representation
	house_obj = gridlabd.get_object(house_name)
	return

#Not needed in deployment - gets entered by utility into db
def get_PVs(house_name,time):
	#import pdb; pdb.set_trace()
	PV_name = 'PV'+house_name[5:]
	PV_obj = gridlabd.get_object(PV_name)

	#Read out settings
	Q_rated = float(PV_obj['rated_power'])/1000. #kWh

	#Save in long-term memory (in the db) - accessible for market code
	parameter_string = '(timedate, Q_rated)'
	value_tuple = (time, Q_rated,)
	#myfct.set_values(PV_name+'_settings', parameter_string, value_tuple)

def get_batteries(house_name,time):
	battery_name = 'Battery'+house_name[5:]
	battery_obj = gridlabd.get_object(battery_name)

	#Read out settings
	SOC_max = float(battery_obj['E_Max'])/1000. #kWh
	soc_min = 0.2 #could be part of user settings
	soc_des = 0.5
	i_max = float(battery_obj['I_Max'].split('+')[1])
	u_max = float(battery_obj['rated_power'])/1000. #kVA
	efficiency = float(battery_obj['round_trip_efficiency'])
	Kes = float(battery_obj['Kes'])

	#Save in long-term memory (in the db) - accessible for market code
	parameter_string = '(timedate, soc_des, soc_min, SOC_max, i_max, u_max, efficiency, Kes)'
	value_tuple = (time, soc_des, soc_min, SOC_max, i_max, u_max, efficiency, Kes,)
	myfct.set_values(battery_name+'_settings', parameter_string, value_tuple)

#This connects to the ChargePoint chargers = an inverter
#No technical information is provided!!
def get_chargers(house_name,time):	
	#Get charger object
	CP_inv_name = 'EV_inverter'+house_name[5:]
	CP_inv_obj = gridlabd.get_object(CP_inv_name)

	#Save in long-term memory (in the db) - accessible for market code
	Qmax = float(CP_inv_obj['rated_power'])
	parameter_string = '(timedate, Qmax, Qset)'
	value_tuple = (time, Qmax, Qmax,) #assume that maximum is allowed
	myfct.set_values('CP'+house_name[5:]+'_settings', parameter_string, value_tuple)

def initialize_EVs(house_name,time):
	#Check if EV is connected
	EV_name = 'EV'+house_name[5:]
	try:
		EV_obj = gridlabd.get_object(EV_name)
		status = True
	except:
		status = False
	if status:
		parameter_string = '(timedate, Kev, tdep, Emax, DeltaE)'
		try:
			Kev = float(EV_obj['Kev'])
		except:
			Kev = 1.0
		try:
			tdep = pandas.to_datetime(EV_obj['tdep'])
		except:
			#Assuming that departure is in the morning
			t0 = pandas.to_datetime(time)
			t0.hours = 0
			tdep = t0 + pandas.Timedelta(hours=0) + pandas.Timedelta(minutes=random.randint(0, 60*1))
			gridlabd.set_value(EV_name,'tdep',str(tdep))
		try:
			Emax = float(EV_obj['battery_capacity'])
		except:
			Emax = 1000.0 #Set very large
		try:
			DeltaE = float(EV_obj['DeltaE'])
		except:
			DeltaE = 100.0 #100% / full charge
		if DeltaE == 0.0:
			DeltaE = 100.0

		value_tuple = (time, str(Kev), str(tdep), Emax, DeltaE,)
		myfct.set_values(EV_name+'_state_in', parameter_string, value_tuple)
	
#Simulates arrival and disconnects EV upon departure - this function should be deleted in physical system
#Therefore also no interaction with DB yet - that's in update_EV_state()
def simulate_EVs(house_name,dt_sim_time):
	EV_name = 'EV'+house_name[5:]
	EV_obj = gridlabd.get_object(EV_name)
	online_t = EV_obj['generator_status']
	CP_inv_name = 'EV_inverter'+house_name[5:]

	if dt_sim_time.hour >= 0 and dt_sim_time.hour <= 19:
		if online_t == 'OFFLINE':
			arrival = numpy.random.choice([True,False],p=[10/60.,1. - 10/60.])
			if arrival:
				#Actual physical parameters
				gridlabd.set_value(EV_name,'generator_status','ONLINE')
				soc = numpy.random.uniform(0.2,0.8)
				gridlabd.set_value(EV_name,'state_of_charge',str(soc)) #Unknow in TESS

				#Settings through User App
				Kev = numpy.random.uniform(0.5,1.5)
				gridlabd.set_value(EV_name,'Kev',str(Kev))
				tdep = dt_sim_time + pandas.Timedelta(hours=7) + pandas.Timedelta(minutes=random.randint(0, 60*1))
				gridlabd.set_value(EV_name,'tdep',str(tdep))
				DeltaE = max(numpy.random.choice(numpy.arange(5.,30.,5.),p=[1/5.]*5),(1.-soc)*100.)
				gridlabd.set_value(EV_name,'DeltaE',str(DeltaE))
				gridlabd.set_value(CP_inv_name,'EV_connected',str(1))				
	
	if online_t == 'ONLINE':
		#EV_obj = gridlabd.get_object(EV_name) #get new departure time
		if pandas.to_datetime(EV_obj['tdep']) < dt_sim_time:
			gridlabd.set_value(EV_name,'generator_status','OFFLINE')
			gridlabd.set_value(CP_inv_name,'EV_connected',str(-1))
	#import pdb; pdb.set_trace()

###########################
#
# These functions here describe the writing from physical representation to the DB
#
###########################

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

# Measures current power at PV inverter
def update_PV_state(PV,dt_sim_time):
	PV_obj = gridlabd.get_object('PV_'+str(PV.id)) # In GLD, this is actually the state from one interval before

	Qmtp = float(PV_obj['P_Out'][1:].split('+')[0])/1000. # W -> kW
	E = Qmtp/(3600./interval)

	#Post state to TESS DB (simulation time) - should have an alpha_t
	data = {'rate_id':1,'meter_id':PV.meter,'start_time':str(dt_sim_time),'end_time':str(dt_sim_time+pandas.Timedelta(minutes=5)),
		'e':E,'qmtp':Qmtp,'p_bid':-1000.,'q_bid':-1000.,'is_bid':True}
	requests.post(db_address+'meter_interval',json=data) #with dummy bid

def update_CP_state(CP_name,dt_sim_time):
	#Check if EV is there
	CP_obj = gridlabd.get_object(CP_name)
	EV_name = 'EV_'+CP_name.split('_')[-1]
	EV_obj = gridlabd.get_object(EV_name)
	#New car arrived
	#import pdb; pdb.set_trace()
	#print(int(CP_obj['EV_connected']))
	if int(CP_obj['EV_connected']) == 1: #This should be whatever signal which pushes the new that a car arrived/disconnected
		#import pdb; pdb.set_trace()
		Kev = float(EV_obj['Kev'])
		tdep = pandas.to_datetime(EV_obj['tdep'])
		Emax = float(EV_obj['battery_capacity'])
		DeltaE = float(EV_obj['DeltaE'])
		#Write to database
		parameter_string = '(timedate, Kev, tdep, Emax, DeltaE)'
		value_tuple = (str(dt_sim_time), str(Kev), str(tdep), Emax, DeltaE,)
		myfct.set_values(EV_name+'_state_in', parameter_string, value_tuple)
		#Reset action pointer
		gridlabd.set_value(CP_name,'EV_connected',str(0))
	elif int(CP_obj['EV_connected']) == -1:
		gridlabd.set_value(CP_name,'EV_connected',str(0))

def update_battery_state(battery_name,dt_sim_time):
	#Get information from physical representation
	batt_obj = gridlabd.get_object(battery_name)

	#Save in long-term memory (in the db) - accessible for market code
	parameter_string = '(timedate, soc_rel)' #timedate TIMESTAMP PRIMARY KEY, 
	value_tuple = (dt_sim_time, float(batt_obj['state_of_charge']),)
	myfct.set_values(battery_name+'_state_in', parameter_string, value_tuple)

def update_EV_state(battery_name,dt_sim_time):
	#Get information from physical representation
	EV_obj = gridlabd.get_object(EV_name)

	#Save in long-term memory (in the db) - accessible for market code
	E = float(EV_obj['state_of_charge'])
# 	treq = 
# trem
# Eest
# Qset
# Qobs


	parameter_string = '(timedate, E, treq, trem, Qset, Qobs)' #timedate TIMESTAMP PRIMARY KEY, 
	value_tuple = (dt_sim_time, E, treq, trem, Qset, Qobs,)
	myfct.set_values(battery_name+'_state_in', parameter_string, value_tuple)

###########################
#
# These functions here describe the implementation of the market results (writing result to state)
#
###########################

def dispatch_PV(PV,dt_sim_time):
	#import pdb; pdb.set_trace()
	#Should refer to DB and not to python object
	if PV.mode == 1:
		# No constraint
		gridlabd.set_value('PV_'+str(PV.id),'P_Out',str(PV.Q_bid)) #What if larger?
	elif PV.mode > 0:
		gridlabd.set_value('PV_'+str(PV.id),'P_Out',str(PV.Q_bid*PV.mode))
	else:
		gridlabd.set_value('PV_'+str(PV.id),'P_Out','0.0')

###############
# System Operator
###############

#Get system state and available capacity

def get_systemstate(dt_sim_time):
	# Available capacity

	available_capacity = 1000. + numpy.random.uniform(-100.,100.) # Should be an INPUT from control room
	data = {'transformer_id':transformer_id,'feeder':'IEEE123','capacity':available_capacity}
	#data = {'feeder':'IEEE123','capacity':available_capacity}
	requests.put(db_address+'transformer/'+str(transformer_id), json=data)
	
	# Used capacity

	load_SLACK = float(gridlabd.get_object('node_149')['measured_real_power'][:-2])/1000. # measured_real_power in [W] --> [kW]
	data = {'transformer_id':transformer_id,'import_capacity':available_capacity,'export_capacity':0.,'q':load_SLACK,'unresp_load':load_SLACK,'start_time':str(dt_sim_time),'end_time':str(dt_sim_time+pandas.Timedelta(seconds=interval))}
	requests.post(db_address+'transformer_interval',json=data)

	# Supply cost : from WECS/control room

	p = numpy.random.uniform()
	if p > 1.0/20.0:
		supply_cost = 0.05
	else:
		supply_cost = 0.2

	data = {'start_time':str(dt_sim_time),'end_time':str(dt_sim_time+pandas.Timedelta(seconds=interval)),'p_bid':p,'q_bid':available_capacity,'is_supply':True,'comment':'','market_id':market_id}
	requests.post(db_address+'bids',json=data)
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