import gridlabd
import pandas as pd
import time
import requests

from HH_global import start_time_str, end_time_str
from HH_global import db_address #, user_name, pw

#First simulation
if False:
	#Set up market
	data = {'source': 'Ercot', 'ts': 5, 'p_max': 10000}
	market = requests.post(db_address+'market',json=data,auth=(user_name,pw))
	#Set up utility
	data = {'name':'HCE','subscription_start':str(pd.Timestamp(start_time_str)),'subscription_end':str(pd.Timestamp(end_time_str))}
	requests.post(db_address+'utility',json=data,auth=(user_name,pw))
	utility = requests.get(db_address+'utilities',json=data,auth=(user_name,pw))
	#Set up rate
	data = {'description':'net_metering'}
	requests.post(db_address+'rate',json=data,auth=(user_name,pw))

	#Set up users
	#Address
	user_no = 1
	data = {'address':'Main Street '+str(user_no),'city':'Aspen','country':'US','postal_code':'00000'}
	requests.post(db_address+'address',json=data,auth=(user_name,pw))
	#Service location
	data = {'address_id':user_no,'map_location':'somewhere'}
	requests.post(db_address+'service_location',json=data,auth=(user_name,pw))
	#Home hub
	data = {'service_location_id':user_no,'market_id':1}
	requests.post(db_address+'home_hub',json=data,auth=(user_name,pw))
	#Meter
	data = {'utility_id':1,'service_location_id':user_no,'home_hub_id':user_no,'feeder':'IEEE123','substation':'HCE-Xcel','meter_type':'Residential'}
	requests.post(db_address+'meter',json=data,auth=(user_name,pw))
	#PV
	data = {'home_hub_id':user_no,'meter_id':user_no,'q_rated':4000,'is_active':True}
	requests.post(db_address+'pv',json=data,auth=(user_name,pw))
	
	#Meter interval
	#data = {'meter_id':1,'rate_id':1,'start_time':str(pd.Timestamp(2000,1,1,0,0)),'end_time':str(pd.Timestamp(2000,1,1,0,5)),'e':0.0,'qmtp':0.0,'p_bid':0.0,'q_bid':0,'is_bid':True}
	#requests.post(db_address+'meter_interval',json=data,auth=(user_name,pw))
	#mis = requests.get(db_address+'meter_interval')
	#Market interval


#Start simulation
gridlabd.command('model.glm')
gridlabd.start('wait')
