import requests
from datetime import datetime

def run_market(db_address):
	while True:
		local_time = datetime.now()
		if (local_time.second%15 == 0) & (local_time.microsecond == 0):
			print('PV generation at '+str(local_time))
			print(requests.get(db_address+'pvs'))
			#hh_list = requests.get(db_address+'home_hubs').json()['results']['data']
			print('Run market')