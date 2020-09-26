#Add manual thermostat control and flexible devices
import numpy as np
import glob
import os
import pandas
import re
import sys
import shutil

#from scipy.stats import norm
#from scipy.stats import truncnorm
import math
import copy
import random

from HH_global import city, player_dir, results_folder
from HH_global import slack_node, start_time_str, end_time_str, interval, flexible_houses, EV_share, PV_share, Batt_share, tmy_file

#First run for new settings (new players, new house parameters, new weather)
def write_calibrationfile():
    #Change absolute path
    root = '/docker_powernet'
    out_dir = 'glm_generation_' + city
    os.chdir(out_dir)
    out_dir = root+'/'+out_dir

    #Total number of houses to generate
    tot_num_houses=2000
    #Probability of each home type
    prob_houses=[0.65196,0.23572,0.074451,0.02692,0.0085,0.00291]
    prob_houses=[m/sum(prob_houses) for m in prob_houses]
    
    #Climate zone for california
    clim_zone="3C"
    
    #Avilable players
    player_list_tmp = os.listdir(player_dir)
    player_list = []
    for p in player_list_tmp:
        if 'player' in p:
            player_list += [p]
    home_count = 0
    tot_zip_dict_sim = dict()
    for player in player_list:
        tot_zip_dict_sim[home_count] = 'glm_generation_'+city+'/' + player_dir+'/'+player #to write into glm file as absolute path
        home_count += 1

    house_dict,player,outputs=gen_home_inputs(out_dir,tot_num_houses,prob_houses,clim_zone,
                                                         tot_zip_dict_sim)
    glm_dict_add,obj_type,globals_list,include_list,sync_list=gen_calibration_glm(out_dir,
            house_dict,player,outputs,tot_zip_dict_sim,0)
    print('Generated GLM file for calibration')
    shutil.copy('IEEE_123_homes_1min_calibration_'+city+'.glm', root)
    os.chdir(root)
    return

def rewrite_glmfile(rewrite_houses=True,run_file=True):
    #Change absolute path
    root = '/docker_powernet'
    out_dir = 'glm_generation_' + city
    os.chdir(out_dir)
    out_dir = root+'/'+out_dir

    #Take Base_123_full.glm and create IEEE123_BP_2bus_1min.glm and IEEE_123_homes_1min.glm
    gen_glm(out_dir,start_time_str,end_time_str,PV_share,Batt_share,EV_share,1,False,rewrite_houses,run_file)

    #Add flexible HVAC
    add_flexHVAC()

    #Reset directory and copy 'IEEE_123_homes_1min.glm' into main folder
    if not rewrite_houses:
        shutil.copy('IEEE_123_homes_1min.glm', root)
        shutil.copy('IEEE123_BP_2bus_1min.glm', root)
    os.chdir(root)
    print(os.getcwd())
    return

def add_flexHVAC():
    file = 'IEEE_123_homes_1min_nothermostatcontrol.glm'
    new_file = 'IEEE_123_homes_1min.glm'

    glm = open(file,'r') 
    new_glm = open(new_file,'w') 
    j = 0
    # Flexible houses
    for line in glm:
        if 'heating_system_type' in line and j < (flexible_houses):
            new_glm.write(line+'\tthermostat_control NONE;\n')
            j += 1
        else:
            new_glm.write(line)
    glm.close()
    new_glm.close()
    return

def gen_glm(out_dir,start_time_str,end_time_str,PV_penetration,bat_penetration,EV_penetration,player_interval,regen_players,rewrite_houses,run_file):
    ##### NETWORK: Load modified GLM file for fully populated case
    base_glm_file='Base_123_full.glm'
    glm_dict_base,obj_type_base,globals_list_base,include_list_base=load_base_glm(out_dir,base_glm_file)
    
    sync_list_base=[]
    glm_dict_base[0]['starttime'] = '"'+start_time_str+'"'
    glm_dict_base[0]['stoptime'] = '"'+end_time_str+'"'
    network_target_file_name='IEEE123_BP_2bus_1min.glm'
    write_base_glm(glm_dict_base,obj_type_base,globals_list_base,include_list_base,out_dir,network_target_file_name,sync_list_base)
    print('Loaded network')
    
    #### PLAYERS: Generate player files in csv format
    #Just get and list existing players, no new player generation
    if not regen_players:
        player_list_tmp = os.listdir(player_dir)
        player_list = []
        for p in player_list_tmp:
            if 'player' in p:
                player_list += [p]
        home_count = 0
        tot_zip_dict_sim = dict()
        for player in player_list:
            tot_zip_dict_sim[home_count] = 'glm_generation_'+city+'/' + player_dir+'/'+player #to write into glm file as absolute path
            home_count += 1
    #Recreate players from Pecan Street data
    else:
        sys.exit('For integrated code, player regeneration based on Pecan Street data has not been tested yet.')
        data_dir=out_dir+'/Pecan_st_data_' + city
        inc_ind_zip='False'
        year_vec=np.array([year])
        tot_zip_dict_sim={}
        home_count=0
	    
        for year in year_vec:
            os.chdir(data_dir)
            filename_list=glob.glob('*_'+str(year)+'.csv') #'d_*_
            start=str(year)+start_time_str[4:]
            end=str(year)+end_time_str[4:]
	        
            for file_name in filename_list:
                print(file_name)
                if regen_players == True:
                    temp_zip_dict=player_gen_csv(start,end,file_name,data_dir,player_dir,inc_ind_zip,player_interval)
                else:
                    match = re.search('(.+?)_(.+?).csv', file_name) #'d_(.+?)_(.+?).csv'
                    house_num=match[1]
                    year=int(match[2])
                    out_file_name="ps_"+str(house_num)+'_'+str(year)+".player"
                    temp_zip_dict=player_dir+'/'+out_file_name #is that correct??list?
                if len(temp_zip_dict)!=0:
                    tot_zip_dict_sim[home_count]=temp_zip_dict
                    home_count=home_count+1
        print('Generated players')
    
    ######## HOUSES
    #Just populate house_dict based on original glm and use existing technical specifications
    if not rewrite_houses:
        base_house_file = 'Base_IEEE_123_homes_1min_nothermostatcontrol.glm'
        house_dict,player,outputs=read_home_inputs(base_house_file) #Copies technical properties from base_house_file

        #Uses existing Base_house_placement.csv for nodes
        df_house_placement = pandas.read_csv('Base_house_placement.csv')  #Copies nodes from Base_house_placement
        df_house_placement.to_csv('house_placement.csv')

        num_placed_homes = len(df_house_placement)
        home_bus_dict = dict.fromkeys(df_house_placement['node_num'])
        df_keys = pandas.DataFrame(columns=['nodes'],data=home_bus_dict.keys())
        new = df_keys['nodes'].str.split("_", n = 1, expand = True) 
        df_keys['number'] = new[0].apply(int)
        df_keys['phase'] = new[1]
        df_keys = df_keys.sort_values(by=['number','phase'])
        home_bus_list_aug = df_keys['nodes'].to_list()

        #Read from PV placement?
        #sys.exit('Substitute ADMD')
        mean_day_energy = np.genfromtxt('mean_day_energy.csv')
        mean_day_energy = mean_day_energy.reshape(mean_day_energy.shape[0],1)
        
        #PV calibration   
        data_dir='PV_calibration_july'
        PV_day_power,PV_area_ref,PV_day_mean=PV_calibration(data_dir)
        
        # % Get PV array sizes 
        PV_area,bat_size=PV_battery_sizing(mean_day_energy,PV_day_mean,PV_area_ref,outputs)        
    
    #Randomly draw house characteristics and generate house_dict anew
    #Only to create Basefile!
    else:
        #Total number of houses to generate
        tot_num_houses=2000
        #Probability of each home type
        prob_houses=[0.65196,0.23572,0.074451,0.02692,0.0085,0.00291]
        prob_houses=[m/sum(prob_houses) for m in prob_houses]
        #Climate zone for california
        clim_zone="3C"
        house_dict,player,outputs=gen_home_inputs(out_dir,tot_num_houses,prob_houses,clim_zone,
                                                             tot_zip_dict_sim)
        #mean_day_energy = np.array(pandas.read_csv('mean_day_energy.csv',header=-1))
        mean_day_energy = np.genfromtxt('mean_day_energy.csv')
        mean_day_energy = mean_day_energy.reshape(mean_day_energy.shape[0],1)
        
        #PV calibration   
        data_dir='PV_calibration_july'
        PV_day_power,PV_area_ref,PV_day_mean=PV_calibration(data_dir)
        
        # % Get PV array sizes 
        PV_area,bat_size=PV_battery_sizing(mean_day_energy,PV_day_mean,PV_area_ref,outputs)
        
        # % House placement in network     
        #bus safety factor
        safety_factor=0.66
        home_bus_list=[]

        #Based on ADMD
        ADMD_per_house=4.611774756466676 #1.9613980468000005
        num_placed_homes,home_bus_list_aug=house_placement2(out_dir,safety_factor,ADMD_per_house,
                                        outputs,home_bus_list,0,rewrite_houses)
    os.chdir(out_dir)
    print('Generated home data')
    
    ######## Generation of flexible appliances

    # % PV placement in network 
    num_PV=round(num_placed_homes*PV_penetration)
    if rewrite_houses:
        PV_placement(out_dir,num_PV,rewrite_houses)
    else:
        print(os.getcwd())
        df_PV_placement = pandas.read_csv('Base_PV_placement.csv')  #Copies from base file (100% PV)
        df_PV_placement.iloc[:num_PV].to_csv('PV_placement.csv')
    
    # %Battery placement in network 
    num_bat=round(num_placed_homes*bat_penetration)
    if rewrite_houses:
        Bat_placement(out_dir,num_bat,rewrite_houses)
    else:
        df_bat_placement = pandas.read_csv('Base_Bat_placement.csv')  #Copies from base file (100% Batteries)
        #df_bat_placement = pandas.read_csv('Base_PV_placement.csv')  #Copies from base file (100% Batteries)
        #df_bat_placement.rename(columns={'PV_node_num':'Bat_node_num','PV_house_index':'Bat_house_index'},inplace=True)
        df_bat_placement.iloc[:num_bat].to_csv('Bat_placement.csv')
    
    # %EV placement in network 
    num_EV=round(num_placed_homes*EV_penetration)
    if rewrite_houses:
        EV_placement(out_dir,num_EV,rewrite_houses)
    else:
        df_EV_placement = pandas.read_csv('Base_EV_placement.csv')  #Copies from base file (100% PV)
        #df_EV_placement = pandas.read_csv('Base_PV_placement.csv')  #Copies from base file (100% Batteries)
        #df_EV_placement.rename(columns={'PV_node_num':'EV_node_num','PV_house_index':'EV_house_index'},inplace=True)
        df_EV_placement.iloc[:num_EV].to_csv('EV_placement.csv')
    
    print('Populated network')
    
    ##### Generate GLM file for populated IEEE 123 feeder 
    PV = str(int(PV_penetration*100))
    Batt = str(int(bat_penetration*100))
    EVs = str(int(EV_penetration*100))
    net_sym_params={#'num_houses':'100',
                'out_file':"IEEE_123_homes_"+str(player_interval)+"min_nothermostatcontrol.glm",
                'inc_ZIP_player':'True',                   #True = add ZIP load object for each house
                'inc_battery':'True',                      #True = put battery in simulation
                'inc_PV':'True',                            #True = put PV in simulation
                'inc_EV':'True',                            #True = put PV in simulation
                'imp_EU':'False',                           #True = include implicit enduses 
                'start_time':" '"+start_time_str+"'",  #simulation start time
                'end_time':" '"+end_time_str+"'"    #simulation end time
                }
    
    glm_dict_add,obj_type,globals_list,include_list,sync_list=gen_network_glm(out_dir,
            net_sym_params,house_dict,player,outputs,tot_zip_dict_sim,home_bus_list_aug,PV_area,bat_size,0,rewrite_houses,run_file)
    print('Generated GLM file')
    return

