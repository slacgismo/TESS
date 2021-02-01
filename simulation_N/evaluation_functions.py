import os
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import matplotlib.pyplot as plt

def get_data(folder,file,divide_by=1):
	df_slack = pd.read_csv(folder+'/'+file,skiprows=range(8))
	df_slack['# timestamp'] = df_slack['# timestamp'].map(lambda x: str(x)[:-4])
	df_slack = df_slack.iloc[:-1]
	df_slack['# timestamp'] = pd.to_datetime(df_slack['# timestamp'])
	df_slack.set_index('# timestamp',inplace=True)
	#df_slack = df_slack.loc[start:end]
	df_slack = df_slack/divide_by #kW
	df_slack = df_slack.loc[df_slack.index.minute%5 == 0]
	return df_slack

def get_TS_data(folder,file):
	df_slack = pd.read_csv(folder+'/'+file,index_col=[0],parse_dates=True)
	df_slack = df_slack.loc[df_slack.index.minute%5 == 0]
	return df_slack

# Assembles all files which contain 'file'
def assemble_data(folder_MVP,file):
	all_files = os.listdir(folder_MVP)
	df_files = pd.DataFrame()
	for f in all_files:
		if file in f:
			df = pd.read_csv(folder_MVP + '/' + f,index_col=[0],parse_dates=True)
			if len(df_files) == 0:
				df_files = df.copy()
			else:
				df_files = df_files.append(df)
	return df_files

# Creates a print-out of income / expenses
def get_proccost_MVP(df_settings,ind_b,ind_MVP):
	RR_b = df_settings['RR'].loc[ind_b]
	RR_MVP = df_settings['RR'].loc[ind_MVP]
	assert RR_b == RR_MVP, 'Retail rates in benchmark and MVP not identical'

	print()
	print('Overall RR before introduction of TS [USD/kWh]: '+str(RR_b/1000.))
	print()

	# Benchmark

	folder_b = df_settings['run'].loc[ind_b] + '/' + df_settings['run'].loc[ind_b]+'_'+"{:04d}".format(ind_b)
	df_slack_b = get_data(folder_b,'load_node_149.csv',1000.)
	df_houses_b = get_data(folder_b,'total_load_all.csv')
	df_PV_b = get_data(folder_b,'total_P_Out.csv',1000.)
	procurement_b = df_slack_b['measured_real_power'].sum()/12. # kWh

	# MVP

	folder_MVP = df_settings['run'].loc[ind_MVP] + '/' + df_settings['run'].loc[ind_MVP]+'_'+"{:04d}".format(ind_MVP)
	df_slack_MVP = get_data(folder_MVP,'load_node_149.csv',1000.)
	df_houses_MVP = get_data(folder_MVP,'total_load_all.csv')
	df_PV_MVP = get_data(folder_MVP,'total_P_Out.csv',1000.)
	procurement_MVP = df_slack_MVP['measured_real_power'].sum()/12. # kWh

	# System cost

	input_folder = 'data_' + df_settings['run'].loc[ind_MVP]
	if df_settings['system_op'].loc[ind_MVP] == 'fixed_proc':
		df_controlroom = pd.read_csv(input_folder + '/' + df_settings['control_room_data'].loc[ind_MVP],index_col=[0],parse_dates=True)
		df_controlroom = df_controlroom.loc[df_controlroom.index.minute%5 == 0]
		df_controlroom['time'] = df_controlroom.index
		df_controlroom.drop_duplicates(subset='time',keep='last',inplace=True)
		df_controlroom.drop('time',axis=1,inplace=True)

		assert len(df_controlroom) == len(df_slack_b)
		assert len(df_controlroom) == len(df_slack_MVP)

		proc_cost_b = (df_slack_b['measured_real_power']/12.*(df_settings['coincident_peak_rate'].loc[ind_b]/1000.*df_controlroom['coincident_peak_actual'] + df_settings['fixed_procurement_cost'].loc[ind_b]/1000.*(1. - df_controlroom['coincident_peak_actual']))).sum()
		proc_cost_MVP = (df_slack_MVP['measured_real_power']/12.*(df_settings['coincident_peak_rate'].loc[ind_MVP]/1000.*df_controlroom['coincident_peak_actual'] + df_settings['fixed_procurement_cost'].loc[ind_MVP]/1000.*(1. - df_controlroom['coincident_peak_actual']))).sum()
		savings = proc_cost_b - proc_cost_MVP
	elif df_settings['system_op'].loc[ind_MVP] == 'EIM':
		df_WS = pd.read_csv(input_folder + '/' + df_settings['market_data'].loc[ind_MVP],index_col=[0],parse_dates=True)
		df_WS = df_WS.loc[df_WS.index.minute%5 == 0]
		df_WS['time'] = df_WS.index
		df_WS.drop_duplicates(subset='time',keep='last',inplace=True)
		df_WS.drop('time',axis=1,inplace=True)
		df_WS = df_WS.loc[df_slack_b.index[0]:df_slack_b.index[-1]]

		assert len(df_WS) == len(df_slack_b)
		assert len(df_WS) == len(df_slack_MVP)

		proc_cost_b = (df_slack_b['measured_real_power']/12.*df_WS[df_settings['which_price'].loc[ind_MVP]]).sum()
		proc_cost_MVP = (df_slack_MVP['measured_real_power']/12.*df_WS[df_settings['which_price'].loc[ind_MVP]]).sum()
		savings = proc_cost_b - proc_cost_MVP

	print('Procurement cost wo TS [USD]: '+str(proc_cost_b))
	print('Energy component of retail rate wo TS [USD/kWh]: '+str(proc_cost_b/procurement_b))
	print()
	print('Procurement cost with TS [USD]: '+str(proc_cost_MVP))
	print('Energy component of retail rate with TS [USD/kWh]: '+str(proc_cost_MVP/procurement_MVP))
	print()
	print('Savings [USD]: '+str(proc_cost_b - proc_cost_MVP))
	print()
	return

