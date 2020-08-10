#Creates the relevant databases
import mysql_functions
import pandas as pd
import mysql.connector
from datetime import datetime
import numpy as np

no_houses = 6
appliances = ['HVAC','PV','EV','BAT','WH']

mydb, mycursor = mysql_functions.connect()

mycursor.execute('SET FOREIGN_KEY_CHECKS = 0')

for house_no in range(1,7):
    table = 'EV_'+str(house_no)+'_'+'state_out'
    sql = "DROP TABLE "+table #not needed
    try:
        mycursor.execute(sql) 
        print(sql)
    except:
        print(table+' does not exist')

# sql = "DROP TABLE system_load" #not needed
# try:
#     mycursor.execute(sql) 
#     print(sql)
# except:
#     print(table+' does not exist')

#consumers: one DB per house and appliance
for h in range(1,no_houses+1):
    #Settings
    table_name = 'house_'+str(h)+'_settings'
    try:
        #mycursor.execute('CREATE TABLE '+table_name+' (id INT AUTO_INCREMENT PRIMARY KEY, k FLOAT, T_min FLOAT, heating_setpoint FLOAT, T_max FLOAT, cooling_setpoint FLOAT, timedate TIMESTAMP)')
        mycursor.execute('CREATE TABLE '+table_name+' (timedate TIMESTAMP PRIMARY KEY, k FLOAT, T_min FLOAT, heating_setpoint FLOAT, T_max FLOAT, cooling_setpoint FLOAT)')
    except Exception as e:
        print('11')
        print('Error: ', e)
    #Time-dependent state variables: begin of interval
    table_name = 'house_'+str(h)+'_state_in'
    try:
        mycursor.execute('CREATE TABLE '+table_name+' (timedate TIMESTAMP PRIMARY KEY, mode VARCHAR(255), actual_mode VARCHAR(255), T_air FLOAT, q_heat FLOAT, q_cool FLOAT)')
    except Exception as e:
        print('11')
        print('Error: ', e)
    #Time-dependent state variables: end of interval
    table_name = 'house_'+str(h)+'_state_out'
    try:
        #mycursor.execute('CREATE TABLE '+table_name+' (id INT AUTO_INCREMENT PRIMARY KEY, k FLOAT, T_min FLOAT, heating_setpoint FLOAT, T_max FLOAT, cooling_setpoint FLOAT, timedate TIMESTAMP)')
        mycursor.execute('CREATE TABLE '+table_name+' (timedate TIMESTAMP PRIMARY KEY, operating_mode VARCHAR(255), p_HVAC FLOAT)')
    except Exception as e:
        print('11')
        print('Error: ', e)

#consumers: one DB per house
for h in range(1,no_houses+1):
    #Settings
    table_name = 'battery_'+str(h)+'_settings'
    try:
        mycursor.execute('CREATE TABLE '+table_name+' (timedate TIMESTAMP PRIMARY KEY, soc_des FLOAT, soc_min FLOAT, SOC_max FLOAT, i_max FLOAT, u_max FLOAT, efficiency FLOAT, Kes FLOAT)')
    except Exception as e:
        print('11')
        print('Error: ', e)
    #Time-dependent state variables: begin of interval
    table_name = 'battery_'+str(h)+'_state_in'
    try:
        mycursor.execute('CREATE TABLE '+table_name+' (timedate TIMESTAMP PRIMARY KEY, soc_rel FLOAT)')
    except Exception as e:
        print('11')
        print('Error: ', e)
    #Time-dependent state variables: end of interval
    table_name = 'battery_'+str(h)+'_state_out'
    try:
        mycursor.execute('CREATE TABLE '+table_name+' (timedate TIMESTAMP PRIMARY KEY, p_demand FLOAT, p_supply FLOAT, q_demand FLOAT, q_supply FLOAT)')
    except Exception as e:
        print('11')
        print('Error: ', e)
