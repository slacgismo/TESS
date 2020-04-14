#This supply function file specifies the specific bidding functions of HCE
import gridlabd
from HH_global import results_folder, flexible_houses, C, p_max, interval, prec, city, market_data
import sys
import pandas

import market_functions as Mfct
import mysql_functions as myfct

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
		p_bid = float(myfct.get_values_td('WS_supply', begin=dt_sim_time, end=dt_sim_time)['WS_price'].iloc[0])
		timestamp_arrival = market.send_supply_bid(dt_sim_time, p_bid, -1.0, 'WS_supply') #Feedback: timestamp of arrival #C determined by market_operator
		return

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