# Creates a print-out of income / expenses
def compare_value_MVP(df_settings,ind_b,ind_MVP):
	RR_b = df_settings['RR'].loc[ind_b]
	RR_MVP = df_settings['RR'].loc[ind_MVP]
	assert RR_b == RR_MVP, 'Retail rates in benchmark and MVP not identical'

	# Benchmark

	folder_b = df_settings['run'].loc[ind_b] + '/' + df_settings['run'].loc[ind_b]+'_'+"{:04d}".format(ind_b)
	df_slack_b = get_data(folder_b,'load_node_149.csv')
	df_houses_b = get_data(folder_b,'total_load_all.csv')
	df_PV_b = get_data(folder_b,'total_P_Out.csv',1000.)

	# MVP

	folder_MVP = df_settings['run'].loc[ind_MVP] + '/' + df_settings['run'].loc[ind_MVP]+'_'+"{:04d}".format(ind_MVP)
	df_slack_MVP = get_data(folder_MVP,'load_node_149.csv')
	df_houses_MVP = get_data(folder_MVP,'total_load_all.csv')
	df_PV_MVP = get_data(folder_MVP,'total_P_Out.csv',1000.)

	# System cost

	input_folder = 'data_' + df_settings['run'].loc[ind_MVP]
	df_controlroom = pd.read_csv(input_folder + '/' + df_settings['control_room_data'].loc[ind_MVP],index_col=[0],parse_dates=True)
	df_controlroom = df_controlroom.loc[df_controlroom.index.minute%5 == 0]

	proc_cost_b = df_slack_b['measured_real_power']*(df_settings['coincident_peak_rate'].loc[ind_b]*df_controlroom['coincident_peak_actual'] + df_settings['fixed_procurement_cost'].loc[ind_b]*(1. - df_controlroom['coincident_peak_actual']))
	proc_cost_MVP = df_slack_MVP['measured_real_power']*(df_settings['coincident_peak_rate'].loc[ind_MVP]*df_controlroom['coincident_peak_actual'] + df_settings['fixed_procurement_cost'].loc[ind_MVP]*(1. - df_controlroom['coincident_peak_actual']))
	savings = proc_cost_b - proc_cost_MVP

	# Token value

	df_tokens = pd.read_csv(folder_MVP + '/df_tokens.csv',index_col=[0],parse_dates=True)
	traded_tokens = (abs(df_tokens['clearing_price'])*df_tokens['clearing_quantity']).sum()
	import pdb; pdb.set_trace()

	# Setup table customers

	df_results = pd.DataFrame(columns=df_houses_b.columns)
	
	df_results = df_results.append(pd.DataFrame(index=['Consumption_b [kWh]'],data=[df_houses_b.sum(axis=0)/12.]))
	df_results = df_results.append(pd.DataFrame(index=['Generation_b [kWh]'],columns=df_houses_b.columns,data=[df_PV_b.sum(axis=0).values/12.]))
	net_consumption = df_results.loc['Consumption_b [kWh]'] - df_results.loc['Generation_b [kWh]']
	df_results = df_results.append(pd.DataFrame(index=['Net_consumption_b [kWh]'],columns=df_houses_b.columns,data=[net_consumption.values]))
	df_results = df_results.append(pd.DataFrame(index=['Retail_cost_b [USD]'],columns=df_houses_b.columns,data=[RR_b/1000.*net_consumption.values]))

	df_results = df_results.append(pd.DataFrame(index=['Token_expenses_b [USD]'],columns=df_houses_MVP.columns,data=[0.*net_consumption.values]))

	df_results = df_results.append(pd.DataFrame(index=['Consumption_MVP [kWh]'],data=[df_houses_MVP.sum(axis=0)/12.]))
	df_results = df_results.append(pd.DataFrame(index=['Generation_MVP [kWh]'],columns=df_houses_MVP.columns,data=[df_PV_MVP.sum(axis=0).values/12.]))
	net_consumption = df_results.loc['Consumption_MVP [kWh]'] - df_results.loc['Generation_MVP [kWh]']
	df_results = df_results.append(pd.DataFrame(index=['Net_consumption_MVP [kWh]'],columns=df_houses_MVP.columns,data=[net_consumption.values]))
	df_results = df_results.append(pd.DataFrame(index=['Retail_cost_MVP [USD]'],columns=df_houses_MVP.columns,data=[RR_MVP/1000.*net_consumption.values]))

	# Token value

	savings = 0.0
	if df_settings['PV_share'].loc[ind_MVP] > 0.0:
		savings += (df_controlroom['coincident_peak_actual']*(df_PV_MVP.sum(axis=1) - df_PV_b.sum(axis=1))*df_settings['coincident_peak_rate'].loc[ind_MVP]).sum()
	token_value = savings/no_tokens
	df_results = df_results.append(pd.DataFrame(index=['Token_expenses_MVP [USD]'],columns=df_houses_MVP.columns,data=[RR_MVP/1000.*net_consumption.values]))

	import pdb; pdb.set_trace()

	# Set up table retailer

	df_results_retail

	return

