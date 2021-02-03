import gldimport
import os
import random
import pandas
import json
import numpy as np
import datetime
from datetime import timedelta
from dateutil import parser
import HH_functions as HHfct
import battery_functions as Bfct
import EV_functions as EVfct
import PV_functions as PVfct
import market_functions as Mfct
import time

from HH_global import results_folder, flexible_houses, C, p_max, market_data, which_price, city
from HH_global import interval, prec, price_intervals, allocation_rule, unresp_factor
from HH_global import FIXED_TARIFF, include_SO

ToU_min = 15
p_min = 20
ToU_max = 19
p_max = 75
p_vec = ToU_min*[p_min] + (ToU_max - ToU_min)*[p_max] + (24 - ToU_max)*[p_min]
mean_p = sum(p_vec)/len(p_vec)
var_p = np.var(p_vec)

def on_init(t):
	global t0;
	t0 = time.time()

	global step;
	step = 0

	#Instead of mysql
	global df_buy_bids, df_supply_bids, df_awarded_bids;
	df_buy_bids = pandas.DataFrame(columns=['timestamp','appliance_name','bid_price','bid_quantity'])
	df_supply_bids = pandas.DataFrame(columns=['timestamp','appliance_name','bid_price','bid_quantity'])
	df_awarded_bids = pandas.DataFrame(columns=['timestamp','appliance_name','bid_price','bid_quantity','S_D'])

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

	global df_prices, df_WS;
	df_prices = pandas.DataFrame(columns=['clearing_price','clearing_quantity','unresponsive_loads','slack_t-1'])
	df_WS = pandas.read_csv('glm_generation_'+city+'/'+market_data,parse_dates=[0],index_col=[0])
	#df_WS = pandas.DataFrame(index=pandas.to_datetime(df_WS.index.astype(str)),columns=df_WS.columns,data=df_WS.values)

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
		global df_house_state, df_battery_state, df_EV_state, df_PV_state;
		global df_buy_bids, df_supply_bids, df_awarded_bids; 
		if step == 0:
			df_house_state = HHfct.get_settings_houses(houses,interval)
		
		#Save DB files and shorten dfs every 12 hours
		saving_interval = 1
		if step > 0 and (dt_sim_time.hour%saving_interval == 0) and (dt_sim_time.minute == 0):
			i = int(step/(saving_interval*12)) #for 5min interval
			df_supply_bids.to_csv(results_folder+'/df_supply_bids.csv')
			#df_supply_bids = pandas.DataFrame(columns = df_supply_bids.columns)
			df_buy_bids.to_csv(results_folder+'/df_buy_bids.csv')
			#df_buy_bids = pandas.DataFrame(columns = df_buy_bids.columns)
			df_awarded_bids.to_csv(results_folder+'/df_awarded_bids.csv')
			#df_awarded_bids = pandas.DataFrame(columns = df_awarded_bids.columns)

		#Get current ToU price
		retail = Mfct.Market()
		retail.Pmin = 0.0
		retail.Pmax = p_max
		retail.Pprec = prec
		if (dt_sim_time.hour >= ToU_min) & (dt_sim_time.hour < ToU_max):
			Pd = p_max
		else:
			Pd = p_min
		df_temp = pandas.DataFrame(index=[dt_sim_time],columns=['clearing_price','clearing_quantity','unresponsive_loads','slack_t-1'],data=[[Pd,0.0,0.0,0.0]])
		df_prices = df_prices.append(df_temp)

		#Update physical values for new period
		#global df_house_state;
		df_house_state = HHfct.update_house(dt_sim_time,df_house_state)
		if len(batterylist) > 0:
			df_battery_state = Bfct.update_battery(df_battery_state)
		if len(EVlist) > 0:
			df_EV_state = EVfct.update_EV(dt_sim_time,df_EV_state)
		#if len(pvlist) > 0:
		#	df_PV_state = PVfct.update_PV(dt_sim_time,df_PV_state)

		#Determine willingness to pay for HVACs
		df_house_state = HHfct.calc_bids_HVAC(dt_sim_time,df_house_state,retail,mean_p,var_p)

		#Batteries try to sell in peak times, and buy in non-peak times until they are full
		#peak hours: sell
		if (dt_sim_time.hour >= ToU_min) & (dt_sim_time.hour < ToU_max):
			df_battery_state
			#Quantity depends on SOC and u
			df_battery_state['residual_s'] = round((3600./interval)*(df_battery_state['SOC_t'] - df_battery_state['SOC_min']*df_battery_state['SOC_max']),prec) #Recalculate to kW
			df_battery_state['q_sell'] = df_battery_state[['residual_s','u_max']].min(axis=1) #in kW / only if fully dischargeable
			df_battery_state['q_sell'].loc[df_battery_state['q_sell'] < 0.1] = 0.0
			df_battery_state['p_sell'] = -p_max #sell in any case
			df_battery_state['q_buy'] = 0.0
			df_battery_state['p_buy'] = -p_max
		else:
			safety_fac = 0.99
			df_battery_state['residual_b'] = round((3600./interval)*(safety_fac*df_battery_state['SOC_max'] - df_battery_state['SOC_t']),prec) #Recalculate to kW
			df_battery_state['q_buy'] = df_battery_state[['residual_b','u_max']].min(axis=1) #in kW
			df_battery_state['q_buy'].loc[df_battery_state['q_buy'] < 0.1] = 0.0
			df_battery_state['p_buy'] = p_max #buy in any case
			df_battery_state['q_sell'] = 0.0
			df_battery_state['p_sell'] = p_max #never sell
			
		#Determine willingness to pay for EVs
		#Quantity
		safety_fac = 0.99
		df_EV_state['q_buy'] = 0.0 #general
		df_EV_state['residual_SOC'] = round((3600./interval)*(safety_fac*df_EV_state['SOC_max'] - df_EV_state['SOC_t']),prec)
		df_EV_state['q_buy'].loc[df_EV_state['connected'] == 1] = df_EV_state.loc[df_EV_state['connected'] == 1][['residual_SOC','u_max']].min(axis=1) #in kW
		df_EV_state['q_buy'].loc[df_EV_state['q_buy'] < 1.] = 0.0

		#Price
		df_EV_state['p_buy'] = 0.0 #general
		#peak hours: only charge if necessary
		if (dt_sim_time.hour >= ToU_min) & (dt_sim_time.hour < ToU_max):
			#Home-based charging
			df_EV_state['delta'] = df_EV_state['next_event'] - dt_sim_time
			df_EV_state['residual_t'] = df_EV_state['delta'].apply(lambda x: x.seconds)/3600.      #residual time until departure; in h
			df_EV_state['time_needed_charging'] = df_EV_state['residual_SOC']/df_EV_state['u_max'] #in h
			df_EV_state['must_charge'] = 0
			df_EV_state['must_charge'].loc[df_EV_state['residual_t'] <= df_EV_state['time_needed_charging']] = 1
			#import pdb; pdb.set_trace()
			#df_EV_state.at[df_EV_state.loc[df_EV_state['must_charge'] == 0].index,'p_buy'] = 0.0
			df_EV_state['p_buy'].loc[df_EV_state['must_charge'] == 0] = 0.0
			#df_EV_state.at[df_EV_state.loc[df_EV_state['must_charge'] == 1].index,'p_buy'] = p_max
			df_EV_state['p_buy'].loc[df_EV_state['must_charge'] == 1] = p_max
		else:
			df_EV_state['p_buy'] = p_max

		#Commercial
		df_EV_state.loc[df_EV_state['charging_type'].str.contains('comm') & (df_EV_state['connected'] == 1) & (df_EV_state['q_buy'] > 0.001),'p_buy'] = retail.Pmax #max for commercial cars

		#Dispatch
		allocation_rule == 'by_price' #open loop!
		df_house_state,df_awarded_bids = HHfct.set_HVAC_by_price(dt_sim_time,df_house_state,mean_p,var_p, Pd,df_awarded_bids) #Switches the HVAC system on and off directly (depending on bid >= p)
		df_bids_battery, df_awarded_bids = Bfct.set_battery_by_price(dt_sim_time,df_battery_state,mean_p,var_p, Pd, df_awarded_bids) #Controls battery based on bid <-> p
		df_EV_state, df_awarded_bids = EVfct.set_EV_by_price(dt_sim_time,df_EV_state,mean_p,var_p, Pd, df_awarded_bids) #Controls EV based on bid <-> p

		step += 1
		return t

