import requests
from datetime import datetime
import pandas
import time

def run_market(db_address):
	while True:
		local_time = datetime.now()
		if (local_time.second%15 == 0): # & (local_time.microsecond == 0):
			#import pdb; pdb.set_trace()
			print(local_time)
			time.sleep(1)

			print('Last solar measurement')
			print(requests.get(db_address+'meter_intervals').json()['results']['data'][-1])
			last_meter_id = requests.get(db_address+'meter_intervals').json()['results']['data'][-1]['meter_id']

			print('Run market')
			
			print('Set PV generation according to market allocation')
			data = {'rate_id':1,'meter_id':last_meter_id,'start_time':str(local_time),'end_time':str(local_time+pandas.Timedelta(minutes=5)),'e':10.0,'qmtp':2.2,'p_bid':9.9,'q_bid':0.0,'is_bid':True}
			requests.put(db_address+'meter_interval/'+str(last_meter_id),json=data)