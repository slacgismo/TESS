import gldimport
import os
import random
import pandas
import json
import numpy as np
import datetime
from datetime import timedelta
from dateutil import parser
import mysql_functions
from mysql_functions import table_list
import HH_functions as HHfct
import battery_functions as Bfct
import EV_functions as EVfct
import PV_functions as PVfct
import market_functions as Mfct
import time

from HH_global import results_folder, flexible_houses, C, p_max, market_data, which_price, city
from HH_global import interval, prec, price_intervals, allocation_rule, unresp_factor
from HH_global import FIXED_TARIFF, include_SO

use_mysql = False

#Should glm characteristics be written to mysql database?
def on_init(t):
	global t0;
	t0 = time.time()

	global step;
	step = 0

	#if use_mysql:
	mysql_functions.clear_databases(table_list)
	#else:


	#Find objects
	global houses;
	if flexible_houses == 0:
		houses = []
	else:
		houses = gldimport.find_objects('class=house')[:flexible_houses]
	
	#global df_house_state;
	#df_house_state = HHfct.get_settings_houses(houses,interval)

	batteries = gldimport.find_objects('class=battery')
	global batterylist, EVlist;
	batterylist, EVlist = gldimport.sort_batteries(batteries)
	global df_battery_state;
	df_battery_state = Bfct.get_settings_batteries(batterylist,interval)
	global df_EV_state;
	df_EV_state = EVfct.get_settings_EVs(EVlist,interval)

	pvs = gldimport.find_objects('class=solar')
	global pvlist, pvinvlist;
	pvlist, pvinvlist = gldimport.sort_pvs(pvs)
	global df_PV_state;
	df_PV_state = PVfct.get_settings(pvlist,interval)

	global df_prices, df_WS;
	df_prices = pandas.DataFrame(columns=['clearing_price','clearing_quantity','unresponsive_loads','slack_t-1'])
	df_WS = pandas.read_csv('glm_generation_'+city+'/'+market_data,parse_dates=[0],index_col=[0])

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
	if not ((dt_sim_time.second == 0) and (dt_sim_time.minute % (interval/60) == 0)):
		return t
	
	else: #interval in minutes #is not start time
		print('Start precommit: '+str(dt_sim_time))
		global step;
		global df_house_state;
		global df_battery_state;
		global df_EV_state;
		global df_PV_state;
		if step == 0:
			df_house_state = HHfct.get_settings_houses(houses,interval)
		
		#Save interim results
		saving_interval = 30
		if (dt_sim_time.hour%saving_interval == 0) and (dt_sim_time.minute == 0):
			saving_results(dt_sim_time,saving_interval)
		#Update physical values for new period
		#global df_house_state;
		print('Update house')
		df_house_state = HHfct.update_house(dt_sim_time,df_house_state)
		if len(batterylist) > 0:
			print('Update battery')
			df_battery_state = Bfct.update_battery(df_battery_state)
			print('Battery updated')
		if len(EVlist) > 0:
			print('Update EV')
			df_EV_state = EVfct.update_EV(dt_sim_time,df_EV_state)
			print('EV updated')
		if len(pvlist) > 0:
			print('Update PV')
			df_PV_state = PVfct.update_PV(dt_sim_time,df_PV_state)
			print('PV updated')

		#Initialize market
		global df_prices, df_WS;
		print('Create market')
		retail, mean_p, var_p = Mfct.create_market(df_prices,p_max,prec,price_intervals)

		#Submit bids
		df_house_state = HHfct.calc_bids_HVAC(dt_sim_time,df_house_state,retail,mean_p,var_p)
		retail = HHfct.submit_bids_HVAC(dt_sim_time,retail,df_house_state)

		#Batteries
		if len(batterylist) > 0:
			print('Reschedule batteries')
			if ((dt_sim_time.hour == 0) and (dt_sim_time.minute == 0)) or step == 0:
				print('Reschedule batteries: '+str(dt_sim_time))
				df_battery_state = Bfct.schedule_battery_ordered(df_WS,df_battery_state,dt_sim_time)
				#sell, buy = Bfct.schedule_battery_cvx(df_WS,df_battery_state,dt_sim_time)
			print('Calculate battery bids')
			df_battery_state = Bfct.calc_bids_battery(dt_sim_time,df_battery_state,retail,mean_p,var_p)
			print('Submit battery bids')
			retail = Bfct.submit_bids_battery(dt_sim_time,retail,df_battery_state)

		if len(EVlist) > 0:
			df_EV_state = EVfct.calc_bids_EV(dt_sim_time,df_EV_state,retail,mean_p,var_p)
			retail = EVfct.submit_bids_EV(dt_sim_time,retail,df_EV_state)
		print('Include PV')
		if len(pvlist) > 0:
			df_PV_state = PVfct.calc_bids_PV(dt_sim_time,df_PV_state,retail)
			retail = PVfct.submit_bids_PV(dt_sim_time,retail,df_PV_state)

		#Include unresponsive load
		print('Include unresp load')
		load_SLACK, unresp_load = Mfct.include_unresp_load(dt_sim_time,retail,df_prices)

		#Include supply
		supply_costs = float(min(df_WS[which_price].loc[dt_sim_time],retail.Pmax))
		retail.sell(C,supply_costs,gen_name='WS') #in [USD/kW] #How can I tweak clearing that we can name biider 'WS'?
		print('Supply costs: '+str(supply_costs))

		#Market clearing
		retail.clear()
		Pd = retail.Pd # cleared demand price
		print('Clearing price: '+str(Pd))
		Qd = retail.Qd #in kW
		print('Clearing quantity: '+str(Qd))
		df_temp = pandas.DataFrame(index=[dt_sim_time],columns=['clearing_price','clearing_quantity','unresponsive_loads','slack_t-1'],data=[[Pd,Qd,unresp_load,load_SLACK]])
		df_prices = df_prices.append(df_temp)
		
		###
		#Redistribute prices and quantities to market participants
		###

		#Save market result for each HVAC system
		if allocation_rule == 'by_price':
			#print('Set HVAC by price')
			df_house_state = HHfct.set_HVAC_by_price(dt_sim_time,df_house_state,mean_p,var_p, Pd) #Switches the HVAC system on and off directly (depending on bid >= p)
		elif allocation_rule == 'by_award':
			df_house_state = HHfct.set_HVAC_by_award(dt_sim_time,df_house_state,retail) #Switches the HVAC system on and off directly (depending on award)
		else:
			sys.exit('No valid pricing rule')

		if len(batterylist) > 0:
			if allocation_rule == 'by_price':
				df_bids_battery = Bfct.set_battery_by_price(dt_sim_time,df_battery_state,mean_p,var_p, Pd) #Controls battery based on bid <-> p
			elif allocation_rule == 'by_award':
				df_bids_battery = Bfct.set_battery_by_award(dt_sim_time,df_battery_state,retail) #Controls battery based on award
		#EVs
		if len(EVlist) > 0:
			if allocation_rule == 'by_price':
				df_EV_state = EVfct.set_EV_by_price(dt_sim_time,df_EV_state,mean_p,var_p, Pd) #Controls EV based on bid <-> p
			elif allocation_rule == 'by_award':
				df_EV_state = EVfct.set_EV_by_award(dt_sim_time,df_EV_state,retail) #Controls EV based on award

		step += 1
		retail.reset()
		gridlabd.save('dump_model.glm')
		return t

