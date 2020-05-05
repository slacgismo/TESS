import os

#Result file
results_folder = 'output'
if not os.path.exists(results_folder):
	os.makedirs(results_folder)

#glm parameters
city = 'Austin'
month = 'july'
start_time_str = '2015-07-15 0:00'
end_time_str = '2015-07-16 23:59'
player_dir = 'players_SanDiego_2015'
tmy_file = '722900TYA.tmy3'
slack_node = 'node_149'

#Flexible appliances
flexible_houses = 1120
PV_share = 0.0
EV_share = 0.0
EV_data = 'None'
EV_speed = 'normal'
Batt_share = 0.0
assert PV_share >= Batt_share, 'More batteries than PV'
#Market parameters
C = 5000.0
market_data = 'Ercot_HBSouth.csv'
p_max = 100.0
load_forecast = 'myopic'
unresp_factor = 1.0
FIXED_TARIFF = False
interval = 300
allocation_rule = 'by_award'

#Appliance specifications
delta = 3.0 #temperature bandwidth - HVAC inactivity
ref_price = 'forward'
price_intervals = 36 #p average calculation 
which_price = 'DA' #battery scheduling

#include System Operator
include_SO = False

#precision in bidding and clearing price
prec = 4
M = 10000 #large number
ip_address = 'none'
