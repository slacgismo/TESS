"""TESS Orderbook Implementation

Quantities

	The sign convention of quantities corresponds to power flowing to the
	device, i.e., demand is positive and supply is negative. Note that
	this is the opposite to the power system sign convention, but
	consistent with the transactive double auction sign convention.

Prices

Order Submit

Dispatch Requests

"""

import os, sys, logging
import datetime
import json
import sqlite3
import random
import enum
import re

class DeviceType:
	"""Fevice types"""
	LOAD = "LOAD"
	FEEDER = "FEEDER"
	HVAC = "HVAC"
	HOTWATER = "HOTWATER"
	PV = "PV"
	ES = "ES"
	EV = "EV"

class OrderFlexibility:
	"""Order flexibility options"""
	NONE = ""
	QUANTITY = "Q"
	TIME = "T"
	QUANTITY_TIME = "QT"

class OrderStatus:
	"""Order status"""
	OPEN = "OPEN"
	CLOSED = "CLOSED"

class OrderType:
	"""Order type"""
	SUPPLY = "SELL"
	DEMAND = "BUY"

class DispatchStatus:
	"""Dispatch status"""
	SENT = "SENT"
	DONE = "DONE"
	FAIL = "FAIL"

#
# Exceptions
#

class OrderbookNotImplemented(Exception):
	"""Feature is not implemented exception"""
	pass

class OrderbookAssertFailed(Exception):
	"""Orderbook assert failed"""
	pass

class OrderbookValueError(Exception):
	"""Orderbook value invalid"""

def guid():
	"""Generate a new GUID"""
	return random.randint(0,2**32-1)

class Data:
	"""Abstract class for table data"""

	def __init__(self,**kwargs):
		"""Constructor for table data object
		- kwargs (dict): field names and values
		"""
		self.keys = []
		for key,value in kwargs.items():
			setattr(self,key,value)
			self.keys.append(key)

	def dict(self):
		"""Convert the data to a dict
		Returns: data (dict)
		"""
		result = {}
		for var in self.keys:
			if var[0] != "_":
				result[var] = getattr(self,var)
		return result

	def json(self):
		"""Convert the data to JSON
		Returns: data in JSON format (str)
		"""
		return json.dumps(self.dict())

	def csv(self,with_header=True,float_format=None):
		"""Convert the object data to CSV
		Returns: data in CSV format (str)
		"""
		keys = []
		values = []
		for key,value in self.dict().items():
			keys.append(key)
			if type(value) == int:
				values.append(str(value))
			elif type(value) == float:
				if float_format:
					values.append(float_format%value)
				else:
					values.append(str(value))
			elif type(value) is str:
				values.append(f'"{value}"')
			elif value == None:
				values.append('')
			else:
				raise OrderbookValueError(f"value '{value}' is invalid")
		if with_header:
			return '\n'.join([','.join(keys),','.join(values)])
		else:
			return ','.join(values)

	def isa(self,type):
		return self.__class__ == type


class Agent(Data):
	"""Agent table data"""

	def __init__(self,**kwargs):
		Data.__init__(self,**kwargs)
		self.validate()

	def validate(self):
		return True

class Device(Data):
	"""Device table data"""

	def __init__(self,**kwargs):
		Data.__init__(self,**kwargs)
		self.validate()

	def validate(self):
		return True

class Order(Data):
	"""Order table data"""

	def __init__(self,**kwargs):
		Data.__init__(self,**kwargs)
		self.validate()

	def validate(self):
		assertIn(self.status,[OrderStatus.OPEN,OrderStatus.CLOSED])

class Dispatch(Data):
	"""Dispatch table data"""

	def __init__(self,**kwargs):
		Data.__init__(self,**kwargs)
		self.validate()

	def validate(self):
		return True

#
# Assert utilities
#

