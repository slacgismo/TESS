import pandas as pd

folder = 'Paper/Paper_0002'
save_path = 'glm_generation_Austin/perfect_baseload_forecast_Oct.csv'

df_nomarket = pd.read_csv(folder+'/load_node_149.csv',skiprows=range(8))
df_nomarket['# timestamp'] = df_nomarket['# timestamp'].map(lambda x: str(x)[:-4])
df_nomarket = df_nomarket.iloc[:-1]
df_nomarket['# timestamp'] = pd.to_datetime(df_nomarket['# timestamp'])
df_nomarket.set_index('# timestamp',inplace=True)
df_nomarket['measured_real_power'] = df_nomarket['measured_real_power']/1000

df_hvac_load = pd.read_csv(folder+'/hvac_load_all.csv',skiprows=range(8))
df_hvac_load['# timestamp'] = df_hvac_load['# timestamp'].map(lambda x: str(x)[:-4])
df_hvac_load = df_hvac_load.iloc[:-1]
df_hvac_load['# timestamp'] = pd.to_datetime(df_hvac_load['# timestamp'])
df_hvac_load.set_index('# timestamp',inplace=True)                           
all_hvac = df_hvac_load.sum(axis=1)

df_nomarket['hvac_load'] = all_hvac

df_nomarket['baseload'] = df_nomarket['measured_real_power'] - df_nomarket['hvac_load']

df_baseload = pd.DataFrame(index=df_nomarket.index,columns=['baseload'],data=df_nomarket['baseload'])
df_baseload.to_csv(save_path)