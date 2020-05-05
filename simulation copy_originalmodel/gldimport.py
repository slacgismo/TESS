#import gridlabd_functions
import os
#import pycurl
from io import StringIO
import json
import gridlabd

def find_objects(criteria) :
	finder = criteria.split("=")
	if len(finder) < 2 :
		raise Exception("find(criteria='key=value'): criteria syntax error")
	objects = gridlabd.get("objects")
	result = []
	for name in objects :
		try:
			item = gridlabd.get_object(name)
			if finder[0] in item.keys() and item[finder[0]] == finder[1] :
				result.append(name)
		except:
			pass
	return result

def get(obj):
	finder = obj.split("=")
	return

def sort_list(unsorted_list):
	sorted_list = []
	if unsorted_list:
		no = [int(x.split('_')[-1]) for x in unsorted_list]
		d = dict(zip(no,unsorted_list))
		for i in range(1,max(no)+1):
			try:
				sorted_list.append(d[i])
			except:
				pass
	return 

def sort_batteries(batteries):
	batterylist_unsorted = [] #;
	EVlist_unsorted = []

	#Batteries not ordered accoridng to house numbers
	for battery in batteries:
		#name = battery['name']
		#if int(battery['name'].split('_')[-1]) < amount:
		if 'Battery_' in battery:
			batterylist_unsorted.append(battery)
		elif 'EV_' in battery:
			EVlist_unsorted.append(battery)

	batterylist = batterylist_unsorted
	#batterylist = sort_list(batterylist_unsorted)
	EVlist = EVlist_unsorted
	#EVlist = sort_list(EVlist_unsorted)

	return batterylist, EVlist

def sort_pvs(pvs):
	pvlist_unsorted = [];

	#Batteries not ordered accoridng to house numbers
	for pv in pvs:
		pvlist_unsorted.append(pv)

	#Sort PVs
	
	pv_list = []
	if pvlist_unsorted:
		pvlist_no = [int(x.split('_')[-1]) for x in pvlist_unsorted]
		d = dict(zip(pvlist_no,pvlist_unsorted))
		for i in range(1,max(pvlist_no)+1):
			try:
				pv_list.append(d[i])
			except:
				pass

	pvinv_list = []
	for pv in pv_list:
		#inverter_name = gridlabd_functions.get(pv,'parent')
		inverter_name = 'PV_inverter_' + pv[3:]
		pvinv_list += [inverter_name]

	return pv_list, pvinv_list