def _assertFailed(errmsg,use_exception=True,show_error=True):
	"""Report assert failed
	Note: this should on be called by assert* functions
	"""
	import inspect
	stack = inspect.stack()
	assert(stack[1].function.startswith("assert"))
	file = os.path.basename(stack[2].filename)
	line = stack[2].lineno
	location = f"{file}:{line}"
	logging.error(f'{stack[2].function}@{location},"{errmsg}"')
	if show_error:
		print(f"ERROR [{stack[2].function}@{location}]: {errmsg}",file=sys.stderr)
	if use_exception:
		raise OrderbookAssertFailed(errmsg)

def assertEqual(a,b,use_exception=False,show_error=True):
	"""Verify that a and b are equal"""
	if a != b:
		_assertFailed(f"{a} == {b} failed",use_exception,show_error)
		return False
	return True

def assertIn(a,b,use_exception=False,show_error=True):
	"""Verify that a is in list b"""
	if not a in b:
		_assertFailed(f"{a} in {b} failed",use_exception,show_error)
		return False
	return True

def assertTrue(a,use_exception=False,show_error=True):
	"""Verify that a is true"""
	if not a:
		_assertFailed(f"{a} failed",use_exception,show_error)
		return False
	return True

def assertIsa(a,b,use_exception=False,show_error=True):
	"""Verify that a class is b"""
	if not a.__class__ == b:
		_assertFailed(f"{a.__class__} in {b} failed",use_exception,show_error)
		return False
	return True

def to_sql(value):
	"""Convert a Python value to a SQL value
	- value: Python value
	Returns: SQL value (str)
	Exceptions: 
	"""
	if type(value) in [int,float]:
		return str(value)
	elif type(value) is str:
		return f"'{value}'"
	elif value == None:
		return 'NULL'
	else:
		raise OrderbookValueError(f"{type(value)}({value}) cannot be converted to SQL value")