# Compares system load and plots it, including coincident peak events
def compare_systemload_MVP(df_settings,ind_b,ind_MVP):
	file = 'load_node_149.csv'

	# System load

	ind = ind_b
	folder = df_settings['run'].loc[ind] + '/' + df_settings['run'].loc[ind]+'_'+"{:04d}".format(ind)
	df_slack_b = get_data(folder,file,1000.)

	ind = ind_MVP
	folder = df_settings['run'].loc[ind] + '/' + df_settings['run'].loc[ind]+'_'+"{:04d}".format(ind)
	df_slack_MVP = get_data(folder,file,1000.)	

	# Load constraint

	folder_data = 'data_' + df_settings['run'].loc[ind]
	df_constraints = pd.read_csv(folder_data + '/' + df_settings['control_room_data'].loc[ind], parse_dates=True, index_col=[0])
	#import pdb; pdb.set_trace()

	# Plot

	fig, [ax1, ax2] = plt.subplots(2, 1,figsize=(16,8), sharex=True, sharey=True)
	
	lns_slack = ax1.plot(df_slack_b['measured_real_power'],label='Feeder load')
	ax1.set_xlim(df_slack_b.index[0],df_slack_b.index[-1])
	ax1.set_ylabel('Measured real power [kW]')
	ax1.title.set_text('Fixed procurement, no TS')
	ax2.plot(df_slack_MVP['measured_real_power'])
	ax2.set_xlim(df_slack_MVP.index[0],df_slack_MVP.index[-1])
	ax2.set_ylabel('Measured real power [kW]')
	ax2.title.set_text('Fixed procurement, with TS')
	i = 0
	for ind in df_constraints.index:
		if df_constraints['coincident_peak_forecasted'].loc[ind] == 1:
			lns_forcp = ax1.axvspan(xmin=ind,xmax=df_constraints.index[i+1], facecolor='r', alpha=0.1, label='Forecasted coincident peak')
			ax2.axvspan(xmin=ind,xmax=df_constraints.index[i+1], facecolor='r', alpha=0.1)
		if df_constraints['coincident_peak_actual'].loc[ind] == 1:
			lns_actcp = ax1.axvspan(xmin=ind,xmax=df_constraints.index[i+1], facecolor='r', alpha=0.5, label='Actual coincident peak')
			ax2.axvspan(xmin=ind,xmax=df_constraints.index[i+1], facecolor='r', alpha=0.5)
		i += 1

	#import pdb; pdb.set_trace()
	lns = lns_slack + [lns_forcp] + [lns_actcp]
	labs = [l.get_label() for l in lns]
	ax1.legend(lns, labs)

	plt.savefig(df_settings['run'].loc[ind_b] + '/01_systemload_MVP_'+str(ind_MVP)+'.png',bbox_inches='tight')
	#import pdb; pdb.set_trace()

	return

