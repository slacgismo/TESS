import os

#Result file
results_folder = 'TESS_mysql/TESS_mysql_0001'
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
interval = 300
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
ip_address = '192.168.1.67'
