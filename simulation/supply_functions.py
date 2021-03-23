#This supply function file specifies the specific bidding functions of HCE

from HH_global import results_folder, flexible_houses, C, p_max, interval, prec, city, market_data
import sys
import pandas
import requests

import market_functions as Mfct
#import mysql_functions as myfct

from HH_global import db_address, transformer_id

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
		market.sell(q_bid,p_bid,gen_name='WS_market')
		return

	# Unresponsive load
	def bid_unrespload(self,dt_sim_time,lem):
		load_SLACK = requests.get(db_address+'transformer_intervals?transformer_id=1&start_time='+str(dt_sim_time)).json()['results']['data'][-1]['q']
		try:
			prev_cleared = requests.get(db_address+'market_intervals?market_id=1&start_time='+str(dt_sim_time - pandas.Timedelta(seconds=interval))).json()['results']['data'][-1]['q_clear']
			prev_unresp = requests.get(db_address+'transformer_intervals?transformer_id=1&start_time='+str(dt_sim_time - pandas.Timedelta(seconds=interval))).json()['results']['data'][-1]['unresp_load']
		except:
			prev_cleared = 0.0
			prev_unresp = 0.0

		prev_traded = prev_cleared - prev_unresp
		q_bid = load_SLACK - prev_traded # at the end of the market period
		p_bid = lem.Pmax
		
		#Send and receive directly
		lem.buy(q_bid,p_bid,appliance_name='unresp_load')
		return
