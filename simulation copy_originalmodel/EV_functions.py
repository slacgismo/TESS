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
from HH_global import flexible_houses, C, p_max, interval, prec, start_time_str, end_time_str, EV_data, EV_speed

dep_hours = [6,7,8,9]
arr_hours = [16,17,18,19,20]
list_SOC = [30.,40.,50.,60.]
list_u = [7.,10.,14.,20.]

def get_settings_EVs(EVlist,interval,mysql=False):
      cols_EV = ['EV_name','house_name','SOC_max','i_max','v_max','u_max','efficiency','charging_type','k','soc_t','SOC_t','connected','next_event','active_t-1','active_t']
      df_EV = pandas.DataFrame(columns=cols_EV)   
      #Read in charging events
      #df_events = pandas.read_csv('EV_events_2016_july_Austin.csv',index_col=[0],parse_dates=True) #'EV_events_2015_july.csv'
      df_events = pandas.read_csv(EV_data,index_col=[0],parse_dates=True)
      first_time = pandas.Timestamp.today()
      first_time = first_time.replace(year=first_time.year + 4) #to ensure working with RT data
      for EV in EVlist:
            df_events[EV] = pandas.to_datetime(df_events[EV]) 
            if df_events[EV].min() < first_time:
                  first_time = df_events[EV].min()
      first_time = first_time.replace(hour=0,minute=0,second=0)
      start_time = pandas.to_datetime(start_time_str)
      delta = start_time - first_time
      for EV in EVlist:
            df_events[EV] = df_events[EV] + delta
            EV_obj = gridlabd.get_object(EV)
            #gridlabd.set_value(EV,'use_internal_battery_model','FALSE')
            house_name = 'GLD_'+EV[3:]
            #Use GridLABD default values
            v_max = float(EV_obj['V_Max']) #keep v_max constant for now
            eff = float(EV_obj['base_efficiency'])
            #Fills TABLE market_appliances
            #SOC_min = float(EV_obj['reserve_state_of_charge']) #in % - 20%
            #SOC_max = float(EV_obj['battery_capacity'])/1000 #Wh in Gridlabd -> kWh
            #str_i_max = EV_obj['I_Max']
            #i_max = str_i_max.split('+')[1]
            #u_max = float(EV_obj['V_Max'])*float(i_max)/1000 #W -> kW #better inverter?
            charging_type = EV_obj['charging_type']
            k = float(EV_obj['k']) #no market: always highest wllingsness to pay
            #Gets next event
            cols = [EV,EV+'_u',EV+'_SOC',EV+'_SOCmax']
            df_events_EV = df_events[cols]
            discard_events = True
            while discard_events:
                  if (df_events_EV[EV].iloc[0] < pandas.to_datetime(start_time_str)) and (df_events_EV[EV].iloc[1] < pandas.to_datetime(start_time_str)):
                        df_events_EV = df_events_EV.iloc[2:]
                  elif (df_events_EV[EV].iloc[0] < pandas.to_datetime(start_time_str)) and (df_events_EV[EV].iloc[1] > pandas.to_datetime(start_time_str)):
                        #Get information from EV events table
                        soc_t = df_events_EV[EV+'_SOC'].iloc[0] #relative soc
                        u_max = df_events_EV[EV+'_u'].iloc[0] #in kW
                        SOC_max = df_events_EV[EV+'_SOCmax'].iloc[0] #in kWh
                        #For start of the simulation
                        soc_t = soc_t + (1. - soc_t)/2. #No EV connected yet - at midnight, initialize with 50% charged already
                        SOC_t = soc_t*SOC_max
                        gridlabd.set_value(EV,'state_of_charge',str(soc_t))
                        gridlabd.set_value(EV,'battery_capacity',str(SOC_max*1000))
                        i_max = 1000*u_max/v_max
                        gridlabd.set_value(EV,'I_Max',str(i_max))
                        gridlabd.set_value(EV,'generator_status','ONLINE')
                        next_event = df_events_EV[EV].iloc[1] #Next event: disconnection
                        df_events_EV = df_events_EV.iloc[1:] #Only discard connection event
                        connected = 1
                        discard_events = False
                  elif (df_events_EV[EV].iloc[0] > pandas.to_datetime(start_time_str)) and (df_events_EV[EV].iloc[1] > pandas.to_datetime(start_time_str)):
                        soc_t = 0.0
                        u_max = 0.0
                        SOC_max= 0.0
                        soc_t = 0.0
                        SOC_t = 0.0
                        i_max = 0.0
                        next_event = df_events_EV[EV].iloc[0] #Next event: connection
                        connected =0
                        gridlabd.set_value(EV,'generator_status','OFFLINE')
                        discard_events = False
                  else:
                        print('Unclear or no EV events at that charging station during that time')
                        soc_t = 0.0
                        i_max = 0.0
                        next_event = pandas.to_datetime(end_time_str) #Next event: none / end_time
                        connected = 0
                        gridlabd.set_value(EV,'generator_status','OFFLINE')
                        discard_events = False
            df_EV = df_EV.append(pandas.Series([EV,house_name,SOC_max,i_max,v_max,u_max,eff,charging_type,k,soc_t,SOC_t,connected,next_event,0,0],index=cols_EV),ignore_index=True)
            df_events_EV.index = df_events_EV.index - df_events_EV.index[0] #reset index to range()
            df_events[cols] = df_events_EV[cols]
            df_events.to_csv('EV_events_pop.csv')
      df_EV.set_index('EV_name',inplace=True)
      #Maybe drop all columns which are not used in this glm
      return df_EV

