import gldimport
import os
import random
import pandas
import json
import numpy as np
import datetime
from datetime import timedelta
from dateutil import parser
import time

import mysql_functions as myfct

import HH_functions as HHfct
from HH_functions import House

import market_functions as Mfct
from market_functions import Market
from market_functions import MarketOperator

import supply_functions as Sfcts
from supply_functions import WSSupplier

#import battery_functions as Bfct
#import EV_functions as EVfct
#import PV_functions as PVfct


from HH_global import results_folder, flexible_houses, C, p_max, market_data, which_price, city, month
from HH_global import interval, prec, price_intervals, allocation_rule, unresp_factor, load_forecast
from HH_global import FIXED_TARIFF, include_SO, EV_data, start_time_str

table_list = ['house_1_settings','house_1_state_in','house_1_state_out','house_2_settings','house_2_state_in','house_2_state_out']
table_list += ['house_3_settings','house_3_state_in','house_3_state_out','house_4_settings','house_4_state_in','house_4_state_out']
table_list += ['house_5_settings','house_5_state_in','house_5_state_out','house_6_settings','house_6_state_in','house_6_state_out']
table_list += ['PV_1_settings','PV_1_state_in','PV_1_state_out','PV_2_settings','PV_2_state_in','PV_2_state_out']
table_list += ['PV_3_settings','PV_3_state_in','PV_3_state_out','PV_4_settings','PV_4_state_in','PV_4_state_out']
table_list += ['PV_5_settings','PV_5_state_in','PV_5_state_out','PV_6_settings','PV_6_state_in','PV_6_state_out']
table_list += ['battery_1_settings','battery_1_state_in','battery_1_state_out','battery_2_settings','battery_2_state_in','battery_2_state_out']
table_list += ['battery_3_settings','battery_3_state_in','battery_3_state_out','battery_4_settings','battery_4_state_in','battery_4_state_out']
table_list += ['battery_5_settings','battery_5_state_in','battery_5_state_out','battery_6_settings','battery_6_state_in','battery_6_state_out']
table_list += ['CP_1_settings','CP_2_settings','CP_3_settings','CP_4_settings','CP_5_settings','CP_6_settings']
table_list += ['EV_1_arrival','EV_2_arrival','EV_3_arrival','EV_4_arrival','EV_5_arrival','EV_6_arrival']
table_list += ['system_load','WS_supply','supply_bids','buy_bids','clearing_pq']

########
#To Do
#
#- customers changing settings not considered yet
#- include mode changes by Supplier or LEMoperator, e.g. into emergency mode
#- check and update mode
########

#Sets up house agents/Home Hubs with settings
def on_init(t):
	global t0;
	t0 = time.time()

	#Empty databases
	myfct.clear_databases(table_list)
	try:
		os.remove(results_folder + '/df_supply_bids.csv')
		os.remove(results_folder + '/df_demand_bids.csv')
		os.remove(results_folder + '/df_prices.csv')
	except:
		pass

	#PHYSICS: Find objects and fill local DB with relevant settings
	#import pdb; pdb.set_trace()
	houses_names = gldimport.find_objects('class=house')
	for house_name in houses_names:
		gldimport.get_houseobjects(house_name,start_time_str)
		gldimport.get_PVs(house_name,start_time_str)
		gldimport.get_batteries(house_name,start_time_str)
		gldimport.get_chargers(house_name,start_time_str) #Gets charger inverters and maximum charging rates
		gldimport.initialize_EVs(house_name,start_time_str) #Checks if EVs are connected

	#MARKET: Create house agents
	global houses;
	houses = []
	for house_name in houses_names:
		houses += [HHfct.create_agent_house(house_name)]

	#Create WS supplier
	global retailer;
	retailer = WSSupplier()

	#Create market operator
	global LEM_operator;
	LEM_operator = MarketOperator(interval,p_max)

	print('Initialize finished after '+str(time.time()-t0))
	return True

def init(t):
	print('Objective-specific Init')
	return True

#Global precommit
#Should be mostly moved to market precommit
def on_precommit(t):
	dt_sim_time = parser.parse(gridlabd.get_global('clock')).replace(tzinfo=None)

	#Run market only every five minutes
	global LEM_operator;
	if not ((dt_sim_time.second == 0) and (dt_sim_time.minute % (LEM_operator.interval/60) == 0)):
		return t
	
	else: #interval in minutes #is not start time
		print('Start precommit: '+str(dt_sim_time))

		############
		#Imitates physical process of arrival
		############

		global houses;
		#Simulates arrival and disconnects EV upon departure - this function should be deleted in physical system
		for house in houses:
			gldimport.simulate_EVs(house.name,dt_sim_time)

		############
		#Get external information and information through APIs: HEILA --> market
		############

		for house in houses:
			#gldimport.update_settings() #If user changes settings in API, this should be called
			gldimport.update_house_state(house.name,dt_sim_time)
			if house.PV:
				gldimport.update_PV_state(house.PV.name,dt_sim_time)
			if house.battery:
				gldimport.update_battery_state(house.battery.name,dt_sim_time)
			if house.EVCP:
				gldimport.update_CP_state(house.EVCP.name,dt_sim_time)
		
		global retailer;
		gldimport.get_slackload(dt_sim_time)
		gldimport.get_WSprice(dt_sim_time)

		############
		#Market side / no phycial APIs involved
		############

		#Get air temperature, determine mode
		for house in houses:
			#Reads in information and updates python objects (house + appliances)
			house.update_state(dt_sim_time)

		#Market Operator creates market for t
		lem = LEM_operator.create_market(name='LEM')

		#Retailer: unresponsive load and supply function
		retailer.bid_supply(dt_sim_time,lem)

		#Houses form bids and submit them to the market IS (central market DB)
		for house in houses:
			house.bid(dt_sim_time,lem)

		#Market processes bids and clears the market
		lem.process_bids(dt_sim_time)
		lem.clear_lem(dt_sim_time)

		#HHs determine dispatch based on price
		for house in houses:
			house.determine_dispatch(dt_sim_time)

		lem.reset()

		############
		# Implemet dispatch
		############

		for house in houses:
			#gldimport.update_settings() #If user changes settings in API, this should be called
			#gldimport.update_house_state(house.name,dt_sim_time)
			if house.PV:
				gldimport.dispatch_PV(house.PV.name,dt_sim_time)

		return t

def on_term(t):
	print('Simulation ended, saving results')
	saving_results()

	global t0;
	t1 = time.time()
	print('Time needed (min):')
	print((t1-t0)/60)
	return None

def save_databases(timestamp=None):
	#mycursor.execute('SHOW TABLES')
	#table_list = mycursor.fetchall()  
	mydb, mycursor = myfct.connect()
	for table_name in table_list:
		query = 'SELECT * FROM '+table_name
		df = pandas.read_sql(query, con=mydb)
		df.to_csv(results_folder+'/'+table_name+'_'+str(timestamp)+'.csv')

	print('Databases saved')
	return

def saving_results():
	#Saving globals
	file = 'HH_global.py'
	new_file = results_folder+'/HH_global.py'
	glm = open(file,'r') 
	new_glm = open(new_file,'w') 
	j = 0
	for line in glm:
	    new_glm.write(line)
	glm.close()
	new_glm.close()

	#Saving mysql databases
	save_databases()
	myfct.clear_databases(table_list) #empty up database

	#Do evaluations
	return

#Object-specific precommit
def precommit(obj,t) :
	print(t)
	tt =  int(300*((t/300)+1))
	print('Market precommit')
	print(tt)
	return gridlabd.NEVER #t #True #tt 