class Orderbook:
	"""Implementation of orderbook mechanism"""
	tables = {}
	primary_keys = {}
	quantity_unit = "MW"
	price_unit = "$/MW.h"

	def __init__(self, 
			database = ':memory:',
			logfile = None,
			loglevel = logging.INFO
		):
		"""Orderbook constructor
		- database (str): database filename (default ':memory:')
		- logfile (str): logfile name (default None)
		- loglevel (int): log level (see logging DATA)
		"""

		self.sql = sqlite3.connect(database)
		if logfile:
			logging.basicConfig(filename = logfile, 
								encoding = 'utf-8', 
								level = loglevel,
								format = f'%(asctime)s,%(levelname)s,Orderbook.%(funcName)s,%(message)s')
		self.create_table("agents",
			agent_id = 'integer',
			primary_key = 'agent_id')

		self.create_table("devices",
			device_id = 'integer',
			primary_key = 'device_id',
			agent_id = 'integer',
			device_type = 'text')

		self.create_table("orders",
			order_id = 'integer',
			primary_key = 'order_id',
			device_id = 'integer',
			quantity = 'real',
			duration = 'real',
			flexibility = 'text',
			price = 'real',
			status = 'text',
			received_at = 'real')
		self.create_index(table="orders",fields=['price','received_at'])

		self.create_table("dispatch",
			dispatch_id = 'integer',
			primary_key = 'dispatch_id',
			device_id = 'integer',
			quantity = 'real',
			duration = 'real',
			price = 'real',
			status = 'text',
			sent_at = 'real')
		self.create_index(table='dispatch',fields=['device_id','sent_at'])

		self.sql.commit()

	def sql_put(self,sql,no_exception=True):
		"""Write data
		sql (str): SQL query string
		no_exception (bool): suppress exceptions (default True)
		Returns: last row id (int) on success or None if failed
		"""
		if not sql.strip():
			return
		try:
			result = self.sql.execute(sql).lastrowid
			msg = re.sub('[\n\t ]+',' ',sql)
			logging.info(f"\"{msg}\",{result}")
			return result
		except:
			e_type, e_value, e_trace = sys.exc_info()
			msg = re.sub('[\n\t ]+',' ',sql)
			logging.error(f"\"{msg}\",{e_type.__name__}({e_value})")
			if not no_exception:
				raise
			return None

	def sql_get(self,sql,no_exception=True):
		"""Read data
		sql (str): SQL query string
		no_exception (bool): suppress exceptions (default True)
		Returns: result (dict) on success or None if failed
		"""
		try:
			cursor = self.sql.cursor()
			cursor.execute(sql)
			result = [list(x) for x in cursor.fetchall()]
			logging.info(f"\"{sql}\",{len(result)}")
			return result
		except:
			logging.error(f"\"{sql}\",-1")
			if not no_exception:
				raise
			return  None

	def restore(self,name):
		"""Restore data
		- name (str): database filename to read
		Returns: None
		"""
		tic = datetime.datetime.now()
		with sqlite3.connect(name) as db:
			db.backup(self.sql)
		logging.info(f'"{name}",{(datetime.datetime.now()-tic).total_seconds()}')

	def backup(self,name):
		"""Backup data
		- name (str): database filename to write
		Returns: None
		"""
		tic = datetime.datetime.now()
		with sqlite3.connect(name) as db:
			self.sql.backup(db)
		logging.info(f'"{name}",{(datetime.datetime.now()-tic).total_seconds()}')

	def dict(self):
		"""Convert data to dict
		Returns: database (dict)
		"""
		result = {}
		for table in self.tables:
			fields = self.tables[table]
			values = self.sql_get(f"select {', '.join(fields)} from {table}")
			result[table] = {}
			primary_key = self.primary_keys[table]
			for row in values:
				data = dict(zip(fields,row))
				if primary_key:
					key = data[primary_key]
					del data[primary_key]
				else:
					key = len(result[table])
				result[table][key] = data
		return result


	def dump_sql(self,sqlfile,with_create=False,with_index=False):
		"""Dump data to SQL
		- sqlfile (str): filename to write SQL in
		- with_create (bool): include table create statements (default False)
		- with_index (bool): include index create statements (default False)
		Returns: None
		"""
		tic = datetime.datetime.now()
		result = self.dict()
		with open(sqlfile,"w") as fh:
			for table, values in result.items():
				fields = self.tables[table]
				primary_key = self.primary_keys[table]
				if with_create:
					print(self._create_table(table,**fields,primary_key=primary_key),file=fh,end=";\n")
				if with_index:
					print(self._create_index(table,fields),file=fh,end=";\n")
				for key,data in values.items():
					if primary_key:
						data[primary_key] = str(key)
					valuestr = []
					for field,value in data.items():
						valuestr.append(to_sql(value))
					# valuestr ="','".join([str(x) for x in data.values()])
					print(f"insert into {table} ({','.join(data.keys())}) values ({','.join(valuestr)})",file=fh,end=";\n")
		logging.info(f'"{sqlfile}",{(datetime.datetime.now()-tic).total_seconds()}')

	def dump_csv(self,csvroot):
		"""Dump data to CSV
		- csvroot (str): root of CSV filenames (one file per table)
		Returns: None
		"""
		tic = datetime.datetime.now()
		result = self.dict()
		for table, values in result.items():
			with open(csvroot+table+".csv","w") as fh:
				fields = self.tables[table]
				print(",".join(fields),file=fh)
				primary_key = self.primary_keys[table]
				for key,data in values.items():
					row = [str(key)]
					for item in data.values():
						if type(item) in [int,float]:
							row.append(str(item))
						elif type(item) is str:
							row.append(f'"{item}"')
						elif item == None:
							row.append('')
						else:
							raise OrderbookValueError(f"{type(item)}({item}) is not valid")
					print(",".join(row),file=fh)
		logging.info(f'"{csvroot}",{(datetime.datetime.now()-tic).total_seconds()}')

	def dump_json(self,jsonfile,**kwargs):
		"""Dump data to JSON
		- jsonfile (str): JSON filename to write
		- kwargs (dict): JSON dump options
		Returns: None
		"""
		tic = datetime.datetime.now()
		with open(jsonfile,"w") as fh:
			json.dump(self.dict(),fh,**kwargs)
		logging.info(f'"{jsonfile}",{(datetime.datetime.now()-tic).total_seconds()}')

	def run_script(self,sqlfile):
		"""Run an SQL script
		- sqlfile (str): SQL file to read
		Returns: number of SQL statements executed (int)
		"""
		n = 0
		with open(sqlfile,'r') as fh:
			commands = ''.join(fh.readlines()).split(';')
			for query in commands:
				self.sql_put(query)
				n += 1
		logging.info(f"done,{n}")
		return n

	def _create_table(self,name,**kwargs):
		"""Generate the SQL create table string
		- name (str): table name
		- kwargs (dict): table field names and SQL types
		Returns: table create statement (str)
		"""
		if "primary_key" in kwargs.keys() and kwargs["primary_key"]:
			primary_key = kwargs["primary_key"]
			del kwargs["primary_key"]
		else:
			primary_key = None
		self.tables[name] = kwargs
		fields = []
		self.primary_keys[name] = primary_key
		for field in kwargs.items():
			if field[0] == primary_key:
				fields.append(f"{' '.join(field)} primary key")
			else:
				fields.append(' '.join(field))
		return f"create table {name} ({', '.join(fields)})"

	def create_table(self,name,**kwargs):
		"""Create a table
		- name (str): table name 
		- kwargs (dict): table field names and SQL types
		Returns: 0 on success, None on failure
		"""
		return self.sql_put(self._create_table(name,**kwargs))


	def _create_index(self,table,fields,unique=False,exist_ok=False):
		"""Generate a create index string
		- table (str): name of table to create index on
		- fields (list): list of field names (str) to index on
		- unique (bool): flag to indicate that the index must be unique (default False)
		- exist_ok (bool): flag to indicate that an existing index should not cause an error (default False)
		Returns: index create statement (str)
		"""
		labels = [x.replace('_','') for x in fields]
		return f"""create {'unique ' if unique else ''}index {'' if exist_ok else 'if not exists'} i_{table}_{'_'.join(labels)} on {table} ({', '.join(fields)})"""

	def create_index(self,table,fields,unique=False,exist_ok=False):
		"""Create an index
		- table (str): name of table to create index on
		- fields (list): list of field names (str) to index on
		- unique (bool): flag to indicate that the index must be unique (default False)
		- exist_ok (bool): flag to indicate that an existing index should not cause an error (default False)
		Returns: 0 on success, None on failure
		"""
		return self.sql_put(self._create_index(table,fields,unique=False,exist_ok=False))

	#
	# Agents
	#
	def add_agent(self):
		"""Add a new agent
		Returns: agent GUID (int)
		"""
		agent_id = guid()
		as_of = datetime.datetime.now().timestamp()
		self.sql_put(f"""insert into agents
			(agent_id)
			values
			({agent_id})
			""")
		self.sql.commit()
		return agent_id

	def get_agents(self):
		"""Get a list of all agents
		Returns: list (list) of agent GUIDs (int)
		"""
		return self.sql_get(f"select agent_id from agents")

	def get_agent(self,agent_id):
		"""Get an agent
		- agent_id (int): agent GUID
		Returns: agent object (Agent) on success, None on failure
		"""
		fields = list(self.tables["agents"].keys())
		values = self.sql_get(f"select {','.join(fields)} from agents where agent_id={agent_id}")
		result = dict(zip(fields,values[0])) if values else {}
		return Agent(**result) if result else None

	#
	# Devices
	#
	def add_device(self,agent_id,device_type):
		"""Add a new device
		- agent_id (int): agent GUID
		- device_type (DeviceType): type of device
		Returns: device GUID (int)
		"""
		device_id = guid()
		self.sql_put(f"""insert into devices
			(device_id, agent_id, device_type)
			values  
			({device_id},{agent_id},'{device_type}')""")
		self.sql.commit()
		return device_id

	def get_devices(self):
		"""Get a list of devices
		Returns: list (list) of device GUIDs (int)
		"""
		return self.sql_get(f"select device_id from devices")

	def get_device(self,device_id):
		"""Get a device
		- device_id (int): device GUID
		Returns: device object (Device) on success, None on failure
		"""
		fields = list(self.tables["devices"].keys())
		values = self.sql_get(f"select {','.join(fields)} from devices where device_id={device_id}")
		result = dict(zip(fields,values[0])) if values else {}
		return Device(**result) if result else None

	#
	# Orders
	#
	def add_order(self,device_id,quantity,duration,flexibility,price=None):
		"""Add a new order
		- device_id (int): device GUID 
		- quantity (float): the quantity in quantity units 
		- duration (float): the duration in seconds
		- flexibility (OrderFlexibility): the order flexibility dimensions (TIME and/or QUANTITY)
		- price (float): the reservation price 
		Returns: order GUID (int)
		"""
		order_id = guid()
		self.sql_put(f"""insert into orders
			(order_id,device_id,quantity,duration,flexibility,price,received_at)
			values
			({order_id},{device_id},{quantity},{duration},'{flexibility}',{price if price != None else "NULL"},{datetime.datetime.now().timestamp()})
			""")
		self.sql.commit()
		return order_id

	def get_orders(self,status=None,side=None):
		"""Get a list of orders
		- status (OrderStatus): order status (None for all orders)
		- side (OrderType): orderbook side (None for all orders)
		Returns: list (list) of order GUIDs (int) 
		"""
		if side == OrderType.SUPPLY:
			return self.sql_get(f"select order_id from orders where quantity < 0 and status == '{OrderStatus.OPEN}'")
		elif side == OrderType.DEMAND:
			return self.sql_get(f"select order_id from orders where quantity > 0 and status == '{OrderStatus.OPEN}'")
		elif status == None:
			return self.sql_get("select order_id from orders")
		else:
			return self.sql_get(f"select order_id from orders where status=='{status}'")

	def get_order(self,order_id):
		"""Get an order
		- order_id (int) order GUID
		Returns: order object (Order) on success, None on failure
		"""
		fields = list(self.tables["orders"].keys())
		values = self.sql_get(f"select {','.join(fields)} from orders where order_id={order_id}")
		result = dict(zip(fields,values[0])) if values else {}
		return Order(**result) if result else None

	def set_order(self,order_id,**kwargs):
		updates = []
		for field,value in kwargs.items():
			updates.append(f"{field}={to_sql(value)}")
		result = self.sql_put(f"update orders set {','.join(updates)} where order_id = {order_id}")
		self.sql.commit()

	#
	# Dispatch
	#
	def add_dispatch(self,device_id,quantity,duration,price):
		dispatch_id = guid()
		self.sql_put(f"""insert into dispatch
			(dispatch_id,device_id,quantity,duration,price,status,sent_at)
			values
			({dispatch_id},{device_id},{quantity},{duration},{price},"{DispatchStatus.SENT}",{datetime.datetime.now().timestamp()})
			""")
		return dispatch_id

	def get_dispatch(self,dispatch_id):
		fields = list(self.tables["dispatch"].keys())
		values = self.sql_get(f"select {','.join(fields)} from dispatch where dispatch_id = {dispatch_id}")
		result = dict(zip(fields,values[0])) if values else {}
		return Dispatch(**result) if result else None

	#
	# Operations
	#
	def submit(self,device_id,quantity,duration,flexibility,price=None):
		"""Submit an order:
		- device_id (int): device making the request
		- quantity (float): quantity requested, negative supply, positive demand
		- duration (float): duration requested in seconds
		- flexibility (OrderFlexibility): quantity and/or time flexibility
		- price (float): price of limit order, None for market orders
		Returns: Dispatch (Dispatch), or order (Order), or None if no match
		"""
		match = self.match(quantity,duration,price)
		if match: # found a matching order --> dispatch
			# TODO: calculate correct dispatch
			logging.warning("dispatch calculations incomplete")
			self.add_dispatch(match.device_id,match.quantity,match.duration,match.price)
			dispatch_id = self.add_dispatch(device_id,quantity,duration,match.price)
			dispatch = self.get_dispatch(dispatch_id)
			return Dispatch(**dispatch.dict())
		elif price: # no match, price --> limit order
			order_id = self.add_order(device_id,quantity,duration,flexibility,price)
			self.set_order(order_id,status=OrderStatus.OPEN)
			order = self.get_order(order_id).dict()
			logging.info(f"\"limit order for device {device_id} for {'flexible ' if OrderFlexibility.QUANTITY in flexibility else ''}quantity {quantity} at {price} over {'flexible ' if OrderFlexibility.TIME in flexibility else ''}{duration} sec accepted\"")
			return Order(**order)
		else:
			logging.info(f"\"market order for device {device_id} for {'flexible ' if OrderFlexibility.QUANTITY in flexibility else ''}quantity {quantity} at {price} over {'flexible ' if OrderFlexibility.TIME in flexibility else ''}{duration} sec rejected\"")
			return None # market order with no match

	def match(self,quantity,duration,price):
		"""Find a match to an order
		"""
		if quantity < 0:
			orders = self.get_orders(side=OrderType.SUPPLY)
		elif quantity > 0:
			orders = self.get_orders(side=OrderType.DEMAND)
		else:
			return None
		if orders:
			return self.get_order(orders[0][0])
		return None

	def dispatch(self,device_id,quantity,duration,price):
		"""Dispatch a device to a quantity
		"""
		logging.warning("dispatch signal not implemented")
		dispatch_id = self.add_dispatch(device_id,quantity,duration,price)
		return self.get_dispatch(dispatch_id)

	def supply_book(self,):
		"""Return supply side of orderbook"""
		return []

	def demand_book(self,):
		"""Return demand side of orderbook"""
		return []