#If no EV data is available, random generation of arrival and departure events as well as SOC_t
def get_settings_EVs_rnd(EVlist,interval,mysql=False):
      cols_EV = ['EV_name','house_name','SOC_max','i_max','v_max','u_max','efficiency','charging_type','k','soc_t','SOC_t','connected','next_event','active_t-1','active_t']
      df_EV = pandas.DataFrame(columns=cols_EV)   
      start_time = dt_sim_time = parser.parse(gridlabd.get_global('clock')).replace(tzinfo=None)
      for EV in EVlist:
            house_name = 'GLD_'+EV[3:]
            EV_obj = gridlabd.get_object(EV)
            #Determine some values
            v_max = float(EV_obj['V_Max']) #keep v_max constant for now
            SOC_max = np.random.choice(list_SOC) #in kWh
            gridlabd.set_value(EV,'battery_capacity',str(SOC_max*1000))
            u_max = np.random.choice(list_u) #in kW
            i_max = 1000*u_max/v_max
            gridlabd.set_value(EV,'I_Max',str(i_max))
            eff = float(EV_obj['base_efficiency'])
            charging_type = EV_obj['charging_type']
            k = float(EV_obj['k']) #no market: always highest wllingsness to pay
            #Randomly generate SOC at midnight
            soc_t = np.random.uniform(0.2,0.8) #relative soc
            soc_t = soc_t + (1. - soc_t)/2. #No EV connected yet - at midnight, initialize with 50% charged already
            gridlabd.set_value(EV,'state_of_charge',str(soc_t))
            SOC_t = soc_t*SOC_max
            connected = 1
            gridlabd.set_value(EV,'generator_status','ONLINE')
            next_event = start_time + pandas.Timedelta(hours=np.random.choice(dep_hours),minutes=np.random.choice(range(60))) #Next event: disconnection
            #Save
            df_EV = df_EV.append(pandas.Series([EV,house_name,SOC_max,i_max,v_max,u_max,eff,charging_type,k,soc_t,SOC_t,connected,next_event,0,0],index=cols_EV),ignore_index=True)
      df_EV.set_index('EV_name',inplace=True)
      #Maybe drop all columns which are not used in this glm
      #import pdb; pdb.set_trace()
      return df_EV

