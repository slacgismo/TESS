# Read out database and save in same format as simulation

import pandas
import requests
from HH_global import db_address, results_folder

start = '2020-10-01'
start = '11/6/2020  00:00:00 AM'
market_freq = '15s'
table_examples = '/Users/admin/Documents/powernet/TESS/simulation_N/TESS/TESS'
table_examples = '/docker_TESS_dep/TESS_mysql/TESS_formsample'

results_eval_folder = '/docker_TESS_dep/TESS_mysql/TESS_mysql_0001_eval'
results_eval_folder = '/docker_TESS_dep/TESS/TESS_API'

# Get market
market = requests.get(db_address+'markets').json()

# Get utility
utility = requests.get(db_address+'utilities').json()
	
# Get rate
rate = requests.get(db_address+'rates').json()

# Get transformer
trafo = requests.get(db_address+'transformers').json()

# Get addresses
address = requests.get(db_address+'addresses').json()

# Get service location
service_locations = requests.get(db_address+'service_locations').json()

# Get Home hubs
hhs = requests.get(db_address+'home_hubs').json()

# Get meters
meters = requests.get(db_address+'meters').json()

# Get PVs
pvs = requests.get(db_address+'pvs').json()

# Time series

# Get bids
mis = requests.get(db_address+'meter_intervals').json()
supply_bids = requests.get(db_address+'bids/?is_supply=true&start_time='+start).json()['results']['data']
buy_bids = requests.get(db_address+'bids/?is_supply=false&start_time='+start).json()['results']['data']

# Get market intervals
market_intervals = requests.get(db_address+'market_intervals').json()['results']['data']

# Get transformer load
db_transformer_meter = pandas.read_csv(results_folder+'/db_transformer_meter.csv',index_col=[0])

# Assemble

last_market_int = pandas.to_datetime(market_intervals[-1]['start_time'])
pandas.date_range(pandas.to_datetime(start),last_market_int,freq=market_freq)

# df_tokens
df_tokes_sample = pandas.read_csv(table_examples+'/df_tokens.csv',index_col=[0],parse_dates=True)
df_tokens = pandas.DataFrame(index=pandas.date_range(pandas.to_datetime(start),last_market_int,freq=market_freq),columns=df_tokes_sample.columns)
for dt in market_intervals:
	dtt = pandas.to_datetime(dt['start_time'])
	if dtt in df_tokens.index:
		df_tokens.at[dtt,'partial'] = dt['alpha']
		df_tokens.at[dtt,'clearing_price'] = dt['p_clear']
		df_tokens.at[dtt,'clearing_quantity'] = dt['q_clear']
for dt in db_transformer_meter.index:
	dtt = dt
	if dtt in df_tokens.index:
		df_tokens.at[dtt,'unresponsive_loads'] = db_transformer_meter['unresp_demand'].loc[dt]
		df_tokens.at[dtt,'slack_t-1'] = db_transformer_meter['current_load'].loc[dt]
df_tokens.dropna(axis=0,how='all',inplace=True)
df_tokens.to_csv(results_eval_folder + '/df_tokens.csv')		

#df_supply_bids - CHECK IF THAT INCLUDES HCE BIDS AFTER hce_bids HAVE BEEN DEPLOYED
df_supply_bids_sample = pandas.read_csv(table_examples+'/df_supply_bids.csv',index_col=[0],parse_dates=True)
df_supply_bids = pandas.DataFrame(index=range(len(supply_bids[1][0])),columns=df_supply_bids_sample.columns)

dtt = 0
for dt in supply_bids[1]:
	df_supply_bids.at[dtt,'timestamp'] = pandas.to_datetime(dt['start_time'])
	df_supply_bids.at[dtt,'appliance_name'] = dt['meter_id']
	df_supply_bids.at[dtt,'bid_price'] = dt['p_bid']
	df_supply_bids.at[dtt,'bid_quantity'] = dt['q_bid']
	dtt += 1
df_supply_bids.to_csv(results_eval_folder + '/df_supply_bids.csv')	

#df_buy_bids - CHECK IF THAT INCLUDES HCE BIDS AFTER hce_bids HAVE BEEN DEPLOYED
df_buy_bids_sample = pandas.read_csv(table_examples+'/df_buy_bids.csv',index_col=[0],parse_dates=True)
try:
	df_buy_bids = pandas.DataFrame(index=range(len(buy_bids[1][0])),columns=df_buy_bids_sample.columns)
except:
	df_buy_bids = pandas.DataFrame(index=[],columns=df_buy_bids_sample.columns)

if len(df_buy_bids) > 0:
	dtt = 0
	for dt in buy_bids[1]:
		df_buy_bids.at[dtt,'timestamp'] = pandas.to_datetime(dt['start_time'])
		df_buy_bids.at[dtt,'appliance_name'] = dt['meter_id']
		df_buy_bids.at[dtt,'bid_price'] = dt['p_bid']
		df_buy_bids.at[dtt,'bid_quantity'] = dt['q_bid']
		dtt += 1
df_buy_bids.to_csv(results_eval_folder + '/df_buy_bids.csv')	

# TO DO

# df_awarded_bids
# df_PV_state



#import pdb; pdb.set_trace()
