# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 13:41:29 2019

@author: MLA

Takes glm as input and creates random arrival and departure events
"""
import pandas as pd
import datetime
import random

"""INPUT"""

file = 'IEEE_123_homes_1min_nothermostatcontrol_25_0_25.glm'
target_name = 'EV_events_2016_25_0_25.csv'

start = datetime.datetime.strptime('2016-07-01 00:00:00', '%Y-%m-%d %H:%M:%S')
end = datetime.datetime.strptime('2016-07-07 23:59:00', '%Y-%m-%d %H:%M:%S')

"""CALCULATION"""

glm = open(file,'r')
obj = False
name = False
ch_type = False
df_types = pd.DataFrame(columns=['EV','EV_SOC','charging_type'])
i = 0

for line in glm:
    if obj and ('EV_B' in line):
        df_types.loc[i,'EV'] = line.split(' ')[1].split(';')[0]  
        df_types.loc[i,'EV_SOC'] = line.split(' ')[1].split(';')[0]+'_SOC'
        name = True
    if name and ('charging_type' in line):
        df_types.loc[i,'charging_type'] = line.split(' ')[1].split(';')[0]
        ch_type = True
    if name and ch_type:
        obj = False
        name = False
        ch_type = False
        i += 1
    if 'object battery' in line:
        obj = True
    
glm.close()

print(df_types)

def random_date(start, end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    return start + datetime.timedelta(seconds=random.randrange(int_delta))

df_events = pd.DataFrame(columns=sorted(list(df_types['EV'])+list(df_types['EV_SOC'])))

for EV in df_types['EV']:
    if df_types['charging_type'].loc[df_types['EV'] == EV].iloc[0] == 'commercial':
        next_event = start
        i = 0
        while next_event <= end:
            if i%2 == 0: #Arrival
                next_event += datetime.timedelta(seconds=random.randrange(3 * 60 * 60))
                df_events.at[i,EV] = next_event
                df_events.at[i,EV+'_SOC'] =  round(random.uniform(0.2,0.8),3)
            else:
                next_event += datetime.timedelta(seconds=random.randrange(1*60*60, 4*60*60))
                df_events.at[i,EV] = next_event
            i += 1
        #to terminate parking after end of simulation period
        if i%2 > 0:
            next_event += datetime.timedelta(seconds=random.randrange(4 * 60 * 60))
            df_events.at[i,EV] = next_event
    else:
        start_d = start
        end_d = end
        d = 0
        while start_d < end:
            df_events.at[2*d,EV] = random_date(start_d + datetime.timedelta(hours=6), start_d + datetime.timedelta(hours=24) - datetime.timedelta(hours=12))
            df_events.at[2*d,EV+'_SOC'] =  round(random.uniform(0.2,0.8),3)
            df_events.at[2*d+1,EV] = random_date(start_d + datetime.timedelta(hours=24) - datetime.timedelta(hours=9), start_d + datetime.timedelta(hours=24) - datetime.timedelta(hours=3))
            start_d += datetime.timedelta(hours=24)
            d += 1

df_events.to_csv(target_name)     
print(df_events)