import gridlabd
import pandas
import time
import requests
print('Requests imported')

###USER input
ind = 1
ip_address = '192.168.1.67'

#write global file with settings from csv file: HH_global.py
df_settings = pandas.read_csv('settings_TESS.csv',index_col=[0],parse_dates=['start_time','end_time'])
import global_functions
global_functions.write_global(df_settings.loc[ind],ind,ip_address)

#Base case
if ind == 0:
	#Rewrites glm file: start and end date, tmy, outputfile
	import glm_functions_sparse
	glm_functions_sparse.rewrite_glmfile()
	#This a newly randomly generated model
	gridlabd.command('model.glm')
	gridlabd.start('wait')
	gridlabd.save('model_bc.glm')
#Test cases
else:
	#This uses the saved model of the first basecase run
	#import glm_functions_sparse
	#glm_functions_sparse.modify_glmfile() #creates model_ts from model_bc (include module gridlabd_functions) - make sure it's identical!
	gridlabd.command('model_ts.glm')
	gridlabd.start('wait')
