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
from HH_global import flexible_houses, C, p_max, interval, prec, which_price, M, results_folder

def get_settings_batteries(batterylist,interval,mysql=False):
      dt = parser.parse(gridlabd.get_global('clock')) #Better: getstart time!
      #prev_timedate = dt - timedelta(minutes=interval/60)
      #Prepare dataframe to save settings and current state
      cols_battery = ['battery_name','house_name','SOC_min','SOC_max','i_max','u_max','efficiency','SOC_t','active_t-1','active_t','threshold_sell','threshold_buy']
      df_battery = pandas.DataFrame(columns=cols_battery)
      for battery in batterylist:
            battery_obj = gridlabd.get_object(battery)
            house_name = 'GLD_'+battery[8:]
            #Fills TABLE market_appliances
            SOC_min = float(battery_obj['reserve_state_of_charge']) #in %
            SOC_max = float(battery_obj['battery_capacity'])/1000 #Wh in Gridlabd -> kWh
            str_i_max = battery_obj['I_Max'].replace('-','+')
            i_max = str_i_max.split('+')[1]
            u_max = float(battery_obj['V_Max'])*float(i_max)/1000 #W -> kW #better inverter?
            eff = float(battery_obj['base_efficiency'])
            #Fills TABLE market_appliance_meter
            SOC_0 = float(battery_obj['state_of_charge'])*SOC_max
            df_battery = df_battery.append(pandas.Series([battery,house_name,SOC_min,SOC_max,i_max,u_max,eff,SOC_0,0,0,0.0,0.0],index=cols_battery),ignore_index=True)          
      df_battery.set_index('battery_name',inplace=True)           
      return df_battery

#Mixture between updated state of the house and HVAC meter setting
def update_battery(df_battery_state):
      #-1: discharging, 0 no activity, 1 charging
      #history is saved by battery recorder (P_out)
      df_battery_state['active_t-1'] = df_battery_state['active_t']
      df_battery_state['active_t'] = 0 
      for batt in df_battery_state.index: #directly from mysql
            battery_obj = gridlabd.get_object(batt)
            SOC_t = float(battery_obj['state_of_charge'])*df_battery_state['SOC_max'].loc[batt] #In Wh #Losses updated by GridlabD ?
            df_battery_state.at[batt,'SOC_t'] = SOC_t
      return df_battery_state

#Schedules battery for next 24 hours by simple ordering
def schedule_battery_ordered(df_WS,df_battery_state,dt_sim_time,i):
      df_WS_prices = df_WS.loc[dt_sim_time:dt_sim_time+datetime.timedelta(hours=23,minutes=55)]
      df_WS_prices = df_WS_prices.sort_values(which_price,axis=0,ascending=False) #,inplace=True)
      #Calculate number of charging/discharging periods
      df_battery_state['no_periods'] = 0
      df_battery_state['no_periods'] = (3600/interval)*((df_battery_state['SOC_max'] - df_battery_state['SOC_min'])/df_battery_state['u_max'])
      df_battery_state['no_periods'] = df_battery_state['no_periods'].astype(int)
      #Sort prices and calculate average prices of no_periods cheapest/most expensive periods
      for ind in df_battery_state.index:
            threshold_sell = df_WS_prices[which_price].iloc[df_battery_state['no_periods'].loc[ind] - 1]
            df_battery_state.at[ind,'threshold_sell'] = threshold_sell
            threshold_buy = df_WS_prices[which_price].iloc[-df_battery_state['no_periods'].loc[ind]]
            df_battery_state.at[ind,'threshold_buy'] = threshold_buy
      df_battery_state.drop('no_periods',axis=1,inplace=True)
      df_battery_state.to_csv(results_folder+'/df_battery_thresholds_'+str(i)+'.csv')
      return df_battery_state

