#This supply function file specifies the specific bidding functions of HCE
import gridlabd
from HH_global import results_folder, flexible_houses, C, p_max, interval, prec, city, market_data
import sys
import pandas

class WSSupplier:

	def __init__(self):
		self.max_C = C #transformer/grid constraint
		self.mode = 'normal' #else: emergency
		self.load_measured = 0.0
		self.prev_cleared = 0.0 #responsive demand which has been cleared in previous interval
		self.p_WS = 0.0

		df_WS = pandas.read_csv('glm_generation_'+city+'/'+market_data,parse_dates=[-1],index_col=[0])
		df_WS = pandas.DataFrame(index=pandas.to_datetime(df_WS.index.astype(str)),columns=df_WS.columns,data=df_WS.values.astype(float))
		self.df_WS = df_WS

	############
	# Get external information and information through APIs
	############

	def get_slackload(self,dt_sim_time): #GUSTAVO: this information comes from HCE systems
		load_SLACK = float(gridlabd.get_object('node_149')['measured_real_power'])/1000. #measured_real_power in [W]
		self.load_measured = load_SLACK
		return

	def get_WSprice(self,dt_sim_time):
		p_WS = float(self.df_WS['RT'].loc[dt_sim_time]) #GUSTAVO: This should be coming from HCE's system or other real-time portal
		self.p_WS = p_WS
		return

	############
	# Market side / no phycial APIs involved
	############

	#Supply function
	#This should include the whole supply curve, not only WS energy
	def bid_supply(self,dt_sim_time,market):
		if self.mode == 'normal':
			P_bid = min(self.p_WS,market.Pmax)
			Q_bid = self.max_C
			#GUSTAVO: this part below should go to the database and not csv
			try:
				df_supply_bids = pandas.read_csv(results_folder + '/df_supply_bids.csv', index_col=[0], parse_dates=['t'])
				df_supply_bids = df_supply_bids.append(pandas.DataFrame(index=[len(df_supply_bids)],columns=['t','name','P_bid','Q_bid'],data=[[dt_sim_time,'WS_supply',P_bid,Q_bid]]))
				df_supply_bids.to_csv(results_folder + '/df_supply_bids.csv')
			except: #only for first time
				df_supply_bids = pandas.DataFrame(index=[0],columns=['t','name','P_bid','Q_bid'],data=[[dt_sim_time,'WS_supply',P_bid,Q_bid]])
				df_supply_bids.to_csv(results_folder + '/df_supply_bids.csv')
		else:
			sys.exit('SO mode not implemented yet')
		return

	#Demand function: unresponsive load
	def bid_unresp(self,dt_sim_time,market):
		P_bid = market.Pmax
		Q_bid = self.load_measured - self.prev_cleared
		#GUSTAVO: this part below should go to the database and not csv
		try:
			df_demand_bids = pandas.read_csv(results_folder + '/df_demand_bids.csv', index_col=[0], parse_dates=['t'])
			df_demand_bids = df_demand_bids.append(pandas.DataFrame(index=[len(df_demand_bids)],columns=['t','name','P_bid','Q_bid']),data=[[dt_sim_time,'unresp_load',P_bid,Q_bid]])
			df_demand_bids.to_csv(results_folder + '/df_demand_bids.csv')
		except: #only for first time
			df_demand_bids = pandas.DataFrame(index=[0],columns=['t','name','P_bid','Q_bid'],data=[[dt_sim_time,'unresp_load',P_bid,Q_bid]])
			df_demand_bids.to_csv(results_folder + '/df_demand_bids.csv')
		return
