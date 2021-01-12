import pandas
import evaluation_functions as efcts
import matplotlib.pyplot as ppt

# UC 1: energy procurement cost savings

ind_b = 0
ind_MVP_red = 1
ind_MVP_incr = 2
ind_EIM = 5

df_settings = pandas.read_csv('settings_TESS.csv',index_col=[0])

# Check back with control room visualizations
# https://docs.google.com/document/d/1KZd-MmBu_Ev3oEuL78RZHHDC7n5c-Habh_XZhFoDY-s/edit

# SCREEN 1 : System load

#efcts.compare_systemload_MVP(df_settings,ind_b,ind_MVP_red)
#efcts.compare_systemload_MVP(df_settings,ind_b,ind_MVP_incr)
#efcts.compare_systemload_EIM(df_settings,ind_b,ind_EIM)

# Disaggregated system load

#fcts.compare_disaggsystemload_MVP(df_settings,ind_b,ind_MVP_red)
#efcts.compare_disaggsystemload_MVP(df_settings,ind_b,ind_MVP_incr)
#efcts.compare_disaggsystemload_EIM(df_settings,ind_b,ind_EIM)

# Procurement cost
#efcts.get_proccost_fixed(df_settings,ind_b,ind_MVP_red) # without TESS
#efcts.get_proccost_fixed(df_settings,ind_b,ind_MVP_incr) # without TESS

# Token value
#efcts.get_token_value(df_settings,ind_b,ind_MVP_red) # without TESS
efcts.get_token_value(df_settings,ind_b,ind_MVP_incr) # without TESS


import pdb; pdb.set_trace()
get_proccost_fixed(ind_MVP) # with TESS
get_proccost_EIM(ind_EIM)

#efcts.compare_value_MVP(df_settings,ind_b,ind_MVP_incr)




# Customer payments
get_retail_income(ind_b) # all customers pay RR + net-metering
get_all_income(ind_MVP) # calculates retail income + tokens
get_all_income(ind_EIM) # calculates retail income + tokens

