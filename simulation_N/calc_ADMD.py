import datetime
import pandas
import math
import numpy as np
import copy
import os

from HH_global import city

def calc_ADMD():
    '''Calculate ADMD from group recorder outputs'''

    #get timestamp and power data from GridLAB-D output
    power_data_temp = pandas.read_csv('glm_generation_'+city+'/calibration_total_load.csv',header=8,usecols=range(1501)) #in kW
    time_data=[[] for k in range(len(power_data_temp['# timestamp']))]
    for t in range(len(power_data_temp['# timestamp'])):
        timestamp_sample=str(power_data_temp['# timestamp'][t])
        time_data[t]=datetime.datetime.strptime(timestamp_sample[0:19],"%Y-%m-%d %H:%M:%S")
    power_data=power_data_temp #copy.deepcopy(power_data_temp)
    
    power_data=power_data.drop('# timestamp',axis=1)
    power_data=np.array(power_data)*1000
    
    #import pdb; pdb.set_trace()
#    #plot individual homes demand    
#    plt.figure(1,figsize=(8,8))
#    for i in range(power_data.shape[1]):
#        plt.plot_date(time_data, power_data[:,i]/1000,'-')
#    formatter = matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S')
#    plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
#    plt.gcf().autofmt_xdate()
#    plt.ylabel('Power (kWh)')

    #calculate total daily energy consumption
    day_energy=np.zeros((int(math.floor((len(power_data_temp)-1))/1440),power_data.shape[1]))
    max_day_energy=np.zeros((power_data.shape[1],1))
    mean_day_energy=np.zeros((power_data.shape[1],1))

    for h in range(power_data.shape[1]):
        for d in range(day_energy.shape[0]):
            day_energy[d,h]=sum(power_data[(d*1440):(d*1440+1440),h])/60 #sum every one minute, divide by 60 for kWh
        max_day_energy[h,0]=max(day_energy[:,h])
        mean_day_energy[h,0]=sum(day_energy[:,h])/math.floor((len(power_data_temp)-1)/1440)
    
    
    #calculate aggregate demand and plot
    agg_power=np.sum(power_data, axis=1) #in kW

    #calculate ADMD (W)
    ADMD=max(agg_power)
    ADMD_per_house=(ADMD/1000)/power_data.shape[1]
    return ADMD_per_house,day_energy,max_day_energy,mean_day_energy

def main():
    out_dir='glm_generation_'+city
    ADMD_per_house,day_energy,max_day_energy,mean_day_energy=calc_ADMD()
    print(ADMD_per_house)
    print(ADMD_per_house)
    print(ADMD_per_house)
#    day_energy.to_csv('day_energy.csv',index=False)
#    max_day_energy.to_csv('max_day_energy.csv',index=False)
#    mean_day_energy.to_csv('mean_day_energy.csv',index=False)
    
    np.savetxt(out_dir+"/day_energy.csv", day_energy, delimiter=",")
    np.savetxt(out_dir+"/max_day_energy.csv", max_day_energy, delimiter=",")
    np.savetxt(out_dir+"/mean_day_energy.csv", mean_day_energy, delimiter=",")


if __name__ == '__main__':
    main()