# Compares system load and plots it, including coincident peak events
def compare_disaggsystemload_MVP(df_settings,ind_b,ind_MVP):

	# System load

	ind = ind_b
	folder = df_settings['run'].loc[ind] + '/' + df_settings['run'].loc[ind]+'_'+"{:04d}".format(ind)
	df_load_b = get_data(folder,'total_load_all.csv').sum(axis=1) # kW -> kW
	df_PV_b = get_data(folder,'total_P_Out.csv',1000).sum(axis=1) # W -> kW

	ind = ind_MVP
	folder = df_settings['run'].loc[ind] + '/' + df_settings['run'].loc[ind]+'_'+"{:04d}".format(ind)
	df_load_MVP = get_data(folder,'total_load_all.csv').sum(axis=1) # kW -> kW
	df_PV_MVP = get_data(folder,'total_P_Out.csv',1000).sum(axis=1) # W -> kW

	# Load constraint

	folder_data = 'data_' + df_settings['run'].loc[ind]
	df_constraints = pd.read_csv(folder_data + '/' + df_settings['control_room_data'].loc[ind], parse_dates=True, index_col=[0]) # kW
	#import pdb; pdb.set_trace()

	# Plot

	fig, [ax1, ax2] = plt.subplots(2, 1,figsize=(16,8), sharex=True, sharey=True)
	
	lns_load = ax1.plot(df_load_b,label='Residential load')
	lns_PV = ax1.plot(df_PV_b,label='PV generation')
	ax1.set_xlim(df_load_b.index[0],df_load_b.index[-1])
	ax1.set_ylabel('Load and generation [kW]')
	ax1.title.set_text('Fixed procurement, no TS')

	ax2.plot(df_load_MVP,label='Total load')
	ax2.plot(df_PV_MVP,label='PV generation')
	ax2.set_xlim(df_load_MVP.index[0],df_load_MVP.index[-1])
	ax2.set_ylabel('Load and generation [kW]')
	ax2.title.set_text('Fixed procurement, with TS')
	i = 0
	for ind in df_constraints.index:
		if df_constraints['coincident_peak_forecasted'].loc[ind] == 1:
			ax1.axvspan(xmin=ind,xmax=df_constraints.index[i+1], facecolor='r', alpha=0.1)
			ax2.axvspan(xmin=ind,xmax=df_constraints.index[i+1], facecolor='r', alpha=0.1)
		if df_constraints['coincident_peak_actual'].loc[ind] == 1:
			ax1.axvspan(xmin=ind,xmax=df_constraints.index[i+1], facecolor='r', alpha=0.5)
			ax2.axvspan(xmin=ind,xmax=df_constraints.index[i+1], facecolor='r', alpha=0.5)
		i += 1
	
	lns = lns_load + lns_PV
	labs = [l.get_label() for l in lns]
	ax1.legend(lns, labs)

	plt.savefig(df_settings['run'].loc[ind_b] + '/02_disaggsystemload_MVP_'+str(ind_MVP)+'.png',bbox_inches='tight')
	#import pdb; pdb.set_trace()

	return

