import numpy as np

import gridlabd_functions
import mysql_functions
from HH_global import *

#Estimate next step's unresponsive load
def myopic(dt_sim_time,dt):
	return float(mysql_functions.get_values('unresponsive_loads',begin=dt_sim_time-dt,end=dt_sim_time-dt)['unresp_load'].iloc[0])

def average(dt_sim_time,margin):
	
	return

#Emergency measure
def shutdown_house(unresp_load,dt_sim_time,houses_off=[],market=None):
	if market:
		Pmax = market.Pmax
	else:
		Pmax = 100.0
	while True:
		house_OFF = np.random.choice(houselist_inflex)
		while house_OFF in houses_off:
			house_OFF = np.random.choice(houselist_inflex)
		house_currHVAC = float(gridlabd_functions.get(house_OFF,'hvac_load')['value'][:-3])
		if house_currHVAC > 0.0:
			unresp_load -= house_currHVAC
			print 'Switch off '+str(house_OFF)+' to '+str(unresp_load)
			gridlabd_functions.set(house_OFF,'thermostat_control','NONE')
			gridlabd_functions.set(house_OFF,'system_mode','OFF')
			houses_off += [house_OFF]
			mysql_functions.set_values('system_operations', '(timedate,q,costs,appliance_name)',(dt_sim_time,house_currHVAC,Pmax,'HVAC'+house_OFF[3:],))
			break
	print 'Ready: '+str(unresp_load)
	return unresp_load, houses_off

#Switch device back on
def switch_on(s_SO):
	#houses
	if 'GLD' in s_SO['appliance_name']:
		gridlabd_functions.set(s_SO['appliance_name'],'thermostat_control','FULL')
	#batteries
	elif 'Bat' in s_SO['appliance_name']:
		gridlabd_functions.set('Bat_inverter_'+s_SO['appliance_name'][8:],'P_Out',-s_SO['q']*1000)
	#EV
	elif 'EV' in s_SO['appliance_name']:
		gridlabd_functions.set('EV_inverter_'+s_SO['appliance_name'][3:],'P_Out',-s_SO['q']*1000)
	else:
		print s_SO['appliance_name']+' is not recognized'
	return

def switch_off(s_awarded,dt_sim_time):
	#houses
	if 'GLD' in s_awarded['appliance_name']:
		gridlabd_functions.set(s_awarded['appliance_name'],'thermostat_control','NONE')
	#batteries
	elif 'Bat' in s_awarded['appliance_name']:
		gridlabd_functions.set('Bat_inverter_'+s_awarded['appliance_name'][8:],'P_Out',0.0)
	#EV
	elif 'EV' in s_awarded['appliance_name']:
		gridlabd_functions.set('EV_inverter_'+s_awarded['appliance_name'][3:],'P_Out',0.0)
	else:
		print s_awarded['appliance_name']+' is not recognized'
	mysql_functions.set_values('system_operations', '(timedate,q,costs,appliance_name)',(dt_sim_time,float(s_awarded['q_bid']),float(s_awarded['p_bid']),s_awarded['appliance_name'],))
	return