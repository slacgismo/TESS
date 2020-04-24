"""
Defines functions for the HH

Uses direct setting of system mode
"""
import gridlabd
import gridlabd_functions
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
from HH_global import flexible_houses, C, p_max, interval, prec, load_forecast, city, month

def get_settings(pvlist,interval,mysql=False):
      cols_PV = ['PV_name','house_name','inverter_name','rated_power','P_Out']
      df_PV = pandas.DataFrame(columns=cols_PV)
      for PV in pvlist:
            house_name = 'GLD_'+PV[3:]
            inverter_name = 'PV_inverter_' + PV[3:]
            rated_power = float(gridlabd.get_object(inverter_name)['rated_power'])/1000
            df_PV = df_PV.append(pandas.Series([PV,house_name,inverter_name,rated_power,0.0],index=cols_PV),ignore_index=True)
      return df_PV

def update_PV(dt_sim_time,df_PV_state):
      for PV in df_PV_state.index: #directly frmom mysql
            P_Out = float(gridlabd.get_object(df_PV_state['inverter_name'].loc[PV])['P_Out'])/1000  #PV production in kW
            df_PV_state.at[PV,'P_Out'] = P_Out
      return df_PV_state

def calc_bids_PV(dt_sim_time,df_PV_state,retail):
      df_PV_state['p_sell'] = 0.0
      if load_forecast == 'myopic':
            df_PV_state['q_sell'] = df_PV_state['P_Out'] #last value; later: add more sophisticated versions based on forecasts and (deviation) cost minimization 
      elif load_forecast == 'perfect':
            try:
                  df_PV_forecast = pandas.read_csv('glm_generation_'+city+'/perfect_PV_forecast_'+month+'.csv')
                  df_PV_forecast['# timestamp'] = df_PV_forecast['# timestamp'].str.replace(r' UTC$', '')
                  df_PV_forecast['# timestamp'] = pandas.to_datetime(df_PV_forecast['# timestamp'])
                  df_PV_forecast.set_index('# timestamp',inplace=True)
                  df_PV_forecast = df_PV_forecast[df_PV_state.PV_name]
                  max_PV_forecast = df_PV_forecast.loc[(df_baseload.index >= dt_sim_time) & (df_baseload.index < dt_sim_time + pandas.Timedelta(str(int(interval/60))+' min'))].max()
            except:
                  df_PV_state['q_sell'] = df_PV_state['P_Out'] #If only perfect load forecast available but not PV data
      return df_PV_state

def submit_bids_PV(dt_sim_time,retail,df_bids,df_supply_bids):
      for ind in df_bids.index:
            if df_bids['q_sell'].loc[ind] > 0.0:
                  retail.sell(df_bids['q_sell'].loc[ind],df_bids['p_sell'].loc[ind],gen_name=df_bids['PV_name'].loc[ind]) #later: pot. strategic quantity reduction
                  #mysql_functions.set_values('supply_bids', '(bid_price,bid_quantity,timedate,gen_name)',(float(df_bids['p_sell'].loc[ind]),float(df_bids['q_sell'].loc[ind]),dt_sim_time,df_bids['PV_name'].loc[ind],))
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
