"""
Defines functions for the HH

Uses direct setting of system mode
"""
import gridlabd
#import gridlabd_functions
#from gridlabd_functions import p_max # ???????????????
#import mysql_functions
#from HH_global import *

import datetime
import numpy as np
import pandas
from dateutil import parser
from datetime import timedelta

"""NEW FUNCTIONS / MYSQL DATABASE AVAILABLE"""

#HVAC
from HH_global import flexible_houses, p_max, interval, prec, load_forecast, customer_op, RR, start_time_str

def get_settings(pvlist,interval,mysql=False):
      cols_PV = ['PV_name','house_name','inverter_name','rated_power','P_Out','inv_ON_t-1','inv_ON_t','q_sell','p_sell']
      df_PV = pandas.DataFrame(columns=cols_PV)
      for PV in pvlist:
            house_name = 'GLD_'+PV[3:]
            inverter_name = 'PV_inverter_' + PV[3:]
            #rated_power = float(gridlabd.get_object(inverter_name)['rated_power'][:-3])/1000
            df_PV = df_PV.append(pandas.Series([PV,house_name,inverter_name,0.0,0.0,1.0,1.0,0.0,0.0],index=cols_PV),ignore_index=True)
      return df_PV

def update_PV(dt_sim_time,df_PV_state):
      # Check if initialization was successful
      if pandas.to_datetime(start_time_str) == dt_sim_time:
            #import pdb; pdb.set_trace()
            for ind in df_PV_state.index:
                  rated_power_inv = float(gridlabd.get_object(df_PV_state['inverter_name'].loc[ind])['rated_power'][:-3])/1000
                  rated_power_PV = float(gridlabd.get_object(df_PV_state['PV_name'].loc[ind])['rated_power'][:-3])/1000
                  df_PV_state.at[ind,'rated_power'] = min(rated_power_inv,rated_power_PV)
      # Update P_Out
      for PV in df_PV_state.index: #directly frmom mysql
            P_Out = float(gridlabd.get_object(df_PV_state['inverter_name'].loc[PV])['P_Out'][:-3])/1000  #PV production in kW
            df_PV_state.at[PV,'P_Out'] = P_Out
      df_PV_state['inv_ON_t-1'] = df_PV_state['inv_ON_t']
      df_PV_state['inv_ON_t'] = 1.0 # in general, the inverter is active!
      return df_PV_state

def calc_bids_PV(dt_sim_time,df_PV_state,retail):
      if customer_op == 'direct':
            df_PV_state['p_sell'] = 0.0
      elif customer_op == 'baseline':
            df_PV_state['p_sell'] = -RR # under net metering, -RR is the minimum price at which PV would be sold at profit (per MWh)
      else:
            import sys; sys.exit('This customer operation mode is not defined')
      if load_forecast == 'myopic':
            #import pdb; pdb.set_trace()
            df_PV_state['q_sell'].loc[df_PV_state['inv_ON_t-1'] > 0.0] = df_PV_state['P_Out'].loc[df_PV_state['inv_ON_t-1'] > 0.0]/df_PV_state['inv_ON_t-1'].loc[df_PV_state['inv_ON_t-1'] > 0.0] #last value corrected by partial operations; later: add more sophisticated versions based on forecasts and (deviation) cost minimization 
            # if inverter had been switched off, bid with rated power (this is very posiive for PV owner)
            # Alternative: last infeed or average infeed
            df_PV_state['q_sell'].loc[df_PV_state['inv_ON_t-1'] == 0.0] = df_PV_state['rated_power'].loc[df_PV_state['inv_ON_t-1'] == 0.0]
      elif load_forecast == 'perfect':
            try:
                  df_PV_forecast = pandas.read_csv('glm_generation_'+city+'/perfect_PV_forecast_'+month+'.csv')
                  df_PV_forecast['# timestamp'] = df_PV_forecast['# timestamp'].str.replace(r' UTC$', '')
                  df_PV_forecast['# timestamp'] = pandas.to_datetime(df_PV_forecast['# timestamp'])
                  df_PV_forecast.set_index('# timestamp',inplace=True)
                  df_PV_forecast = df_PV_forecast[df_PV_state.PV_name]
                  max_PV_forecast = df_PV_forecast.loc[(df_baseload.index >= dt_sim_time) & (df_baseload.index < dt_sim_time + pandas.Timedelta(str(int(interval/60))+' min'))].max()
            except:
                  df_PV_state['q_sell'] = df_PV_state['P_Out']/df_PV_state['inv_ON_t-1'] #If only perfect load forecast available but not PV data
      return df_PV_state

