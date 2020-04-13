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

from HH_global import start_time_str, end_time_str
from HH_global import city, player_dir, results_folder
from HH_global import slack_node, start_time_str, end_time_str, interval, flexible_houses, EV_share, PV_share, Batt_share, tmy_file

#Only for bc
def rewrite_glmfile():
    print('Some of the parameters in the global/settings files are not accounted for')
    print('E.g. shares of DER')

    ########
    # Time: re-write default.glm
    ########

    default = 'config/default.glm'
    open(default, 'w').close()
    default_out = open(default,"w+")
    default_out.write('// this file is used if local.glm is not found\n')
    default_out.write('#define TIMEZONE=${TIMEZONE:-US/CA/Los Angeles}\n')
    default_out.write('#define WEATHER=${WEATHER:-'+tmy_file+'}\n')
    default_out.write('#define STARTTIME=${STARTTIME:-'+start_time_str+'}\n')
    default_out.write('#define STOPTIME=${STOPTIME:-'+end_time_str+'}')
    default_out.close()

    ########
    # Time: re-write default.glm
    ########
    results_folder = 'TESS/TESS_BC'
    original_model = open('model_default.glm','r')
    new_model = open('model.glm','w+')
    for line in original_model:
        if ('file' in line) and ('.csv' in line):
            line_split = line.split('/')
            new_line = '\tfile ' + results_folder + '/' + line_split[1].split(';')[0] + ';\n'
            #import pdb; pdb.set_trace()
            new_model.write(new_line)
        else:
            new_model.write(line)
    original_model.close()
    new_model.close()
    return

def modify_glmfile():
    original_model = open('model_bc.glm','r')
    new_model = open('model_ts.glm','w+')
    for line in original_model:
        if (line == '// modules\n'):
            new_model.write(line)
            new_model.write('module gridlabd_functions;\n')
        elif ('file' in line) and ('_BC' in line) and ('.csv' in line):
            #import pdb; pdb.set_trace()
            line_split = line.split('/')
            new_line = '\tfile ' + results_folder + '/' + line_split[2].split(';')[0][:-1] + ';\n'
            new_model.write(new_line)
        else:
            new_model.write(line)
    original_model.close()
    new_model.close()
    return