def on_term(t):
	print('Simulation ended, saving results')
	saving_results()

	global t0;
	t1 = time.time()
	print('Time needed (min):')
	print((t1-t0)/60)
	return None

def saving_results():
	#Save settings of objects
	global df_house_state;
	df_house_state.to_csv(results_folder+'/df_house_state.csv')
	global df_battery_state
	df_battery_state.to_csv(results_folder+'/df_battery_state.csv')
	global df_EV_state
	df_EV_state.to_csv(results_folder+'/df_EV_state.csv')
	#global df_PV_state;
	#df_PV_state.to_csv(results_folder+'/df_PV_state.csv')

	#Saving former mysql
	global df_prices;
	df_prices.to_csv(results_folder+'/df_prices.csv')
	global df_supply_bids;
	df_supply_bids.to_csv(results_folder+'/df_supply_bids.csv')
	global df_buy_bids;
	df_buy_bids.to_csv(results_folder+'/df_buy_bids.csv')
	global df_awarded_bids;
	df_awarded_bids.to_csv(results_folder+'/df_awarded_bids.csv')

	#Saving mysql databases
	#import download_databases
	#download_databases.save_databases(timestamp)
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

#Object-specific precommit
def precommit(obj,t) :
	print(t)
	tt =  int(300*((t/300)+1))
	print('Market precommit')
	print(tt)
	return gridlabd.NEVER #t #True #tt 


