# This runs the market with a gridlabd model as a representation of the physical model

import os
import pandas as pd
import time
from datetime import date

import gridlabd

import requests

from HH_global import start_time_str, end_time_str

# Only with GridLAB-D : Rewrite players to today's day

player_path = 'glm_generation_Austin/players_Austin'
players = os.listdir(player_path)
for player in players:
	if '.player' in player:
		original_player = open(player_path + '/' + player, "r")
		#player = open(player_path + '/' + player, "w+").close()
		new_player = open(player_path + '/copy_' + player, "w+")
		first_line = True
		for line in original_player:
			if first_line:
				new_line = str(date.today()) + ' 00:00:00,' + line.split(',')[1]
				new_player.write(new_line)
				first_line = False
			else:
				new_player.write(line)
		original_player.close()
		os.remove(player_path + '/' + player)
		os.rename(player_path + '/copy_' + player,player_path + '/' + player)

# Only with GridLAB-D : Re-write glm model to today's date

config_path = 'config'
original_default = open(config_path + '/default copy.glm', "r")
#default = open(config_path + '/default.glm', "w+").close()
default = open(config_path + '/default.glm', "w+")
for line in original_default:
	print(line)
	if 'STARTTIME' in line:
		default.write('#define STARTTIME=${STARTTIME:-' + str(date.today()) + ' 00:00:00}\n')
	elif 'STOPTIME' in line:
		default.write('#define STOPTIME=${STOPTIME:-' + str(date.today() + pd.Timedelta(days=1)) + ' 00:00:00}')
	else:
		default.write(line)
default.close()

# Adjust/Re-write

# folders
# interval (interval for markets should be identical with recorders)

#Start simulation

gridlabd.command('model_RT.glm')
#gridlabd.command('-D')
#gridlabd.command('run_realtime=TRUE') # CHECK - locks in clock with real-time

# Does not work with R_ simulation, therefore execution stops here
# Enter manually into terminal:

# gridlabd model_RT.glm


