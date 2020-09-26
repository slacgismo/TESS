#This is only for the minimum viable product (PV)
import requests
import gldimport_api_MVP as gldimport
import os
import random
import pandas
import json
import numpy as np
import datetime
from datetime import timedelta
from dateutil import parser
import time

import HH_functions as HHfct
# from HH_functions import House

import market_functions as Mfct
from market_functions import Market
from market_functions import MarketOperator

import supply_functions as Sfcts
from supply_functions import WSSupplier

#import battery_functions as Bfct
#import EV_functions as EVfct
#import PV_functions as PVfct

from HH_global import db_address #, user_name, pw
from HH_global import results_folder, flexible_houses, C, p_max, market_data, which_price, city, month
from HH_global import interval, prec, price_intervals, allocation_rule, unresp_factor, load_forecast
from HH_global import FIXED_TARIFF, include_SO, EV_data, start_time_str

#True if physical model is simulated by GLD
gld_simulation = True

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

	# Get users and create house agents
	hh_list = requests.get(db_address+'home_hubs').json()['results']['data']
	hh_ids = []
	for hh in hh_list:
		hh_ids += [hh['home_hub_id']]
	global houses;
	houses = []
	for hh_id in hh_ids:
		houses += [HHfct.create_agent_house(hh_id)]

	#Create WS supplier
	global retailer;
	retailer = WSSupplier()

	#Create market operator
	global LEM_operator;
	LEM_operator = MarketOperator(interval,p_max) #Does that need to be updated based on DB?

	#Create db_transformer_meter (not yet as DB)
	db_transformer_meter = pandas.DataFrame(columns=['system_state','supply_cost','available_capacity','current_load','unresp_demand'])
	db_transformer_meter.to_csv(results_folder+'/db_transformer_meter.csv')

	return True

# At each market interval : bidding, clearing, and dispatching
def on_precommit(t):

	#Run market only every five minutes
	dt_sim_time = parser.parse(gridlabd.get_global('clock')).replace(tzinfo=None)
	global LEM_operator;
	if not ((dt_sim_time.second == 0) and (dt_sim_time.minute % (LEM_operator.interval/60) == 0)):
		return t
	
	else: #interval in minutes #is not start time
		print('Start precommit: '+str(dt_sim_time))

		import pdb; pdb.set_trace()
		# Check clock and if it's actually five minutes

		############
		#Imitates physical process of EV arrival
		############

		# global houses;
		# #Simulates arrival and disconnects EV upon departure - this function should be deleted in physical system
		# for house in houses:
		# 	gldimport.simulate_EVs(house.name,dt_sim_time)

		############
		# Physical info : physical model --> TESS DB
		############

		# GLD --> DB
		if gld_simulation:
			# Houses / Load
			for house in houses:
				#gldimport.update_settings() #If user changes settings in API, this should be called
				#if house.HVAC:
				#	gldimport.update_house_state(house.name,dt_sim_time) #For HVAC systems
				if house.PV:
					gldimport.update_PV_state(house.PV,dt_sim_time)
				#if house.battery:
				#	gldimport.update_battery_state(house.battery.name,dt_sim_time)
				#if house.EVCP:
				#	gldimport.update_CP_state(house.EVCP.name,dt_sim_time)
			# External information : system / grid
			gldimport.get_systemstate(dt_sim_time) # --> TABLE transformer_meter
			# External information : supply costs
			gldimport.get_supplycosts(dt_sim_time) # --> TABLE transformer_meter
		# Real-world implementation --> DB
		else:
			import sys; sys.exit('Physical data comes from lab/field: Not implemented yet')

		############
		#Market side / no phycial APIs involved
		############

		#Get air temperature, determine mode
		for house in houses:
			#Reads in information from DB and updates python objects (house + appliances)
			house.update_state(dt_sim_time)

		#Market Operator creates market for t
		lem = LEM_operator.create_market(name='LEM')

		#Retailer: unresponsive load and supply function
		retailer.bid_supply(dt_sim_time,lem)
		retailer.bid_unrespload(dt_sim_time,lem)

		#Houses form bids and submit them to the market IS (central market DB)
		for house in houses:
			house.bid(dt_sim_time,lem)

		#Market processes bids and clears the market
		#lem.process_bids(dt_sim_time) # only needed if separate sending and processing of bids (not the case if identical DB for meter_interval and market)
		lem.clear_lem(dt_sim_time)

		#HHs determine dispatch based on price
		for house in houses:
			house.determine_dispatch(dt_sim_time)

		lem.reset()

		############
		# Implement dispatch : TESS DB physical --> model
		############

		# GLD --> DB
		if gld_simulation:
			for house in houses:
				#gldimport.update_settings() #If user changes settings in API, this should be called
				#gldimport.update_house_state(house.name,dt_sim_time)
				if house.PV:
					gldimport.dispatch_PV(house.PV,dt_sim_time)
		# Real-world implementation --> DB
		else:
			import sys; sys.exit('Physical data comes from lab/field: Not implemented yet')

		return t