#Schedules battery for next 24 hours by convex optimization
def schedule_battery_cvx(df_WS,df_battery_state,dt_sim_time):
      import cvxpy as cvx
      df_WS_prices = df_WS.loc[dt_sim_time:dt_sim_time+datetime.timedelta(hours=23,minutes=55)]
      
      battery_rate = cvx.Variable((len(df_battery_state),len(df_WS_prices))) #battery x time periods
      battery_energy = cvx.Variable((len(df_battery_state),len(df_WS_prices)))

      constraint_rate = df_battery_state['u_max'].to_numpy().reshape(len(df_battery_state['u_max']),1)*np.ones((1,len(df_WS_prices))) 
      constraint_energy = df_battery_state['SOC_max'].to_numpy().reshape(len(df_battery_state['SOC_max']),1)*np.ones((1,len(df_WS_prices))) 

      constraints = [battery_rate >= -constraint_rate, battery_rate <= constraint_rate]
      constraints += [battery_energy[:,0] == df_battery_state['SOC_t'], battery_energy >= 0, battery_energy <= constraint_energy]
      for i in np.arange(1, len(df_WS_prices)):
            #remove eff and use the one from df
            constraints += [battery_energy[:,i] == 0.996*battery_energy[:,i-1] + battery_rate[:,i-1]*(interval/3600.)] #batt_rate positive for charging; neg for discharging

      obj = cvx.sum(battery_rate*df_WS_prices[which_price]) 
      #+ 0.0001*cvx.sum_squares(battery_rate)
      #- 0.001*cvx.sum(cvx.abs(battery_rate) - constraint_rate/2)
      #- 0.001*(cvx.sum_squares(cvx.abs(battery_rate) - constraint_rate/2))
      #0.001*(cvx.sum(-(battery_rate - constraint_rate/2)**2)) #
      prob = cvx.Problem(cvx.Minimize(obj), constraints) #Cost minimization (bec discharging is negative)
      prob.solve()

      #Sort prices and calculate average prices of no_periods cheapest/most expensive periods
      price_array = df_WS_prices[which_price].to_numpy().reshape(1,len(df_WS_prices))
      price_array = np.ones((len(df_battery_state),1))*price_array
      #Lowest threshold of selling (discharging / negative rate)
      sell = np.copy(battery_rate.value)
      sell[sell > -0.001] = 0
      sell[sell <= -0.001] = 1 #discharging
      sell = np.multiply(sell, price_array)
      #Highest threshold of buying
      buy = np.copy(battery_rate.value)
      buy[buy < 0.001] = 0
      buy[buy >= 0.001] = 1 #charging
      buy = np.multiply(buy, price_array)
      np.savetxt(results_folder+'/df_battery_sell_'+str(dt_sim_time)+'.csv',sell)
      np.savetxt(results_folder+'/df_battery_buy_'+str(dt_sim_time)+'.csv',buy)
      return

def batt_myopic_bid(df_bids_battery,mean_p):
      df_bids_battery['p_sell'] = mean_p / df_bids_battery['eff']
      df_bids_battery['p_buy'] = mean_p * df_bids_battery['eff']
      return df_bids_battery

def batt_schedule_bythreshold(df_bids_battery,dt_sim_time):
      df_bids_battery['p_sell'] = df_bids_battery['threshold_sell']
      df_bids_battery['p_buy'] = df_bids_battery['threshold_buy']
      return df_bids_battery

def calc_bids_battery(dt_sim_time,df_state_battery,retail,mean_p,var_p):
      #Simple price rule
      #df_bids_battery = batt_myopic_bid(df_bids_battery,mean_p)
      df_state_battery = batt_schedule_bythreshold(df_state_battery,dt_sim_time)
      #Quantity depends on SOC and u
      df_state_battery['residual_s'] = round((3600./interval)*(df_state_battery['SOC_t'] - df_state_battery['SOC_min']*df_state_battery['SOC_max']),prec) #Recalculate to kW
      df_state_battery['q_sell'] = df_state_battery[['residual_s','u_max']].min(axis=1) #in kW / only if fully dischargeable
      df_state_battery['q_sell'].loc[df_state_battery['q_sell'] < 0.1] = 0.0

      safety_fac = 0.99
      df_state_battery['residual_b'] = round((3600./interval)*(safety_fac*df_state_battery['SOC_max'] - df_state_battery['SOC_t']),prec) #Recalculate to kW
      df_state_battery['q_buy'] = df_state_battery[['residual_b','u_max']].min(axis=1) #in kW
      df_state_battery['q_buy'].loc[df_state_battery['q_buy'] < 0.1] = 0.0
      #print df_bids_battery[['SOC_max','SOC','residual_s','q_sell','residual_b','q_buy']] #check if q* correctly formed
      
      """Should we enable negative prices?"""
      df_state_battery['lower_bound'] = 0.0
      df_state_battery['p_sell'] = df_state_battery[['p_sell','lower_bound']].max(axis=1)
      df_state_battery['lower_bound'] = 0.0
      df_state_battery['p_buy'] = df_state_battery[['p_buy','lower_bound']].max(axis=1)
      return df_state_battery

