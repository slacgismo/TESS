import test_import
import os
print('os')
#import gridlabd_functions
#print('gridlabd_functions')
#import mysql_functions
#print('mysql_functions')
#from HH_global import *
import random
import pandas
#import pycurl
import json
#from StringIO import StringIO
import numpy as np
import datetime
from datetime import timedelta
from dateutil import parser

print('Global initialize')

"""Simulation parameters"""

#number of flexible houses
global flexible_houses
flexible_houses = 300

#Capacity restriction
global C
C = 2500 #in kW

#Start and end times
global start_tim, end_time, interval
start_time = datetime.datetime(2016, 7, 1, 0, 0)
end_time = datetime.datetime(2016, 7, 7, 23, 59)
interval = 300 #in seconds

#precision in bidding and clearing price
global prec
prec = 4

#mysql databases
global table_list
table_list = ['buy_bids','capacity_restrictions','clearing_pq','market_prices','supply_bids']
table_list += ['unresponsive_loads','market_bus_meter','market_buses','market_house_meter','market_houses']
table_list += ['market_HVAC_meter','market_HVAC','market_battery_meter','market_battery']
table_list += ['market_pv','market_pv_meter','WS_market','market_appliance_meter','market_appliances','market_EV','market_EV_meter']

#interval of market clearing
#interval = int(gridlabd_functions.get('retail','interval')['value'])

"""Model parameters"""
#Store in mysql database?

"""Houses"""

global houses;
houses = test_import.find('class=house')
#print(houses)

"""Batteries"""

batteries = test_import.find('class=battery')
batterylist_unsorted = [] #;
EVlist_unsorted = []

#Batteries not ordered accoridng to house numbers
for battery in batteries:
	name = battery['name']
	#if int(battery['name'].split('_')[-1]) < amount:
	if 'Battery_' in name:
		batterylist_unsorted.append(name)
	elif 'EV_' in name:
		EVlist_unsorted.append(name)

#Sort batteries
global batterylist
batterylist = []
if batterylist_unsorted:
	batterylist_no = [int(x.split('_')[-1]) for x in batterylist_unsorted]
	d = dict(zip(batterylist_no,batterylist_unsorted))
	for i in range(1,max(batterylist_no)+1):
		try:
			batterylist.append(d[i])
		except:
			pass

"""EVs"""

#Sort EVs
global EVlist
EVlist = []
if EVlist_unsorted:
	EVlist_no = [int(x.split('_')[-1]) for x in EVlist_unsorted]
	d = dict(zip(EVlist_no,EVlist_unsorted))
	for i in range(1,max(EVlist_no)+1):
		try:
			EVlist.append(d[i])
		except:
			pass

"""PVs"""

#Get list of battery objects in GLM file and assign to global GLD variable "batterylist"
pvs = test_import.find('class=solar')
pvlist_unsorted = [];

#Batteries not ordered accoridng to house numbers
for pv in pvs:
	name = pv['name']
	#if int(pv['name'].split('_')[-1]) < amount:
	pvlist_unsorted.append(name)

#Sort PVs
global pvlist
pvlist = []
if pvlist_unsorted:
	pvlist_no = [int(x.split('_')[-1]) for x in pvlist_unsorted]
	d = dict(zip(pvlist_no,pvlist_unsorted))
	for i in range(1,max(pvlist_no)+1):
		try:
			pvlist.append(d[i])
		except:
			pass

global pvinv_list
pvinv_list = []
for pv in pvlist:
	#inverter_name = gridlabd_functions.get(pv,'parent')
	inverter_name = 'PV_inverter_' + pv[3:]
	pvinv_list += [inverter_name]

# mysql_functions.clear_databases()
print('Initialize finished')