def update_EV(dt_sim_time,df_EV_state):
      print('Update EV')
      df_EV_state['active_t-1'] = df_EV_state['active_t']
      df_EV_state['active_t'] = 0
      df_events = pandas.read_csv('EV_events_pop.csv',index_col=[0], parse_dates=df_EV_state.index.tolist())
      for EV in df_EV_state.index:
            EV_number = int(EV.split('_')[-1])
            next_event, next_u, next_soc, next_socmax = df_events[[EV,EV+'_u',EV+'_SOC',EV+'_SOCmax']].iloc[0]
            next_event = next_event.to_pydatetime()
            #Event change
            if next_event <= dt_sim_time: #event change in the last period -> change in status of battery
                  #prev_event, prev_soc = df_events[[EV,EV+'_SOC']].iloc[0]
                  df_events[[EV,EV+'_u',EV+'_SOC',EV+'_SOCmax']] = df_events[[EV,EV+'_u',EV+'_SOC',EV+'_SOCmax']].shift(-1)

                  #Randomly choose for fast-charging
                  if EV_speed == 'fast':
                        energy_refuel = (1. - next_soc)*next_socmax
                        list_EVs = [(24.,22.),(50.,32.),(50.,60.),(120.,90.)]
                        EV_type = np.random.choice(len(list_EVs),1)[0]
                        next_u, next_socmax = list_EVs[EV_type]
                        next_soc = max(next_socmax - energy_refuel,0.0)/next_socmax
                  
                  #next_event, next_soc = df_events[[EV,EV+'_SOC']].iloc[0]
                  if not np.isnan(next_soc):
                        #Set EV
                        gridlabd.set_value(EV,'generator_status','ONLINE')  
                        gridlabd.set_value(EV,'state_of_charge',str(next_soc))
                        gridlabd.set_value(EV,'battery_capacity',str(next_socmax*1000))
                        i_max = 1000*next_u/df_EV_state['v_max'].loc[EV]
                        gridlabd.set_value(EV,'I_Max',str(i_max))
                        gridlabd.set_value(EV,'P_Max',str(next_u*1000))
                        gridlabd.set_value(EV,'E_Max',str(next_u*1000*1))
                        EV_inv = 'EV_inverter' + EV[2:]
                        gridlabd.set_value(EV_inv,'rated_power',str(1.2*next_u*1000))
                        gridlabd.set_value(EV_inv,'rated_battery_power',str(1.2*next_u*1000))
                        #import pdb; pdb.set_trace()
                         
                        #Set df_EV_state   
                        df_EV_state.at[EV,'SOC_max'] = next_socmax
                        df_EV_state.at[EV,'i_max'] = i_max
                        df_EV_state.at[EV,'u_max'] = next_u
                        df_EV_state.at[EV,'connected'] = 1 #Does this one not work such that delay in connection?
                        df_EV_state.at[EV,'soc_t'] = next_soc
                        df_EV_state.at[EV,'SOC_t'] = next_soc*next_socmax
                        df_EV_state.at[EV,'next_event'] = next_event
                  else: #if next event associated with non-NaN SOC - now connected and pot. charging
                        #Set EV (only switch off)
                        gridlabd.set_value(EV,'generator_status','OFFLINE')  
                        gridlabd.set_value(EV,'state_of_charge',str(0.0))
                        #Set df_EV_state   
                        df_EV_state.at[EV,'SOC_max'] = 0.0
                        df_EV_state.at[EV,'i_max'] = 0.0
                        df_EV_state.at[EV,'u_max'] = 0.0
                        df_EV_state.at[EV,'connected'] = 0 #Does this one not work such that delay in connection?
                        df_EV_state.at[EV,'soc_t'] = 0.0
                        df_EV_state.at[EV,'SOC_t'] = 0.0
                        df_EV_state.at[EV,'next_event'] = next_event
            #After last event (no upcoming events)
            elif pandas.isnull(next_event):
                  #Set EV (only switch off)
                  gridlabd.set_value(EV,'generator_status','OFFLINE')  
                  #Set df_EV_state   
                  df_EV_state.at[EV,'SOC_max'] = 0.0
                  df_EV_state.at[EV,'i_max'] = 0.0
                  df_EV_state.at[EV,'u_max'] = 0.0
                  df_EV_state.at[EV,'connected'] = 0 #Does this one not work such that delay in connection?
                  df_EV_state.at[EV,'soc_t'] = 0.0
                  df_EV_state.at[EV,'SOC_t'] = 0.0
                  df_EV_state.at[EV,'next_event'] = next_event
            #During charging event: Update EV state (SOC)
            elif pandas.isnull(next_socmax):
                  # Updating through GridlabD model
                  EV_obj = gridlabd.get_object(EV)
                  soc_t = float(EV_obj['state_of_charge'])
                  df_EV_state.at[EV,'soc_t'] = soc_t
                  SOC_t = soc_t*float(EV_obj['battery_capacity'])/1000 #In Wh #Losses updated by GridlabD ?
                  df_EV_state.at[EV,'SOC_t'] = SOC_t

                  # Updating using df
                  #print('GLD battery model is not used, manual updating!')
                  #gridlabd.set_value(EV,'state_of_charge',str(df_EV_state['soc_t'].loc[EV])) #in p.u. 
            else:
                  pass

      df_events.to_csv('EV_events_pop.csv')
      return df_EV_state