#Writes base network into glm_dict (no loads included) 
def load_base_glm(base_file_dir,base_glm_file):
    f = open(base_glm_file, 'r')
    glm=f.readlines()
    
    glm_dict={}
    obj_type={}
    glm_list=list()
    globals_list=list()
    include_list=list()
    
    #edit out all comments
    for l in glm:
        line_temp=l.lstrip().rstrip().rstrip('\n').split('//')[0]   
        #Comment somewhere in line
        if len(line_temp)>1:
            #There is some content in line, extract content
            if l.split('//')[0]!='':
                glm_list.append(line_temp.rstrip())
        #No comment in line
        else:
            #Line is not a space
            if line_temp!='':
                glm_list.append(line_temp)
                
    obj_num=0
    obj_flag=0
    #put info into dict structure
    for l in glm_list:
        #Setting global variable
        if l[0:4]=='#set':
            globals_list.append(l)
        elif l[0:8]=='#include':
            include_list.append(l)
        elif 'object' in l:
            obj_flag=1
            line_temp=l.rstrip('{').rstrip().split(' ')
            obj_type[obj_num]={'object':line_temp[1]}
            prop_num=0
        elif 'module' in l:
            obj_flag=1
            line_temp=l.rstrip('{').rstrip().split(' ')
            # if line_temp[1][-1] == ';':
            #     line_temp[1] = line_temp[1][:-1]
            #     glm_dict[obj_num]={line_temp[0]:line_temp[1].rstrip(';')}
            #     obj_num=obj_num+1
            #     prop_num=0
            # else:
            obj_type[obj_num]={'module':line_temp[1]}
            prop_num=0
        elif 'clock' in l:
            obj_flag=1
            obj_type[obj_num]={'clock':'clock'}
            prop_num=0
        elif l=='}' or l=='};':
            obj_num=obj_num+1
            obj_flag=0
        else:
            if obj_flag==1:
                line_temp=l.split(' ',maxsplit=1)
                if prop_num==0:
                    glm_dict[obj_num]={line_temp[0]:line_temp[1].rstrip(';')}
                    prop_num=prop_num+1
                else:
                    glm_dict[obj_num][line_temp[0]]=line_temp[1].rstrip(';')
            else:
                print('error')
    return glm_dict,obj_type,globals_list,include_list

def write_base_glm(glm_dict,obj_type,globals_list,include_list,out_dir,file_name,sync_list,calibration=False):  
    glm_out = open(file_name,"w+")

    if calibration:
        #Write header
        glm_out.write('#set iteration_limit=100000;\n\n')
        glm_out.write('#set minimum_timestep=60;\n\n')
        glm_out.write('clock {\n')
        glm_out.write('\tstarttime "'+start_time_str+'";\n')
        glm_out.write('\tstoptime "'+end_time_str+'";\n')
        glm_out.write('}\n\n')
        glm_out.write('module residential {\n')
        glm_out.write('\timplicit_enduses NONE;\n')
        glm_out.write('}\n\n')
    
    for i in range(len(globals_list)):
        glm_out.write(globals_list[i]+'\n\n')
        
    for i in glm_dict.keys():    
    #for i in range(len(glm_dict)):
        if 'clock' in obj_type[i].keys():
            write_clock_dict(glm_out,glm_dict[i])
        
    for i in glm_dict.keys():    
    #for i in range(len(glm_dict)):
        if 'module' in obj_type[i].keys():
            write_mod_dict(glm_out,glm_dict[i],obj_type[i]['module'])
    
    for i in range(len(include_list)):
        glm_out.write(include_list[i]+'\n\n')

    for i in glm_dict.keys():
        if 'filter' in obj_type[i].keys():
            write_filter_dict(glm_out,glm_dict[i],obj_type[i]['filter'])
    
    for i in glm_dict.keys():
        if 'class' in obj_type[i].keys():
            write_class_dict(glm_out,glm_dict[i],obj_type[i]['class'])
    
    for i in glm_dict.keys():    
    #for i in range(len(glm_dict)):f
        if 'object' in obj_type[i].keys():
            if 'name' in glm_dict[i].keys():
                if slack_node in glm_dict[i]['name']:
                    write_slack(glm_out,glm_dict,i,obj_type[i]['object'])
                else:
                    write_obj_dict(glm_out,glm_dict,i,obj_type[i]['object'])
            else:
                write_obj_dict(glm_out,glm_dict,i,obj_type[i]['object'])

    for i in glm_dict.keys():    
    #for i in range(len(glm_dict)):
        if 'recorder' in obj_type[i].keys():
            write_recorder_dict(glm_out,glm_dict,i,obj_type[i]['object'])

    for i in range(len(sync_list)):
        glm_out.write(sync_list[i]+'\n\n')
    
    glm_out.close()


def player_gen_csv(start,end,file_name,data_dir,out_dir,inc_ind_zip,player_interval=1):
    '''Generate player files from Pecan Street data files'''
    
    if player_interval==1:
        inc_str='+60s,'
    elif player_interval==5:
        inc_str='+300s,'
    
    zip_load_count=0

    start_time=datetime.datetime.strptime(start,"%Y-%m-%d %H:%M:%S")
    end_time=datetime.datetime.strptime(end,"%Y-%m-%d %H:%M:%S")
    
    match = re.search('(.+?)_(.+?).csv', file_name) #'d_(.+?)_(.+?).csv'
    house_num=match[1]
    year=int(match[2])
    
    #start_time=datetime.datetime(year, 1, 5,10,3)
    #end_time = datetime.datetime(year, 1, 7, 23, 59)
    step = datetime.timedelta(seconds=60)
    
    time_year = []
    time_month = []
    time_day = []
    time_hour = []
    time_minute = []
    dt=start_time
    
    while dt < end_time:
        time_year.append(dt.year)
        time_month.append(dt.month)
        time_day.append(dt.day)
        time_hour.append(dt.hour)
        time_minute.append(dt.minute)
        dt =dt+ step
    
    df_short=pandas.DataFrame(np.column_stack((np.asarray(time_year),np.asarray(time_month),np.asarray(time_day),
                              np.asarray(time_hour),np.asarray(time_minute))),
                              columns=['year','month','day','hour','minute'])
    
    
    os.chdir(data_dir)    
    ps_data=pandas.read_csv(file_name,header=0)
    
    time_list=[[] for k in range(len(ps_data['dataid']))]
    year_list=[[] for k in range(len(ps_data['dataid']))]
    month_list=[[] for k in range(len(ps_data['dataid']))]
    day_list=[[] for k in range(len(ps_data['dataid']))]
    min_list=[[] for k in range(len(ps_data['dataid']))]
    hour_list=[[] for k in range(len(ps_data['dataid']))]
    
    timestamp_vec_temp=list(ps_data.localminute)
    for t in range(len(ps_data.dataid)):
        timestamp_temp=str(timestamp_vec_temp[t])
        time_list[t]=datetime.datetime.strptime(timestamp_temp,"%Y-%m-%d %H:%M:%S")
        hour_list[t]=time_list[t].hour
        min_list[t]=time_list[t].minute
        day_list[t]=time_list[t].day
        month_list[t]=time_list[t].month
        year_list[t]=time_list[t].year
    
    
    ps_data['year']=np.array(year_list)
    ps_data['month']=np.array(month_list)
    ps_data['day']=np.array(day_list)
    ps_data['minute']=np.array(min_list)
    ps_data['hour']=np.array(hour_list)
    
    df=pandas.merge(df_short,ps_data,on=['year','month','day','hour','minute'],how='left')
    
    df=df.drop(labels=['Unnamed: 0','dataid','localminute','use','air1','air2','air3','airwindowunit1','furnace1',
                       'furnace2','gen','grid','heater1','year','month','day','hour','minute'],axis=1)
    df=df.fillna(0)
    tot_load=df.sum(axis=1)

    out_file_name="ps_"+str(house_num)+'_'+str(year)+".player"
    temp_zip_dict='players_Austin/'+out_file_name
    zip_load_count=zip_load_count+1
    os.chdir(out_dir)    
    f = open(out_file_name,"w+")
    
    count_step=1
    for tt in range(df.shape[0]):
        if count_step==1:
            f.write(str(start_time)+','+str(round(tot_load[tt],2))+"\n")
        else:
            if player_interval==1:
                f.write(inc_str+str(round(tot_load[tt],2))+"\n")
            elif player_interval==5:
                if (count_step-1)%5==0:
                    f.write(inc_str+str(round(tot_load[tt],2))+"\n")                    
        count_step=count_step+1
    f.close()
    return temp_zip_dict

