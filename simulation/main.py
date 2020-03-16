import gridlabd
import pandas
import time

###USER input
ind = 1
df_settings = pandas.read_csv('settings_TESS.csv',index_col=[0])

#write global file with settings from csv file: HH_global.py
import global_functions
global_functions.write_global(df_settings.loc[ind],ind,'none')

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
	time.sleep(5)
	#import pdb; pdb.set_trace()
	import glm_functions_sparse
	glm_functions_sparse.modify_glmfile() #creates model_ts from model_bc (include module gridlabd_functions)
	time.sleep(5)
	#pdb.set_trace()
	gridlabd.command('model_ts.glm')
	gridlabd.start('wait')