def submit_bids_PV(dt_sim_time,retail,df_bids,df_supply_bids):
      for ind in df_bids.index:
            if df_bids['q_sell'].loc[ind] > 0.0:
                  if customer_op == 'baseline':
                        retail.buy(df_bids['q_sell'].loc[ind],df_bids['p_sell'].loc[ind],appliance_name=df_bids['PV_name'].loc[ind]) #later: pot. strategic quantity reduction
                        df_supply_bids = df_supply_bids.append(pandas.DataFrame(columns=df_supply_bids.columns,data=[[dt_sim_time,df_bids['PV_name'].loc[ind],float(df_bids['p_sell'].loc[ind]),float(df_bids['q_sell'].loc[ind])]]),ignore_index=True)
                  elif customer_op == 'direct':
                        retail.sell(df_bids['q_sell'].loc[ind],df_bids['p_sell'].loc[ind],gen_name=df_bids['PV_name'].loc[ind]) #later: pot. strategic quantity reduction
                        df_supply_bids = df_supply_bids.append(pandas.DataFrame(columns=df_supply_bids.columns,data=[[dt_sim_time,df_bids['PV_name'].loc[ind],float(df_bids['p_sell'].loc[ind]),float(df_bids['q_sell'].loc[ind])]]),ignore_index=True)
      return retail, df_supply_bids

def set_PV(dt_sim_time,market,df_bids,df_awarded_bids):
      try:
            list_awards_S = market.S_awarded[:,3]
            list_awards_S = [x for x in list_awards_S if x is not None]
      except:
            list_awards_S = []
      #if not 'PV_' in list_awards_S:
      #      return
      #import pdb; pdb.set_trace()
      for bidder in list_awards_S:
            if 'PV_' in bidder:
                  s_bids = df_bids.loc[df_bids['PV_name'] == bidder]
                  if len(s_bids) > 1:
                        import sys
                        sys.exit('More than one line matching')
                  p_bid = s_bids['p_sell']
                  q_bid = s_bids['q_sell'] #kW
                  df_awarded_bids = df_awarded_bids.append(pandas.DataFrame(columns=df_awarded_bids.columns,data=[[dt_sim_time,bidder,float(p_bid),float(q_bid),'S']]),ignore_index=True)
      return df_awarded_bids

def set_PV_GLD(dt_sim_time,df_PV_state,df_awarded_bids,partial,alpha):
      #import pdb; pdb.set_trace()
      for ind in df_PV_state.index:        
            PV = df_PV_state['PV_name'].loc[ind]
            # if inverter has not been and is not switched off, only save bid and NO interaction with GLD 
            if (df_PV_state['inv_ON_t'].loc[ind] == 1.) and (df_PV_state['inv_ON_t-1'].loc[ind] == 1.):
                  # Keep inverter unchanged: 
                  pass
            elif (df_PV_state['inv_ON_t'].loc[ind] > 0.0) and (df_PV_state['inv_ON_t-1'].loc[ind] < 1.):
                  gridlabd.set_value(df_PV_state['inverter_name'].loc[ind],'generator_status','ONLINE')
                  gridlabd.set_value(df_PV_state['inverter_name'].loc[ind],'P_Out',str(df_PV_state['inv_ON_t'].loc[ind]*df_PV_state['q_sell'].loc[ind]))  #Switch on inverter at 1.0 or alpha
            # if inverter is to be switched off
            elif (df_PV_state['inv_ON_t'].loc[ind] == 0.0):
                  #gridlabd.set_value(df_PV_state['inverter_name'].loc[ind],'P_Out','0.0') #Switch inverter (partially) off
                  gridlabd.set_value(df_PV_state['inverter_name'].loc[ind],'generator_status','OFFLINE') #Switch inverter (partially) off
            else:
                  print('Should not happen unless for the first iteration')
      return df_PV_state,df_awarded_bids

