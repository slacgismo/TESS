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
	houses_names = gldimport.find_objects('class=house')
	for house_name in houses_names:
		gldimport.get_houseobjects(house_name,start_time_str)

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
	#global df_prices, df_WS;
	#df_prices = pandas.DataFrame(columns=['clearing_price','clearing_quantity','unresponsive_loads','slack_t-1'])
	#df_WS = pandas.read_csv('glm_generation_'+city+'/'+market_data,parse_dates=[-1],index_col=[0])
	#df_WS = pandas.DataFrame(index=pandas.to_datetime(df_WS.index.astype(str)),columns=df_WS.columns,data=df_WS.values.astype(float))
	
	#Align weekdays of Pecan Street Data and WS: For yearly data only (TESS, not powernet)
	# year_sim = parser.parse(gridlabd.get_global('clock')).replace(tzinfo=None).year
	# first_weekday = pandas.Timestamp(year_sim,1,1).weekday() 
	# first_weekday_WS = df_WS.index[0].weekday()
	# while not first_weekday_WS == first_weekday:
	# 	df_WS = df_WS.iloc[1:]
	# 	first_weekday_WS = df_WS.index[0].weekday()
	# df_WS =df_WS.iloc[:(365*24*12)] #Should not be hardcoded
	# df_WS.index = pandas.date_range(pandas.Timestamp(year_sim,1,1,0),pandas.Timestamp(year_sim,12,31,23,55),freq='5min')

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
		#Get external information and information through APIs
		############

		global houses;
		for house in houses:
			#gldimport.update_settings() #If user changes settings in API, this should be called
			gldimport.update_house_state(house.name,dt_sim_time)
		
		global retailer;
		gldimport.get_slackload(dt_sim_time)
		gldimport.get_WSprice(dt_sim_time)

		############
		#Market side / no phycial APIs involved
		############

		#Get air temperature, determine mode
		for house in houses:
			#house.update_settings()
			#HHfct.update_houseobjects(house_name,start_time_str)
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

		############
		#Get external information and information through APIs
		############

		#HHs determine dispatch based on price
		for house in houses:
			house.determine_dispatch(dt_sim_time)

		lem.reset()
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


