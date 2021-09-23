import os
import pandas
import requests

db_address = 'http://host.docker.internal:5000/api/v1/'
gld_simulation = True # True : uses gridlabd as representation of physical model
dispatch_mode = True # True : implements dispatch decisions by writing them to the database

# Only needed if gld_simulation = False
#start_time_str = '2021-07-22 15:23:45' # GREENWICH simulation start at local computer (in Greenwhich; if offline data is used, if not choose any)
start_time_db = '2021-07-22 09:00:00' #start of db (if offline data is used, if not choose == start_time_str)
#DeltaT = pandas.Timestamp(start_time_str) - pandas.Timestamp(start_time_db) # Time offset between DB and current computer time

# Market settings
market_id = 1
try:
	interval = int(requests.get(db_address+'markets?market_id='+str(market_id)).json()['results']['data'][0]['ts'])
	print(interval)
except:
	interval = 60
transformer_id = 1
p_max = 100.0

# Comes from control room
C = 'random' # for testing
market_data = 'random' #'Ercot_HBSouth.csv'

# Control room
load_forecast = 'myopic'
unresp_factor = 0.0
ref_price = 'historical'
price_intervals = 288 #p average calculation 
which_price = 'DA' #battery scheduling

# Result file
results_folder = 'results'

