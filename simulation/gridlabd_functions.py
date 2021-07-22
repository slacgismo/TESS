#This is only for the minimum viable product (PV)
import os
import random
import pandas
import json
import numpy as np
import datetime
from datetime import timedelta
from dateutil import parser
import time

from HH_global import db_address, gld_simulation, dispatch_mode
from HH_global import interval, start_time_db, p_max

import HH_functions as HHfct
#import battery_functions as Bfct
#import EV_functions as EVfct
#import PV_functions as PVfct

import market_functions as Mfct
from market_functions import Market
from market_functions import MarketOperator

import supply_functions as Sfcts
from supply_functions import WSSupplier

if gld_simulation:
	import gldimport_api_MVP as gldimport

#Sets up house agents/Home Hubs with settings
def on_init(t):
	global t0;
	t0 = time.time()

	# Calculate DeltaT
	dt_start = pandas.Timestamp.now()
	global DeltaT;
	DeltaT = dt_start - pandas.Timestamp(start_time_db) # Time offset between DB and current computer time
	print('Initialize')

	# Gets the list of active home hubs (!!!! does not filter for active == in the TESS database YET)
	import requests
	hh_list = requests.get(db_address+'home_hubs').json()['results']['data']
	hh_ids = []
	for hh in hh_list:
		hh_ids += [hh['home_hub_id']]
	
	# Creates house objects for each active home hub
	global houses;
	houses = []
	for hh_id in hh_ids:
		houses += [HHfct.create_agent_house(hh_id)]

	#Create WS supplier object
	global retailer;
	retailer = WSSupplier()

	#Create market operator object
	global LEM_operator;
	LEM_operator = MarketOperator(interval,p_max) #Does that need to be updated based on DB?

	return True

# At each market interval : bidding, clearing, and dispatching
def on_precommit(t):

	# Get run time

	if gld_simulation:
		dt_sim_time = parser.parse(gridlabd.get_global('clock')).replace(tzinfo=None)
	else:
		#import pdb; pdb.set_trace()
		dt_sim_time = pandas.Timestamp.now() - DeltaT

	# Run market only every interval

	global LEM_operator;
	if not ((dt_sim_time.second%interval == 0)): # and (dt_sim_time.minute % (LEM_operator.interval/60) == 0)):
		return t

	else: #interval in minutes #is not start time
		print('Start precommit: '+str(dt_sim_time))
		import pdb; pdb.set_trace()

		############
		# Physical info : physical model --> TESS DB
		############

		if gld_simulation:
			
			# Read out states of house / appliances

			for house in houses: # only for PV so far - other appliances placeholder in MVP
				#if house.HVAC:
				#	gldimport.update_house_state(house.name,dt_sim_time) #For HVAC systems
				if house.PV:
					gldimport.update_PV_state(house.PV,dt_sim_time)
				#if house.battery:
				#	gldimport.update_battery_state(house.battery.name,dt_sim_time)
				#if house.EVCP:
				#	gldimport.simulate_EVs(house.name,dt_sim_time)
				#	gldimport.update_CP_state(house.EVCP.name,dt_sim_time)
			
			# Read out system information
			
			gldimport.get_systemstate(dt_sim_time) # External information : system / grid # --> TABLE transformer_meter

		############
		# Market side / no phycial APIs involved
		############

		#Reads in information from DB and updates python objects (house + appliances)

		for house in houses:
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
		
		if dispatch_mode: # Applies market results to DB for implementation
			for house in houses:
				house.determine_dispatch(dt_sim_time)
		else:
			for house in houses:
				house.default(dt_sim_time)

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

		return t