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

# efcts.get_proccost_MVP(df_settings,ind_b,ind_MVP_red) # without TESS
# efcts.get_proccost_MVP(df_settings,ind_b,ind_MVP_incr) # without TESS
# efcts.get_proccost_MVP(df_settings,ind_b,ind_EIM) # without TESS
# import pdb; pdb.set_trace()

# Token value

# token_value = efcts.get_token_value(df_settings,ind_b,ind_MVP_red) # without TESS
# token_value = efcts.get_token_value(df_settings,ind_b,ind_MVP_incr) # without TESS
# token_value = efcts.get_token_value(df_settings,ind_b,ind_EIM) # without TESS

# Customer bills

#token_value = efcts.get_bills_baseline(df_settings,ind_b,ind_MVP_red) # without TESS
token_value = efcts.get_bills_baseline(df_settings,ind_b,ind_MVP_incr) # without TESS
import pdb; pdb.set_trace()

token_value = efcts.get_token_value(df_settings,ind_b,ind_MVP_incr) # without TESS
token_value = efcts.get_token_value(df_settings,ind_b,ind_EIM) # without TESS



# HCE income

get_retail_income(ind_b) # all customers pay RR + net-metering
get_all_income(ind_MVP) # calculates retail income + tokens
get_all_income(ind_EIM) # calculates retail income + tokens

