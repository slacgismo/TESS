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
		#import pdb; pdb.set_trace()
		unresp_load = requests.get(db_address+'transformer_intervals?transformer_id=1&start_time='+str(dt_sim_time)).json()['results']['data'][-1]['unresp_load']
		q_bid = unresp_load
		p_bid = lem.Pmax
		data = {'start_time':str(dt_sim_time),'end_time':str(dt_sim_time+pandas.Timedelta(seconds=interval)),'p_bid':p_bid,'q_bid':q_bid,'is_supply':False,'comment':'unresp_load','market_id':market_id}
		requests.post(db_address+'bids',json=data)
		
		#Send and receive directly
		lem.buy(q_bid,p_bid,appliance_name='unresp_load')
		return lem
