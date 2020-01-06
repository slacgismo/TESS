"""TESS mysql library

Provide MySQL operations needed for TESS

TESS Table Access Functions:

  add_<table>(<constraint-key>=<constraint-value>,name=<name>,value=<value>)
   - or -
  add_<table>(<constraint-key>=<constraint-value>,<name>=<value>,...)
   - or -
  add_<table>(<data-dict>)  

	This function is used to add a record to a table.  If the table includes
	any constraint keys, these must be included. In addition, all non-NULL
	fields must be included.

	Note that the semantics are from the perspective of the database, not
	the system, i.e., "add_user" means "add a record to the user table", not
	"add a user to the system".

	The `add` functions always return a record id on success or None on failure.

  find_<table>(<criteria-dict>,use_throw=<bool>)

  	This function finds a record that matches the criteria given. If multiple
  	records are found, the most recent one is returned.  The criteria is given
  	as <dict> object. Only exact matches are permitted.

	The `find` functions always return a record id on success or None on failure.

  get_<table>(<record-id>)

  	This function gets a record using the record id.

	The `get` functions always return a data dict on success or None on failure.

  set_<table>(<record-id>,<name>=<value>,...)

  	This function changes a record using the record id. In most cases this
  	actually involved getting the most recent values, and adding a new record
  	with the updated values. Only some table/fields allow this operation, such 
  	as 'config.value', 'device.name', 'order.{bid,quantity,duration,current,
  	closed}', 'preference.value', 'resource.{quantity_unit,price_unit}',
  	'setting.value', 'user.{name,email,sha1pwd}'. This function is useful
  	because it copies the constraint keys and other unchanged values so they
  	don't need to be copied by the caller.

	The `set` functions always return the number of records changed or None.

"""

import sys, os
assert(sys.version_info.major>2)

import pymysql as mysql
import config
import json
import datetime

module = sys.modules[__name__]
module_name = __file__.split(os.path.sep)[-1][:-3]

################################################################################
#
# OUTPUT STREAMS
#
################################################################################
debug_stream = sys.stderr

def set_debug(level):
	"""Set debug level
	Parameters:
	  level <int> - the new debug level (None or <int>)
	Returns: None or <int> - the old debug level
	"""
	debug(0,f"set_debug(level={level})")
	old = config.debug_level
	config.debug_level = level
	debug(0,f"set_debug(...)",old)
	return old

def get_debug():
	return config.debug_level

def debug(level,*args):
	"""Write debugging output

	Parameters:
		level <int> - debug level of output (also sets indent)
		*args <list> - debug output messages

	Returns: None
	"""
	if ( type(config.debug_level) is int and level <= config.debug_level ):
		print(f"\nDEBUG[TESS/{module_name}]: {' '*level}", 
			end="", 
			file=debug_stream)
		first = True
		for message in args:
			print(message, end="", file=debug_stream)
			if first and len(args) > 1:
				print(" -> ", end="", file=debug_stream)
				first = False
		print("", file=debug_stream,flush=True)

################################################################################
#
# CONNECTION
#
################################################################################
user = None
admin = None
def get_connection():
	debug(0,f"get_connection()")
	global user
	global admin
	result = {"user":user,"admin":admin}
	debug(0,f"get_connection(...)",result)
	return result

def set_connection(local=True):
	"""Connect to the database

	Parameters:
	  local <bool> - specify the local instance (default is True)
	"""
	debug(0,f"set_connection(local={local})")
	global user
	global admin
	old = get_connection()
	if local:
		debug(0,f"connecting to local mysql server")
		user = mysql.connect(**config.local)
		admin = mysql.connect(**config.local_a)
	else:
		debug(0,f"connecting to remote mysql server")
		user = mysql.connect(**config.remote)
		admin = mysql.connect(**config.remote_a)
	debug(0,f"set_connection(...)",old)
	return old

if __name__ == '__main__':
	set_connection(local=True)
else:
	set_connection(local=False)

################################################################################
#
# DATABASE
#
################################################################################
database = None

def add_database(schema=config.schema_name):
	""" Create the database

	This can only be run if the database does not exist already to protect an 
	existing database from accidental damage.
	"""
	debug(1,f"add_database(schema='{schema}')")
	run_query(f"CREATE DATABASE `{schema}` DEFAULT CHARACTER SET utf8mb4 "
		+ "COLLATE utf8mb4_0900_ai_ci",connection=admin)
	run_script("create_schema.sql",connection=admin,schema=schema)
	debug(1,f"add_database(...)",None)

