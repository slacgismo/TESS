"""TESS Version Database

The database structure is stored in the schema file (by default tess2db.schema).

Standard operations are implemented for each table as described in the schema.

The TESS database maintains a time-series record of the state of the TESS
system such that the analysis can consider the values in effect at any
particular moment in time. The `set_clock` method is used to change the effective
time of 
"""
import os, sys
import datetime
import re
import logging
import json
import sqlite3
import uuid
import time

logfile = None
loglevel = logging.INFO
modname = os.path.splitext(os.path.basename(__file__))[0]

def timestamp():
	"""Return the current timestamp in seconds of epoch"""
	return datetime.datetime.now().timestamp()

class Tess2DbException(Exception):
	pass

class Tess2Db:
	"""TESS2 database implementation
	Arguments:
		database (str) - database name (default ':memory:')
		schema (str) - schema name (default 'tess2db.schema')
		logfile (str or None) - file in which to log output (default stderr)
		loglevel (logging.LEVEL) - log level (default logging.ERROR)
		new (bool) - destroy existing database (default False)
	"""

	schema = None

	def __init__(self,
				 database = ':memory:',
				 schema = "tess2db.schema",
				 logfile = "/dev/stderr",
				 loglevel = logging.ERROR,
				 new = False
				):
		"""Construct a TESS2 database"""
		logging.basicConfig(filename = logfile, 
							encoding = 'utf-8', 
							level = loglevel,
							format = f'%(asctime)s,%(levelname)s,{modname}.{__class__.__name__}.%(funcName)s,%(message)s')
		with open(schema,"r") as fh:
			self.schema = json.load(fh)
		self._connect(database)
		list(map(self._table,self.schema))
		list(map(self._index,self.schema))
		list(map(self._constraints,self.schema))
		for table, specs in self.schema.items():
			for operation in specs["operations"]:
				if not hasattr(self,operation):
					raise Tess2DbException(f"table '{table}' operation '{operation}' not found")
		self.clock = None


	@staticmethod
	def _sql(value):
		"""Convert a Python value to a SQL value

		Arguments:
			value (int, float, str, bool, or None) -  Python value
		
		Returns: 
			(str) SQL value
		
		Exceptions:
			Tess2DbException - unable to convert data type to SQL value
		"""
		if type(value) in [int,float]:
			return str(value)
		elif type(value) is bool:
			return 1 if value else 0
		elif type(value) is str:
			return f"'{value}'"
		elif value == None:
			return 'NULL'
		else:
			raise Tess2DbException(f"{type(value)}({value}) cannot be converted to SQL value")

	def _connect(self,database):
		"""Connect to a database

		Arguments:
			database (str) - database name"""
		self.sql = sqlite3.connect(database)
		logging.info(f"connected to {database}")

	def _create_table(self,name,exist_ok=False):
		"""Generate the SQL create table string
		
		Arguments:
			name (str) -  table name
		
		Returns: 
			(str) table create statement
		"""
		specs = self.schema[name]
		for key in ["fields","index","unique","operations"]:
			if not key in specs.keys():
				raise Tess2DbException(f"table '{name}' missing '{key}' specifications")
		fields= [' '.join(x) for x in specs["fields"].items()]
		return f"""create table {'if not exists' if exist_ok else ''} {name} ({', '.join(fields)})"""

	def _table(self,name,new=False,exist_ok=True):
		"""Create a table in the schema

		Arguments:
			name (str) - table name
			new (bool) - drop existing table (default False)
			exist_ok (bool) - ignore command if table exists (default True)
		"""
		specs = self.schema[name]
		if new:
			self._execute(f"drop table if exists {name}")
		self._execute(self._create_table(name,exist_ok=exist_ok))

	def _create_index(self,table,fields,unique=False,exist_ok=False):
		"""Generate a create index string

		Arguments:
			table (str) - name of table to create index on
			fields (list) - list of field names (str) to index on
			unique (bool) - flag to indicate that the index must be unique (default False)
			exist_ok (bool) - flag to indicate that an existing index should not cause an error (default False)
		
		Returns: 
			(str) index create statement
		"""
		labels = [x.replace('_','') for x in fields]
		return f"""create {'unique index' if unique else 'index'} {'' if exist_ok else 'if not exists'} {'u' if unique else 'i'}_{table}_{'_'.join(labels)} on {table} ({', '.join(fields)})"""

	def _index(self,name,new=False,exist_ok=True):
		"""Create an index in the schema

		Arguments:
			name (str) - table name
			new (bool) - drop the old index (default False)
			exist_ok - only create if table doesn't exist (default True)
		"""
		specs = self.schema[name]
		if new:
			self._execute(f"drop index {'if exists' if exist_ok else ''} {name}")
		try:
			index = specs["index"]
		except:
			index = []
		for fields in index:
			self._execute(self._create_index(name,fields,exist_ok=exist_ok,unique=False))
		try:
			index = specs["unique"]
		except:
			index = []
		for fields in index:
			self._execute(self._create_index(name,fields,exist_ok=exist_ok,unique=True))
	
	def _constraints(self,name):
		"""Create constraints (not supported by sqlite3)"""
		specs = self.schema[name]
		try:
			constraints = specs["constraints"]
		except:
			constraints = []
		if constraints:
			raise Tess2DbException("constraints are not supported")
		# # too bad; sqlite does not support alter table ... add constraint
		# for constraint in constraints:
		# 	field = constraint[0]
		# 	foreign_key = constraint[1]
		# 	self._execute(f"alter table {name} add constraint fk_{field.replace('_','')} foreign key {field} references {foreign_key}")

	def _execute(self,query):
		"""Execute a SQL command
		
		Arguments:
			query (str) - SQL command

		Returns:
			(cursor) select result
			(int) insert rowid
			(int) rows affected
		Exception:
			sqlite3.IntegrityError
		"""
		try:
			if query.startswith("select"):
				cursor = self.sql.cursor()
				result = cursor.execute(query)
				logging.info(f"\"{query}\",")
			elif query.startswith("insert"):
				result = self.sql.execute(query).lastrowid
				logging.info(f"\"{query}\",{result}")
			else:
				result = self.sql.execute(query).rowcount
				logging.info(f"\"{query}\",{result} found")
			return result
		except:
			e_type, e_value, e_trace = sys.exc_info()
			logging.error(f"\"{query}\",{e_type.__name__} {e_value}")
			raise

	def _select(self,query):
		"""Execute a SQL select command

		Arguments:
			query (str) - SQL query string

		Returns:
			(list of dict) Rows of tagged data
		"""
		result = self.sql.execute(query)
		fields = [x[0] for x in result.description]
		result = [dict(zip(fields,list(x))) for x in result.fetchall()]
		logging.info(f"\"{query}\",{len(result)} found")
		return result

	def _insert(self,table,**kwargs):
		"""Execute a SQL insert command

		Arguments:
			table (str) - table name
			kwargs - field values

		Returns:
			(int) 1 on success, 0 on failure
		
		Exceptions:
			sqlite3.IntegrityError

		"""
		fields = []
		values = []
		for key,value in kwargs.items():
			fields.append(key)
			values.append(self._sql(value))
		return self._execute(f"insert into {table} ({', '.join(fields)}) values ({', '.join(values)})")

	def _update(self,table,where="",**kwargs):
		"""Execute a SQL update command

		Arguments:
			table (str) - table name
			where (str) - where clause
			kwargs - field values

		Returns:
			(int) count of rows affected

		Exceptions:
			sqlite3.IntegrityError
		"""
		updates = ", ".join([f"{x}={self._sql(kwargs[x])}" for x in kwargs.keys()])
		return self._execute(f"update {table} set {updates} where {where if where else ''}")

	def _dict(self):
		"""Convert data to dict
		
		Returns: 
			(dict) list of row data keyed by table
		"""
		result = {}
		for table in self.schema.keys():
			result[table] = self._select(f"select * from {table}")
		return result

	#
	# Utilities
	#

	def set_clock(self,as_of):
		"""Set the clock as of which queries a executed

		Arguments:
			as_of (real) - the new clock (None to clear it)

		Returns:
			(real) the old clock
		"""
		old = self.clock
		self.clock = as_of
		logging.info(f"set_clock,{as_of}")
		return old

	def get_clock(self):
		"""Get the clock as of which queries are executed

		Returns:
			(real) the current clock 
		"""
		return self.clock if self.clock else timestamp()

	def begin(self):
		"""Start a transaction"""
		self.sql.begin()

	def commit(self):
		"""End a transaction"""
		self.sql.commit()

	def rollback(self):
		"""Rollback a transaction"""
		self.sql.rollback()

	def delete_all(self,tables=[]):
		"""Delete all records from tables
		
		Arguments:
			tables (list) - list of tables to clear (default all tables in schema)
		"""
		for table in tables if tables else self.schema.keys():
			self._execute(f"delete from {table}")

	def restore(self,name):
		"""Restore data

		Arguments:
			name (str) - database filename to read
		"""
		tic = datetime.datetime.now()
		with sqlite3.connect(name) as db:
			db.backup(self.sql)
		logging.info(f'"{name}",{(datetime.datetime.now()-tic).total_seconds()}')

	def backup(self,name):
		"""Backup data

		Arguments:
			name (str) - database filename to write
		"""
		tic = datetime.datetime.now()
		with sqlite3.connect(name) as db:
			self.sql.backup(db)
		logging.info(f'"{name}",{(datetime.datetime.now()-tic).total_seconds()}')

	def dump_sql(self,sqlfile,with_create=False,with_index=False):
		"""Dump data to SQL

		Arguments:
			sqlfile (str) - filename to write SQL in
			with_create (bool) - include table create statements (default False)
			with_index (bool) - include index create statements (default False)
		"""
		tic = datetime.datetime.now()
		result = self._dict()
		with open(sqlfile,"w") as fh:
			for table, values in result.items():
				if with_create:
					fields = self.schema[table]['fields']
					print(self._create_table(table,fields),file=fh,end=";\n")
				if with_index:
					for fields in self.schema[table]['index']:
						print(self._create_index(table,fields,unique=False),file=fh,end=";\n")
					for fields in self.schema[table]['unique']:
						print(self._create_index(table,fields,unique=True),file=fh,end=";\n")
				for data in values:
					valuestr = []
					for field,value in data.items():
						valuestr.append(self._sql(value))
					print(f"insert into {table} ({','.join(data.keys())}) values ({','.join(valuestr)})",file=fh,end=";\n")
		logging.info(f'"{sqlfile}",{(datetime.datetime.now()-tic).total_seconds()}')

	def dump_csv(self,csvroot):
		"""Dump data to CSV

		Arguments:
			csvroot (str) - root of CSV filenames (one file per table)
		"""
		tic = datetime.datetime.now()
		result = self._dict()
		for table, values in result.items():
			with open(csvroot+table.lower()+".csv","w") as fh:
				fields = self.schema[table]["fields"]
				if values:
					assert(list(fields)==list(values[0].keys()))
				print("rowid,"+(",".join(fields)),file=fh)
				for rowid,data in enumerate(values):
					row = [str(rowid)]
					for item in data.values():
						if type(item) in [int,float]:
							row.append(str(item))
						elif type(item) is str:
							row.append(f'"{item}"')
						elif type(item) == bool:
							row.append(1 if item else 0)
						elif item == None:
							row.append('')
						else:
							raise OrderbookValueError(f"{type(item)}({item}) is not valid")
					print(",".join(row),file=fh)
		logging.info(f'"{csvroot}",{(datetime.datetime.now()-tic).total_seconds()}')

	def dump_json(self,jsonfile,**kwargs):
		"""Dump data to JSON

		Arguments:
			jsonfile (str) - JSON filename to write
			kwargs (dict) - JSON dump options
		"""
		tic = datetime.datetime.now()
		with open(jsonfile,"w") as fh:
			json.dump(self._dict(),fh,**kwargs)
		logging.info(f'"{jsonfile}",{(datetime.datetime.now()-tic).total_seconds()}')

	def run_script(self,sqlfile):
		"""Run an SQL script
		- sqlfile (str): SQL file to read
		Returns: number of SQL statements executed (int)
		"""
		tic = datetime.datetime.now()
		with open(sqlfile,"r") as fh:
			script = "\n".join(fh.readlines())
			result = self.sql.executescript(script)
			logging.info(f'"{sqlfile}",{(datetime.datetime.now()-tic).total_seconds()}')
			return result
		return None

	#
	# Users
	#
	def add_user(self,valid_at=timestamp,**kwargs):
		"""Add a user to the database

		Arguments:
			lastname (str) - user lastname
			firstname (str) - user firstname
			email (str) - user email
			phone (str) - user phone

		Returns:
			str - user_id
		"""
		user_id = uuid.uuid4().hex
		if "email" in kwargs.keys() and self.get_user_email(kwargs['email']) != None:
			raise Tess2DbException(f"email '{kwargs['email']}' already in use")
		if "phone" in kwargs.keys() and self.get_user_phone(kwargs['phone']) != None:
			raise Tess2DbException(f"phone '{kwargs['phone']}' already in use")
		self._insert("users",valid_at=valid_at(),user_id=user_id,**kwargs)
		return user_id

	def get_user(self,user_id):
		"""Get user data

		Arguments:
			user_id (str) - the user id
			as_of (real) - 

		Returns:
			dict - user data
		"""
		result = self._select(f"select * from users where user_id = '{user_id}' and valid_at <= {self.get_clock()} order by valid_at desc limit 1")
		return result[0] if result else None

	def get_user_email(self,email):
		"""Get user id from email

		Arguments:
			email (str) - user email address

		Returns:
			(str) - user id that matches
			None - no match
		"""
		result = self._select(f"select user_id from users where email = '{email}' and valid_at <= {self.get_clock()} order by valid_at desc limit 1")
		return result[0]['user_id'] if result else None

	def get_user_phone(self,phone):
		"""Get user id from phone

		Arguments:
			phone (str) - user phone number

		Returns:
			 (str) - user_id that matches
			 None - no match
		"""
		result = self._select(f"select user_id from users where phone = '{phone}' and valid_at <= {self.get_clock()} order by valid_at desc limit 1")
		return result[0]['user_id'] if result else None
		
	def set_user(self,user_id,**kwargs):
		"""Set user data

		Arguments:
			user_id (str) - user id
			lastname (str) - last name
			firstname (str) - first name
			email (str) - email address
			phone (str) - phone number

		Returns:
			(int) - Row id
		"""
		if self.clock:
			raise Tess2DbException("unable to use set functions while clock is set")
		values = self.get_user(user_id)
		values["valid_at"] = max(timestamp(),values["valid_at"]+0.000001)
		for key,value in kwargs.items():
			values[key] = value
		return self._insert("users",**values)

	def get_users(self):
		"""Get all users

		Returns:
			list - list of user ids
		"""
		return [x['user_id'] for x in self._select(f"select distinct user_id from users where valid_at <= {self.get_clock()} ")]

	def get_users_lastname(self,lastname):
		"""Get user ids from last name

		Arguments:
			lastname (str) - user last name

		Returns:
			(list) - list of matching user_ids
		"""
		found = self._select(f"select user_id from users where lastname = '{lastname}' and valid_at <= {self.get_clock()} ")
		return [values["user_id"] for values in found if self.get_user(values["user_id"])["lastname"] == lastname]
		
	#
	# Agent
	#
	def add_agent(self,**kwargs):
		"""Add a user to the database

		Arguments:
			user_id (str) - user id associated with this agent

		Returns:
			str - user_id
		"""
		agent_id = uuid.uuid4().hex
		self._insert("agents",valid_at=timestamp(),agent_id=agent_id,**kwargs)
		return agent_id

	def get_agent(self,agent_id):
		"""Get agent data

		Arguments:
			agent_id (str) - the agent id

		Returns:
			dict - agent data
		"""
		result = self._select(f"select * from agents where agent_id = '{agent_id}' and valid_at <= {self.get_clock()} order by valid_at desc limit 1")
		return result[0] if result else None

	def set_agent(self,agent_id,**kwargs):
		"""Set agent data

		Arguments:
			agent_id (str) - agent id
			user_id (str) - user id

		Returns:
			(int) rows affected, i.e., 1 on success, 0 on error
		"""
		if self.clock:
			raise Tess2DbException("unable to use set functions while clock is set")
		values = self.get_agent(agent_id)
		values["valid_at"] = max(timestamp(),values["valid_at"]+0.000001)
		for key,value in kwargs.items():
			values[key] = value
		return self._insert("users",**values)

	def get_agents(self):
		"""Get all agents

		Returns:
			list - list of agent ids
		"""
		return [x['agent_id'] for x in self._select("select distinct agent_id from agents where valid_at <= {self.get_clock()} ")]

	def get_agents_userid(self,user_id):
		"""Get agents for user_id

		Arguments:
			user_id (str) - user id

		Returns:
			(list) - list of matching agent_ids
		"""
		found = self._select(f"select agent_id from agents where user_id = '{user_id}' and valid_at <= {self.get_clock()} ")
		return [values["agent_id"] for values in found if self.get_agent(values["agent_id"])["user_id"] == user_id]
		