# Compares system load and plots it, including coincident peak events
def compare_systemload_EIM(df_settings,ind_b,ind_EIM):
	file = 'load_node_149.csv'

	# System load

	ind = ind_b
	folder = df_settings['run'].loc[ind] + '/' + df_settings['run'].loc[ind]+'_'+"{:04d}".format(ind)
	df_slack_b = get_data(folder,file,1000.)

	ind = ind_EIM
	folder = df_settings['run'].loc[ind] + '/' + df_settings['run'].loc[ind]+'_'+"{:04d}".format(ind)
	df_slack_EIM = get_data(folder,file,1000.)	

	df_slack = df_slack_b.merge(df_slack_EIM,how='inner',left_index=True,right_index=True)
	df_slack_b = df_slack_b.loc[df_slack.index[0]:df_slack.index[-1]]
	df_slack_EIM = df_slack_EIM.loc[df_slack.index[0]:df_slack.index[-1]]

	max_load = max(df_slack_b['measured_real_power'].max(),df_slack_EIM['measured_real_power'].max())*1.1
	min_load = min(df_slack_b['measured_real_power'].min(),df_slack_EIM['measured_real_power'].min())
	if min_load > 0.0:
		min_load = 0.9*min_load
	else:
		min_load = min_load*1.1

	# Load constraint

	folder_data = 'data_' + df_settings['run'].loc[ind_EIM]
	df_prices = pd.read_csv(folder_data + '/' + df_settings['market_data'].loc[ind_EIM], parse_dates=True, index_col=[0])
	df_prices = df_prices.loc[df_slack_b.index[0]:df_slack_b.index[-1]]

	file = 'df_tokens.csv'
	df_tokens = get_TS_data(folder,file)

	max_price = max(df_prices[df_settings['which_price'].loc[ind_EIM]].max(),df_tokens['clearing_price'].max())*1.1
	min_price = min(df_prices[df_settings['which_price'].loc[ind_EIM]].min(),df_tokens['clearing_price'].min())
	if min_price > 0.0:
		min_price = 0.9*min_price
	else:
		min_price = min_price*1.1

	# Plot

	fig, [ax1, ax2] = plt.subplots(2, 1, figsize=(16,8), sharex=True, sharey=True)
	lns_slack = ax1.plot(df_slack_b['measured_real_power'],label='Feeder load')
	ax2.set_xlim(df_slack_b.index[0],df_slack_b.index[-1])
	ax12 = ax1.twinx()
	lns_price = ax12.plot(df_prices[df_settings['which_price'].loc[ind_EIM]],'r',label='WS price')
	ax1.set_ylabel('Load and generation [kW]')
	ax1.set_ylim(min_load,max_load)
	ax12.set_ylabel('Wholesale market price [USD]')
	ax12.set_ylim(min_price,max_price)
	ax1.title.set_text('EIM procurement, no TS')

	ax2.plot(df_slack_EIM['measured_real_power'])
	ax22 = ax2.twinx()
	#ax22.plot(df_prices[df_settings['which_price'].loc[ind_EIM]],'r',label='WS price')
	lns_TS = ax22.plot(df_tokens['clearing_price'],'g',label='LEM price')
	ax2.set_xlim(df_slack_EIM.index[0],df_slack_EIM.index[-1])
	ax2.set_ylabel('Load and generation [kW]')
	ax2.set_ylim(min_load,max_load)
	ax22.set_ylabel('Local electricity market price [USD]')
	ax22.set_ylim(min_price,max_price)
	ax2.title.set_text('EIM procurement, with TS')

	lns = lns_slack + lns_price + lns_TS
	labs = [l.get_label() for l in lns]
	ax1.legend(lns, labs)

	plt.savefig(df_settings['run'].loc[ind] + '/01_systemload_EIM_'+str(ind_EIM)+'.png',bbox_inches='tight')

	return

