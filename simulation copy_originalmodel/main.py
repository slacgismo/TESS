import gridlabd

###USER input
ind = 0
df_settings = pandas.read_csv('settings_TESS.csv',index_col=[0])

##################
#Assemble correct glm files
#################
#write global file with settings from csv file: HH_global.py
import global_functions
global_functions.write_global(df_settings.loc[ind],ind,'none')
#Rewrites glm file: start and end date, tmy, outputfile
import glm_functions_sparse
glm_functions_sparse.rewrite_glmfile(rewrite_houses=False) #Re-populates houses

gridlabd.command('model.glm')
#gridlabd.save('tmp_model.glm')
gridlabd.start('wait')