def set_database(schema=config.schema_name):
	global database
	debug(1,f"set_database(schema='{schema}')")
	result = database
	database = schema
	debug(1,f"set_database(...)",result)

def get_database(schema=None):
	global database
	debug(1,f"get_database(schema='{schema}')")
	try:
		if schema == None:
			if database == None:
				database = config.schema_name
			schema = database
		result = get_log(log_id=1)
	except:
		result = None
	debug(1,f"get_database(...) -> {result}")
	return result

def del_database(schema=config.schema_name):
	debug(1,f"del_database(schema='{schema}')")
	result = run_query(f"DROP SCHEMA IF EXISTS `{schema}`;",connection=admin)
	debug(1,f"del_database(...)",result)

def save_database(filename,use_throw=False):
	raise Exception(f"save_database(filename='{filename}',use_throw={use_throw}) not implemented yet")

def load_database(filename,use_throw=False):
	raise Exception(f"load_database(filename='{filename}',use_throw={use_throw}) not implemented yet")

################################################################################
#
# CONFIG
#
################################################################################
def add_config(system_id,name,value):
	debug(1,f"add_config(system_id={system_id},name='{name}',value='{value}')")
	query = make_insert(table="config",data={"system_id":system_id,"name":name,"value":value})
	result = run_query(query,connection=admin)
	config_id = result["last_insert_id"]
	debug(1,f"add_config(...)",config_id)
	return config_id

def get_config(config_id,use_throw=True):
	debug(1,f"get_config(config_id={config_id},use_throw={use_throw})")
	query = make_select(table="config",key="config_id",value=config_id)
	result = run_query(query)
	try:
		data = result["data"][0]
	except:
		if use_throw:
			raise Exception("config not found")
		data = []
	debug(1,f"get_config(...) -> {data}")
	return data

def find_config(system_id,name,use_throw=False):
	debug(1,f"find_config(system_id={system_id},name='{name}',use_throw={use_throw})")
	query = make_select(table="config",key=["system_id","name"],value=[system_id,name])
	result = run_query(query)
	try:
		data = result["data"][0]["config_id"]
	except:
		if use_throw:
			raise Exception("config not found")
		data = None
	debug(1,f"find_config(...)",data)
	return data

def set_config(system_id,name,value,use_throw=True):
	debug(1,f"set_config(system_id={system_id},name='{name}',value='{value}',use_throw={use_throw})")
	query = make_select(table="config",key="name",value=name)
	result = run_query(query)
	if result["rows_affected"] == 0 and use_throw:
		raise f"name='{name}' not found in config"
	result = add_config(system_id=system_id,name=name,value=value)
	debug(1,f"set_config(...)",result)
	return result
	
################################################################################
#
# DEVICE
#
################################################################################
def add_device(user_id,name):
	debug(1,f"add_device(user_id={user_id},name='{name}')")
	query = make_insert(table="device",data={"user_id":user_id,"name":name})
	result = run_query(query,connection=admin)
	device_id = result["last_insert_id"]
	debug(1,f"add_device(...)",device_id)
	return device_id

def get_device(device_id,use_throw=True):
	debug(1,f"get_device(device_id={device_id},use_throw={use_throw})")
	query = make_select(table="device",key="device_id",value=device_id)
	result = run_query(query)
	try:
		data = result["data"][0]
	except:
		if use_throw:
			raise Exception("device not found")
		data = []
	debug(1,f"get_device(...) -> {data}")
	return data

def find_device(unique_id,use_throw=False):
	debug(1,f"find_device(unique_id={unique_id},use_throw={use_throw})")
	query = make_select(table="device",key="unique_id",value=unique_id)
	result = run_query(query)
	try:
		data = result["data"][0]["device_id"]
	except:
		if use_throw:
			raise Exception("device not found")
		data = None
	debug(1,f"find_device(...)",data)
	return data

def set_device(device_id,name,use_throw=True):
	debug(1,f"set_device(device_id={device_id},name='{name}',use_throw={use_throw})")
	data = get_device(device_id,use_throw)
	result = add_device(user_id=data["user_id"],name=name)
	debug(1,f"set_device(...)",result)
	return result