#consumers: one DB per house
for h in range(1,no_houses+1):
    #Settings
    table_name = 'CP_'+str(h)+'_settings'
    try:
        mycursor.execute('CREATE TABLE '+table_name+' (timedate TIMESTAMP PRIMARY KEY, Qmax FLOAT, Qset FLOAT)')
    except Exception as e:
        print('11')
        print('Error: ', e)
    table_name = 'EV_'+str(h)+'_state_in'
    try:
        mycursor.execute('CREATE TABLE '+table_name+' (timedate TIMESTAMP PRIMARY KEY, Kev FLOAT, tdep TIMESTAMP, Emax FLOAT, DeltaE FLOAT)')
    except Exception as e:
        print('11')
        print('Error: ', e)
    table_name = 'EV_'+str(h)+'_state_out'
    try:
        mycursor.execute('CREATE TABLE '+table_name+' (timedate TIMESTAMP PRIMARY KEY, P_bid FLOAT, Q_bid FLOAT, mode FLOAT, DeltaE FLOAT)')
    except Exception as e:
        print('11')
        print('Error: ', e)
#consumers: one DB per house
for h in range(1,no_houses+1):
    #Settings
    table_name = 'PV_'+str(h)+'_settings'
    try:
        mycursor.execute('CREATE TABLE '+table_name+' (timedate TIMESTAMP PRIMARY KEY, Q_rated FLOAT)')
    except Exception as e:
        print('11')
        print('Error: ', e)
    table_name = 'PV_'+str(h)+'_state_in'
    try:
        mycursor.execute('CREATE TABLE '+table_name+' (timedate TIMESTAMP PRIMARY KEY, E FLOAT, Qmtp FLOAT)')
    except Exception as e:
        print('11')
        print('Error: ', e)
    table_name = 'PV_'+str(h)+'_state_out'
    try:
        mycursor.execute('CREATE TABLE '+table_name+' (timedate TIMESTAMP PRIMARY KEY, P_bid FLOAT, Q_bid FLOAT, mode FLOAT)')
    except Exception as e:
        print('11')
        print('Error: ', e)
    # #Time-dependent state variables: begin of interval
    # table_name = 'EV_'+str(h)+'_state_in'
    # try:
    #     mycursor.execute('CREATE TABLE '+table_name+' (timedate TIMESTAMP PRIMARY KEY, soc_rel FLOAT)')
    # except Exception as e:
    #     print('11')
    #     print('Error: ', e)
    # #Time-dependent state variables: end of interval
    # table_name = 'EV_'+str(h)+'_state_out'
    # try:
    #     mycursor.execute('CREATE TABLE '+table_name+' (timedate TIMESTAMP PRIMARY KEY, p_demand FLOAT, p_supply FLOAT, q_demand FLOAT, q_supply FLOAT)')
    # except Exception as e:
    #     print('11')
    #     print('Error: ', e)

#WS supplier
try:
    mycursor.execute('CREATE TABLE WS_supply (timedate TIMESTAMP PRIMARY KEY, source VARCHAR(255), p_max FLOAT, is_active BOOLEAN, is_archived BOOLEAN, created_at TIMESTAMP, updated_at TIMESTAMP)')
except Exception as e:
    print('13')
    print('Error: ', e)



#market operator
try:
    mycursor.execute('CREATE TABLE market (market_id TIMESTAMP PRIMARY KEY, C FLOAT, slack_load FLOAT)')
except Exception as e:
    print('13')
    print('Error: ', e)

try:
    mycursor.execute('CREATE TABLE system_load (timedate TIMESTAMP PRIMARY KEY, C FLOAT, slack_load FLOAT)')
except Exception as e:
    print('13')
    print('Error: ', e)
try:
    mycursor.execute('CREATE TABLE supply_bids (id INT AUTO_INCREMENT PRIMARY KEY, p_bid FLOAT, q_bid FLOAT, arrival_time TIMESTAMP, gen_name VARCHAR(255) not null)')
except Exception as e:
    print('12')
    print('Error: ', e)

try:
    mycursor.execute('CREATE TABLE buy_bids (id INT AUTO_INCREMENT PRIMARY KEY, p_bid FLOAT, q_bid FLOAT, arrival_time TIMESTAMP, appliance_name VARCHAR(255) not null)')
except Exception as e:
    print('9')
    print('Error: ', e)

try:
    mycursor.execute('CREATE TABLE clearing_pq (timedate TIMESTAMP PRIMARY KEY, operating_mode VARCHAR(255), capacity FLOAT, unresp_load FLOAT, p_cleared FLOAT, q_cleared FLOAT, tie_break FLOAT)')
except Exception as e:
    print('10')
    print('Error: ', e)

mycursor.execute('SET FOREIGN_KEY_CHECKS = 0')  
