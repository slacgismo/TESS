import pandas as pd
from datetime import timedelta
from dateutil import parser

def on_precommit(t):
	gridlabd.save('model_tmp.glm')
	# dt_sim_time = parser.parse(gridlabd.get_global('clock')).replace(tzinfo=None)
	# if dt_sim_time == pd.Timestamp(2016,7,1,0,15,0):
	# 	sc = gridlabd.get_object('switch_coordinator')
	# 	#import pdb; pdb.set_trace()
	# 	gridlabd.set_value('switch_coordinator','armed','switch_2')
	# 	print('Switch 2 armed')
	# gridlabd.save('model_'+str(dt_sim_time)+'.glm')
	# print(gridlabd.get_object('switch_coordinator'))
	return t