import os

#Data input
input_folder = 'data_TESS'
start_time_str = '2016-07-01 00:00'
end_time_str = '2016-07-31 23:59'
tmy_file = '722900TYA.tmy3'

#Result file
results_folder = 'TESS/TESS_0005'
if not os.path.exists(results_folder):	os.makedirs(results_folder)

#Flexible appliances
no_houses = 6
flexible_houses = 0
PV_share = 1.0
EV_share = 0.0
EV_data = 'None'
EV_speed = 'slow'
Batt_share = 0.0
assert (flexible_houses == 0.0), 'No house has flexible HVAC'
assert (PV_share == 1.0), 'All houses have PV'
assert (EV_share == 0.0), 'EV not implemented yet'
assert (Batt_share == 0.0), 'Battery not implemented yet'

#TS parameters
customer_op = 'direct'
system_op = 'EIM'
fixed_procurement_cost = 0.0
coincident_peak_rate = 0.0
control_room_data = 'df_controlroom_2016_July_6houses_unconstr.csv'
RR = 30.0
market_data = 'CAISO_KETTNER_2019_2016.csv'
p_max = 100000.0
slack_node = 'node_149'
load_forecast = 'myopic'
unresp_factor = 1.0
FIXED_TARIFF = False
interval = 300
allocation_rule = 'by_award'

#Appliance specifications
delta = 3.0 #temperature bandwidth - HVAC inactivity
ref_price = 'historical'
price_intervals = 288 #p average calculation 
which_price = 'RT' #battery scheduling

#include System Operator
include_SO = False

#precision in bidding and clearing price
prec = 4
M = 10000 #large number
ip_address = 'none'