def gen_home_inputs(input_dir,tot_num_houses,prob_houses,clim_zone,tot_zip_dict):
    '''Generate parameters of homes'''
    #print(input_dir)

    #os.chdir(input_dir)
    ACH = pandas.read_csv("ACH.csv",header=0)
    np.random.seed(1)
    
    ####Define mappings
    #Home type mapping
    type_vec=["elec_gas_1","elec_gas_2","elec_res_1","elec_res_2","HP_1","HP_2"]
    #Cooling type mapping
    cool_equip=dict([("elec_gas_1","ELECTRIC"),("elec_gas_2","ELECTRIC"),("elec_res_1","ELECTRIC"),("elec_res_2","ELECTRIC"),("HP_1","HEAT_PUMP"),("HP_2","HEAT_PUMP")])
    #Heating type mapping
    heat_equip=dict([("elec_gas_1","GAS"),("elec_gas_2","GAS"),("elec_res_1","RESISTANCE"),("elec_res_2","RESISTANCE"),("HP_1","HEAT_PUMP"),("HP_2","HEAT_PUMP")])
    #Factor for converting units of air flow rate, specific to each climate zone
    LBL_factor_1=dict([("1A-2A",20),("2B",21.5),("3A",24.5),("3B-4B",21.3),
                       ("3C",21.5),("4A",18.5),("4C",21.5),("5A",18.5),
                       ("5B-5C",18.5),("6A-6B",17),("7A-7B-7AK-8AK",18.5)])
    LBL_factor_2=dict([("1A-2A",16),("2B",17.2),("3A",19.6),("3B-4B",17.4),
                       ("3C",17.2),("4A",14.8),("4C",17.5),("5A",14.8),
                       ("5B-5C",14.8),("6A-6B",13.6),("7A-7B-7AK-8AK",14.8)])
    
    #Mean and std of various input parameters, derived from EIA RECS data
    floor_area_mean=dict([("elec_gas_1",2041),("elec_gas_2",3104),("elec_res_1",2041),("elec_res_2",3104),("HP_1",2041),("HP_2",3104)])
    floor_area_sd=dict([("elec_gas_1",801),("elec_gas_2",1069),("elec_res_1",801),("elec_res_2",1069),("HP_1",801),("HP_2",1069)])
    cool_set_mean=dict([("elec_gas_1",70.9),("elec_gas_2",71),("elec_res_1",70.9),("elec_res_2",71),("HP_1",70.9),("HP_2",71)])
    cool_set_sd=dict([("elec_gas_1",1),("elec_gas_2",1),("elec_res_1",1),("elec_res_2",1),("HP_1",1),("HP_2",1)])
    heat_set_mean=dict([("elec_gas_1",66.3),("elec_gas_2",66.6),("elec_res_1",66.3),("elec_res_2",66.6),("HP_1",66.3),("HP_2",66.6)])
    heat_set_sd=dict([("elec_gas_1",4.59),("elec_gas_2",4.21),("elec_res_1",4.59),("elec_res_2",4.21),("HP_1",4.59),("HP_2",4.21)])
    
    #number of homes we have Pecan Street data for zip loads
    num_ps_homes=len(tot_zip_dict)
    
    #Set average roof pitch angle for roof area calculation (degrees)
    roof_pitch=25
    #Fraction roof space available for PV
    PV_roof_frac=1/3
    
    #Initialize variables
    PV_max_area,cooling_setpoint,heating_setpoint,floor_area,name,airchange_per_hour,window_wall_ratio,player,number_of_stories,cooling_system_type,heating_system_type,T_min_l,T_max_l,k_l=([] for i in range(14))
    
    house_dict={}
    
    #Loop through all homes    
    for i in range(tot_num_houses):
        #House name
        type_house=np.random.choice(type_vec,p=prob_houses)
        #name_temp="H_"+str('{:04}'.format(i+1))+"_"+type_house
        name_temp="GLD_"+str('{:04}'.format(i+1))
        #number of stories
        num_stor=int(type_house[-1])
        #floor area truncated normal distribution
        a, b = (1000 - floor_area_mean[type_house]) / floor_area_sd[type_house], (4000 - floor_area_mean[type_house]) / floor_area_sd[type_house]
        mu=floor_area_mean[type_house]
        sigma=floor_area_sd[type_house]
        floor_area_temp=int(truncnorm.rvs(a,b,loc=mu,scale=sigma))
        
        #Max area for PV array based on floor area
        if num_stor==1:
            PV_max_area_temp=(floor_area_temp*PV_roof_frac)/(math.cos(math.radians(roof_pitch)))
        elif num_stor==2:
            PV_max_area_temp=(floor_area_temp*PV_roof_frac)/(2*math.cos(math.radians(roof_pitch)))

        
        #cooling setpoint (need to refine this later)
        seed=np.random.randint(1,1*10^9,1)
        heating_setpoint_temp=int(np.random.normal(heat_set_mean[type_house],heat_set_sd[type_house],1))
        cooling_setpoint_temp=int(np.random.normal(cool_set_mean[type_house],cool_set_sd[type_house],1))
        #cooling_setpoint_temp=heating_setpoint_temp+5

        if heating_setpoint_temp + 5.0 > cooling_setpoint_temp:
            heating_setpoint_temp = cooling_setpoint_temp - 5.0
        
        #set HVAC settings
        T_min = heating_setpoint_temp - 3
        T_max = cooling_setpoint_temp + 3
        k = round(max(min(float(np.random.normal(3.0,1,1)),4.0),2.0),1)
        
        #Air change per hour
        #Bin homesize to get info from probability distribution
        if floor_area_temp<1250:
            sqft_rnd=1000
        elif floor_area_temp<1750:
            sqft_rnd=1500
        elif floor_area_temp<2250:
            sqft_rnd=2000
        elif floor_area_temp<2750:
            sqft_rnd=2500
        elif floor_area_temp<3250:
            sqft_rnd=3000
        elif floor_area_temp<3750:
            sqft_rnd=3500
        else:
            sqft_rnd=4000

        ACH_subset=ACH[(ACH.IECC_Climate=="3C")&(ACH.sqft==sqft_rnd)]
        #random_gen=max(min(np.random.norm(0.5,0.125),0.0),1.0)
        random_gen = np.random.uniform()
        ACH_subset2=ACH_subset[(ACH.CDF<random_gen)]
        
        #Pick out value in ACH CDF using random number
        if len(ACH_subset2)!=0:
            if num_stor==1:
                airchange_per_hour_temp=float(max(ACH_subset2.ACH50)/LBL_factor_1[clim_zone])
            else:
                airchange_per_hour_temp=float(max(ACH_subset2.ACH50)/LBL_factor_2[clim_zone])
        else:
            if num_stor==1:
                airchange_per_hour_temp=float(min(ACH_subset.ACH50)/LBL_factor_1[clim_zone])
            else:
                airchange_per_hour_temp=float(min(ACH_subset.ACH50)/LBL_factor_2[clim_zone])
                
        wall_window_ratio_temp=round(float(np.random.normal(0.15,.01,1)),2)
                
        house_dict[i]={'name':name_temp,
                'number_of_stories':str(num_stor),
                'cooling_setpoint':str(cooling_setpoint_temp),
                'heating_setpoint':str(heating_setpoint_temp),
                'T_min':str(T_min),
                'T_max':str(T_max),
                'k':str(k),
                'cooling_system_type':cool_equip[type_house],
                'heating_system_type':heat_equip[type_house],
                'floor_area':str(floor_area_temp),
                'window_wall_ratio':str(wall_window_ratio_temp),
                'airchange_per_hour':str(round(airchange_per_hour_temp,2))}
        
        #Append for output dataframe  
        name.append(name_temp)
        number_of_stories.append(num_stor)
        floor_area.append(floor_area_temp)
        heating_setpoint.append(heating_setpoint_temp)
        cooling_setpoint.append(heating_setpoint_temp+5)
        T_min_l.append(house_dict[i]['T_min'])
        T_max_l.append(house_dict[i]['T_max'])
        k_l.append(house_dict[i]['k'])
        cooling_system_type.append(cool_equip[type_house])
        heating_system_type.append(heat_equip[type_house])
        airchange_per_hour.append(round(airchange_per_hour_temp,2))
        window_wall_ratio.append(wall_window_ratio_temp)
        player.append(int(np.random.choice(range(num_ps_homes),1))) 
        PV_max_area.append(int(PV_max_area_temp))

    outputs=pandas.DataFrame({'name':name,'number_of_stories':number_of_stories,'floor_area':floor_area,
                      'heating_setpoint':heating_setpoint,'cooling_setpoint':cooling_setpoint,
                      'T_min':T_min,'T_max':T_max,'k':k,
                      'cooling_system_type':cooling_system_type,'heating_system_type':heating_system_type,
                      'airchange_per_hour':airchange_per_hour,'window_wall_ratio':window_wall_ratio,
                      'player':player,'PV_max_area':PV_max_area})
    
    return house_dict,player,outputs