################################################################################
#
# LOG
#
################################################################################
def add_log(message):
	debug(1,f"add_log(message='{message}'")
	query = make_insert(table="log",data={"message",message})
	result = run_query(query)
	debug(1,f"add_log(...)",result)
	return result

def get_log(log_id,use_throw=False):
	debug(1,f"get_log(log_id='{log_id}'")
	query = make_select(table="log",key="log_id",value=log_id)
	try:
		result = run_query(query)["data"][0]["message"]
	except:
		if use_throw:
			raise Exception("log not found")
		result = None
	debug(1,f"get_log(...)",result)
	return result
	
################################################################################
#
# METER
#
################################################################################
def add_meter(device_id,price_id,quantity):
	debug(1,f"add_meter(device_id={device_id},price_id={price_id},quantity={quantity})")
	query = make_insert(table="meter",data={"device_id":device_id,"price_id":price_id,"quantity":quantity})
	result = run_query(query)
	meter_id = result["last_insert_id"]
	debug(1,f"add_meter(...)",meter_id)
	return meter_id

def get_meter(meter_id,use_throw=False):
	debug(1,f"meter_id(meter_id={meter_id},use_throw={use_throw})")
	query = make_select(table="meter",key="meter_id",value=meter_id)
	result = run_query(query)
	try:
		data = result["data"][0]
	except:
		if use_throw:
			raise Exception("meter not found")
		data = None
	debug(1,f"meter_id(...) -> {data}")
	return data
	
def find_meter(device_id,use_throw=False):
	debug(1,f"find_meter(device_id={device_id},use_throw={use_throw})")
	query = make_select(table="meter",key="device_id",value=device_id)
	result = run_query(query)
	try:
		data = result["data"][0]["device_id"]
	except:
		if use_throw:
			raise Exception("meter not found")
		data = None
	debug(1,f"find_meter(...)",data)
	return data

	
def set_meter(**kwargs):
	raise Exception("set_meter() not allowed")

################################################################################
#
# ORDER
#
################################################################################
def add_order(device_id,resource_id,quantity,bid,current=None,duration=None):
	debug(1,f"add_order(device_id={device_id},resource_id={resource_id},quantity={quantity},bid={bid},current={current},duration={duration})")
	query = make_insert(table="order",
		data={"device_id":device_id,"resource_id":resource_id,"quantity":quantity,
			"bid":bid,"current":current,"duration":duration})
	result = run_query(query)
	order_id = result["last_insert_id"]
	debug(1,f"add_order(...)",order_id)
	return order_id

def get_order(order_id,use_throw=False):
	debug(1,f"get_order(order_id={order_id},use_throw={use_throw})")
	query = make_select(table="order",key="order_id",value=order_id)
	try:
		result = run_query(query)["data"][0]
	except:
		if use_throw:
			raise Exception("order not found")
		result = None
	debug(1,f"get_order(...)",result)
	return result
	
def find_order(unique_id,use_throw=False):
	debug(1,f"find_order(unique_id={unique_id},use_throw={use_throw})")
	query = make_select(table="order",key="unique_id",value=unique_id)
	result = run_query(query)
	try:
		order_id = result["data"][0]["order_id"]
	except:
		if use_throw:
			raise Exception("order not found")
		order_id = None
	debug(1,f"find_order(...)",order_id)
	return order_id
	
def set_order(**kwargs):
	debug(1,f"set_order({kwargs})")
	if "use_throw" in kwargs.keys():
		use_throw = kwargs["use_throw"]
	else:
		use_throw = False
	try:
		if not "order_id" in kwargs.keys():
			raise Exception("missing order_id")
		order_id = kwargs["order_id"]
		sets = []
		for key,value in kwargs.items():
			if key in ["price_id","closed"]:
				sets.append(f"`{key}` = '{value}'")
			elif not key in ["use_throw","order_id"]:
				raise Exception(f"key '{key}' is not valid")
		query = f"UPDATE `order` SET {','.join(sets)} WHERE `order_id` = '{order_id}' LIMIT 1"
		if sets == []:
			raise Exception("missing 'field=value' argument")
		result = run_query(query)["rows_affected"]
		assert(result==1)
	except:
		if use_throw:
			raise
		result = None
	debug(1,f"set_order(...)",result)
	return result
	
################################################################################
#
# PREFERENCE
#
################################################################################
def add_preference(user_id,name,value):
	debug(1,f"add_preference(user_id={user_id},name={name},value={value})")
	query = make_insert(table="preference",data={"user_id":user_id,"name":name,"value":value},connection=admin)
	result = run_query(query,connection=admin)
	preference_id = result["last_insert_id"]
	debug(1,f"add_preference(...)",preference_id)
	return preference_id

