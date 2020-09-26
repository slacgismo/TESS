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

import requests
from HH_global import db_address
#import mysql_functions as myfct

"""NEW FUNCTIONS / MYSQL DATABASE AVAILABLE"""

#HVAC
from HH_global import flexible_houses, C, p_max, interval, prec, load_forecast, city, month

class PV:
      def __init__(self, pv_id, meter, Q_rated):
            self.id = pv_id
            self.meter = meter
            self.Q_rated = Q_rated
            self.Qmtp = 0.0 #Last measured power
            self.E = 0.0 #Energy in past 15min
            self.P_bid = 0.0
            self.Q_bid = 0.0
            self.alpha = 1.0
            self.mode = 1

      def update_state(self,pv_interval):
            self.Qmtp = pv_interval['qmtp']
            self.E = pv_interval['e']

      def bid(self,dt_sim_time,market,P_exp,P_dev):
            self.P_bid = 0.0
            if self.alpha > 0.0:
                  self.Q_bid = self.Qmtp / self.alpha
            else:
                  self.Q_bid = self.Q_rated
            if (self.Q_bid > 0.0):
                  #Send and receive directly
                  market.sell(q_bid,p_bid,gen_name=self.name)
                  #Send and receive with delay (in RT deployment)
                  #timestamp_arrival = market.send_supply_bid(dt_sim_time, float(self.P_bid), float(self.Q_bid), self.name) #Feedback: timestamp of arrival #C determined by market_operator
            self.alpha = 1.0
            return

      def dispatch(self,dt_sim_time,p_lem,alpha):
            if self.P_bid < p_lem:
                  self.mode = 1
            elif numpy.abs(self.P_bid - p_lem) < 0.001:
                  self.mode = alpha
            else:
                  self.mode = 0 #Curtailment during negative prices?
            
            #Post state to TESS DB (simulation time) - should have an alpha_t
            #df_meter = requests.get(db_address+'meter_intervals/'+str(self.id))
            #data = {'rate_id':1,'meter_id':PV.meter,'start_time':str(dt_sim_time),'end_time':str(dt_sim_time+pandas.Timedelta(minutes=5)),'e':E,'qmtp':Qmtp,'p_bid':0.,'q_bid':0.,'is_bid':True}
            #requests.put(db_address+'meter_interval',json=data) #with dummy bid
            

def get_PV(house,hh_id):
      pvs = requests.get(db_address+'pvs').json()['results']['data']
      for pv in pvs:
            if pv['home_hub_id'] == hh_id:
                  pv = PV(pv['pv_id'],pv['meter_id'],pv['q_rated'])
                  house.PV = pv
                  return house
      print('No PV installed by hh '+str(hh_id))
      return house



# OLD

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