def compare_disaggsystemload_EIM(df_settings,ind_b,ind_EIM):

	# System load

	ind = ind_b
	folder = df_settings['run'].loc[ind] + '/' + df_settings['run'].loc[ind]+'_'+"{:04d}".format(ind)
	df_load_b = get_data(folder,'total_load_all.csv').sum(axis=1) # kW -> kW
	if df_settings['PV_share'].loc[ind] > 0.0:
		df_PV_b = get_data(folder,'total_P_Out.csv',1000).sum(axis=1) # W -> kW

	ind = ind_EIM
	folder = df_settings['run'].loc[ind] + '/' + df_settings['run'].loc[ind]+'_'+"{:04d}".format(ind)
	df_load_EIM = get_data(folder,'total_load_all.csv').sum(axis=1) # kW -> kW
	if df_settings['PV_share'].loc[ind] > 0.0:
		df_PV_EIM = get_data(folder,'total_P_Out.csv',1000).sum(axis=1) # W -> kW

	# Prices

	folder_data = 'data_' + df_settings['run'].loc[ind_EIM]
	df_prices = pd.read_csv(folder_data + '/' + df_settings['market_data'].loc[ind_EIM], parse_dates=True, index_col=[0])
	df_prices = df_prices.loc[df_load_b.index[0]:df_load_b.index[-1]]

	# Load constraint

	folder_data = 'data_' + df_settings['run'].loc[ind_EIM]
	df_constraints = pd.read_csv(folder_data + '/' + df_settings['control_room_data'].loc[ind_EIM], parse_dates=True, index_col=[0])

	# Plot

	fig, [ax1, ax2] = plt.subplots(2, 1, figsize=(16,8), sharex=True, sharey=True)

	# No TS
	lns_load = ax1.plot(df_load_b,label='Residential load')
	if df_settings['PV_share'].loc[ind_b] > 0.0:
		lns_PV = ax1.plot(df_PV_b,label='PV generation')
	ax1.set_xlim(df_load_b.index[0],df_load_b.index[-1])
	ax12 = ax1.twinx()
	lns_price = ax12.plot(df_prices[df_settings['which_price'].loc[ind_EIM]],'r',label='WS price')
	ax1.set_xlim(df_load_b.index[0],df_load_b.index[-1])
	ax1.set_ylabel('Load and generation [kW]')
	ax12.set_ylabel('Wholesale market price [USD]')
	ax1.title.set_text('EIM procurement, no TS')

	# TS
	ax2.plot(df_load_EIM,label='Total load')
	if df_settings['PV_share'].loc[ind_EIM] > 0.0:
		ax2.plot(df_PV_EIM,label='PV generation')
	ax2.set_xlim(df_load_EIM.index[0],df_load_EIM.index[-1])
	ax22 = ax2.twinx()
	ax22.plot(df_prices[df_settings['which_price'].loc[ind_EIM]],'r')
	ax2.set_xlim(df_load_EIM.index[0],df_load_EIM.index[-1])
	ax2.set_ylabel('Load and generation [kW]')
	ax22.set_ylabel('Wholesale market price [USD]')
	ax2.title.set_text('EIM procurement, with TS')

	lns = lns_load + lns_PV + lns_price
	labs = [l.get_label() for l in lns]
	ax1.legend(lns, labs)

	plt.savefig(df_settings['run'].loc[ind] + '/02_disaggsystemload_EIM_'+str(ind_EIM)+'.png',bbox_inches='tight')

	return