if __name__ == "__main__":

	logfile = 'unittest.log'
	if os.path.exists(logfile):
		os.remove(logfile)

	book = Orderbook(logfile=logfile)

	# test add agents
	book.add_agent()
	agent_id = book.add_agent()
	agents = book.get_agents()
	assertEqual(len(agents),2)

	# test get agent
	assertEqual(book.get_agent(agent_id).agent_id,agent_id)

	# test add devices
	hvac_id = book.add_device(agent_id,DeviceType.HVAC)
	pv_id = book.add_device(agent_id,DeviceType.PV)

	# test get devices
	devices = book.get_devices()
	assertEqual(len(devices),2)
	device = book.get_device(pv_id)
	assertEqual(device.device_id,pv_id)

	# test submit sell order
	result = book.submit(
		device_id = pv_id,
		quantity =-10.0,
		duration = 1.0,
		price = 5.0,
		flexibility = OrderFlexibility.QUANTITY_TIME
		)
	assertTrue(result.isa(Order))
	assertEqual(result.device_id,pv_id)
	assertEqual(result.quantity,-10.0)
	assertEqual(result.duration,1.0)
	assertEqual(result.price,5.0)
	assertEqual(result.flexibility,OrderFlexibility.QUANTITY_TIME)
	assertEqual(result.status,OrderStatus.OPEN)

	result = book.submit(
		device_id = pv_id,
		quantity = -10.0,
		duration = 1.0,
		price = 5.0,
		flexibility = OrderFlexibility.QUANTITY_TIME
		)
	assertIsa(result,Dispatch)
	assertEqual(result.quantity,-10.0)
	assertEqual(result.duration,1.0)
	assertEqual(result.price,5.0)

	# test add buy order
	result = book.submit(
		device_id=hvac_id,
		quantity = 5.0,
		duration = 0.1,
		flexibility = OrderFlexibility.QUANTITY
		)
	assertEqual(result,None)
	
	# test back and restore
	book.backup('unittest.db')
	book.restore('unittest.db')
	assertEqual(len(agents),2)
	assertEqual(book.get_agent(agent_id).agent_id,agent_id)
	assertEqual(len(book.get_devices()),2)
	assertEqual(book.get_device(pv_id).device_id,pv_id)

	book.dump_json('unittest.json',indent=4)
	book.dump_csv('unittest_')
	book.dump_sql('unittest.sql',with_create=True,with_index=True)