def get_preference(preference_id,use_throw=False):
	debug(1,f"get_preference(preference_id={preference_id},use_throw={use_throw})")
	query = make_select(table="preference",key="preference_id",value=preference_id)
	try:
		result = run_query(query)["data"][0]
	except:
		if use_throw: 
			raise Exception("preference not found")
		result = None
	debug(1,f"get_price(...)",result)
	return result
	
def find_preference(user_id,name,use_throw=False):
	debug(1,f"find_preference(user_id={user_id},name={name},use_throw={use_throw})")
	query = make_select(table="preference",key=["user_id","name"],value=[user_id,name])
	result = run_query(query)
	try:
		preference_id = result["data"][0]["preference_id"]
	except:
		if use_throw:
			raise Exception("preference not found")
		preference_id = None
	debug(1,f"find_price(...)",preference_id)
	return preference_id
	
def set_preference(**kwargs):
	# TODO: this should do a get(), then an add() with mods
	raise Exception("set_preference() not implemented yet")
	
################################################################################
#
# PRICE
#
################################################################################
def add_price(resource_id,quantity,price,margin=None):
	debug(1,f"add_price(resource_id={resource_id},quantity={quantity},price={price},margin={margin})")
	if margin == None:
		query = make_insert(table="price",data={"resource_id":resource_id,"price":price,"quantity":quantity},connection=admin)
	else:
		query = make_insert(table="price",data={"resource_id":resource_id,"price":price,"quantity":quantity,"margin":margin},connection=admin)
	result = run_query(query,connection=admin)
	price_id = result["last_insert_id"]
	debug(1,f"add_price(...)",price_id)
	return price_id

def get_price(price_id,use_throw=False):
	debug(1,f"get_price(price_id={price_id},use_throw={use_throw})")
	query = make_select(table="price",key="price_id",value=price_id)
	try:
		result = run_query(query)["data"][0]
	except:
		if use_throw:
			raise Exception("price not found")
		result = None
	debug(1,f"get_price(...)",result)
	return result
	
def find_price(resource_id,use_throw=False):
	debug(1,f"find_price(resource_id={resource_id},use_throw={use_throw})")
	query = make_select(table="price",key="resource_id",value=resource_id)
	result = run_query(query)
	try:
		price_id = result["data"][0]["price_id"]
	except:
		if use_throw:
			raise Exception("price not found")
		price_id = None
	debug(1,f"find_price(...)",price_id)
	return price_id
	
def set_price(**kwargs):
	raise Exception("set_price() not allowed")
	
################################################################################
#
# RESOURCE
#
################################################################################
def add_resource(system_id,name,quantity_unit,price_unit):
	debug(1,f"add_resource(name='{name}')")
	query = make_insert(table="resource",data={"system_id":system_id,"name":name,"quantity_unit":quantity_unit,"price_unit":price_unit},connection=admin)
	result = run_query(query,connection=admin)
	system_id = result["last_insert_id"]
	debug(1,f"add_resource(...)",system_id)
	return system_id

def get_resource(resource_id,use_throw=False):
	debug(1,f"get_resource(resource_id={resource_id},use_throw={use_throw})")
	query = make_select(table="resource",key="resource_id",value=resource_id)
	try:
		result = run_query(query)["data"][0]
	except:
		if use_throw:
			raise Exception("resource not found")
	debug(1,f"get_resource(...)",result)
	return result
	
def find_resource(system_id,name,use_throw=False):
	debug(1,f"find_resource(system_id={system_id},use_throw={use_throw})")
	query = make_select(table="resource",key=["system_id","name"],value=[system_id,name])
	result = run_query(query)
	if len(result["data"]) == 1:
		data = result["data"][0]["resource_id"]
	elif use_throw:
		raise Exception("resource not found")
	else:
		data = None
	debug(1,f"find_resource(...)",data)
	return data
	
def set_resource(**kwargs):
	raise Exception("set_resource() not allowed")
	
################################################################################
#
# SETTING
#
################################################################################
def add_setting(device_id,name,value):
	debug(1,f"add_setting(device_id={device_id},name='{name}',value='{value}'')")
	query = make_insert(table="setting",data={"device_id":device_id,"name":name,"value":value})
	result = run_query(query,connection=admin)
	system_id = result["last_insert_id"]
	debug(1,f"add_resource(...)",system_id)
	return system_id

