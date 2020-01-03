"""
Run a test of basic TESS functionality

The purpose of this test script is to exercise *all* the TESS table functions.
"""
try:
	from mysql.tess import *;
except:
	from tess import *;
import datetime;

#
# DEBUG
# 
set_debug(9);
debug(-1,f"set debugging to level {get_debug()}");

#
# CONNECT
#
set_connection(local=True);

#
# DATABASE
# 

# create database
if get_database(schema="test"):
	del_database(schema="test");
add_database(schema="test");
set_database(schema="test");
debug(-1,"create database ok");

#
# SYSTEM
#

# add test system
system_name = "test";
system_id = add_system(name=system_name);

# get system id
assert(find_system(name=system_name)["data"][0]["system_id"] == system_id);
assert(get_system(system_id=system_id)["name"] == system_name);
debug(-1,"system test ok",system_id);

#
# CONFIG
#

# add a new system configuration parameter, then change it and check the value
config_name = "test-name";
config_value = ["test-value1","test-value2","test-value3"];
add_config(system_id=system_id,name=config_name,value=config_value[0]);
config_id = add_config(system_id=system_id,name=config_name,value=config_value[1]);
config_data = get_config(config_id=config_id)
assert(config_data["value"] == config_value[1]);
set_config(system_id=system_id,name=config_name,value=config_value[2]);
config_id = find_config(system_id=system_id,name=config_name);
config_data = get_config(config_id=config_id)
assert(config_data["value"] == config_value[2]);
debug(-1,"config test ok",config_id);

#
# USER
#

# create a new user
user_name = "test1";
user_email = "test1@tess.org";
good_password = "good-password";
bad_password = "bad-password";
user_id = add_user(system_id=system_id,name=user_name,email=user_email,password=good_password);
assert(find_user(name=user_name) == user_id);

# get user info

assert(get_user(user_id=user_id)["name"] == user_name);

# check good user password
assert(get_user(user_id=user_id,password=good_password)["name"] == user_name);

# check bad user password (return)
assert(get_user(user_id=user_id,password=bad_password) == None);

# check bad user password (throw)
try:
	get_user(user_id=user_id,password="bad-password",use_throw=True);
	assert(False);
except:
	assert(True);
debug(-1,"user test ok",user_id);

#
# PREFERENCE
#

# add a user prefernce, check it, change it, and check it again
preference_name = "test-name";
preference_value = "test-value";
preference_id = add_preference(user_id=user_id,name=preference_name,value=preference_value);
assert(get_preference(preference_id=preference_id)["value"] == preference_value);
assert(find_preference(user_id=user_id,name=preference_name) == preference_id);
debug(-1,"preference test ok",preference_id);

#
# TOKEN
#

# add a token, check it, delete it, check it again
token_id = add_token(user_id=user_id);
token_data = get_token(token_id=token_id);
assert(token_data["user_id"] == user_id);
assert(find_token(unique_id=token_data["unique_id"]) == token_id);
set_token(token_id=token_id,is_valid=False);
assert(get_token(token_id=token_id) == None);
assert(find_token(unique_id=token_data["unique_id"]) == None);
debug(-1,"token test ok",token_id);


#
# DEVICE
#

# add a new device, then rename it and check the value
device_id = add_device(user_id=user_id,name="meter1");
device_data = get_device(device_id=device_id);
assert(device_data["name"] == "meter1");
assert(find_device(unique_id=device_data["unique_id"]) == device_id);
device_id = set_device(device_id=device_id,name="meter2");
device_data = get_device(device_id=device_id);
assert(device_data["name"] == "meter2");
debug(-1,"device test ok",device_id);

#
# SETTING
#

# add a setting, check it, change it, and check it again
setting_name = "test-name";
setting_value = "test-value";
setting_id = add_setting(device_id=device_id,name=setting_name,value=setting_value);
assert(find_setting(device_id=device_id,name=setting_name) == setting_id);
setting_data = get_setting(setting_id=setting_id);
assert(setting_data["value"] == setting_value);
debug(-1,"setting test ok",setting_id);

#
# RESOURCE
#

# add a resource and check it
resource_name = "test-resource";
resource_quantity_unit = "quantity-unit";
resource_price_unit = "price-unit";
resource_id = add_resource(system_id=system_id,name=resource_name,quantity_unit=resource_quantity_unit,price_unit=resource_price_unit);
assert(resource_id == find_resource(system_id=system_id,name="test-resource"));
resource_data = get_resource(resource_id=resource_id);
assert(resource_data["name"] == "test-resource")
debug(-1,"resource test ok",resource_id);

#
# PRICE
#

# add a new price, find it, get it, and check it
quantity = 1.23;
price = 2.34; 
price_id = add_price(resource_id=resource_id,quantity=quantity,price=price);
assert(price_id == find_price(resource_id=resource_id));
price_data = get_price(price_id=price_id);
assert(price_data["price"] == price);
assert(price_data["quantity"] == quantity)
debug(-1,"price test ok",price_id);

#
# METER
#

# add a new meter entry and check it
quantity = 3.45;
meter_id = add_meter(device_id=device_id,price_id=price_id,quantity=quantity);
assert(find_meter(device_id=device_id) == device_id)
meter_data = get_meter(meter_id=meter_id);
assert(meter_data["quantity"] == quantity);
debug(-1,"meter test ok",meter_id);

#
# ORDER
#

# add a new order, check it, then change it, check it again, then delete it
quantity = 4.56;
bid = 5.67;
order_id = add_order(device_id=device_id,resource_id=resource_id,quantity=quantity,bid=bid);
order_data = get_order(order_id=order_id);
assert(order_data["quantity"] == quantity);
assert(order_data["bid"] == bid);
assert(order_data["current"] == None);
assert(order_data["duration"] == None);
assert(find_order(order_data["unique_id"]) == order_id);
assert(set_order(order_id=order_id,closed=datetime.datetime.now()) == 1);
set_order(order_id=order_id,price_id=price_id,use_throw=True);
assert(set_order(order_id=order_id,duration=0,current=0) == None);
debug(-1,"order test ok",order_id);

#
# TRANSACTION
#

# add a transaction and check it
amount = 6.78;
transaction_id = add_transaction(meter_id=meter_id,amount=amount);
transaction_data = get_transaction(transaction_id);
assert(transaction_data["balance"] == amount);
transaction_id = add_transaction(meter_id=meter_id,amount=-amount);
transaction_data = get_transaction(transaction_id);
assert(transaction_data["balance"] == 0.0);
debug(-1,"transaction test ok",transaction_id);

#
# TIMESERIES
#

# add multiple price entries (quantity,price)
data = [
	(1,2),
	(2,3),
	(3,4),
	(4,5),
	(5,6),
	(6,7),	
	];
import time;
time.sleep(1);
starting = datetime.datetime.now();
time.sleep(1);
for value in data:
	add_price(resource_id,quantity=value[0],price=value[1]);

# get a price timeseries and check it
timeseries = get_timeseries(resource_id,starting=starting);
assert(len(data) == len(timeseries));
for n in range(len(data)):
	assert(timeseries[n]["quantity"] == data[n][0]);
	assert(timeseries[n]["price"] == data[n][1])

# run a billing summary (not sure exactly what this is yet)

# all done, cleanup
del_database(schema="test");

debug(-1,"timeseries test ok");
