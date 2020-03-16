def write_global(series_settings,ind,ip_address):
    global_file = 'HH_global.py'
    glm = open(global_file,'w') 
    #import pdb; pdb.set_trace()

    # Flexible houses
    glm.write('import os\n\n')

    glm.write('#Result file\n')
    glm.write('results_folder = \''+series_settings['run']+'/'+series_settings['run']+'_'+"{:04d}".format(ind)+'\'\n')
    glm.write('if not os.path.exists(results_folder):\n')
    glm.write('\tos.makedirs(results_folder)\n\n')

    glm.write('#glm parameters\n')
    glm.write('city = \''+series_settings['city']+'\'\n')
    glm.write('month = \''+series_settings['month']+'\'\n')
    glm.write('start_time_str = \''+series_settings['start_time']+'\'\n')
    glm.write('end_time_str = \''+series_settings['end_time']+'\'\n')
    glm.write('player_dir = \''+series_settings['player_dir']+'\'\n')
    glm.write('tmy_file = \''+series_settings['tmy']+'\'\n')
    glm.write('slack_node = \''+series_settings['slack_node']+'\'\n\n')

    glm.write('#Flexible appliances\n')
    glm.write('flexible_houses = '+str(series_settings['flexible_houses'])+'\n')
    glm.write('PV_share = '+str(float(series_settings['PV_share']))+'\n')
    glm.write('EV_share = '+str(float(series_settings['EV_share']))+'\n')
    glm.write('EV_data = \''+series_settings['EV_data']+'\'\n')
    glm.write('EV_speed = \''+series_settings['EV_speed']+'\'\n')
    glm.write('Batt_share = '+str(float(series_settings['Batt_share']))+'\n')
    glm.write('assert PV_share >= Batt_share, \'More batteries than PV\'\n')
    #glm.write('assert PV_share >= EV_share, \'More EVs than PV\'\n\n')
    
    glm.write('#Market parameters\n')
    glm.write('C = '+str(float(series_settings['line_capacity']))+'\n')
    glm.write('market_data = \''+series_settings['market_data']+'\'\n')
    glm.write('p_max = '+str(float(series_settings['p_max']))+'\n')
    glm.write('load_forecast = \''+series_settings['load_forecast']+'\'\n')
    glm.write('unresp_factor = '+str(float(series_settings['unresp_factor']))+'\n')
    glm.write('FIXED_TARIFF = '+str(series_settings['fixed_tariff'])+'\n')
    glm.write('interval = '+str(int(series_settings['interval']))+'\n')
    glm.write('allocation_rule = \''+series_settings['allocation_rule']+'\'\n\n')

    glm.write('#Appliance specifications\n')
    glm.write('delta = '+str(float(series_settings['delta']))+' #temperature bandwidth - HVAC inactivity\n')
    glm.write('ref_price = \''+series_settings['ref_price']+'\'\n')
    glm.write('price_intervals = '+str(int(series_settings['price_intervals']))+' #p average calculation \n')
    glm.write('which_price = \''+series_settings['which_price']+'\' #battery scheduling\n\n')
 
    glm.write('#include System Operator\n')
    glm.write('include_SO = '+str(series_settings['include_SO'])+'\n\n')

    glm.write('#precision in bidding and clearing price\n')
    glm.write('prec = '+str(int(series_settings['prec']))+'\n')
    glm.write('M = '+str(int(series_settings['M']))+' #large number\n')
    glm.write('ip_address = \''+ip_address+'\'\n')

    glm.close()
    return