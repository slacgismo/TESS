import os
import mysql.connector
import datetime
from datetime import timedelta
from dateutil import parser
import gridlabd
import pandas

global table_list
from HH_global import ip_address
from credentials import host, user, port, pw, db

table_list = ['buy_bids','supply_bids','awarded_bids']

#for connections outside of this file
def connect():
      mydb = mysql.connector.connect(
            host=host, #'192.168.1.67', #SLAC #'192.168.1.67', #zu Hause '192.168.1.67', #'10.21.152.169', #'198.129.217.106', #network ip
            user=user, #'root',
            port=port,
            passwd=pw,
            database=db
        )
      print('Connected!')
      mycursor = mydb.cursor(buffered = True)
      return mydb, mycursor

mydb, mycursor = connect()

#Clear output databses before start of simulation
def clear_databases(table_list):
      #mydb, mycursor = connect()
      mycursor.execute('SET FOREIGN_KEY_CHECKS = 0')
      for market_table in table_list:
            Delete_all_query = 'truncate table '+market_table+' '
            mycursor.execute(Delete_all_query)
            mydb.commit()
            #print("All Records Deleted Successfully from "+market_table)
      mycursor.execute('SET FOREIGN_KEY_CHECKS = 1')
      print("All Records Successfully Deleted from Database")
      return

def set_WSmarket(df_prices):
      for ind in df_prices.index:
            timestamp = df_prices['timestamp'].loc[ind].to_pydatetime()
            value_tuple = (float(df_prices['RT'].loc[ind]),float(df_prices['DA'].loc[ind]),timestamp,)
            set_values('WS_market','(RT,DA,timedate)',value_tuple)
      return

#Sets values in a database
def set_values(market_table, parameter_string, value_tuple):
      #mydb, mycursor = connect()
      str_VALUE = ''
      for el in value_tuple:
            str_VALUE += '%s, '
      query = 'INSERT INTO '+market_table+parameter_string+' VALUES('+str_VALUE[:-2]+')' #(%s, %s, %s, %s)
      #print query
      mycursor.execute(query, value_tuple)
      return mydb.commit()

def update_value(market_table,col,value,dt_sim_time,id):
      #UPDATE `table_name` SET `column_name` = `new_value' [WHERE condition];
      query = 'UPDATE '+market_table+' SET '+col+'='+str(value)+', timedate='+'"'+str(dt_sim_time)+'"'+' WHERE id = '+str(id) #(%s, %s, %s, %s)
      #print query
      mycursor.execute(query)
      return mydb.commit()

#Gets values from a database (market_table is type string)
def get_values(market_table, begin=None, end=None):
      if begin and end:
            query = 'SELECT * FROM '+market_table+' WHERE timedate >= %(begin)s AND timedate <= %(end)s'
            df = pandas.read_sql(query, con=mydb, params={'begin': begin, 'end': end})
      elif begin:
            query = 'SELECT * FROM '+market_table+' WHERE timedate >= %(begin)s'
            df = pandas.read_sql(query, con=mydb, params={'begin': begin, 'end': end})
      else:
            query = 'SELECT * FROM '+market_table
            df = pandas.read_sql(query, con=mydb)   
      return df

def get_max_value(market_table,col):
      query = 'SELECT MAX('+col+') FROM '+market_table
      mycursor.execute(query)
      for i in mycursor:
            if i[0]:
                  return i[0]
            else:
                  return 0

#Gets specific value from a database (market_table is type string)
def get_spec_value(market_table, column, condition, begin=None, end=None):
      if begin and end:
            query = 'SELECT * FROM '+market_table+' WHERE timedate >= %(begin)s AND timedate <= %(end)s'
            df = pandas.read_sql(query, con=mydb, params={'begin': begin, 'end': end})
      else:
            query = 'SELECT * FROM '+market_table
            df = pandas.read_sql(query, con=mydb)   
      return df