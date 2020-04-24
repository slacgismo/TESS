import pandas as pd
import mysql.connector
from datetime import datetime
import numpy as np
import mysql_functions
from mysql_functions import table_list

from HH_global import results_folder

"""Downloads all databases as csvs"""

mydb, mycursor = mysql_functions.connect()

def get_values(market_table, begin=None, end=None):
    query = 'SELECT * FROM '+market_table   
    return pd.read_sql(query, con=mydb)

def save_databases(timestamp):
	#mycursor.execute('SHOW TABLES')
	#table_list = mycursor.fetchall()  
	for table_name in table_list:
	    df = get_values(table_name)
	    df.to_csv(results_folder+'/'+table_name+'_'+str(timestamp)+'.csv')

	print('Databases saved')
	return