def submit_bids_battery(dt_sim_time,retail,df_bids,df_supply_bids,df_buy_bids):
      for ind in df_bids.index:
            if df_bids['q_sell'].loc[ind] > 0.0:
                  retail.sell(df_bids['q_sell'].loc[ind],df_bids['p_sell'].loc[ind],gen_name=ind)
                  df_supply_bids = df_supply_bids.append(pandas.DataFrame(columns=df_supply_bids.columns,data=[[dt_sim_time,ind,float(df_bids['p_sell'].loc[ind]),float(df_bids['q_sell'].loc[ind])]]),ignore_index=True)
                  #mysql_functions.set_values('supply_bids', '(bid_price,bid_quantity,timedate,gen_name)',(float(df_bids['p_sell'].loc[ind]),float(df_bids['q_sell'].loc[ind]),dt_sim_time,ind,))
            if df_bids['q_buy'].loc[ind] > 0.0:
                  retail.buy(df_bids['q_buy'].loc[ind],df_bids['p_buy'].loc[ind],active=df_bids['active_t-1'].loc[ind],appliance_name=ind)
                  df_buy_bids = df_buy_bids.append(pandas.DataFrame(columns=df_buy_bids.columns,data=[[dt_sim_time,ind,float(df_bids['p_buy'].loc[ind]),float(df_bids['q_buy'].loc[ind])]]),ignore_index=True)
                  #mysql_functions.set_values('buy_bids', '(bid_price,bid_quantity,timedate,appliance_name)',(float(df_bids['p_buy'].loc[ind]),float(df_bids['q_buy'].loc[ind]),dt_sim_time,ind,))
      df_bids['active_t-1'] = 0
      return retail,df_supply_bids,df_buy_bids

def set_battery_GLD(dt_sim_time,df_bids_battery,df_awarded_bids):
      #Check efficiencies!!!
      #Set charging/discharging
      #Change from no to battery_name
      #Do more quickly by setting database through Gridlabd?
      for battery in df_bids_battery.index:
            batt_number = int(battery.split('_')[-1]) #int(battery.split('_')[1])
            SOC = df_bids_battery['SOC_t'].loc[battery] #this is SOC at the beginning of the period t
            active = df_bids_battery['active_t'].loc[battery] #this is activity in t
            if active == 1:
                  q_bid = df_bids_battery['q_buy'].loc[battery]
                  p_bid = df_bids_battery['p_buy'].loc[battery]
                  gridlabd.set_value('Bat_inverter_'+battery[8:],'P_Out',str(-1000*q_bid)) #kW -> W    
                  #mysql_functions.set_values('awarded_bids','(appliance_name,p_bid,q_bid,timedate)',(battery,float(p_bid),-float(q_bid)/1000,dt_sim_time))
                  df_awarded_bids = df_awarded_bids.append(pandas.DataFrame(columns=df_awarded_bids.columns,data=[[dt_sim_time,battery,float(p_bid),float(q_bid),'D']]),ignore_index=True)
            elif active == -1:
                  q_bid = df_bids_battery['q_sell'].loc[battery]
                  p_bid = df_bids_battery['p_sell'].loc[battery]
                  gridlabd.set_value('Bat_inverter_'+battery[8:],'P_Out',str(1000*q_bid)) #kW -> W
                  #Include sales as negative
                  #mysql_functions.set_values('awarded_bids','(appliance_name,p_bid,q_bid,timedate)',(battery,float(p_bid),-float(q_bid)/1000,dt_sim_time))
                  df_awarded_bids = df_awarded_bids.append(pandas.DataFrame(columns=df_awarded_bids.columns,data=[[dt_sim_time,battery,float(p_bid),float(q_bid),'S']]),ignore_index=True)
            else:
                  gridlabd.set_value('Bat_inverter_'+battery[8:],'P_Out','0.0')
      return df_bids_battery, df_awarded_bids

def set_battery_by_price(dt_sim_time,df_bids_battery,mean_p,var_p,Pd,df_awarded_bids):
      #Determine activity
      df_bids_battery.at[:,'active_t'] = 0
      df_bids_battery.at[(df_bids_battery['p_buy'] >= Pd) & (df_bids_battery['SOC_t'] < df_bids_battery['SOC_max']),'active_t'] = 1
      df_bids_battery.at[(df_bids_battery['p_sell'] <= Pd) & (df_bids_battery['SOC_t'] > 0.0),'active_t'] = -1
      #Set DB and GLD
      df_bids_battery, df_awarded_bids = set_battery_GLD(dt_sim_time,df_bids_battery,df_awarded_bids)
      return df_bids_battery,df_awarded_bids

def set_battery_by_award(dt_sim_time,df_bids_battery,market,df_awarded_bids):
      df_bids_battery.at[:,'active_t'] = 0
      try:
            list_awards_D = market.D_awarded[:,3]
            list_awards_D = [x for x in list_awards_D if x is not None]
      except:
            list_awards_D = []
      for bidder in list_awards_D:
            if 'Battery_' in bidder:
                  df_bids_battery.at[bidder,'active_t'] = 1
      #print 'Suppliers '+str(market.S_awarded)
      try:
            list_awards_S = market.S_awarded[:,3]
            list_awards_S = [x for x in list_awards_S if x is not None]
      except:
            list_awards_S = []
      for bidder in list_awards_S:
            if 'Battery_' in bidder:
                  df_bids_battery.at[bidder,'active_t'] = -1
      #Set DB and GLD
      df_bids_battery, df_awarded_bids = set_battery_GLD(dt_sim_time,df_bids_battery,df_awarded_bids)
      return df_bids_battery, df_awarded_bids


