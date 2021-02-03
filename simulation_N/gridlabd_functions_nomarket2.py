import test_import
import os
import random
import pandas
import json
import numpy as np
import datetime
from datetime import timedelta
from dateutil import parser
#import mysql_functions
#from mysql_functions import table_list
#import HH_functions as HHfct
#import battery_functions as Bfct
#import EV_functions as EVfct
#import PV_functions as PVfct
#import market_functions as Mfct
import time

#from HH_global import flexible_houses, C, p_max, interval, prec, price_intervals, unresp_factor, FIXED_TARIFF, include_SO

#To Do
#Battery
#PV
#EV

#What should be recorded in mysql
#Only if not recordable in GridlabD and non-static information which cannot be saved by simple to_csv() at the end!!
#bids

#Should glm characteristics be written to mysql database?
def on_init(t):
	print('Initialize finished')
	return True

def init(t):
	print('Objective-specific Init')
	return True

#Global precommit
#Should be mostly moved to market precommit
def on_precommit(t):
	return t

def on_term(t):
	print('Simulation ended, saving results')
	return None

#Object-specific precommit
def precommit(obj,t) :
	return gridlabd.NEVER #t #True #tt 