def read_home_inputs(base_house_file):
    '''Read parameters of homes into house_dict'''
    house_dict={}
    #Initialize variables
    PV_max_area,cooling_setpoint,heating_setpoint,floor_area,name,airchange_per_hour,window_wall_ratio,player,number_of_stories,cooling_system_type,heating_system_type,T_min,T_max,k=([] for i in range(14))
    #1999: {'name': 'GLD_2000', 'number_of_stories': '2', 'cooling_setpoint': '70', 'heating_setpoint': '65', 'T_min': '62', 'T_max': '73', 
    #'k': '2.7', 'cooling_system_type': 'ELECTRIC', 'heating_system_type': 'GAS', 'floor_area': '3006', 'window_wall_ratio': '0.15', 'airchange_per_hour': '0.55'}

    f = open(base_house_file, 'r')
    glm=f.readlines()
    
    glm_dict={}
    obj_type={}
    glm_list=list()
    globals_list=list()
    include_list=list()
    
    #edit out all comments
    for l in glm:
        line_temp=l.lstrip().rstrip().rstrip('\n').split('//')[0]   
        #Comment somewhere in line
        if len(line_temp)>1:
            #There is some content in line, extract content
            if l.split('//')[0]!='':
                glm_list.append(line_temp.rstrip())
        #No comment in line
        else:
            #Line is not a space
            if line_temp!='':
                glm_list.append(line_temp)
          
    obj_num=0
    obj_flag=0
    zip_flag=0
    #put info into dict structure
    for l in glm_list:
        #Starts object statement for house
        if 'object house' in l:
            obj_flag=1
            house_dict[obj_num] = {}
        #Terminates object statement for house
        elif l=='}' or l=='};':
            if zip_flag == 1:
                obj_num=obj_num+1
            obj_flag=0
            zip_flag=0
        elif 'object ZIPload' in l:
            zip_flag=1
        elif zip_flag == 1 and 'base_power' in l:
            line_temp=l.split(' ',maxsplit=1)
            #house_dict[obj_num]['player']=int(line_temp[1].split('.',maxsplit=1)[0].split('_')[1])
            player.append(int(line_temp[1].split('.',maxsplit=1)[0].split('_')[1])) 
        elif 'hvac_energy_5min' in l:
            pass
        else:
            if obj_flag==1:
                line_temp=l.split(' ',maxsplit=1)
                house_dict[obj_num][line_temp[0]]=line_temp[1].rstrip(';')
    
    roof_pitch = 25
    PV_roof_frac = 1/3.
    #Write player list
    for i in house_dict.keys():
        #Append for output dataframe  
        name.append(house_dict[i]['name'])
        number_of_stories.append(house_dict[i]['number_of_stories'])
        floor_area.append(house_dict[i]['floor_area'])
        heating_setpoint.append(house_dict[i]['heating_setpoint'])
        cooling_setpoint.append(house_dict[i]['cooling_setpoint'])
        T_min.append(house_dict[i]['T_min'])
        T_max.append(house_dict[i]['T_max'])
        k.append(house_dict[i]['k'])
        cooling_system_type.append(house_dict[i]['cooling_system_type'])
        heating_system_type.append(house_dict[i]['heating_system_type'])
        airchange_per_hour.append(house_dict[i]['airchange_per_hour'])
        window_wall_ratio.append(house_dict[i]['window_wall_ratio'])
        #player.append(house_dict[i]['player']) 
        
        #Max area for PV array based on floor area
        if int(house_dict[i]['number_of_stories'])==1:
            PV_max_area_temp=(float(house_dict[i]['floor_area'])*PV_roof_frac)/(math.cos(math.radians(roof_pitch)))
        elif int(house_dict[i]['number_of_stories'])==2:
            PV_max_area_temp=(float(house_dict[i]['floor_area'])*PV_roof_frac)/(2*math.cos(math.radians(roof_pitch)))
        PV_max_area.append(PV_max_area_temp)

    outputs=pandas.DataFrame({'name':name,'number_of_stories':number_of_stories,'floor_area':floor_area,
                      'heating_setpoint':heating_setpoint,'cooling_setpoint':cooling_setpoint,
                      'T_min':T_min,'T_max':T_max,'k':k,
                      'cooling_system_type':cooling_system_type,'heating_system_type':heating_system_type,
                      'airchange_per_hour':airchange_per_hour,'window_wall_ratio':window_wall_ratio,
                      'player':player,'PV_max_area':PV_max_area})
        
    return house_dict,player,outputs
   
    
def write_obj_dict(file,gld_dict,dict_key,obj_type):
    '''Write dictionary corresponding to GLD objects to .glm file'''
    
    if dict_key==-1:
        file.write('object '+obj_type+' {\n')
        for i,j in gld_dict.items():
            file.write('\t'+str(i)+' '+str(j)+';\n')
        file.write('}\n\n')
    else:
        file.write('object '+obj_type+' {\n')
        for i,j in gld_dict[dict_key].items():
            file.write('\t'+str(i)+' '+str(j)+';\n')
        file.write('}\n\n')

def write_slack(file,gld_dict,dict_key,obj_type):
    '''Write dictionary corresponding to GLD objects to .glm file'''
    
    file.write('object meter {\n')
    file.write('\t'+'name'+' '+gld_dict[dict_key]['name']+';\n')
    file.write('\t'+'phases'+' '+gld_dict[dict_key]['phases']+';\n')
    file.write('\t'+'nominal_voltage'+' '+gld_dict[dict_key]['nominal_voltage']+';\n')
    #Recorder
    file.write('\t'+'object'+' '+'recorder'+' {\n')
    file.write('\t\t'+'property measured_real_power;\n')
    file.write('\t\t'+'interval 60;\n')
    file.write('\t\t'+'file '+results_folder+'/load_node_149.csv;\n')
    file.write('\t'+'};\n')
    file.write('}\n')
        
def write_mod_dict(file,gld_dict,mod_name):
    '''Write dictionary corresponding to GLD module to .glm file'''
    if len(gld_dict)==0:
        file.write('module '+mod_name+';\n\n')
    else:
        file.write('module '+mod_name+' {\n')
        for i,j in gld_dict.items():
            file.write('\t'+str(i)+' '+str(j)+';\n')
        file.write('}\n\n')

def write_class_dict(file,gld_dict,class_name):
    '''Write dictionary corresponding to GLD class to .glm file'''
    if len(gld_dict)==0:
        file.write('class '+class_name+';\n\n')
    else:
        file.write('class '+class_name+' {\n')
        for i,j in gld_dict.items():
            if 'double' in i:
                file.write('\t'+'double'+' '+str(j)+';\n')
            else:
                file.write('\t'+str(i)+' '+str(j)+';\n')
        file.write('}\n\n')
   
#def write_filter_dict(file,gld_dict,class_name):
#    '''Write dictionary corresponding to GLD filter to .glm file'''
#    if len(gld_dict)==0:
#        file.write('filter '+class_name+';\n\n')
#    else:
#        file.write('filter '+class_name+' {\n')
#        for i,j in gld_dict.items():
#            file.write('\t'+str(i)+' '+str(j)+';\n')
#        file.write('}\n\n')
 
def write_filter_dict(file,gld_dict,class_name):
    '''Write dictionary corresponding to GLD filter to .glm file'''
    if len(gld_dict)==0:
        file.write('filter '+class_name+';\n\n')
    else:
        file.write('filter '+class_name)
        for i,j in gld_dict.items():
            file.write(str(i)+' = '+str(j)+';\n')
        file.write('\n')
           
def write_clock_dict(file,gld_dict):
    '''Write dictionary corresponding to GLD clock to .glm file'''
    file.write('clock {\n')
    for i,j in gld_dict.items():
        file.write('\t'+str(i)+' '+str(j)+';\n')
    file.write('}\n\n')
    #Include gridlabd module
    file.write('module gridlabd_functions;\n\n')

def write_recorder_dict(file,gld_dict,class_name):
    '''Write dictionary corresponding to GLD class to .glm file'''
    if len(gld_dict)==0:
        file.write('class '+class_name+';\n\n')
    else:
        file.write('class '+class_name+' {\n')
        for i,j in gld_dict.items():
            if 'double' in i:
                file.write('\t'+'double'+' '+str(j)+';\n')
            else:
                file.write('\t'+str(i)+' '+str(j)+';\n')
        file.write('}\n\n')     
        
def PV_calibration(data_dir):
    os.chdir(data_dir)
    power_files_list=glob.glob("PV_power*.csv")
    
    power_data_temp = pandas.read_csv("PV_power_140.csv",header=8,names=['timestamp','measured_real_power'])
    day_num=math.floor(len(power_data_temp.measured_real_power)/1440)
    PV_cal_num=len(power_files_list)

    PV_day_power=np.zeros((day_num,PV_cal_num))
    PV_day_mean=np.zeros((PV_cal_num,1))
    PV_area_ref=np.zeros((PV_cal_num,1))

    for j in range(PV_cal_num):
        PV_area_ref[j,0]=int(140+20*j)
        power_file="PV_power_"+str(int(PV_area_ref[j,0]))+".csv"
        power_data_temp = pandas.read_csv(power_file,header=8,names=['timestamp','measured_real_power'])
        power_data_temp.measured_real_power[len(power_data_temp.measured_real_power)-1]=0
        for i in range(0,day_num):
            PV_day_power[i,j]=-sum(power_data_temp.measured_real_power[((i))*1440:((i)*1440+1440)])/(60)
        PV_day_mean[j,0]=sum(PV_day_power[:,j])/day_num
            
    return PV_day_power,PV_area_ref,PV_day_mean


def PV_battery_sizing(mean_day_energy,PV_day_mean,PV_area_ref,outputs):
    '''PV and battery sizing per house'''
    PV_area_est=np.interp(mean_day_energy,np.ndarray.flatten(PV_day_mean),np.ndarray.flatten(PV_area_ref))
    PV_area=np.zeros((PV_area_est.shape[0],PV_area_est.shape[1]))
    bat_size=np.zeros((PV_area_est.shape[0],PV_area_est.shape[1]))
    for i in range(min(PV_area.shape[0],len(outputs))):
        PV_area[i,0]=min(outputs.PV_max_area[i],PV_area_est[i,0])
        bat_size_tmp = round(np.interp(PV_area[i,0],np.ndarray.flatten(PV_area_ref),np.ndarray.flatten(PV_day_mean)),-3)/0.8
        bat_size[i,0] = 2000*math.ceil(bat_size_tmp/2000)
    df = pandas.DataFrame(columns=['PV_area'],data=PV_area)
    df['bat_size'] = bat_size
    df['mean_energy'] = mean_day_energy
    df.to_csv('overview_houses.csv')
    return PV_area,bat_size


