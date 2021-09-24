#This supply function file specifies the bidding functions of the retailer

import sys
import pandas
import requests

import market_functions as Mfct

from HH_global import p_max, interval, market_data, market_id, db_address, transformer_id

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
		p_bid = requests.get(db_address+'bids?is_supply=true&start_time='+str(dt_sim_time)).json()['results']['data'][0][-1]['p_bid']
		q_bid = requests.get(db_address+'bids?is_supply=true&start_time='+str(dt_sim_time)).json()['results']['data'][0][-1]['q_bid']
		market.sell(q_bid,p_bid,gen_name='WS_market_import')
		return market

	# Export function
	def bid_export(self,dt_sim_time,market):
		p_bid = requests.get(db_address+'bids?is_supply=false&start_time='+str(dt_sim_time)).json()['results']['data'][0][-1]['p_bid']
		q_bid = requests.get(db_address+'bids?is_supply=false&start_time='+str(dt_sim_time)).json()['results']['data'][0][-1]['q_bid']
		market.buy(q_bid,p_bid,appliance_name='WS_market_export') # +1% of cost for prefer import over export
		return market

	# Unresponsive load
	def bid_unrespload(self,dt_sim_time,lem):

		# Calculate unresponsive load
		data_new = requests.get(db_address+'transformer_intervals').json()['results']['data'][-1]
		load_SLACK = data_new['q']
		try:
			# Get previous clearing price
			p_t1 = requests.get(db_address+'market_intervals').json()['results']['data'][-1]['p_clear']
			# Get clear supply bids
			#bids_t1 = requests.get(db_address+'/meter_intervals?start_time='+str(dt_sim_time - pandas.Timedelta(seconds=interval))).json()['results']['data'] #Use last measurement
			cleared_flex_supply = 0.0
			supply_bids_all = requests.get(db_address+'bids?is_supply=true&start_time='+str(dt_sim_time - pandas.Timedelta(seconds=interval))).json()['results']['data'][1]
			supply_bids = []
			for supply in supply_bids_all:
				if pandas.Timestamp(supply['start_time']) == (dt_sim_time - pandas.Timedelta(seconds=interval)):
					supply_bids += [supply]
			for bid in supply_bids:
				if bid['p_bid'] <= p_t1:
					cleared_flex_supply += bid['q_bid']
			# Get cleared demand bids
			cleared_flex_demand = 0.0 # in MVP
			# Compute
			unresp_load = load_SLACK - cleared_flex_demand + cleared_flex_supply
		except:
			unresp_load = load_SLACK
		#import pdb; pdb.set_trace()
		# Update database with unresponsive load
		data_new['unresp_load'] = unresp_load
		requests.put(db_address+'transformer_interval/'+str(transformer_id),json=data_new)

		# Place and save unresponsive load bid
		q_bid = unresp_load
		p_bid = lem.Pmax
		data = {'start_time':str(dt_sim_time),'end_time':str(dt_sim_time+pandas.Timedelta(seconds=interval)),'p_bid':p_bid,'q_bid':q_bid,'is_supply':False,'comment':'unresp_load','market_id':market_id}
		requests.post(db_address+'bids',json=data)
		lem.buy(q_bid,p_bid,appliance_name='unresp_load')
		return lem