if __name__ == '__main__':

	test = Tess2Db(loglevel=logging.INFO)
	
	#
	# Test users
	#
	user1 = test.add_user(lastname="Test1",firstname="Name1",email="name1@test.com",phone="phone1")
	users = test.get_users()
	assert(users == [user1])
	try: # this should fail duplicate email/phone checks
		test.add_user(lastname="Test1",firstname="Name1",email="name1@test.com",phone="phone1") 
		assert(False) # should not get here
	except Tess2DbException:
		pass # should get here instead
	users = test.get_users()
	assert(users == [user1])

	rewind = timestamp()
	
	user2 = test.add_user(lastname="Test2",firstname="Name2",email="name2@test.com",phone="phone2")
	users = test.get_users()
	assert(user2 in users)
	assert(test.get_user(user2)['user_id'] == user2)

	test.set_user(user2,lastname="Test2a")
	assert(test.get_user(user2)['lastname'] == "Test2a")

	user3 = test.add_user(lastname="Test2",firstname="Name1a",email="name1a@test.com",phone="phone1a")
	assert(test.get_users_lastname("Test2") == [user3])
	assert(test.get_user_email("name1a@test.com") == user3)
	assert(test.get_user_phone("phone1a") == user3)

	test.commit()

	#
	# Test agents
	#
	agent1 = test.add_agent(user_id=user1)
	agent = test.get_agent(agent1)
	assert(agent["agent_id"] == agent1)
	assert(agent["user_id"] == user1)
	assert(test.get_agents_userid(user1) == [agent1])

	test.commit()

	#
	# Test utilities
	#
	test.backup('unittest.db')

	test.dump_json('unittest.json',indent=4)
	test.dump_csv('unittest_')
	test.dump_sql('unittest.sql',with_create=True,with_index=True)

	# test.delete_all(test.schema.keys())
	# test.restore('unittest.db')
	# assert(test.get_user(user_id)['lastname'] == "Test2a")

	try:
		test.run_script('unittest.sql')
	except sqlite3.IntegrityError:
		pass

	test.delete_all(test.schema.keys())
	test.run_script('unittest.sql')
	assert(test.get_user(user2)['lastname'] == "Test2a")

	#
	# Test clock
	#
	test.set_clock(rewind)
	users = test.get_users()
	assert(users == [user1])

	try:
		test.set_user(user1,lastname="Denied") # this should fail because the clock is set
		assert(False) 
	except Tess2DbException:
		pass

	test.set_clock(None)
	users = test.get_users()
	assert(sorted(users) == sorted([user1,user2,user3]))