def get_setting(setting_id,use_throw=False):
	debug(1,f"add_setting(setting_id={setting_id},use_throw={use_throw})")
	query = make_select(table="setting",key="setting_id",value=setting_id)
	try:
		result = run_query(query)["data"][0]
	except:
		if use_throw: 
			raise Exception("setting not found")
		result = None
	debug(1,f"add_setting(...)",result)
	return result
	
def find_setting(device_id,name,use_throw=False):
	debug(1,f"find_setting(device_id={device_id},name={name},use_throw={use_throw})")
	query = make_select(table="setting",key=["device_id","name"],value=[device_id,name])
	result = run_query(query)
	try:
		data = result["data"][0]["setting_id"]
	except:
		if use_throw:
			raise Exception("setting not found")
		data = None
	debug(1,f"find_setting(...)",data)
	return data
	
def set_setting(**kwargs):
	raise Exception("set_setting() not implemented yet")
	
################################################################################
#
# SYSTEM
#
################################################################################
def add_system(name):
	debug(1,f"add_system(name='{name}')")
	query = make_insert(table="system",data={"name":name},connection=admin)
	result = run_query(query,connection=admin)
	system_id = result["last_insert_id"]
	debug(1,f"add_system(...)",system_id)
	return system_id

def get_system(system_id,use_throw=False):
	debug(1,f"get_system(system_id={system_id},use_throw={use_throw})")
	query = make_select(table="system",key="system_id",value=system_id)
	try:
		result = run_query(query)["data"][0]
	except:
		if use_throw:
			raise Exception("system not found")
		result = None
	debug(1,f"get_system(...)",result)
	return result

def find_system(name=config.system_name,use_throw=False):
	debug(1,f"find_system(name='{name}')")
	try:
		result = run_query(f"SELECT * FROM `{database}`.`system` WHERE `name` = '{name}' ORDER BY `created` DESC LIMIT 1")
	except:
		if use_throw: 
			raise Exception("system not found")
		result = None
	debug(1,f"find_system(...)",result)
	return result

def set_system(**kwargs):
	raise Exception("set_system() not allowed")

################################################################################
#
# TOKEN
#
################################################################################
def add_token(user_id):
	debug(1,f"add_token(user_id='{user_id}')")
	query = make_insert(table="token",data={"user_id":user_id},connection=admin)
	result = run_query(query,connection=admin)
	token_id = result["last_insert_id"]
	debug(1,f"add_token(...)",token_id)
	return token_id

def get_token(token_id,use_throw=False):
	debug(1,f"get_token(token_id={token_id},use_throw={use_throw})")
	query = make_select(table="token",key=["token_id","is_valid"],value=[token_id,True])
	try:
		result = run_query(query)["data"][0]
	except:
		if use_throw:
			raise Exception("token not found")
		result = None
	debug(1,f"get_token(...)",result)
	return result
	
def find_token(unique_id,use_throw=False):
	debug(1,f"find_token(unique_id={unique_id},use_throw={use_throw})")
	query = make_select(table="token",key=["unique_id","is_valid"],value=[unique_id,True])
	try:
		result = run_query(query)["data"][0]["token_id"]
	except:
		if use_throw:
			raise Exception("token not found")
		result = None
	debug(1,f"find_token(...)",result)
	return result

def set_token(token_id,is_valid):
	debug(1,f"set_token(token_id={token_id},is_valid={is_valid}")
	query = f"UPDATE `token` SET `is_valid` = '{is_valid}' WHERE `token_id` = {token_id} ORDER BY `created` DESC LIMIT 1"
	try:
		result = run_query(query)["rows_affected"]
		assert(result == 1)
	except:
		result = None
	debug(1,f"set_token(...)",result)
	
################################################################################
#
# TRANSACTION
#
################################################################################
def add_transaction(meter_id,amount):
	debug(1,f"add_transaction(meter_id='{meter_id}',amount={amount})")
	last_id = find_transaction(meter_id=meter_id)
	if last_id == None:
		balance = 0.0
	else:
		balance = get_transaction(last_id)["balance"]
	query = make_insert(table="transaction",data={"meter_id":meter_id,"amount":amount,"balance":(float(balance)+float(amount))},connection=admin)
	result = run_query(query,connection=admin)
	transaction_id = result["last_insert_id"]
	debug(1,f"add_transaction(...)",transaction_id)
	return transaction_id