def house_placement2(input_dir,safety_factor,ADMD_per_house,outputs,home_bus_list,num_duplicates,rewrite_houses=False):
    '''Maps houses to buses, without land-value weight'''
    np.random.seed(1)
    os.chdir(input_dir)
    #Load transformer phase data
    bus_data=pandas.read_csv("bus_data.csv",header=0)
    if home_bus_list!=[]:
        bus_data=bus_data.loc[bus_data['meter'].isin(home_bus_list)].reset_index()
    
    if num_duplicates>0:
        nodes_temp=bus_data.transformer
        nodes=copy.deepcopy(nodes_temp)
        P_spot_temp=bus_data.P_spot
        P_spot=copy.deepcopy(P_spot_temp)
        key_index=0
        for j in range(len(nodes_temp)):
            nodes[key_index]='B1_N'+nodes[key_index]
            key_index=key_index+1
        key_index=len(nodes_temp)
        for i in range(num_duplicates):
            for j in range(len(nodes_temp)):
                nodes[key_index]='B'+str(i+2)+'_N'+nodes_temp[j]
                #nodes[key_index]=nodes_temp[j]+'_x'+str(i+1)
                P_spot[key_index]=P_spot_temp[j]
                key_index=key_index+1
    else:  
        nodes=bus_data.transformer
        P_spot=bus_data.P_spot

    num_nodes=len(nodes)
    num_houses=len(outputs)

    home_rating=np.ones((num_houses,1))*ADMD_per_house
    node_rating=P_spot*safety_factor
    
    #keep track of placed load
    node_total=np.zeros(num_nodes)
    place_iterations=np.zeros(num_houses)
    
    #place each home in network
    h=0

    place_iterations=np.zeros(num_houses)
    node_num=list()
    
    while ((max(node_rating-node_total)>ADMD_per_house) and (h<num_houses)):
        node_t=0
        add=30
        node_r=20
        
        #find node that hasn't already reached capacity
        while (node_t+add>node_r):
            node_index=np.random.choice(range(0,num_nodes))
            add=home_rating[h]
            node_t=node_total[node_index]
            node_r=node_rating[node_index]
            #number of times tried to place home at a node
            place_iterations[h]=place_iterations[h]+1;
            
            #if you can't find an open node for a home
            if place_iterations[h]>100:
                while node_t+add>node_r:
                    node_index=np.random.choice(range(0,num_nodes)) #use equal probability
                    add=home_rating[h]
                    node_t=node_total[node_index]
                    node_r=node_rating[node_index]
                    #number of times tried to place home at a node
                    place_iterations[h]=place_iterations[h]+1;
        h=h+1
    
        node_num.append(nodes[node_index])
        node_total[node_index]=node_total[node_index]+home_rating[h]
    
        
    num_placed_homes=len(node_num)
    
    #Plot results
#    plt.figure(1,figsize=(10,10))
#    plt.bar(range(len(node_total)),node_total)
#    plt.xticks(range(len(node_total)),nodes)
#    plt.gcf().autofmt_xdate()
#    plt.xlabel("Node")
#    plt.ylabel("ADMD per node (kW)")
    
    #save data
    node_num_df=pandas.DataFrame(node_num,columns=["node_num"])
    node_num_df.to_csv('house_placement.csv',index=False)
    if rewrite_houses:
        node_num_df.to_csv('Base_house_placement.csv',index=False)
    return num_placed_homes,nodes


def PV_placement(input_dir,num_PV,rewrite_houses=False):
    '''Maps PV arrays to buses '''
    os.chdir(input_dir)
    House_placement_df = pandas.read_csv('house_placement.csv')
    
    #Assign equal probability to all homes in network
    PV_house_index=np.random.choice(range(len(House_placement_df)),replace=False,size=((num_PV,1)))
    
    PV_node_num=list()
    for i in range(num_PV):
        PV_node_num.append(str(House_placement_df.node_num[int(PV_house_index[i])]))
    
    PV_node_num_df=pandas.DataFrame({'PV_node_num':PV_node_num})
    PV_house_index_df=pandas.DataFrame(PV_house_index + 1,columns=["PV_house_index"])
    PV_placement_df=pandas.concat([PV_node_num_df,PV_house_index_df],axis=1)
    PV_placement_df.to_csv('PV_placement.csv',index=False)
    if rewrite_houses:
        PV_placement_df.to_csv('Base_PV_placement.csv',index=False)
    
def Bat_placement(input_dir,num_bat,rewrite_houses=False):
    '''Maps batterys to buses '''
   
    os.chdir(input_dir)
    House_placement_df = pandas.read_csv('house_placement.csv')
    PV_placement_df = pandas.read_csv('PV_placement.csv')

    #only place batteries at nodes with PV
    # Bat_house_index=np.random.choice(PV_placement_df.PV_house_index,replace=False,size=((num_bat,1)))
    # Bat_node_num=list()
    # for i in range(num_bat):
    #     Bat_node_num.append(str(House_placement_df.node_num[int(Bat_house_index[i]-1)]))
    
    # Bat_node_num_df=pandas.DataFrame({'Bat_node_num':Bat_node_num})
    # Bat_house_index_df=pandas.DataFrame(Bat_house_index,columns=["Bat_house_index"])
    # Bat_placement_df=pandas.concat([Bat_node_num_df,Bat_house_index_df],axis=1)
    # Bat_placement_df.sort_values('Bat_house_index',inplace=True)

    #place batteries exactly where PV is
    Bat_placement_df = PV_placement_df.copy()
    Bat_placement_df.rename(columns={'PV_node_num':'Bat_node_num','PV_house_index':'Bat_house_index'},inplace=True)

    #only place batteries at nodes with PV
    Bat_node_num=list()
    for i in range(num_bat):
        Bat_node_num.append(str(House_placement_df.node_num[i]))

    Bat_placement_df.to_csv('Bat_placement.csv',index=False)
    if rewrite_houses:
        Bat_placement_df.to_csv('Base_Bat_placement.csv',index=False)

def EV_placement(input_dir,num_EV,rewrite_houses=False):
    '''Maps EVs to buses '''
   
    os.chdir(input_dir)
    House_placement_df = pandas.read_csv('house_placement.csv')
    PV_placement_df = pandas.read_csv('PV_placement.csv')
    
    #only place batteries at nodes with PV
    # EV_house_index=np.random.choice(PV_placement_df.PV_house_index,replace=False,size=((num_EV,1)))
    #place anywhere?
    #EV_house_index=np.random.choice(range(len(House_placement_df)),replace=False,size=((num_EV,1)))
    # EV_node_num=list()
    # for i in range(num_EV):
    #     EV_node_num.append(str(House_placement_df.node_num[int(EV_house_index[i]-1)]))    
    # EV_node_num_df=pandas.DataFrame({'EV_node_num':EV_node_num})
    # EV_house_index_df=pandas.DataFrame(EV_house_index,columns=["EV_house_index"])
    # EV_placement_df=pandas.concat([EV_node_num_df,EV_house_index_df],axis=1)
    # EV_placement_df.sort_values('EV_house_index',inplace=True)

    EV_placement_df = PV_placement_df.copy()
    EV_placement_df.rename(columns={'PV_node_num':'EV_node_num','PV_house_index':'EV_house_index'},inplace=True)

    EV_node_num=list()
    for i in range(num_EV):
        EV_node_num.append(str(House_placement_df.node_num[i]))

    EV_placement_df.to_csv('EV_placement.csv',index=False)
    if rewrite_houses:
        EV_placement_df.to_csv('Base_EV_placement.csv',index=False)


def PV_inverter_rating(pv_size):
    if pv_size <= 115:
      inv_rating = 2000
    elif pv_size <= 170:
      inv_rating = 3000
    elif pv_size <= 225:
      inv_rating = 4000
    elif pv_size <= 280:
      inv_rating = 5000
    elif pv_size <= 340:
      inv_rating = 6000
    elif pv_size <= 450:
      inv_rating = 8000
    elif pv_size <= 560:
      inv_rating = 10000
    elif pv_size <= 675:
      inv_rating = 12000
    elif pv_size <= 840:
      inv_rating = 15000
    elif pv_size <= 1000:
      inv_rating = 18000
    elif pv_size <= 1120:
      inv_rating = 20000
    elif pv_size <= 1400:
      inv_rating = 25000
    elif pv_size <= 1700:
      inv_rating = 30000
    else:
        sys.exit('Error: not an appropriate PV size')
    return inv_rating

