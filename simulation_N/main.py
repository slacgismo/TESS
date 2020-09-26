import sys
assert(sys.version_info.major>2)
import gridlabd
import time
import pandas
#import pdb; pdb.set_trace()

###USER input
ind = 3
df_settings = pandas.read_csv('settings_TESS.csv',index_col=[0])

##################
#Assemble correct glm files
#################
#write global file with settings from csv file: HH_global.py
#import global_functions
#global_functions.write_global(df_settings.loc[ind],ind,'none')
#re-write glm model for flexible devices - deactivate if no new file needs to be generated
#import glm_functions
#glm_functions.rewrite_glmfile(rewrite_houses=False) #Re-populates houses

##################
# Run GridlabD
#################
print('run Gridlabd')
#gridlabd.command('IEEE123_BP_2bus_1min.glm')
gridlabd.command('model.glm')

gridlabd.command('-D')
gridlabd.command('suppress_repeat_messages=FALSE')
#gridlabd.command('--debug')
#gridlabd.command('--verbose')
gridlabd.command('--warn')
gridlabd.start('wait')

# Determine bills and token balances at the end of each month

# Year-long balance


