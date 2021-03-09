import os

db_address = 'http://host.docker.internal:5000/api/v1/'
gld_simulation = True # True : uses gridlabd as representation of physical model
dispatch_mode = True # True : implements dispatch decisions by writing them to the database

# Result file
results_folder = 'results'

# Market settings
interval = 15 # [s]; Normal operations: 300 s


###
# Probably not important (check before deleting)
####

#glm parameters
city = 'Austin'
month = 'Jan'
start_time_str = '2016-07-01 00:00:00'
end_time_str = '2016-07-02 00:00:00'
player_dir = 'players_SanDiego_2015'
tmy_file = '722540TYA.tmy3'
slack_node = 'node_149'

#Flexible appliances
flexible_houses = 0
PV_share = 0.25
EV_share = 0.1
EV_data = 'None'
EV_speed = 'slow'
Batt_share = 0.1
assert PV_share >= Batt_share, 'More batteries than PV'
#Market parameters
C = 1250.0
market_data = 'Ercot_HBSouth.csv'
p_max = 100.0
load_forecast = 'myopic'
unresp_factor = 0.0
FIXED_TARIFF = False
allocation_rule = 'by_award'

#Appliance specifications
delta = 3.0 #temperature bandwidth - HVAC inactivity
ref_price = 'historical'
price_intervals = 288 #p average calculation 
which_price = 'DA' #battery scheduling

#include System Operator
include_SO = False

#precision in bidding and clearing price
prec = 4
M = 10000 #large number