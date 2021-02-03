"""

By Marie-Louise Arlt

gridlabd_functions for simulation of HCE model under the current institutional setup, i.e. fixed price + coincident peak charge + MVP (PV only)

"""

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

from HH_global import results_folder, flexible_houses, C, p_max, market_data, control_room_data, which_price
from HH_global import interval, prec, price_intervals, allocation_rule, unresp_factor, load_forecast
from HH_global import FIXED_TARIFF, include_SO, EV_data
from HH_global import input_folder, fixed_procurement_cost, coincident_peak_rate, system_op

def on_init(t):

	global t0;
	t0 = time.time()

	global step;
	step = 0

	#Documentation
	global df_buy_bids, df_supply_bids, df_awarded_bids;
	df_buy_bids = pandas.DataFrame(columns=['timestamp','appliance_name','bid_price','bid_quantity'])
	df_supply_bids = pandas.DataFrame(columns=['timestamp','appliance_name','bid_price','bid_quantity'])
	df_awarded_bids = pandas.DataFrame(columns=['timestamp','appliance_name','bid_price','bid_quantity','S_D'])

	#Customers
	customers = gldimport.find_objects('class=house')

	#Find houses with flexible HVAC (0 in MVP)
	global houses;
	if flexible_houses == 0:
		houses = []
	else:
		houses = gldimport.find_objects('class=house')[:flexible_houses]
	global df_house_state;
	df_house_state = HHfct.get_settings_houses(houses,interval)

	#Batteries and EVs
	batteries = gldimport.find_objects('class=battery')
	global batterylist, EVlist;
	batterylist, EVlist = gldimport.sort_batteries(batteries)
	global df_battery_state;
	df_battery_state = Bfct.get_settings_batteries(batterylist,interval)
	global df_EV_state;
	if (EV_data == 'None') or (len(EVlist) == 0):
		df_EV_state = EVfct.get_settings_EVs_rnd(EVlist,interval)
	else:
		df_EV_state = EVfct.get_settings_EVs(EVlist,interval)

	#PVs
	pvs = gldimport.find_objects('class=solar')
	global pvlist, pvinvlist;
	pvlist, pvinvlist = gldimport.sort_pvs(pvs)
	global df_PV_state;
	df_PV_state = PVfct.get_settings(pvlist,interval)
	if load_forecast == 'perfect':
		global df_PV_forecast;
		try:
			df_PV_all = pandas.read_csv(input_folder+'/perfect_PV_forecast_'+dt_sim_time.month+'_all.csv',parse_dates=True,skiprows=8)
			df_PV_all['# timestamp'] = df_PV_all['# timestamp'].str.replace(r' UTC$', '')
			df_PV_all['# timestamp'] = pandas.to_datetime(df_PV_all['# timestamp'])
			df_PV_all.set_index('# timestamp',inplace=True)
			df_PV_forecast = pandas.DataFrame(index=df_PV_all.index,columns=['PV_infeed'],data=df_PV_all[df_PV_state['inverter_name']].sum(axis=1))
			df_PV_forecast.to_csv(input_folder+'/perfect_PV_forecast_'+dt_sim_time.month+'.csv')
		except:
			print('No perfect PV forecast found, use myopic PV forecast')
			df_PV_forecast = None

	#Tokens
	global df_tokens;
	df_tokens = pandas.DataFrame(columns=['clearing_price','clearing_quantity','partial','alpha','unresponsive_loads','system_mode','slack_t-1'])
	global df_controlroom;
	df_controlroom = pandas.read_csv(input_folder + '/' + control_room_data,index_col=[0],parse_dates=True) # This includes the control room ts of coincident peak forecast

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

		#Save DB files and shorten dfs every 24 hours
		saving_interval = 1
		if step == 0:
			global time_daystart 
			time_daystart = time.time()
		if step > 0 and (dt_sim_time.hour == 0) and (dt_sim_time.minute == 0):
			#i = int(step/(saving_interval*12)) #for 5min interval
			dt_sim_time_prev = dt_sim_time - pandas.Timedelta(days=1)
			specifier = str(dt_sim_time_prev.year)+format(dt_sim_time_prev.month,'02d')+format(dt_sim_time_prev.day,'02d')
			df_supply_bids.to_csv(results_folder+'/df_supply_bids_'+specifier+'.csv')
			#df_supply_bids = pandas.DataFrame(columns = df_supply_bids.columns)
			df_buy_bids.to_csv(results_folder+'/df_buy_bids_'+specifier+'.csv')
			#df_buy_bids = pandas.DataFrame(columns = df_buy_bids.columns)
			df_awarded_bids.to_csv(results_folder+'/df_awarded_bids_'+specifier+'.csv')
			#df_awarded_bids = pandas.DataFrame(columns = df_awarded_bids.columns)
			df_buy_bids = pandas.DataFrame(columns=['timestamp','appliance_name','bid_price','bid_quantity'])
			df_supply_bids = pandas.DataFrame(columns=['timestamp','appliance_name','bid_price','bid_quantity'])
			df_awarded_bids = pandas.DataFrame(columns=['timestamp','appliance_name','bid_price','bid_quantity','S_D'])
			time_dayend = time.time()
			print('Time needed for past simulation day '+str(dt_sim_time)+': '+str((time_dayend - time_daystart)/60.)+' min')
			time_daystart = time_dayend

		#Update physical values for new period
		df_house_state = HHfct.update_house(dt_sim_time,df_house_state)
		if len(batterylist) > 0:
			df_battery_state = Bfct.update_battery(df_battery_state)
		if len(EVlist) > 0:
			if EV_data == 'None':
				df_EV_state = EVfct.update_EV_rnd(dt_sim_time,df_EV_state)
			else:
				df_EV_state = EVfct.update_EV(dt_sim_time,df_EV_state)
		if len(pvlist) > 0:
			df_PV_state = PVfct.update_PV(dt_sim_time,df_PV_state)

		#Initialize market
		global df_tokens, df_controlroom;
		retail, mean_t, var_t = Mfct.create_market_noEIM(df_controlroom,df_tokens,p_max,prec,price_intervals,dt_sim_time)

		#Customer bidding

		#HVACs
		df_house_state = HHfct.calc_bids_HVAC(dt_sim_time,df_house_state,retail,mean_t,var_t)
		retail,df_buy_bids = HHfct.submit_bids_HVAC(dt_sim_time,retail,df_house_state,df_buy_bids)

		#Batteries
		if len(batterylist) > 0:
			if ((dt_sim_time.hour == 0) and (dt_sim_time.minute == 0)) or step == 0:
				specifier = str(dt_sim_time.year)+format(dt_sim_time.month,'02d')+format(dt_sim_time.day,'02d')
				df_battery_state = Bfct.schedule_battery_ordered(df_WS,df_battery_state,dt_sim_time,specifier)
				#sell, buy = Bfct.schedule_battery_cvx(df_WS,df_battery_state,dt_sim_time)
			df_battery_state = Bfct.calc_bids_battery(dt_sim_time,df_battery_state,retail,mean_t,var_t)
			retail,df_supply_bids,df_buy_bids = Bfct.submit_bids_battery(dt_sim_time,retail,df_battery_state,df_supply_bids,df_buy_bids)
		if len(EVlist) > 0:
			df_EV_state = EVfct.calc_bids_EV(dt_sim_time,df_EV_state,retail,mean_t,var_t)
			retail,df_buy_bids = EVfct.submit_bids_EV(dt_sim_time,retail,df_EV_state,df_buy_bids)

		#PV bids
		if len(pvlist) > 0:
			global df_PV_forecast;
			if (load_forecast == 'myopic') or (df_PV_forecast is None):
				df_PV_state = PVfct.calc_bids_PV(dt_sim_time,df_PV_state,retail)
				retail,df_supply_bids = PVfct.submit_bids_PV(dt_sim_time,retail,df_PV_state,df_supply_bids)
			elif load_forecast == 'perfect':
				#PV_forecast = df_PV_forecast['PV_infeed'].loc[dt_sim_time]
				PV_forecast = df_PV_forecast['PV_infeed'].loc[(df_PV_forecast.index >= dt_sim_time) & (df_PV_forecast.index < dt_sim_time + pandas.Timedelta(str(int(interval/60))+' min'))].min()/1000
				if PV_forecast > 0.0:
					retail.sell(PV_forecast,0.0,gen_name='PV')
					df_supply_bids = df_supply_bids.append(pandas.DataFrame(columns=df_supply_bids.columns,data=[[dt_sim_time,'PV',0.0,PV_forecast]]),ignore_index=True)

		#Unresponsive load

		retail, load_SLACK, unresp_load, df_buy_bids = Mfct.determine_unresp_load(dt_sim_time,retail,df_tokens,df_buy_bids,df_awarded_bids)
		retail.buy(unresp_load,appliance_name='unresp')
		df_buy_bids = df_buy_bids.append(pandas.DataFrame(columns=df_buy_bids.columns,data=[[dt_sim_time,'unresponsive_loads',p_max,round(float(unresp_load),prec)]]),ignore_index=True)

		#Supply from transmission level

		max_capacity = df_controlroom['C_max'].loc[dt_sim_time] #Max import
		min_capacity = df_controlroom['C_min'].loc[dt_sim_time] #Min import / max export

		#Supply cost

		if system_op == 'fixed_proc':
			coincident_peak_forecasted = df_controlroom['coincident_peak_forecasted'].loc[dt_sim_time]
			if coincident_peak_forecasted == 0:
				supply_costs = fixed_procurement_cost #df_controlroom['fixed_procurement'].loc[dt_sim_time]
			else:
				supply_costs = coincident_peak_rate #df_controlroom['coincident_peak_rate'].loc[dt_sim_time]
		else:
			import sys; sys.exit('EIM not implemented yet')
			supply_costs = df_WS['RT'].loc[dt_sim_time]

		# Include import and export constraints

		if min_capacity > 0.0:
			#Minimum import
			retail.sell(min_capacity,-retail.Pmax,gen_name='min_import') #in [USD/kW]
			df_supply_bids = df_supply_bids.append(pandas.DataFrame(columns=df_supply_bids.columns,data=[[dt_sim_time,'min_import',-retail.Pmax,min_capacity]]),ignore_index=True)
			#Additional import
			retail.sell(max_capacity - min_capacity,supply_costs,gen_name='add_import') #in [USD/kW]
			df_supply_bids = df_supply_bids.append(pandas.DataFrame(columns=df_supply_bids.columns,data=[[dt_sim_time,'add_import',supply_costs,max_capacity - min_capacity]]),ignore_index=True)
		elif min_capacity == 0:
			#No export, no minimum import		
			retail.sell(max_capacity,supply_costs,gen_name='import') #in [USD/kW]
			df_supply_bids = df_supply_bids.append(pandas.DataFrame(columns=df_supply_bids.columns,data=[[dt_sim_time,'import',supply_costs,max_capacity]]),ignore_index=True)
		else:
			#No minimum import		
			retail.sell(max_capacity,supply_costs,gen_name='import') #in [USD/kW]
			df_supply_bids = df_supply_bids.append(pandas.DataFrame(columns=df_supply_bids.columns,data=[[dt_sim_time,'import',supply_costs,max_capacity]]),ignore_index=True)
			#Possible export
			retail.buy(-min_capacity,supply_costs-0.01,appliance_name='export') #in [USD/kW]
			df_buy_bids = df_buy_bids.append(pandas.DataFrame(columns=df_buy_bids.columns,data=[[dt_sim_time,'export',supply_costs-0.01,-min_capacity]]),ignore_index=True)
		
		#Market clearing

		retail.clear()
		Pd = retail.Pd # cleared demand price
		print('Clearing price: '+str(Pd))
		Qd = retail.Qd #in kW
		print('Clearing quantity: '+str(Qd))
		partial = retail.partial # Demand or supply
		alpha = retail.alpha # Share of marginal bids

		#Check system conditions

		available_supply = df_supply_bids.loc[df_supply_bids['timestamp'] == dt_sim_time]['bid_quantity'].sum()
		available_demand = df_buy_bids.loc[df_buy_bids['timestamp'] == dt_sim_time]['bid_quantity'].sum()
		if available_supply >= unresp_load*0.999:
			if abs(available_supply - Qd) < 0.1:
				system_op_mode = 'SUPPLY_CONTRAINED' # Not sufficient supply
			elif abs(available_demand - Qd) < 0.1:
				system_op_mode = 'DEMAND_CONTRAINED' # Not sufficient demand
			else:
				system_op_mode = 'NORMAL' # Not sufficient demand
		else:
			system_op_mode = 'EMERGENCY'

		#Save market / system result

		df_temp = pandas.DataFrame(index=[dt_sim_time],columns=df_tokens.columns,data=[[Pd,Qd,unresp_load,partial,alpha,system_op_mode,load_SLACK]])
		df_tokens = df_tokens.append(df_temp)
		
		###
		#Redistribute prices and quantities to market participants
		###

		#no alpha and partial yet
		if allocation_rule == 'by_price':
			#print('Set HVAC by price')
			df_house_state,df_awarded_bids = HHfct.set_HVAC_by_price(dt_sim_time,df_house_state,mean_t,var_t, Pd,df_awarded_bids) #Switches the HVAC system on and off directly (depending on bid >= p)
		elif allocation_rule == 'by_award':
			df_house_state,df_awarded_bids = HHfct.set_HVAC_by_award(dt_sim_time,df_house_state,retail,df_awarded_bids) #Switches the HVAC system on and off directly (depending on award)
		else:
			sys.exit('No valid pricing rule')

		if len(pvlist) > 0:
			# no control of PVs (if inverter cannot disconnect remotely)
			#df_awarded_bids = PVfct.set_PV(dt_sim_time,retail,df_PV_state,df_awarded_bids)
			# control of PVs (if inverter can disconnect remotely)
			df_awarded_bids = PVfct.set_PV_by_price(dt_sim_time,df_PV_state,Pd,df_awarded_bids,partial,alpha)
		#import pdb; pdb.set_trace()
		#no alpha and partial yet
		if len(batterylist) > 0:
			if allocation_rule == 'by_price':
				df_bids_battery, df_awarded_bids = Bfct.set_battery_by_price(dt_sim_time,df_battery_state,mean_t,var_t, Pd, df_awarded_bids) #Controls battery based on bid <-> p
			elif allocation_rule == 'by_award':
				df_bids_battery, df_awarded_bids = Bfct.set_battery_by_award(dt_sim_time,df_battery_state,retail, df_awarded_bids) #Controls battery based on award

		#no alpha and partial yet
		if len(EVlist) > 0:
			if allocation_rule == 'by_price':
				df_EV_state, df_awarded_bids = EVfct.set_EV_by_price(dt_sim_time,df_EV_state,mean_t,var_t, Pd, df_awarded_bids) #Controls EV based on bid <-> p
			elif allocation_rule == 'by_award':
				df_EV_state, df_awarded_bids = EVfct.set_EV_by_award(dt_sim_time,df_EV_state,retail,df_awarded_bids) #Controls EV based on award
		
		#import pdb; pdb.set_trace()
		#Save all simulation results temporarily at each hour for potential restart
		# if dt_sim_time.minute == 0:
		# 	print('Last save at '+str(dt_sim_time))
		# 	gridlabd.save('tmp_model.glm')
		# 	df_house_state.to_csv('tmp_df_house_state.csv')
		# 	df_PV_state.to_csv('tmp_df_PV_state.csv')
		# 	df_battery_state.to_csv('tmp_df_battery_state.csv')
		# 	df_EV_state.to_csv('tmp_df_EV_state.csv')

		# 	df_prices.to_csv('tmp_df_prices.csv')
		# 	df_supply_bids.to_csv('tmp_df_supply_bids.csv')
		# 	df_buy_bids.to_csv('tmp_df_buy_bids.csv')
		# 	df_awarded_bids.to_csv('tmp_df_awarded_bids.csv')

		# Every DeltaT change calculate tokens



		step += 1
		retail.reset()
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
	global df_PV_state;
	df_PV_state.to_csv(results_folder+'/df_PV_state.csv')

	#Saving former mysql
	global df_tokens;
	df_tokens.to_csv(results_folder+'/df_tokens.csv')
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