def update_EV_rnd(dt_sim_time,df_EV_state):
      print('Update EV')
      df_EV_state['active_t-1'] = df_EV_state['active_t']
      df_EV_state['active_t'] = 0


      today = pandas.Timestamp(dt_sim_time.year,dt_sim_time.month,dt_sim_time.day)
      for EV in df_EV_state.index:
            EV_number = int(EV.split('_')[-1])
            next_event = df_EV_state['next_event'].loc[EV]
            #Event change
            if next_event <= dt_sim_time: #event change in the last period -> change in status of battery

                  #Randomly choose for fast-charging
                  if EV_speed == 'fast':
                        energy_refuel = (1. - next_soc)*next_socmax
                        list_EVs = [(24.,22.),(50.,32.),(50.,60.),(120.,90.)]
                        EV_type = np.random.choice(len(list_EVs),1)[0]
                        next_u, next_socmax = list_EVs[EV_type]
                        next_soc = max(next_socmax - energy_refuel,0.0)/next_socmax
                  
                  #just arrived
                  if df_EV_state['connected'].loc[EV] == 0:
                        #Set EV
                        next_u = df_EV_state['u_max'].loc[EV]
                        gridlabd.set_value(EV,'generator_status','ONLINE')
                        soc_t = np.random.uniform(0.2,0.8)  
                        gridlabd.set_value(EV,'state_of_charge',str(soc_t))
                        gridlabd.set_value(EV,'battery_capacity',str(df_EV_state['SOC_max'].loc[EV]*1000))
                        i_max = 1000*next_u/df_EV_state['v_max'].loc[EV]
                        gridlabd.set_value(EV,'I_Max',str(i_max))
                        gridlabd.set_value(EV,'P_Max',str(next_u*1000))
                        gridlabd.set_value(EV,'E_Max',str(next_u*1000*1))
                        EV_inv = 'EV_inverter' + EV[2:]
                        gridlabd.set_value(EV_inv,'rated_power',str(1.2*next_u*1000))
                        gridlabd.set_value(EV_inv,'rated_battery_power',str(1.2*next_u*1000))
                        #import pdb; pdb.set_trace()
                         
                        #Set df_EV_state   
                        df_EV_state.at[EV,'connected'] = 1 #Does this one not work such that delay in connection?
                        df_EV_state.at[EV,'soc_t'] = soc_t
                        df_EV_state.at[EV,'SOC_t'] = soc_t*df_EV_state['SOC_max'].loc[EV]
                        
                        #Departure time tomorrow
                        df_EV_state.at[EV,'next_event'] = today + pandas.Timedelta(days=1,hours=np.random.choice(dep_hours),minutes=np.random.choice(range(60))) #Next event: disconnection
                  
                  else: #if next event associated with non-NaN SOC - now connected and pot. charging
                        #Set EV (only switch off)
                        gridlabd.set_value(EV,'generator_status','OFFLINE')  
                        gridlabd.set_value(EV,'state_of_charge',str(0.0))
                        #Set df_EV_state   
                        df_EV_state.at[EV,'connected'] = 0 #Does this one not work such that delay in connection?
                        df_EV_state.at[EV,'soc_t'] = 0.0
                        df_EV_state.at[EV,'SOC_t'] = 0.0
                        #Arrival time today
                        df_EV_state.at[EV,'next_event'] = today + pandas.Timedelta(hours=np.random.choice(arr_hours),minutes=np.random.choice(range(60))) #Next event: disconnection
            
            #During charging event: Update EV state (SOC)
            elif df_EV_state['connected'].loc[EV] == 1:
                  # Updating through GridlabD model
                  # EV_obj = gridlabd.get_object(EV)
                  # soc_t = float(EV_obj['state_of_charge'])
                  # df_EV_state.at[EV,'soc_t'] = soc_t
                  # SOC_t = soc_t*float(EV_obj['battery_capacity'])/1000 #In Wh #Losses updated by GridlabD ?
                  # df_EV_state.at[EV,'SOC_t'] = SOC_t

                  # Updating using df
                  #print('GLD battery model is not used for EVs, manual updating!')
                  gridlabd.set_value(EV,'state_of_charge',str(df_EV_state['soc_t'].loc[EV])) #in p.u. 
            else:
                  pass

      return df_EV_state