def gen_network_glm(input_dir,net_sym_params,house_dict,player,inputs,tot_zip_dict,home_bus_list,PV_area,bat_size,num_duplicates,rewrite_houses,grid):
    '''Generate .glm file as addition to base .glm file of network
    Places homes, PV, batteries at nodes specified in csv files'''   
    
    os.chdir(input_dir)
    #glm = open(net_sym_params['out_file'],"w+")
        
    #Define phases of each transformer
    transformer_data = pandas.read_csv("bus_data.csv",header=0)
    nodes=transformer_data[['phase','transformer']]
    #phase_dict=nodes.set_index('transformer').T.to_dict('list')
    meter_ref=copy.deepcopy(transformer_data.meter)
    transformer_ref=copy.deepcopy(transformer_data.transformer)
    phase_ref=copy.deepcopy(transformer_data.phase)
    phase_dict={}
    for i in range(len(phase_ref)):
        phase_dict[transformer_ref[i]]=phase_ref[i]

    #Load home, PV, and battery placement data
    house_placement_df=pandas.read_csv("house_placement.csv",header=0)
    PV_placement_df=pandas.read_csv("PV_placement.csv",header=0)
    Bat_placement_df=pandas.read_csv("Bat_placement.csv",header=0)
    EV_placement_df=pandas.read_csv("EV_placement.csv",header=0)
    
    #Initialize dictionaries for object data
    glm_dict={}
    obj_type={}
    globals_list=[]
    include_list=[]
    key_index=0
    sync_list=[]
     
    
    #Modules
    if net_sym_params['imp_EU']=='True':
        glm_dict[key_index]={'implicit_enduses':'LIGHTS|CLOTHESWASHER|WATERHEATER|REFRIGERATOR|DRYER|FREEZER|DISHWASHER'}
        obj_type[key_index]={'module':'residential'}
        key_index=key_index+1        
    else:
        glm_dict[key_index]={'implicit_enduses':'NONE'}
        obj_type[key_index]={'module':'residential'}
        key_index=key_index+1       
        
    glm_dict[key_index]={}
    obj_type[key_index]={'module':'climate'}
    key_index=key_index+1
    
    glm_dict[key_index]={}
    obj_type[key_index]={'module':'tape'}
    key_index=key_index+1
    
    glm_dict[key_index]={}
    obj_type[key_index]={'module':'generators'}
    key_index=key_index+1
    
    #Filter
    #glm_dict[key_index]={'(z,5min)':'(1.0 + 1.0 z + 1.0 z^2 + 1.0 z^3 + 1.0 z^4)/(z^5)'}
    #obj_type[key_index]={'filter':'sumHVAC'}
    #key_index=key_index+1
    
    #Climate object
    glm_dict[key_index]={'name':'tmy_file',
               'tmyfile':tmy_file,
               'interpolate':'LINEAR'}
    obj_type[key_index]={'object':'climate'}
    key_index=key_index+1

    #Triplex line conductor
    if grid:
        glm_dict[key_index]={'name':'''"c1/0 AA triplex"''',
                 'resistance':'0.97',
                 'geometric_mean_radius':'0.0111'}
        
        obj_type[key_index]={'object':'triplex_line_conductor'}
        key_index=key_index+1
        
        #Triplex line configuration
        glm_dict[key_index]={'name':'triplex_line_config',
                            'conductor_1':'''"c1/0 AA triplex"''',
                            'conductor_2':'''"c1/0 AA triplex"''',
                            'conductor_N':'''"c1/0 AA triplex"''',
                            'insulation_thickness':'0.08',
                            'diameter':'0.368'}
        obj_type[key_index]={'object':'triplex_line_configuration'}
        key_index=key_index+1

            
        #Transformer configuration 
        glm_dict[key_index]={'name':'house_transformer',
                         'connect_type':'SINGLE_PHASE_CENTER_TAPPED',
                         'install_type':'PADMOUNT',
                         'primary_voltage':'2401.7771 V',
                         'secondary_voltage':'124 V',
                         'power_rating':'250',
                         'impedance':'0.015+0.0675j'}
        obj_type[key_index]={'object':'transformer_configuration'}
        key_index=key_index+1

    #Player class
    glm_dict[key_index]={'double':'value'}
    obj_type[key_index]={'class':'player'}
    key_index=key_index+1

    #Player objects
    for p in range(len(tot_zip_dict)):
        glm_dict[key_index]={'name':'player_'+str(p),
                'file':tot_zip_dict[p]}
        obj_type[key_index]={'object':'player'}
        key_index=key_index+1
    
    #House transformer and node objects
    if grid:
        for j in range(len(transformer_ref)):
            if (transformer_ref[j] in np.array(home_bus_list)):
                #Triplex node
                glm_dict[key_index]={'name':'node_'+str(transformer_ref[j]),
                              'nominal_voltage':'124.00',
                              'phases':str(phase_ref[j])+"S"}
                obj_type[key_index]={'object':'triplex_node'}
                key_index=key_index+1
                
                #Transformer
                glm_dict[key_index]={'name':'house_trans_'+str(transformer_ref[j]),
                          'phases':str(phase_ref[j])+'S',
                          'from':'meter_'+str(meter_ref[j]),
                          'to':'node_'+str(transformer_ref[j]),
                          'configuration':'house_transformer'}
                obj_type[key_index]={'object':'transformer'}
                key_index=key_index+1
    
    #define houses
    """Adjust for changes in class"""
    glm_dict[key_index]={'double':'k','double1':'T_max','double2':'T_min'} #,'double3':'hvac_energy_5min'} #,'double4':'air_temperature','double5':'mass_temperature'}
    obj_type[key_index]={'class':'house'}
    key_index=key_index+1
    
    #Get equilibrium temperatures
   #grid = False
    if grid:
        df_T_air = pandas.read_csv('calibration_T_all.csv',skiprows=range(8))
        df_T_air['# timestamp'] = df_T_air['# timestamp'].map(lambda x: str(x)[:-4])
        df_T_air['# timestamp'] = pandas.to_datetime(df_T_air['# timestamp'])
        df_T_air.set_index('# timestamp',inplace=True)
    
        df_T_mass = pandas.read_csv('calibration_Tm_all.csv',skiprows=range(8))
        df_T_mass['# timestamp'] = df_T_mass['# timestamp'].map(lambda x: str(x)[:-4])
        df_T_mass['# timestamp'] = pandas.to_datetime(df_T_mass['# timestamp'])
        df_T_mass.set_index('# timestamp',inplace=True)        
    
    #Loop through houses
    df_house_install = pandas.DataFrame(columns=['house','node','stores','floor','pv_area','pv_inv_rated_power','battery_capacity','batt_inv_rated_power'])

    for i in range(len(house_placement_df)):
        #Triplex meter
        if grid:
            phase_temp=str(phase_dict[house_placement_df.node_num[i]])
            if rewrite_houses:
                meter_name = 'meter_'+house_dict[i]['name'][0:4]+'B1_N'+str(house_placement_df.node_num[i])+'_'+house_dict[i]['name'][4:]
            else:
                meter_name = 'meter_'+house_dict[i]['name']
            glm_dict[key_index]={'name':meter_name,
                       'nominal_voltage':'124.00',
                       'groupid':'House_meter',
                       'phases':phase_temp+"S"}         
            obj_type[key_index]={'object':'triplex_meter'}
            key_index=key_index+1
            
        #House object
        glm_dict[key_index]=copy.deepcopy(house_dict[i])
        if rewrite_houses:
            new_parent_name ='meter_'+house_dict[i]['name'][0:4]+'B1_N'+str(house_placement_df.node_num[i])+'_'+house_dict[i]['name'][4:]
            new_name = house_dict[i]['name'][0:4]+'B1_N'+str(house_placement_df.node_num[i])+'_'+house_dict[i]['name'][4:]
        else:
            new_parent_name ='meter_'+house_dict[i]['name']
            new_name = house_dict[i]['name']
        glm_dict[key_index]['parent'] = new_parent_name
        glm_dict[key_index]['name']=new_name

        if grid:
            try:
                delta = df_T_mass[house_dict[i]['name']].iloc[-1] - df_T_air[house_dict[i]['name']].iloc[-1]
                T_air = df_T_air[house_dict[i]['name']].iloc[-1] + random.uniform(-1.5,1.5)
            except:
                short_name = 'GLD_'+ house_dict[i]['name'].split('_')[-1]
                delta = df_T_mass[short_name].iloc[-1] - df_T_air[short_name].iloc[-1]
                T_air = df_T_air[short_name].iloc[-1] + random.uniform(-1.5,1.5)
            glm_dict[key_index]['air_temperature'] = T_air #at midnight
            glm_dict[key_index]['mass_temperature'] = T_air + delta #at midnight
        
        obj_type[key_index]={'object':'house'}
        df_house_install = df_house_install.append(pandas.DataFrame(index = [int(house_dict[i]['name'].split('_')[-1])], columns = df_house_install.columns, data = [[new_name,house_placement_df.node_num[i],glm_dict[key_index]['number_of_stories'],glm_dict[key_index]['floor_area'],0.0,0.0,0.0,0.0]])) 
        key_index=key_index+1
        
        #Write zip load for house
        if net_sym_params['inc_ZIP_player']=='True':
            if rewrite_houses:
                new_parent_name = house_dict[i]['name'][0:4]+'B1_N'+str(house_placement_df.node_num[i])+'_'+house_dict[i]['name'][4:]
                new_ZIP_name ='zip_'+house_dict[i]['name'][0:4]+'B1_N'+str(house_placement_df.node_num[i])+'_'+house_dict[i]['name'][4:]
            else:
                new_parent_name = house_dict[i]['name']
                new_ZIP_name ='zip_'+house_dict[i]['name']
            glm_dict[key_index]={'parent':new_parent_name,
                    'name':new_ZIP_name,
                    'power_fraction':'0.5',
                    'impedance_fraction':'0.5',
                    'current_fraction':'0.0',
                    'power_pf':'0.9',
                    'current_pf':'0.9',
                    'impedance_pf':'0.9',
                    'heat_fraction':'0.0',    
                    'base_power':'player_'+str(player[i])+'.value'}
            
            
            obj_type[key_index]={'object':'ZIPload'}
            key_index=key_index+1
                       
    
        #Triplex line
        if grid:
            if rewrite_houses:
                new_meter_name = 'meter_'+house_dict[i]['name'][0:4]+'B1_N'+str(house_placement_df.node_num[i])+'_'+house_dict[i]['name'][4:]
            else:
                new_meter_name ='meter_'+house_dict[i]['name']
            glm_dict[key_index]={'name':'house_line_'+house_dict[i]['name'],
                          'from':'node_'+str(house_placement_df.node_num[i]),
                          'to':new_meter_name,
                          'phases':str(phase_temp)+'S',
                          'length':'30 ft',
                          'configuration':'triplex_line_config'}
            
            obj_type[key_index]={'object':'triplex_line'}
            key_index=key_index+1

    # PV objects 
    if net_sym_params['inc_PV']=='True':
        
        for i in range(len(PV_placement_df)):
            #PV triplex line object
            phase_temp=str(phase_dict[PV_placement_df.PV_node_num[i]])
            glm_dict[key_index]={'name':'PV_line_'+str(i+1),
                             'from':'node_'+str(PV_placement_df.PV_node_num[i]),
                             'to':'PV_meter_B1_N'+str(PV_placement_df.PV_node_num[i])+'_'+str('{:04}'.format(PV_placement_df.PV_house_index[i])),
                             'phases':str(phase_temp)+'S',
                             'length':'30 ft',
                             'configuration':'triplex_line_config'}              
            obj_type[key_index]={'object':'triplex_line'}
            key_index=key_index+1
               
        
            #Triplex meter
            glm_dict[key_index]={'name':'PV_meter_B1_N'+str(PV_placement_df.PV_node_num[i])+'_'+str('{:04}'.format(PV_placement_df.PV_house_index[i])),
                              'nominal_voltage':'124.00',
                              'groupid':'PV_meter',
                              'phases':str(phase_temp)+'S'}
            obj_type[key_index]={'object':'triplex_meter'}
            key_index=key_index+1
            
            #Inverter object
            glm_dict[key_index]={'name':'PV_inverter_B1_N'+str(PV_placement_df.PV_node_num[i])+'_'+str('{:04}'.format(PV_placement_df.PV_house_index[i])),
                       'phases':str(phase_temp)+'S',
                       'parent':'PV_meter_B1_N'+str(PV_placement_df.PV_node_num[i])+'_'+str('{:04}'.format(PV_placement_df.PV_house_index[i])),
                       'generator_status':'ONLINE',
                       'inverter_type':'FOUR_QUADRANT',
                       'four_quadrant_control_mode':'CONSTANT_PF',
                       'generator_mode':'SUPPLY_DRIVEN',
                       'rated_power':str(PV_inverter_rating(PV_area[PV_placement_df.PV_house_index[i] - 1])),
                       'inverter_efficiency':'0.95'}

            obj_type[key_index]={'object':'inverter'}
            key_index=key_index+1
        
            #PV object
            glm_dict[key_index]={'name':'PV_B1_N'+str(PV_placement_df.PV_node_num[i])+'_'+str('{:04}'.format(PV_placement_df.PV_house_index[i])),
                   'phases':str(phase_temp)+'S',
                   'parent':'PV_inverter_B1_N'+str(PV_placement_df.PV_node_num[i])+'_'+str('{:04}'.format(PV_placement_df.PV_house_index[i])),
                   'generator_status':'ONLINE',
                   'generator_mode':'SUPPLY_DRIVEN',
                   'panel_type':'SINGLE_CRYSTAL_SILICON',
                   'area':str(round(float(PV_area[PV_placement_df.PV_house_index[i] - 1])))+' ft^2',
                   'tilt_angle':'25.0',
                   'efficiency':'0.15',
                   'soiling':'0.95',
                   'derating':'0.99',
                   'a_coeff':'-3.2',
                   'orientation_azimuth':'225',
                   'orientation':'FIXED_AXIS',
                   'SOLAR_TILT_MODEL':'SOLPOS',
                   'SOLAR_POWER_MODEL':'FLATPLATE'}
            
            df_house_install.at[int(PV_placement_df.PV_house_index[i]),'pv_area'] = round(float(PV_area[PV_placement_df.PV_house_index[i] - 1]))
            df_house_install.at[int(PV_placement_df.PV_house_index[i]),'pv_inv_rated_power'] = PV_inverter_rating(PV_area[PV_placement_df.PV_house_index[i] - 1])

            obj_type[key_index]={'object':'solar'}

            key_index=key_index+1
  
    glm_dict[key_index]={'char32':'charging_type','double':'k'}
    obj_type[key_index]={'class':'battery'}
    key_index=key_index+1
    
    # Battery objects
    if net_sym_params['inc_battery']=='True':
        
        for i in range(len(Bat_placement_df)):
            #Triplex line object
            phase_temp=str(phase_dict[Bat_placement_df.Bat_node_num[i]])
            glm_dict[key_index]={'name':'Bat_line_'+str(i+1),
                         'from':'node_'+str(Bat_placement_df.Bat_node_num[i]),
                         'to':'Bat_meter_B1_N'+str(Bat_placement_df.Bat_node_num[i])+'_'+str('{:04}'.format(Bat_placement_df.Bat_house_index[i])),
                         'phases':str(phase_temp)+'S',
                         'length':'30 ft',
                         'configuration':'triplex_line_config'}
            obj_type[key_index]={'object':'triplex_line'}
            key_index=key_index+1
            
            #Triplex meter object
            glm_dict[key_index]={'name':'Bat_meter_B1_N'+str(Bat_placement_df.Bat_node_num[i])+'_'+str('{:04}'.format(Bat_placement_df.Bat_house_index[i])),
                               'groupid':'Bat_meter',
                               'nominal_voltage':'124.00',
                               'phases':phase_temp+'S'}
            obj_type[key_index]={'object':'triplex_meter'}
            key_index=key_index+1
            

            bat_size_i = round(float(bat_size[Bat_placement_df.Bat_house_index[i] - 1]))
            if bat_size_i < 8000:
                inv_size_i = '4000.0'
            else:
                inv_size_i = '8000.0'

            #Inverter object
            glm_dict[key_index]={'name':'Bat_inverter_B1_N'+str(Bat_placement_df.Bat_node_num[i])+'_'+str('{:04}'.format(Bat_placement_df.Bat_house_index[i])),
                        'generator_status':'ONLINE',
                        'inverter_type':'FOUR_QUADRANT',
                        'four_quadrant_control_mode':'CONSTANT_PQ',
                        'parent':'Bat_meter_B1_N'+str(Bat_placement_df.Bat_node_num[i])+'_'+str('{:04}'.format(Bat_placement_df.Bat_house_index[i])),
                        'rated_power':inv_size_i,
                        'inverter_efficiency':'0.95',
                        'Q_Out':'0'}
            obj_type[key_index]={'object':'inverter'}
            key_index=key_index+1
                        
            #Battery object
            glm_dict[key_index]={'name':'Battery_B1_N'+str(Bat_placement_df.Bat_node_num[i])+'_'+str('{:04}'.format(Bat_placement_df.Bat_house_index[i])),
                    'parent':'Bat_inverter_B1_N'+str(Bat_placement_df.Bat_node_num[i])+'_'+str('{:04}'.format(Bat_placement_df.Bat_house_index[i])),
                    'use_internal_battery_model':'TRUE',
                    'battery_type':'LI_ION',
                    'power_factor':'1.0',
                    'V_Max':'260',
                    'I_Max':'15',
                    'E_Max':str(bat_size_i),
                    #'E_Max':'7000',
                    'power_type':'DC',
                    'battery_capacity':str(bat_size_i),
                    #'battery_capacity':'7000',
                    'base_efficiency':'0.95',
                    'state_of_charge':'0.2',
                    'generator_mode':'SUPPLY_DRIVEN'}

            df_house_install.at[int(Bat_placement_df.Bat_house_index[i]),'battery_capacity'] = bat_size_i
            df_house_install.at[int(Bat_placement_df.Bat_house_index[i]),'batt_inv_rated_power'] = inv_size_i
            obj_type[key_index]={'object':'battery'}
            key_index=key_index+1

    # Battery objects
    if net_sym_params['inc_EV']=='True':
        
        for i in range(len(EV_placement_df)):
            #Triplex line object
            phase_temp=str(phase_dict[EV_placement_df.EV_node_num[i]])
            glm_dict[key_index]={'name':'EV_line_'+str(i+1),
                         'from':'node_'+str(EV_placement_df.EV_node_num[i]),
                         'to':'EV_meter_B1_N'+str(EV_placement_df.EV_node_num[i])+'_'+str('{:04}'.format(EV_placement_df.EV_house_index[i])),
                         'phases':str(phase_temp)+'S',
                         'length':'30 ft',
                         'configuration':'triplex_line_config'}
            obj_type[key_index]={'object':'triplex_line'}
            key_index=key_index+1
            
            #Triplex meter object
            glm_dict[key_index]={'name':'EV_meter_B1_N'+str(EV_placement_df.EV_node_num[i])+'_'+str('{:04}'.format(EV_placement_df.EV_house_index[i])),
                               'groupid':'EV_meter',
                               'nominal_voltage':'124.00',
                               'phases':phase_temp+'S'}
            obj_type[key_index]={'object':'triplex_meter'}
            key_index=key_index+1
            
            #Inverter object
            glm_dict[key_index]={'name':'EV_inverter_B1_N'+str(EV_placement_df.EV_node_num[i])+'_'+str('{:04}'.format(EV_placement_df.EV_house_index[i])),
                        'generator_status':'ONLINE',
                        'inverter_type':'FOUR_QUADRANT',
                        'four_quadrant_control_mode':'CONSTANT_PQ',
                        'parent':'EV_meter_B1_N'+str(EV_placement_df.EV_node_num[i])+'_'+str('{:04}'.format(EV_placement_df.EV_house_index[i])),
                        'rated_power':'3000.0',
                        'inverter_efficiency':'0.95'
                        #,
                        #'Q_Out':'0'
                        }
            obj_type[key_index]={'object':'inverter'}
            key_index=key_index+1
                        
            #Battery object
            glm_dict[key_index]={'name':'EV_B1_N'+str(EV_placement_df.EV_node_num[i])+'_'+str('{:04}'.format(EV_placement_df.EV_house_index[i])),
                    'parent':'EV_inverter_B1_N'+str(EV_placement_df.EV_node_num[i])+'_'+str('{:04}'.format(EV_placement_df.EV_house_index[i])),
                    'use_internal_battery_model':'TRUE',
                    'battery_type':'LI_ION',
                    'power_factor':'1.0',
                    'V_Max':'260',
                    'I_Max':'15',
                    #'E_Max':str(round(float(bat_size[Bat_placement_df.Bat_house_index[i]]))),
                    #'E_Max':'7000',
                    'power_type':'DC',
                    #'battery_capacity':str(round(float(bat_size[Bat_placement_df.Bat_house_index[i]]))),
                    'battery_capacity':'7000',
                    'base_efficiency':'0.95',
                    'state_of_charge':'0.2',
                    'generator_mode':'SUPPLY_DRIVEN',
                    'charging_type':np.random.choice(['residential','commercial'])}
            if glm_dict[key_index]['charging_type'] == 'residential':
                glm_dict[key_index]['k'] = str(np.random.randint(1,11))
            else:
                glm_dict[key_index]['k'] = '0'

            obj_type[key_index]={'object':'battery'}
            key_index=key_index+1

    #Recorders
    glm_dict[key_index]={'name':'rec_total_load','group':'"class=house"','property':'total_load','file':results_folder+'/total_load_all.csv','interval':'60','limit':'100000'}
    obj_type[key_index]={'object':'group_recorder'}
    key_index=key_index+1
    
    glm_dict[key_index]={'name':'rec_hvac_load','group':'"class=house"','property':'hvac_load','file':results_folder+'/hvac_load_all.csv','interval':'60','limit':'100000'}
    obj_type[key_index]={'object':'group_recorder'}
    key_index=key_index+1
    
    glm_dict[key_index]={'name':'rec_T','group':'"class=house"','property':'air_temperature','file':results_folder+'/T_all.csv','interval':'60','limit':'100000'}
    obj_type[key_index]={'object':'group_recorder'}
    key_index=key_index+1
    
    glm_dict[key_index]={'name':'rec_Tm','group':'"class=house"','property':'mass_temperature','file':results_folder+'/Tm_all.csv','interval':'60','limit':'100000'}
    obj_type[key_index]={'object':'group_recorder'}
    key_index=key_index+1
    
    glm_dict[key_index]={'name':'rec_pv_infeed','group':'"class=inverter"','property':'P_Out','file':results_folder+'/total_P_Out.csv','interval':'60','limit':'100000'}
    obj_type[key_index]={'object':'group_recorder'}
    key_index=key_index+1

    glm_dict[key_index]={'name':'rec_batt_soc','group':'"class=battery"','property':'state_of_charge','file':results_folder+'/battery_SOC.csv','interval':'60','limit':'100000'}
    obj_type[key_index]={'object':'group_recorder'}
    key_index=key_index+1

    #glm_dict[key_index]={'filename':results_folder+'/Vdump.csv','filemode':'"a"','runtime':'TS_NEVER','maxcount':'1500','mode':'polar'}
    #obj_type[key_index]={'object':'voltdump'}
    #key_index=key_index+1

    df_house_install.to_csv('df_house_floor.csv')
    if rewrite_houses:
        file_name_glm = 'Base_IEEE_123_homes_1min_nothermostatcontrol.glm'
    else:
        file_name_glm = net_sym_params['out_file']
    write_base_glm(glm_dict,obj_type,globals_list,include_list,input_dir,file_name_glm,sync_list)
    return glm_dict,obj_type,globals_list,include_list,sync_list
    
