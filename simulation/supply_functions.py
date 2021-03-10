#This supply function file specifies the specific bidding functions of HCE

from HH_global import results_folder, flexible_houses, C, p_max, interval, prec, city, market_data
import sys
import pandas
import requests

import market_functions as Mfct
#import mysql_functions as myfct

from HH_global import db_address

class WSSupplier:

	def __init__(self):
		
		self.load_measured = 0.0
		self.prev_cleared = 0.0 #responsive demand which has been cleared in previous interval
		self.p_WS = 0.0

	############
	# Market side / no phycial APIs involved
	############

	#Supply function
	#This should include the whole supply curve, not only WS energy
	def bid_supply(self,dt_sim_time,market):
		# From DB through API
		#p_bid = requests.get(db_address+'WS_supply')['results']['data']
		#q_bid = requests.get(db_address+'WS_supply')['results']['data']

		# Temporary solution
		db_transformer_meter = pandas.read_csv(results_folder+'/db_transformer_meter.csv',index_col=[0],parse_dates=True)
		p_bid = db_transformer_meter['supply_cost'].loc[dt_sim_time]
		q_bid = db_transformer_meter['available_capacity'].loc[dt_sim_time]
		
		#Send and receive directly
		market.sell(q_bid,p_bid,gen_name='WS_market')

		#Send and receive with delay (in RT deployment)
		#timestamp = send_supply_bid(self, dt_sim_time,p_bid,q_bid,name)
		return

	# Unresponsive load
	def bid_unrespload(self,dt_sim_time,lem):
		# From DB through API
		#p_bid = lem.Pmax
		#q_bid = requests.get(db_address+'WS_supply')['results']['data']

		# Temporary solution with db_transformer_meter (should be through API)
		# import pdb; pdb.set_trace()
		# requests.get(db_address+'bids/?is_supply=true&start_time='+str(dt_sim_time)).json()['results']['data'][1][(self.meter-7)]
		# requests.get(db_address+'HceBids')
		# data = {'start_time':str(dt_sim_time),'end_time':str(dt_sim_time+pandas.Timedelta(minutes=5)),'p_bid':0.,'q_bid':0.,'is_supply':True,'comment':'','market_id':1}
		# requests.post(db_address+'HceBids',json=data) #with dummy bid
		# requests.post(db_address+'hce_bids',json=data) #with dummy bid

		db_transformer_meter = pandas.read_csv(results_folder+'/db_transformer_meter.csv',index_col=[0],parse_dates=True)
		p_bid = lem.Pmax
		try:
			p_lem_prev = requests.get(db_address+'market_intervals').json()['results']['data'][-1]['p_clear']
		except:
			p_lem_prev = None # just a dummy, won't be needed (only for first simulation period)

		current_load = db_transformer_meter['current_load'].loc[dt_sim_time]

		local_supply_dict = requests.get(db_address+'bids?is_supply=true&start_time='+str(dt_sim_time - pandas.Timedelta(minutes=5))).json()['results']['data'][1]
		local_supply = 0.0
		for loc in local_supply_dict:
			if pandas.to_datetime(loc['start_time']) == dt_sim_time: # Only at first simulation period, otherwise earlier sim periods are available
				break
			else:
				if loc['p_bid'] < p_lem_prev:
					local_supply += loc['qmtp']
		
		local_flex_demand = 0.0 # Needs to be adjusted for more appliances participating
		q_bid = current_load + local_supply - local_flex_demand # Calculate unresponsive load as residual
		db_transformer_meter.at[dt_sim_time,'unresp_demand'] = q_bid
		db_transformer_meter.to_csv(results_folder+'/db_transformer_meter.csv')
		
		#Send and receive directly
		lem.buy(q_bid,p_bid,appliance_name='unresp_load')

		#Send and receive with delay (in RT deployment)
		#timestamp = send_supply_bid(self, dt_sim_time,p_bid,q_bid,name)

	#Demand function: unresponsive load
	# def bid_unresp(self,dt_sim_time,market):
	# 	P_bid = market.Pmax
	# 	Q_bid = self.load_measured - self.prev_cleared
	# 	#GUSTAVO: this part below should go to the database and not csv
	# 	try:
	# 		df_demand_bids = pandas.read_csv(results_folder + '/df_demand_bids.csv', index_col=[0], parse_dates=['t'])
	# 		df_demand_bids = df_demand_bids.append(pandas.DataFrame(index=[len(df_demand_bids)],columns=['t','name','P_bid','Q_bid'],data=[[dt_sim_time,'unresp_load',P_bid,Q_bid]]))
	# 		df_demand_bids.to_csv(results_folder + '/df_demand_bids.csv')
	# 	except: #only for first time
	# 		df_demand_bids = pandas.DataFrame(index=[0],columns=['t','name','P_bid','Q_bid'],data=[[dt_sim_time,'unresp_load',P_bid,Q_bid]])
	# 		df_demand_bids.to_csv(results_folder + '/df_demand_bids.csv')
	# 	return