def calc_bids_EV(dt_sim_time,df_bids_EV,retail,mean_p,var_p):
      #Quantity
      safety_fac = 1.0
      df_bids_EV['q_buy'] = 0.0 #general
      #df_bids_EV['residual_u'] = round((3600./interval)*(safety_fac*df_bids_EV['SOC_max'] - df_bids_EV['SOC_t']),prec) #u at which EV would need to be charged during the interval to completely fill it
      df_bids_EV['residual_u'] = (3600./interval)*(safety_fac*df_bids_EV['SOC_max'] - df_bids_EV['SOC_t']).values.astype(float).round(prec) #u at which EV would need to be charged during the interval to completely fill it
      df_bids_EV['q_buy'].loc[df_bids_EV['connected'] == 1] = df_bids_EV.loc[df_bids_EV['connected'] == 1][['residual_u','u_max']].min(axis=1) #in kW
      df_bids_EV['q_buy'].loc[df_bids_EV['q_buy'] < 1.] = 0.0

      #Price
      df_bids_EV['p_buy'] = 0.0 #general
      #Commercial
      df_bids_EV.loc[df_bids_EV['charging_type'].str.contains('comm') & (df_bids_EV['connected'] == 1) & (df_bids_EV['q_buy'] > 0.001),'p_buy'] = retail.Pmax #max for commercial cars
      #Home-based charging
      df_bids_EV['delta'] = df_bids_EV['next_event'] - dt_sim_time
      df_bids_EV['residual_t'] = df_bids_EV['delta'].apply(lambda x: x.seconds)/3600.      #residual time until departure
      rel_index = df_bids_EV.loc[df_bids_EV['charging_type'].str.contains('resi') & (df_bids_EV['connected'] == 1) & (df_bids_EV['q_buy'] > 0.0) & (df_bids_EV['residual_t']*3600 >= interval),'p_buy'].index
      #Bid calculation
      #df_bids_EV.at[rel_index,'p_buy'] = retail.Pmax - df_bids_EV['k'].loc[rel_index] * df_bids_EV['residual_t'].loc[rel_index]
      #Uncommented on 12/23
      #df_bids_EV['intercept'] = mean_p - df_bids_EV['k']*df_bids_EV['u_max']
      #df_bids_EV.at[rel_index,'p_buy'] =  df_bids_EV['intercept'].loc[rel_index] + df_bids_EV['k'].loc[rel_index]*df_bids_EV['residual_u'].loc[rel_index]/df_bids_EV['residual_t'].loc[rel_index]
      #Test on 12/23 - consistent with final report
      df_bids_EV.at[rel_index,'p_buy'] =  p_max - df_bids_EV['k'].loc[rel_index]*(df_bids_EV['u_max'].loc[rel_index] - df_bids_EV['residual_u'].loc[rel_index])

      df_bids_EV['lower_bound'] = 0.0
      df_bids_EV['upper_bound'] = p_max
      df_bids_EV['p_buy'] = df_bids_EV[['p_buy','lower_bound']].max(axis=1) #non-negative bids
      df_bids_EV['p_buy'] = df_bids_EV[['p_buy','upper_bound']].min(axis=1) #non-negative bids
      #print(df_bids_EV[['residual_SOC','delta','p_buy']])

      #For no market case
      #df_bids_EV.loc[df_bids_EV['charging_type'].str.contains('resi') & (df_bids_EV['connected'] == 1) & (df_bids_EV['residual_SOC'] > 0.001),'p_buy'] = retail.Pmax
      return df_bids_EV

def submit_bids_EV(dt_sim_time,retail,df_bids,df_buy_bids):
      for ind in df_bids.index:
            if df_bids['q_buy'].loc[ind] > 0.001: #Unconnected cars have q_buy = 0
                  retail.buy(df_bids['q_buy'].loc[ind],df_bids['p_buy'].loc[ind],active=df_bids['active_t'].loc[ind],appliance_name=ind)
                  #mysql_functions.set_values('buy_bids', '(bid_price,bid_quantity,timedate,appliance_name)',(float(df_bids['p_buy'].loc[ind]),float(df_bids['q_buy'].loc[ind]),dt_sim_time,ind,))
                  df_buy_bids = df_buy_bids.append(pandas.DataFrame(columns=df_buy_bids.columns,data=[[dt_sim_time,ind,float(df_bids['p_buy'].loc[ind]),float(df_bids['q_buy'].loc[ind])]]),ignore_index=True)
      return retail,df_buy_bids