def get_transaction(transaction_id,use_throw=False):
	debug(1,f"get_transaction(transaction_id={transaction_id},use_throw={use_throw})")
	query = make_select(table="transaction",key="transaction_id",value=transaction_id)
	try:
		result = run_query(query)["data"][0]
	except:
		if use_throw:
			raise Exception("transaction not found")
		result = None
	debug(1,f"get_transaction(...)",result)
	return result
	
def find_transaction(meter_id,use_throw=False):
	debug(1,f"find_transaction(meter_id={meter_id},use_throw={use_throw})")
	query = make_select(table="transaction",key="meter_id",value=meter_id)
	try:
		result = run_query(query)["data"][0]["transaction_id"]
	except:
		if use_throw:
			raise Exception("transaction not found")
		result = None
	debug(1,f"find_transaction(...)",result)
	return result

def set_transaction(**kwargs):
	raise Exception("set_transaction() not allowed")
	
################################################################################
#
# USER
#
################################################################################
def add_user(system_id,name,email,password,role="CUSTOMER"):
	debug(1,f"create_user(name='{name}',email='{email}',pwd='{password}')")
	result = run_query(f"INSERT `user` (`system_id`,`name`,`role`,`email`,`sha1pwd`) VALUES ({system_id},'{name}','CUSTOMER','{email}',SHA1('{password}'));",connection=admin)
	user_id = result["last_insert_id"]
	debug(1,f"create_user(...)",user_id)
	return user_id

def get_user(user_id,password=None,use_throw=False):
	debug(1,f"get_user(user_id={user_id},password='{password}')")
	if password is None:
		result = run_query(f"SELECT * FROM `user` WHERE `user_id` = '{user_id}' ORDER BY CREATED DESC LIMIT 1")
	else:
		result = run_query(f"SELECT * FROM `user` WHERE `user_id` = '{user_id}' AND SHA1('{password}') = `sha1pwd` ORDER BY CREATED DESC LIMIT 1")
	try:
		data = result["data"][0]
	except:
		if use_throw:
			raise Exception("user not found")
		data = None
	debug(1,f"get_user(...)",data)
	return data

def find_user(name,use_throw=False):
	debug(1,f"find_user(name='{name}')")
	result = run_query(f"SELECT * FROM `user` WHERE `name` = '{name}' ORDER BY `created` DESC LIMIT 1")
	try:
		user_id = result["data"][0]["user_id"]
	except:
		if use_throw:
			raise Exception("user not found")
		user_id = None
	debug(1,f"find_user(...)",user_id)
	return user_id

def set_user(**kwargs):
	raise Exception("set_user() not allowed")

################################################################################
#
# TIMESERIES
#
################################################################################
def get_timeseries(resource_id,
	items=["quantity","price","margin"],
	starting=datetime.datetime(2000,1,1,0,0,0),
	ending=datetime.datetime(3000,1,1,0,0,0),
	use_throw=False):
	"""Get timeseries data for a resource

	Parameters:
		resource_id <int> - the resource to which the time series refers
		item <list> - the items to retrieve, e.g., ["price", "quantity", "margin"]
		starting <datetime> - the start date/time
		ending <datetime> - the end datetime
	Returns:
		data <dict> - indexed by time as a tuple in order of <item>
	"""
	debug(1,f"get_timeseries(resource_id={resource_id},items={items},starting={starting},ending={ending},use_throw={use_throw})")
	result = run_query(f"SELECT `created`,`quantity`,`price`,`margin` FROM `price` WHERE `resource_id` = {resource_id} AND `created` BETWEEN '{starting}' AND '{ending}' ORDER BY `price_id` ASC,`created` ASC")
	data = result["data"]
	debug(1,f"get_timeseries(...)",data)
	return data

def get_billing(user_id,starting,ending):
	"""Get 
	"""

