# #This is only for the minimum viable product (PV)
import requests
# import gldimport_api_MVP as gldimport
# import os
# import random
# import pandas
# import json
# import numpy as np
# import datetime
from datetime import timedelta
from dateutil import parser
import time

db_address = 'http://host.docker.internal:5000/api/v1/'

# import HH_functions as HHfct
# # from HH_functions import House

# import market_functions as Mfct
# from market_functions import Market
# from market_functions import MarketOperator

# import supply_functions as Sfcts
# from supply_functions import WSSupplier

# #import battery_functions as Bfct
# #import EV_functions as EVfct
# #import PV_functions as PVfct

# from HH_global import db_address #, user_name, pw
# from HH_global import results_folder, flexible_houses, C, p_max, market_data, which_price, city, month
# from HH_global import interval, prec, price_intervals, allocation_rule, unresp_factor, load_forecast
# from HH_global import FIXED_TARIFF, include_SO, EV_data, start_time_str

# #True if physical model is simulated by GLD
# gld_simulation = True

########
#To Do
#
#- customers changing settings not considered yet
#- include mode changes by Supplier or LEMoperator, e.g. into emergency mode
#- check and update mode
########

#Sets up house agents/Home Hubs with settings
def on_init(t):
	print('initialization')

	return True

# At each market interval : bidding, clearing, and dispatching
def on_precommit(t):

	#Run market only every five minutes
	dt_sim_time = parser.parse(gridlabd.get_global('clock')).replace(tzinfo=None)
	if not (dt_sim_time.second == 0):
		return t
	
	else: #interval in minutes #is not start time
		print('Full minute precommit; now we wait for 10s')
		#print(requests.get(db_address+'meter_intervals').json())
		time.sleep(10)
		print('10s are over')
		return t