#Partial charging if car drives off?
def set_EV_GLD(dt_sim_time,df_bids_EV,df_awarded_bids):
      #Set charging/discharging
      #Change from no to battery_name
      #Do more quickly by setting database through Gridlabd?
      for EV in df_bids_EV.index:
            EV_number = int(EV.split('_')[-1]) #int(battery.split('_')[1])
            #print df_bids_EV[['connected','SOC','active','next_event']].loc[df_bids_EV['appliance_id'] == EV_number]
            #print type(df_bids_EV['next_event'].loc[df_bids_EV['appliance_id'] == EV_number].values[0])
            #print pd.isnull(df_bids_EV['next_event'].loc[df_bids_EV['appliance_id'] == EV_number].values[0])
            SOC = df_bids_EV['SOC_t'].loc[EV] #this is SOC at the beginning of the period t
            active = df_bids_EV['active_t'].loc[EV] #this is activity in t
            connected = df_bids_EV['connected'].loc[EV]
            if active == 1:
                  q_bid = -1000*df_bids_EV['q_buy'].loc[EV]
                  p_bid = df_bids_EV['p_buy'].loc[EV]
                  gridlabd.set_value('EV_inverter_'+EV[3:],'P_Out',str(q_bid)) #kW -> W    
                  #mysql_functions.set_values('awarded_bids','(appliance_name,p_bid,q_bid,timedate)',(EV,float(p_bid),-float(q_bid)/1000,dt_sim_time))
                  df_awarded_bids = df_awarded_bids.append(pandas.DataFrame(columns=df_awarded_bids.columns,data=[[dt_sim_time,EV,float(p_bid),-float(q_bid)/1000,'D']]),ignore_index=True)
                  
            #elif active == -1:
            #     gridlabd_functions.set('EV_inverter_'+EV[3:],'P_Out',1000*df_bids_EV['q_sell'].loc[df_bids_EV['appliance_id'] == batt_number].values[0]) #kW -> W
            else:
                  gridlabd.set_value('EV_inverter_'+EV[3:],'P_Out','0.0')
      
      print('GLD battery model is not used for EV, manual updating!')
      df_bids_EV['SOC_t'] = df_bids_EV['SOC_t'] + df_bids_EV['active_t']*df_bids_EV['q_buy']/12
      df_bids_EV['soc_t'] = df_bids_EV['SOC_t']/df_bids_EV['SOC_max']
      
      return df_bids_EV,df_awarded_bids

#All EVs switch on for which bid is more or equal to published clearing price
def set_EV_by_price(dt_sim_time,df_bids_EV,mean_p,var_p,Pd,df_awarded_bids):
      #Determine activity
      df_bids_EV.at[(df_bids_EV['p_buy'] >= Pd) & (df_bids_EV['SOC_t'] < df_bids_EV['SOC_max']),'active_t'] = 1
      #df_bids_EV.at[(df_bids_EV['p_sell'] <= Pd) & (df_bids_EV['SOC'] > 0.0),'active'] = -1
      #Set DB and GLD
      df_bids_EV,df_awarded_bids = set_EV_GLD(dt_sim_time,df_bids_EV,df_awarded_bids)
      return df_bids_EV,df_awarded_bids

#Only EVs switch on which got explicitely cleared even
#Not awarded EVs don't switch on even if their bid equals the bid of the marginal demand unit/the clearing price
def set_EV_by_award(dt_sim_time,df_bids_EV,market,df_awarded_bids):
      try:
            list_awards_D = market.D_awarded[:,3]
            list_awards_D = [x for x in list_awards_D if x is not None]
      except:
            list_awards_D = []
      for bidder in list_awards_D:
            if 'EV_' in bidder:
                  df_bids_EV.at[bidder,'active_t'] = 1
      #Set DB and GLD
      df_bids_EV, df_awarded_bids = set_EV_GLD(dt_sim_time,df_bids_EV,df_awarded_bids)
      return df_bids_EV,df_awarded_bids