def set_PV_by_price(dt_sim_time,df_PV_state,Pd,df_awarded_bids,partial,alpha):
      # Determine inverter setting
      if customer_op == 'baseline':
            df_PV_state.at[df_PV_state['p_sell'] >= Pd,'inv_ON_t'] = 0. # in case of baseline, it's a buy bid - switch off if bid is cleared
            if (alpha < 1.0) and (partial == 'D'):
                  df_PV_state.at[df_PV_state['p_sell'] == Pd,'inv_ON_t'] = 1. - alpha
      elif customer_op == 'direct':
            df_PV_state.at[df_PV_state['p_sell'] > Pd,'inv_ON_t'] = 0. # Switch off if supply bid is not cleared
            if (alpha < 1.0) and (partial == 'S'):
                  df_PV_state.at[df_PV_state['p_sell'] == Pd,'inv_ON_t'] = alpha
      # Set inverter
      #import pdb; pdb.set_trace()
      df_PV_state,df_awarded_bids = set_PV_GLD(dt_sim_time,df_PV_state,df_awarded_bids,partial,alpha)
      # Record awarded bids
      if customer_op == 'baseline':
            for ind in df_PV_state.index:
                  PV = df_PV_state['PV_name'].loc[ind]
                  p_bid = df_PV_state['p_sell'].loc[ind]
                  q_bid = df_PV_state['q_sell'].loc[ind]
                  if (df_PV_state['q_sell'].loc[ind] > 0.0) and (df_PV_state['p_sell'].loc[ind] > Pd): # if a positive bid exists
                        df_awarded_bids = df_awarded_bids.append(pandas.DataFrame(columns=df_awarded_bids.columns,data=[[dt_sim_time,PV,float(p_bid),float(q_bid),'D']]),ignore_index=True)
                  elif (df_PV_state['q_sell'].loc[ind] > 0.0) and (df_PV_state['p_sell'].loc[ind] == Pd): # if a positive bid exists
                        df_awarded_bids = df_awarded_bids.append(pandas.DataFrame(columns=df_awarded_bids.columns,data=[[dt_sim_time,PV,float(p_bid),float(alpha*q_bid),'D']]),ignore_index=True)
      elif customer_op == 'direct':
            for ind in df_PV_state.index:
                  PV = df_PV_state['PV_name'].loc[ind]
                  p_bid = df_PV_state['p_sell'].loc[ind]
                  q_bid = df_PV_state['q_sell'].loc[ind]
                  if (df_PV_state['q_sell'].loc[ind] > 0.0) and (df_PV_state['p_sell'].loc[ind] < Pd): # if a positive bid exists
                        df_awarded_bids = df_awarded_bids.append(pandas.DataFrame(columns=df_awarded_bids.columns,data=[[dt_sim_time,PV,float(p_bid),float(q_bid),'S']]),ignore_index=True)
                  elif (df_PV_state['q_sell'].loc[ind] > 0.0) and (df_PV_state['p_sell'].loc[ind] == Pd): # if a positive bid exists
                        df_awarded_bids = df_awarded_bids.append(pandas.DataFrame(columns=df_awarded_bids.columns,data=[[dt_sim_time,PV,float(p_bid),float(alpha*q_bid),'S']]),ignore_index=True)
      return df_awarded_bids
