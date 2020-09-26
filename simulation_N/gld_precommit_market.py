import os
import rwText
import json
#from cvxpy import *
import random
import math
import pandas as pd

import datetime
from dateutil import parser
import gridlabd_functions
import mysql_functions
from HH_global import *
import HH_functions as HHfct
import market_functions as Mfct
#from HHoptimizer_funcDefs import *

sim_time = os.getenv("clock")
#interval = int(gridlabd_functions.get('retail','interval')['value']) #in seconds

#Run market only every five minutes
#Remark: The file is currently called at every event (i.e. 1min) but the main part is not executed.
#Potentially, it would be faster to do the check in the glm file before switching to the Python layer? 
print sim_time
if (sim_time[17:19] == "00") and (int(sim_time[15:16]) % (interval/60) == 0): #interval in minutes

	print 'Precommit'
	print sim_time
	dt_sim_time = parser.parse(sim_time[:-4])

	#Update physical values for new period
	df_house_state = HHfct.update_house(dt_sim_time)
	df_battery_state = HHfct.update_battery(dt_sim_time)
	df_PV_state = HHfct.update_PV(dt_sim_time)
	df_EV_state = HHfct.update_EV(dt_sim_time)
	
	#Initialize market
	retail = Mfct.Market()
	retail.reset()
	retail.Pmin = 0.0
	retail.Pmax = 100.0
	retail.Pprec = prec

	#Get historical parameters from mysql database
	df_prices = mysql_functions.get_values('clearing_pq', dt_sim_time-datetime.timedelta(days=1))
	mean_p = df_prices['clearing_price'].iloc[-36:].mean() #last hour
	var_p = df_prices['clearing_price'].var()
	if math.isnan(mean_p):
		mean_p = (retail.Pmax - retail.Pmin)/2
	#print var_p
	if math.isnan(var_p) or var_p == 0.0:
		var_p = 0.10
	mysql_functions.set_values('market_prices', '(mean_price,var_price,timedate)',(float(mean_p),float(var_p),dt_sim_time-datetime.timedelta(seconds=interval),))

	###
	#Demand side
	###

	#HVAC
	df_bids_HVAC = HHfct.calc_bids_HVAC(dt_sim_time,df_house_state,retail,mean_p,var_p)
	retail = HHfct.submit_bids_HVAC(dt_sim_time,retail,df_bids_HVAC)
	print retail.D_active

	#Batteries
	df_bids_battery = HHfct.calc_bids_battery(dt_sim_time,df_battery_state,retail,mean_p,var_p)
	retail = HHfct.submit_bids_battery(dt_sim_time,retail,df_bids_battery)

	#PV
	df_bids_PV = HHfct.calc_bids_PV(dt_sim_time,df_PV_state,retail)
	retail = HHfct.submit_bids_PV(dt_sim_time,retail,df_bids_PV)

	#EV
	dt_sim_time,df_EV_state,retail
	df_bids_EV = HHfct.calc_bids_EV(dt_sim_time,df_EV_state,retail,mean_p,var_p)
	retail = HHfct.submit_bids_EV(dt_sim_time,retail,df_bids_EV)

	#Include unresponsive load
	load_SLACK = float(gridlabd_functions.get('node_149','measured_real_power')['value'][:-1])/1000 #save to mysql #measured_real_power in [W]
	active_prev = retail.get_active() #needs to be after buy bid submission
	unresp_load = load_SLACK - active_prev
	mysql_functions.set_values('unresponsive_loads', '(unresp_load,slack,active_loads,timedate)',(unresp_load,load_SLACK,active_prev,dt_sim_time,))
	retail.buy(unresp_load)

	###
	#Supply side
	###

	#supply_costs = round(random.uniform(retail.Pmin,retail.Pmax),prec)
	supply_costs = min(mysql_functions.get_values('WS_market',begin=dt_sim_time,end=dt_sim_time)['RT'].iloc[0],retail.Pmax)
	print'supply costs: '+str(supply_costs)
	#Max capacity (later from CC)
	#C = 3262 + random.uniform(-10,10) #for test purposes [in kW]
	C = 800.0 #capacity restriction
	mysql_functions.set_values('capacity_restrictions', '(cap_rest,timedate)',(C,dt_sim_time,)) #in kW
	retail.sell(C,supply_costs,gen_name='WS') #in [USD/kW] #How can I tweak clearing that we can name biider 'WS'?
	mysql_functions.set_values('supply_bids', '(bid_price,bid_quantity,timedate,gen_name)',(float(supply_costs),float(C),dt_sim_time,'wholesale'))

	###
	#Market clearing (kW)
	###

	retail.clear()
	Pd = retail.Pd # cleared demand price
	Qd = retail.Qd #in kW
	mysql_functions.set_values('clearing_pq', '(clearing_price,clearing_quantity,timedate)',(Pd,Qd,dt_sim_time,))
	#for calculation of monthly bill in GridlabD / to be deleted when DB is active in GridlabD
	gridlabd_functions.set('retail','price',Pd)

	###
	#Redistribute prices and quantities to market participants
	###

	#Save market result for each HVAC system
	#df_bids_HVAC = HHfct.set_HVAC_T(dt_sim_time,df_bids_HVAC,mean_p,var_p, Pd) #Sets new T setpoint according to price
	#df_bids_HVAC = HHfct.set_HVAC_by_price(dt_sim_time,df_bids_HVAC,mean_p,var_p, Pd) #Switches the HVAC system on and off directly (depending on bid >= p)
	df_bids_HVAC = HHfct.set_HVAC_by_award(dt_sim_time,df_bids_HVAC,retail) #Switches the HVAC system on and off directly (depending on award)



	#Battery
	#df_bids_battery = HHfct.set_battery_by_price(dt_sim_time,df_bids_battery,mean_p,var_p, Pd) #Controls battery based on bid <-> p
	df_bids_battery = HHfct.set_battery_by_award(dt_sim_time,df_bids_battery,retail) #Controls battery based on award

	#No informtion necessary for PV
	#Potentially later: curtail if overproduction

	#EVs
	#df_bids_EV = HHfct.set_EV_by_price(dt_sim_time,df_bids_EV,mean_p,var_p, Pd) #Controls EV based on bid <-> p
	df_bids_EV = HHfct.set_EV_by_award(dt_sim_time,df_bids_EV,retail) #Controls EV based on award