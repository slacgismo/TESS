"""
Defines functions for photovoltaics to update physical measurements and participate in TESS
"""
import datetime
import numpy as np
import pandas
from dateutil import parser
from datetime import timedelta
import requests

from HH_global import db_address, p_max, interval, load_forecast, dispatch_mode

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

      # Updates Python object with physical state
      def update_state(self):
            #import pdb; pdb.set_trace()
            pv_interval = requests.get(db_address+'meter_intervals?meter_id='+str(self.meter)).json()['results']['data'][-1] #Use last measurement
            self.Qmtp = pv_interval['qmtp']
            self.E = pv_interval['e']

      # Bids generation to the market
      def bid(self,dt_sim_time,market,P_exp,P_dev):
            self.P_bid = 0.0 # At zero marginal cost
            if self.alpha > 0.0: # Use latest measurement as estimate for generation in future period
                  self.Q_bid = self.Qmtp / self.alpha
            else:
                  self.Q_bid = self.Q_rated
            if (round(self.Q_bid,market.Qprec) > 0.0):
                  market.sell(self.Q_bid ,self.P_bid,gen_name=self.id)
            last_meter_id = requests.get(db_address+'meter_intervals?meter_id='+str(self.meter)).json()['results']['data'][-1]['meter_interval_id']
            data = {'meter_interval_id': last_meter_id,'rate_id':1,'meter_id':self.meter,'start_time':str(dt_sim_time),'end_time':str(dt_sim_time+pandas.Timedelta(seconds=interval)),'e':self.E,'qmtp':self.Qmtp,'p_bid':self.P_bid,'q_bid':self.Q_bid,'is_bid':True}
            requests.put(db_address+'meter_interval/'+str(last_meter_id),json=data)
            return

      # Writes mode to table to get picked up by PV panels
      def dispatch(self,dt_sim_time,p_lem,alpha):
            if self.P_bid < p_lem:
                  self.mode = 1
            elif np.abs(self.P_bid - p_lem) < 0.001: # marginal bid
                  if (alpha > 1.0) or (alpha < 0.0):
                        alpha = 1.0
                  self.mode = alpha
            else:
                  self.mode = 0 #Curtailment during negative prices?

            data = requests.get(db_address+'meter_intervals?meter_id='+str(self.meter)).json()['results']['data'][-1]
            data['mode_market'] = self.mode
            if dispatch_mode:
                  data['mode_dispatch'] = self.mode
            else:
                  data['mode_dispatch'] = 1.0 # set default : full PV feed-in

            # make IOT Core publish here
            requests.put(db_address+'meter_interval/'+str(data['meter_interval_id']),json=data)

      # For testing - PV should always be on (unless explicitly disconnected by control room)
      def default(self,dt_sim_time,p_lem,alpha):
            data = requests.get(db_address+'meter_intervals?meter_id='+str(self.meter)).json()['results']['data'][-1]
            data['mode'] = 1 # Is on / generates at full power
            requests.put(db_address+'meter_interval/'+str(data['meter_interval_id']),json=data)

# Checks pv table if there is a PV associated with the home hub
def get_PV(house,hh_id):
      pvs = requests.get(db_address+'pvs').json()['results']['data']
      for pv in pvs:
            if pv['home_hub_id'] == hh_id:
                  pv = PV(pv['pv_id'],pv['meter_id'],pv['q_rated'])
                  house.PV = pv
                  return house
      #import pdb; pdb.set_trace()
      print('No PV registered by hh '+str(hh_id))
      return house