def gen_calibration_glm(input_dir,house_dict,player,inputs,tot_zip_dict,num_duplicates):
    '''Generate .glm file as addition to base .glm file of network
    Places homes, PV, batteries at nodes specified in csv files'''   
    
    os.chdir(input_dir)
    
    #Initialize dictionaries for object data
    glm_dict={}
    obj_type={}
    globals_list=[]
    include_list=[]
    key_index=0
    sync_list=[]
    
    #Modules
    glm_dict[key_index]={'implicit_enduses':'NONE'}
    obj_type[key_index]={'module':'residential'}
    key_index=key_index+1       
        
    glm_dict[key_index]={}
    obj_type[key_index]={'module':'climate'}
    key_index=key_index+1
    
    glm_dict[key_index]={}
    obj_type[key_index]={'module':'tape'}
    key_index=key_index+1
    
    glm_dict[key_index]={}
    obj_type[key_index]={'module':'generators'}
    key_index=key_index+1
    
    #Climate object
    glm_dict[key_index]={'name':'tmy_file',
               'tmyfile':tmy_file,
               'interpolate':'LINEAR'}
    obj_type[key_index]={'object':'climate'}
    key_index=key_index+1

    #Player class
    glm_dict[key_index]={'double':'value'}
    obj_type[key_index]={'class':'player'}
    key_index=key_index+1

    #Player objects
    for p in range(len(tot_zip_dict)):
        glm_dict[key_index]={'name':'player_'+str(p),
                'file':tot_zip_dict[p]}
        obj_type[key_index]={'object':'player'}
        key_index=key_index+1
    
    #define houses
    """Adjust for changes in class"""
    glm_dict[key_index]={'double':'k','double1':'T_max','double2':'T_min'} #,'double3':'hvac_energy_5min'} #,'double4':'air_temperature','double5':'mass_temperature'}
    obj_type[key_index]={'class':'house'}
    key_index=key_index+1   
    
    #Loop through houses
    df_house_install = pandas.DataFrame(columns=['house','node','stores','floor','pv_area','pv_inv_rated_power','battery_capacity','batt_inv_rated_power'])
    for i in range(len(house_dict.keys())):

        #House object
        glm_dict[key_index]=copy.deepcopy(house_dict[i])
        glm_dict[key_index]['name']=house_dict[i]['name']
        
        obj_type[key_index]={'object':'house'}
        df_house_install = df_house_install.append(pandas.DataFrame(index = [int(house_dict[i]['name'].split('_')[-1])], columns = df_house_install.columns, data = [[house_dict[i]['name'],'None',glm_dict[key_index]['number_of_stories'],glm_dict[key_index]['floor_area'],0.0,0.0,0.0,0.0]])) 
        key_index=key_index+1
        
        #Write zip load for house
        new_parent_name = house_dict[i]['name']
        new_ZIP_name ='zip_'+house_dict[i]['name']
        glm_dict[key_index]={'parent':new_parent_name,
                'name':new_ZIP_name,
                'power_fraction':'0.5',
                'impedance_fraction':'0.5',
                'current_fraction':'0.0',
                'power_pf':'0.9',
                'current_pf':'0.9',
                'impedance_pf':'0.9',
                'heat_fraction':'0.0',    
                'base_power':'player_'+str(player[i])+'.value'}       
        obj_type[key_index]={'object':'ZIPload'}
        key_index=key_index+1

    #Recorders
    glm_dict[key_index]={'name':'rec_total_load','group':'"class=house"','property':'total_load','file':'glm_generation_'+city+'/calibration_total_load.csv','interval':'60','limit':'100000'}
    obj_type[key_index]={'object':'group_recorder'}
    key_index=key_index+1
    
    glm_dict[key_index]={'name':'rec_T','group':'"class=house"','property':'air_temperature','file':'glm_generation_'+city+'/calibration_T_all.csv','interval':'60','limit':'100000'}
    obj_type[key_index]={'object':'group_recorder'}
    key_index=key_index+1
    
    glm_dict[key_index]={'name':'rec_Tm','group':'"class=house"','property':'mass_temperature','file':'glm_generation_'+city+'/calibration_Tm_all.csv','interval':'60','limit':'100000'}
    obj_type[key_index]={'object':'group_recorder'}
    key_index=key_index+1

    #df_house_install.to_csv('glm_generation_'+city+'/df_house_floor_calibration.csv')
    df_house_install.to_csv('df_house_floor_calibration.csv')
    file_name = 'IEEE_123_homes_1min_calibration_'+city+'.glm' #In main folder where gridlabd runs
    write_base_glm(glm_dict,obj_type,globals_list,include_list,input_dir,file_name,sync_list,calibration=True)
    return glm_dict,obj_type,globals_list,include_list,sync_list
    