################################################################################
#
# MYSQL CALLS
#
################################################################################
def run_query(query,connection=user):
	"""Run a MySQL query on a connection

	Parameters:
		query <str> - query string
		connection <pymysql.connections.Connection object> - connection to use, 
			default is `{module_name}.user`
		schema <str> - schema name, default is current database, "" for none

	Returns: <dict> - depends on query type
		INSERT/REPLACE:
		{
			"rows_affected" : <int>,
			"last_insert_id" : <int>
		}
		SELECT:
		{
			"rows_affected" : <int>,
			"header" : <dict>,
			"data" : <list>,
		}
		Otherwise:
		{
			"rows_affected" : <int>,
		}
	"""
	debug(2,f"run_query(query='{query}',connection={connection})")
	connection.begin()
	try:
		result = {}
		query_type = query.split(" ")[0]
		if query_type in ["INSERT","REPLACE"]:
			cursor = connection.cursor()
			result["rows_affected"] = cursor.execute(query)
			cursor.close()
			cursor = connection.cursor()
			if result["rows_affected"] > 0 and cursor.execute("SELECT LAST_INSERT_ID()") == 1:
				result["last_insert_id"] = cursor.fetchone()[0]
			else:
				result["last_insert_id"] = None
			cursor.close()
		elif query_type in ["SELECT"]:
			cursor = connection.cursor()
			result["rows_affected"] = cursor.execute(query)
			if not cursor.description == None:
				result["header"] = {}
				headings = []
				for values in cursor.description:
					result["header"][values[0]] = values[1:]
					headings.append(values[0])
				result["data"] = []
				for row in cursor:
					result["data"].append(dict(zip(headings,row)))
			cursor.close()
		else:
			cursor = connection.cursor()
			result["rows_affected"] = cursor.execute(query)
			cursor.close()
		connection.commit()
		debug(2,f"run_query(...)",result)
		return result
	except:
		connection.rollback()
		raise

def run_script(filename,connection=user,schema=None):
	"""Run a MySQL script

	Parameters:
		filename <str> - name of file containing the script to run
		connection <pymysql.connections.Connection object> - connection to use, 
			default is `{module_name}.user`

	Returns:
		<int> - the total number of rows affected
	"""
	debug(2,f"run_script(filename='{filename}',connection={connection},schema='{schema}')")
	if schema == None:
		schema = database
	if not schema == None:
		connection.select_db(schema)
	rows_affected = 0
	connection.begin()
	try:
		with open(filename,"r") as f:
			script = f.readlines()
			command = ""
			for line in script:
				line = line.strip()
				if len(line) == 0 or line[0] == '#':
					continue
				command += f" {line}"
				if line[-1] == ';':
					cursor = connection.cursor()
					debug(2,f"run_script(...): running query \"{command}\"")
					rows_affected += cursor.execute(command)
					cursor.close()
					command = ""
		connection.commit()
	except:
		connection.rollback()
		raise
	debug(2,f"run_script(...)",rows_affected)
	return rows_affected

def make_insert(table,data,connection=user,schema=None):
	"""Build a MySQL INSERT query"""
	debug(2,f"make_insert(table='{table}',data={data},schema='{schema}')")
	if schema == None:
		schema = database
	if not schema == None:
		connection.select_db(schema)
	columns = []
	values = []
	for key,value in data.items():
		columns.append(f"`{str(key)}`")
		if value == None:
			values.append("NULL")
		else:
			values.append(f"'{str(value)}'")
	columns = ",".join(columns)
	values = ",".join(values)
	query = f"INSERT INTO `{table}` ({columns}) VALUES ({values});"
	debug(2,f"make_insert(...) -> {query}")
	return query

def make_select(table,key,value,connection=user,schema=None):
	"""Build a MySQL SELECT query"""
	debug(2,f"make_select(table={table},key={key},value={value})")
	if schema == None:
		schema = database
	if not schema == None:
		connection.select_db(schema)
	if type(key) is str:
		result = f"SELECT * FROM `{table}` WHERE `{key}` = '{value}' ORDER BY `{table}_id` DESC LIMIT 1"
	else:
		where = []
		for n,v in dict(zip(key,value)).items():
			if v == None:
				v = "NULL"
			else:
				v = f"'{v}'"
			where.append(f"`{n}`={v}")
		result = f"SELECT * FROM `{table}` WHERE {' AND '.join(where)} ORDER BY `{table}_id` DESC LIMIT 1"
	debug(2,f"make_select(...)",result)
	return result

# setup the configured database automatically, if not already done
if not get_database():
	debug(0,f"running first time setup of {config.schema_name} database")
	add_database()
set_database()
debug(0,f"selected database '{database}'")
if not find_system():
	run_script("initialize_database.sql",connection=admin)
	debug(0,f"first time setup of {schema_name} database finished ok")
