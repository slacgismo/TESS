import sys
assert(sys.version_info.major>2)
import gridlabd
import time
import pandas
import global_functions
#import pdb; pdb.set_trace()

##################
#HOW TO
#################

#Set correct settings in settings_calibration.csv
df_settings =pandas.read_csv('settings_calibration.csv',index_col=[0])

#Move clock and rest from header from network file IEEE123_bus
#Delete group_recorders
#Include group_recorder.csv
#Run IEEE_123_homes.glm (no network)

# ##################
# #Assemble correct glm files
# #################
# #write global file with settings from csv file: HH_global.py
# global_functions.write_global(df_settings.loc[0],0,'noip_nomysql')
# #re-write glm model for flexible devices - deactivate if no new file needs to be generated
# import glm_functions
# glm_functions.write_calibrationfile() #2000 houses to calculate mean_energy

# #NOT NEEDED? - Rewrite to calibration file with clock etc.
# #glm_functions.modify_glmfile()

# # ##################
# # #Run GridlabD
# # #################
# from HH_global import city
# gridlabd.command('IEEE_123_homes_1min_calibration_'+city+'.glm')
# gridlabd.command('-D')
# gridlabd.command('suppress_repeat_messages=FALSE')
# #gridlabd.command('--debug')
# #gridlabd.command('--verbose')
# gridlabd.command('--warn')
# gridlabd.start('wait')

# ##################
# #Calculate new mean_energy_day and ADMD
# #################
# print('Start ADMD')
# import calc_ADMD
# calc_ADMD.main()
# sys.exit('Include ADMD_per_house into glm_functions file')

# ##################
# #Repopulate glm house file and create Base_IEEE_123_homes_1min_nothermostatcontrol
# #################
# import global_functions
# global_functions.write_global(df_settings.loc[1],1,'noip_nomysql') #Includes already PV=100% etc. for base_placement creation
# import glm_functions
# glm_functions.rewrite_glmfile(rewrite_houses=True)