##nNOT NEEDED ANYMORE

def modify_glmfile():
    print(os.getcwd())
    file = 'IEEE_123_homes_1min.glm'
    new_file = 'IEEE_123_homes_1min_calibration_'+city+'.glm'
    glm = open(file,'r') 
    new_glm = open(new_file,'w') 
    j = 0

    #Write header
    new_glm.write('#set iteration_limit=100000;\n\n')
    new_glm.write('#set minimum_timestep=60;\n\n')
    new_glm.write('clock {\n')
    new_glm.write('\tstarttime "2015-07-01 00:00:00";\n')
    new_glm.write('\tstoptime "2015-07-31 23:59:00";\n')
    new_glm.write('}\n\n')
    new_glm.write('module residential {\n')
    new_glm.write('\timplicit_enduses NONE;\n')
    new_glm.write('}\n\n')

    #Write old file 
    for line in glm:
        if (not 'group_recorder' in line) and (not 'meter' in line) and (not 'thermostat_control' in line) and (not 'temperature' in line):
            new_glm.write(line)
        elif 'meter' in line:
            pass 
        elif 'thermostat_control' in line:
            pass
        elif 'temperature' in line:
            pass
        else:
            break
    
    #Add group_recorder
    new_glm.write('object group_recorder {\n')
    new_glm.write('\tname rec_Tm;\n')
    new_glm.write('\tgroup "class=house";\n')
    new_glm.write('\tproperty mass_temperature;\n')
    new_glm.write('\tfile glm_generation_'+city+'/calibration_Tm_all.csv;\n')
    new_glm.write('\tinterval 60;\n')
    new_glm.write('\tlimit 100000;\n')
    new_glm.write('}\n\n')

    new_glm.write('object group_recorder {\n')
    new_glm.write('\tname rec_T;\n')
    new_glm.write('\tgroup "class=house";\n')
    new_glm.write('\tproperty air_temperature;\n')
    new_glm.write('\tfile glm_generation_'+city+'/calibration_T_all.csv;\n')
    new_glm.write('\tinterval 60;\n')
    new_glm.write('\tlimit 100000;\n')
    new_glm.write('}\n\n')

    new_glm.write('object group_recorder {\n')
    new_glm.write('\tname rec_hvac_load;\n')
    new_glm.write('\tgroup "class=house";\n')
    new_glm.write('\tproperty hvac_load;\n')
    new_glm.write('\tfile glm_generation_'+city+'/calibration_hvac_load.csv;\n')
    new_glm.write('\tinterval 60;\n')
    new_glm.write('\tlimit 100000;\n')
    new_glm.write('}\n')

    new_glm.write('object group_recorder {\n')
    new_glm.write('\tname rec_total_load;\n')
    new_glm.write('\tgroup "class=house";\n')
    new_glm.write('\tproperty total_load;\n')
    new_glm.write('\tfile group_recorder_'+city+'.csv;\n')
    new_glm.write('\tinterval 60;\n')
    new_glm.write('\tlimit 100000;\n')
    new_glm.write('}\n')

    glm.close()
    new_glm.close()
    return