def on_term(t):
	print('Simulation ended, saving results')
	saving_results('final',6)

	global t0;
	t1 = time.time()
	print('Time needed (min):')
	print((t1-t0)/60)
	return None

def saving_results(timestamp,saving_interval):
	global df_house_state;
	df_house_state.to_csv(results_folder+'/df_house_state.csv')
	global df_prices;
	df_prices.to_csv(results_folder+'/df_prices.csv')
	global df_battery_state
	df_battery_state.to_csv(results_folder+'/df_battery_state.csv')
	global df_EV_state
	df_EV_state.to_csv(results_folder+'/df_EV_state.csv')
	global df_PV_state;
	df_PV_state.to_csv(results_folder+'/df_PV_state_.csv')

	#Saving mysql databases
	import download_databases
	download_databases.save_databases(timestamp)
	#mysql_functions.clear_databases(table_list) #empty up database

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

	#Do evaluations
	return

# def saving_results(timestamp,saving_interval):
# 	global df_house_state;
# 	df_house_state.to_csv(results_folder+'/df_house_state.csv')
# 	global df_prices;
# 	df_prices.to_csv(results_folder+'/df_prices_'+str(timestamp)+'.csv')
# 	global df_battery_state
# 	df_battery_state.to_csv(results_folder+'/df_battery_state.csv')
# 	global df_EV_state
# 	df_EV_state.to_csv(results_folder+'/df_EV_state.csv')
# 	global df_PV_state;
# 	df_PV_state.to_csv(results_folder+'/df_PV_state_.csv')

# 	#Saving mysql databases
# 	import download_databases
# 	download_databases.save_databases(timestamp)
# 	mysql_functions.clear_databases(table_list) #empty up database

# 	#Saving globals
# 	file = 'HH_global.py'
# 	new_file = results_folder+'/HH_global.py'
# 	glm = open(file,'r') 
# 	new_glm = open(new_file,'w') 
# 	j = 0
# 	for line in glm:
# 	    new_glm.write(line)
# 	glm.close()
# 	new_glm.close()

# 	#Do evaluations
# 	return

#Object-specific precommit
def precommit(obj,t) :
	print(t)
	tt =  int(300*((t/300)+1))
	print('Market precommit')
	print(tt)
	return gridlabd.NEVER #t #True #tt 