def get_token_value(df_settings,ind_b,ind_MVP):
	folder_data = df_settings['run'].loc[ind_MVP] + '/' + df_settings['run'].loc[ind_MVP] + '_' + "{:04d}".format(ind_MVP)

	# Tokens traded
	df_tokens = pd.read_csv(folder_data + '/df_tokens.csv', parse_dates=True, index_col=[0])
	df_tokens['tokens_traded'] = (abs(df_tokens['clearing_price'])/12.*df_tokens['clearing_quantity']/1000.)
	tokens_traded = df_tokens['tokens_traded'].sum()
	
	# Savings

	# Benchmark
	folder_b = df_settings['run'].loc[ind_b] + '/' + df_settings['run'].loc[ind_b]+'_'+"{:04d}".format(ind_b)
	df_slack_b = get_data(folder_b,'load_node_149.csv',1000.)
	df_houses_b = get_data(folder_b,'total_load_all.csv')
	df_PV_b = get_data(folder_b,'total_P_Out.csv',1000.)
	procurement_b = df_slack_b['measured_real_power'].sum()/12. # kWh

	# MVP
	folder_MVP = df_settings['run'].loc[ind_MVP] + '/' + df_settings['run'].loc[ind_MVP]+'_'+"{:04d}".format(ind_MVP)
	df_slack_MVP = get_data(folder_MVP,'load_node_149.csv',1000.)
	df_houses_MVP = get_data(folder_MVP,'total_load_all.csv')
	df_PV_MVP = get_data(folder_MVP,'total_P_Out.csv',1000.)
	procurement_MVP = df_slack_MVP['measured_real_power'].sum()/12. # kWh

	assert len(df_slack_MVP) == len(df_houses_MVP)
	assert len(df_slack_MVP) == len(df_PV_MVP)

	input_folder = 'data_' + df_settings['run'].loc[ind_MVP]
	if df_settings['system_op'].loc[ind_MVP] == 'fixed_proc':
		df_controlroom = pd.read_csv(input_folder + '/' + df_settings['control_room_data'].loc[ind_MVP],index_col=[0],parse_dates=True)
		df_controlroom = df_controlroom.loc[df_controlroom.index.minute%5 == 0]
		df_controlroom['time'] = df_controlroom.index
		df_controlroom.drop_duplicates(subset='time',keep='last',inplace=True)
		df_controlroom.drop('time',axis=1,inplace=True)

		assert len(df_controlroom) == len(df_slack_b)
		assert len(df_controlroom) == len(df_slack_MVP)

		# Proc cost in benchmark senario: WS and PV
		proc_cost_b = (df_slack_b['measured_real_power']/12.*(df_settings['coincident_peak_rate'].loc[ind_b]/1000.*df_controlroom['coincident_peak_actual'] + df_settings['fixed_procurement_cost'].loc[ind_b]/1000.*(1. - df_controlroom['coincident_peak_actual']))).sum()
		proc_cost_b += df_PV_b.sum().sum()*df_settings['RR'].loc[ind_b]/1000. # Net metering
		proc_cost_MVP = (df_slack_MVP['measured_real_power']/12.*(df_settings['coincident_peak_rate'].loc[ind_MVP]/1000.*df_controlroom['coincident_peak_actual'] + df_settings['fixed_procurement_cost'].loc[ind_MVP]/1000.*(1. - df_controlroom['coincident_peak_actual']))).sum()
		if df_settings['customer_op'].loc[ind_MVP] == 'baseline':
			proc_cost_MVP += df_PV_MVP.sum().sum()*df_settings['RR'].loc[ind_MVP]/1000. # Net metering
		else:
			import pdb; pdb.set_trace()
			proc_cost_MVP += (df_PV_MVP.sum(axis=1)*df_tokens['clearing_price']/12./1000.).sum() # Net metering
		savings = proc_cost_b - proc_cost_MVP
	elif df_settings['system_op'].loc[ind_MVP] == 'EIM':
		df_WS = pd.read_csv(input_folder + '/' + df_settings['market_data'].loc[ind_MVP],index_col=[0],parse_dates=True)
		df_WS = df_WS.loc[df_WS.index.minute%5 == 0]
		df_WS['time'] = df_WS.index
		df_WS.drop_duplicates(subset='time',keep='last',inplace=True)
		df_WS.drop('time',axis=1,inplace=True)
		df_WS = df_WS.loc[df_slack_b.index[0]:df_slack_b.index[-1]]

		assert len(df_WS) == len(df_slack_b)
		assert len(df_WS) == len(df_slack_MVP)

		proc_cost_b = (df_slack_b['measured_real_power']/12.*df_WS[df_settings['which_price'].loc[ind_MVP]]/1000.).sum()
		proc_cost_b += df_PV_b.sum().sum()*df_settings['RR'].loc[ind_b]/1000. # Net metering
		proc_cost_MVP = (df_slack_MVP['measured_real_power']/12.*df_WS[df_settings['which_price'].loc[ind_MVP]]/1000.).sum()
		proc_cost_MVP += (df_PV_MVP.sum(axis=1)/12.*df_tokens['clearing_price']/1000.).sum()
		savings = proc_cost_b - proc_cost_MVP

	# Token value

	if tokens_traded != 0.0:
		token_value = savings/tokens_traded
	else:
		token_value = 0.0

	print()
	print('Savings of retailer: ' + str(savings))
	print('Number of tokens traded: ' + str(tokens_traded))
	print('Token value: ' + str(token_value))
	print()
	print('Share of periods with no tokens traded [%]: ' + str(100.*len(df_tokens.loc[(df_tokens['clearing_price']*df_tokens['clearing_quantity']) == 0.0])/len(df_tokens)))
	print('Share of periods with positive equilibrium token price [%]: ' + str(100.*len(df_tokens.loc[(df_tokens['clearing_price']*df_tokens['clearing_quantity']) > 0.0])/len(df_tokens)))
	print('Share of periods with negative equilibrium token price [%]: ' + str(100.*len(df_tokens.loc[(df_tokens['clearing_price']*df_tokens['clearing_quantity']) < 0.0])/len(df_tokens)))
	print()
	return token_value

# Assembles table for all time steps of the simulation
def assemble_data(folder,file):
	for name in os.listdir(folder):
		if file in name:
			df = pd.read_csv(folder + '/' + name,index_col=[0],parse_dates=True)
			try:
				df_bids = df_bids.append(df,ignore_index=True)
			except:
				df_bids = df.copy()
	return df_bids

def get_bills_baseline(df_settings,ind_b,ind_MVP):

	# Benchmark (net metering at fixed RR)
	print('\nBenchmark\n')

	# Price / RR
	RR = df_settings['RR'].loc[ind_b]
	print('Retail rate [USD/kWh]: ' + str(RR/1000.))

	# Read in load
	folder_b = df_settings['run'].loc[ind_b] + '/' + df_settings['run'].loc[ind_b]+'_'+"{:04d}".format(ind_b)
	df_slack_b = get_data(folder_b,'load_node_149.csv',1000.)
	df_houses_b = get_data(folder_b,'total_load_all.csv')
	df_PV_b = get_data(folder_b,'total_P_Out.csv',1000.)
	procurement_b = df_slack_b['measured_real_power'].sum()/12. # kWh

	# Calculate net load and bill at RR
	df_houses_b_consumption = pd.DataFrame(index=df_houses_b.index,columns=df_houses_b.columns,data=((df_houses_b.values - df_PV_b.values)/12.))
	bills_b = df_houses_b_consumption.sum(axis=0)*RR/1000.
	print('Retail bills in benchmark scenario for billing time [USD]: ' + str(df_slack_b.index[0]) + ' to ' + str(df_slack_b.index[-1]))
	print(bills_b)

	# MVP
	print('\nTransactive system\n')

	# Tokens traded

	RR = df_settings['RR'].loc[ind_MVP]
	print('Retail rate [USD/kWh]: ' + str(RR/1000.))
	token_value = get_token_value(df_settings,ind_b,ind_MVP)
	print('Token value [USD/kWh]: ' + str(token_value/1000.))

	# MVP
	folder_MVP = df_settings['run'].loc[ind_MVP] + '/' + df_settings['run'].loc[ind_MVP]+'_'+"{:04d}".format(ind_MVP)
	df_slack_MVP = get_data(folder_MVP,'load_node_149.csv',1000.)
	df_houses_MVP = get_data(folder_MVP,'total_load_all.csv')
	df_PV_MVP = get_data(folder_MVP,'total_P_Out.csv',1000.)
	procurement_MVP = df_slack_MVP['measured_real_power'].sum()/12. # kWh

	df_tokens = pd.read_csv(folder_MVP + '/df_tokens.csv', parse_dates=True, index_col=[0])
	df_awarded_bids = assemble_data(folder_MVP,'df_awarded_bids')
	df_awarded_bids['timestamp'] = pd.to_datetime(df_awarded_bids['timestamp'])
	df_awarded_bids.set_index('timestamp',inplace=True)
	#df_supply_bids = assemble_data(folder_MVP,'df_supply_bids')

	# Calculate net load and bill at RR
	df_houses_MVP_consumption = pd.DataFrame(index=df_houses_MVP.index,columns=df_houses_MVP.columns,data=((df_houses_MVP.values - df_PV_MVP.values)/12.))
	bills_MVP = df_houses_MVP_consumption.sum(axis=0)*RR/1000.
	df_bills_MVP = pd.DataFrame(index=bills_MVP.index,columns=['Gross bills'],data=bills_MVP.values)
	df_bills_MVP['No of tokens earned'] = 0.0
	for appliance in df_bills_MVP.index:
		appliance_name = 'PV_' + str(appliance.split('_')[1])
		df_awarded_bids_i = df_awarded_bids.loc[df_awarded_bids['appliance_name'] == appliance_name]
		df_awarded_bids_i.at[df_awarded_bids_i.index,'clearing_price'] = df_tokens['clearing_price'].loc[df_awarded_bids_i.index]
		import sys; sys.exit('Fix the sign in token price')
		token_house = (-df_awarded_bids_i['bid_quantity']*df_awarded_bids_i['clearing_price']/12./1000.).sum()
		token_balance = token_house * token_value
		df_bills_MVP.loc[appliance,'No of tokens earned'] = token_house
		df_bills_MVP.loc[appliance,'Token balance [USD]'] = token_balance
	df_bills_MVP['Net bills'] = df_bills_MVP['Gross bills'] - df_bills_MVP['Token balance [USD]']
	print('Retail bills in benchmark scenario for billing time [USD]: ' + str(df_slack_MVP.index[0]) + ' to ' + str(df_slack_MVP.index[-1]))
	print(df_bills_MVP)

	return
