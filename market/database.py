"""TESS Database

Table data may be accessed using the `get_*()` methods.  These may include the
indexes available in the table, as well as a `where` list for each condition
used.  For example:

  get_system(where = ["name","HCE"])

return the entry for the system whose name matches "HCE".
"""
import sys, os;
import pymysql as my;
import config;
import json;

debug_level = [0,9];

module = sys.modules[__name__];
module_name = __file__.split(os.path.sep)[-1][:-3];

def debug(level,*args):
	if ( debug_level[0] <= level and level <= debug_level[-1] ):
		print(f"\nDEBUG(tess/{module_name}):{' '*level}", end="");
		for message in args:
			if type(message) is str:
				print(message, end="");
			else:
				print(json.dumps(message,indent=4), end="");
		print("");

class Tess :

	def __init__(self,schema):
		debug(1,f"connect={config.mysql}");
		self.db = my.connect(**config.mysql);
		self.db.select_db(schema);

	def __delete__(self):
		close(self.db);

	def select(self,
			   table,
			   join = "JOIN",
			   fields = ["*"],
			   where = None,
			   order = None,
			   limit = None):
		"""Select fields from a table with certain conditions
		Parameters:
			table 	(string) specifies the table table name, e.g., "system" 
					or "system join resources using (system_id)"
			fields 	(string or list of strings) specifies the table columns,
					default is "*"
			where 	(string or list of strings/tuples) specifies the where 
					clauses, default is none, list is "AND"
		"""
		debug(2,f"select(table={table},fields={fields},where={where},order={order},limit={limit})");
		select = self.db.cursor();
		if type(table) is list:
			table = f" {join} ".join(table);
		def mkfields(fields):
			debug(4,f"mkfields(fields='{fields}')");
			if fields == '*' or fields == ['*']:
				result = '*';
			else:
				result = f"`{'`,`'.join(fields)}`";
			debug(4,f"mkfields(fields='{fields}') -> ",result);
			return result;
		query = f"SELECT {mkfields(fields)} FROM `{table}`";
		if type(where) is list and len(where) > 0:
			def mkwhere(clause):
				debug(4,f"mkwhere(clause={clause})");
				result = None;
				if type(clause) is str:
					result = clause;
				elif type(clause) is list and len(clause) > 0:
					if len(clause) == 1: # NOT ISNULL(`&1`)
						result = "NOT ISNULL(`%s`)" % (clause[0]);
					elif len(clause) == 2: # `&1` = '&2'
						if clause[1] is None: # ISNULL(`&1`) 
							result = "ISNULL(%s)" % (clause[0]);
						else:
							result = "`%s` = '%s'" % (clause[0],clause[1]);
					elif len(clause) == 3: # `&1`&2'&1'
						result = "`%s`%s'%s'" % (clause[0],clause[1],clause[2]);
					elif len(clause) > 3: # &1 &2 &3 &4 ...
						result = " ".join(clause);
				if result == None:
					raise Exception(f"clause '{clause}' is not valid");
				debug(4,f"mkwhere(clause={clause}) -> ",result);
				return result;
			if type(where[0]) is list:
				clauses = [];
				for clause in where:
					clauses.append(mkwhere(clause));
				where = " AND ".join(clauses);
			else:
				where = mkwhere(where);
		if type(where) is str:
			query += f" WHERE {where}";
		if type(order) is str:
			if order[0] == '-':
				query += f" ORDER BY `{order[1:]}` DESC";
			else:
				query += f" ORDER BY `{order}` ASC";
		if not limit is None:
			query += f" LIMIT {limit}";
		debug(3,f"query -> {query}");
		select.execute(query);
		result = [];
		if fields == ["*"]:
			fields = list(map(lambda x:x[0],select.description));
		debug(3,f"fields -> ",fields);
		for row in select:
			debug(3,f"row -> {row}");
			if len(row) == 1:
				result.extend(row);
			else:
				result.append(dict(zip(fields,row)));
		select.close();
		debug(2,f"select(table={table},fields={fields},where={where},order={order},limit={limit}) -> ",result);
		if len(result) == 1:
			return result[0];
		else:
			return result;

	def get_config(self,
				   config_id = None,
				   system_id = None,
				   where=[],
				   limit = None):
		debug(1,f"get_config(config_id={config_id},system_id={system_id},limit={limit})");
		if not config_id is None: where.append(["config_id","=",config_id]);
		if not system_id is None: where.append(["system_id","=",system_id]);
		result = self.select(table="config",where=where,order="-created",limit=limit);
		debug(1,f"get_config(config_id={config_id},system_id={system_id},limit={limit}) -> {result}");
		return result;

	def get_device(self,
				   device_id = None,
				   user_id = None,
				   unique_id = None,
				   where = [],
				   limit = None):
		debug(1,f"get_device(device_id={device_id},user_id={user_id},unique_id={unique_id},where={where},limit={limit})");
		if not device_id is None: where.append(["device_id","=",device_id]);
		if not user_id is None: where.append(["user_id","=",user_id]);
		if not unique_id is None: where.append(["unique_id","=",unique_id]);
		result = self.select(table = "device",where = where,limit=limit);
		debug(1,f"get_device(device_id={device_id},user_id={user_id},unique_id={unique_id},where={where},limit={limit}) -> {result}");
		return result;

	def get_meter(self,
				  meter_id = None,
				  device_id = None,
				  price_id = None,
				  where = [],
				  limit = None):
		debug(1,f"get_meter(meter_id={meter_id},device_id={device_id},price_id={price_id},where={where},limit={limit})");
		if not meter_id is None: where.append(["meter_id","=",meter_id]);
		if not device_id is None: where.append(["device_id","=",device_id]);
		if not price_id is None: where.append(["price_id","=",price_id]);
		result = self.select(table = "meter",where = where,limit=limit);
		debug(1,f"get_meter(meter_id={meter_id},device_id={device_id},price_id={price_id},where={where},limit={limit}) -> {result}");
		return result;

	def get_order(self,
				  order_id = None,
				  device_id = None,
				  resource_id = None,
				  unique_id = None,
				  where = [],
				  limit = None):
		debug(1,f"get_order(order_id={order_id},device_id={device_id},resource_id={resource_id},unique_id={unique_id},where={where},limit={limit})");
		if not order_id is None: where.append(["order_id","=",order_id]);
		if not device_id is None: where.append(["device_id","=",device_id]);
		if not resource_id is None: where.append(["resource_id","=",resource_id]);
		if not unique_id is None: where.append(["unique_id","=",unique_id]);
		result = self.select(table = "order",where = where,limit=limit);
		debug(1,f"get_order(order_id={order_id},device_id={device_id},resource_id={resource_id},unique_id={unique_id},where={where},limit={limit}) -> {result}");
		return result;

	def get_preference(self,
					   preference_id = None,
					   user_id = None,
					   where = [],
				   	   limit = None):
		debug(1,f"get_preference(preference_id={preference_id},user_id={user_id},where={where},limit={limit})");
		if not preference_id is None: where.append(["preference_id","=",preference_id]);
		if not user_id is None: where.append(["user_id","=",user_id]);
		result = self.select(table = "preference",where = where,limit=limit);
		debug(1,f"get_preference(preference_id={preference_id},user_id={user_id},where={where},limit={limit}) -> {result}");
		return result;

	def get_price(self,
				  price_id = None,
				  user_id = None,
				  where = [],
				  limit = None):
		debug(1,f"get_price(price_id={price_id},user_id={user_id},where={where},limit={limit})");
		if not price_id is None: where.append(["price_id","=",price_id]);
		if not user_id is None: where.append(["user_id","=",user_id]);
		result = self.select(table = "price",where = where,limit=limit);
		debug(1,f"get_price(price_id={price_id},user_id={user_id},where={where},limit={limit}) -> {result}");
		return result;
	
	def get_resource(self,
					 resource_id = None,
					 system_id = None,
				     where = [],
				     limit = None):
		debug(1,f"get_resource(resource_id={resource_id},system_id={system_id},where={where},limit={limit})");
		result = [];
		if not resource_id is None: where.append(["resource_id","=",resource_id]);
		if not system_id is None: where.append(["system_id","=",system_id]);
		result = self.select(table="resource",where=where,limit=limit);
		debug(1,f"get_resource(resource_id={resource_id},system_id={system_id},where={where},limit={limit}) -> {result}");
		return result;

	def get_setting(self,
					setting_id = None,
					user_id = None,
				    where = [],
				    limit = None):
		debug(1,f"get_setting(setting_id={setting_id},user_id={user_id},where={where},limit={limit})");
		if not setting_id is None: where.append(["setting_id","=",setting_id]);
		if not user_id is None: where.append(["user_id","=",user_id]);
		result = self.select(table = "setting",where = where,limit=limit);
		debug(1,f"get_setting(setting_id={setting_id},user_id={user_id},where={where},limit={limit}) -> {result}");
		return result;

	def get_system(self,
				   system_id = None,
				   where = [],
				   limit = None):
		debug(1,f"get_system(system_id={system_id},where={where},limit={limit})");
		if system_id != None: where.append(["system_id","=",system_id]);
		result = self.select(table="system",where=where,limit=limit);
		debug(1,f"get_system(system_id={system_id},where={where},limit={limit}) -> {result}");
		return result;

	def get_token(self,
				  transaction_id = None,
				  user_id = None,
				  unique_id = None,
				  where = [],
				  limit = None):
		debug(1,f"get_token(transaction_id={transaction_id},user_id={user_id},unique_id={unique_id},where={where},limit={limit})");
		if transaction_id != None: where.append(["transaction_id","=",transaction_id]);
		if user_id != None: where.append(["user_id","=",user_id]);
		if unique_id != None: where.append(["unique_id","=",unique_id]);
		result = self.select(table="token",where=where,limit=limit);
		debug(1,f"get_token(transaction_id={transaction_id},user_id={user_id},unique_id={unique_id},where={where},limit={limit}) -> {result}");
		return result;

	def get_transaction(self,
						transaction_id = None,
						user_id = None,
				        where = [],
				   		limit = None):
		debug(1,f"get_token(transaction_id={transaction_id},user_id={user_id},where={where},limit={limit})");
		if transaction_id != None: where.append(["transaction_id","=",transaction_id]);
		if user_id != None: where.append(["user_id","=",user_id]);
		result = self.select(table="transaction",where=where,limit=limit);
		debug(1,f"get_token(transaction_id={transaction_id},user_id={user_id},where={where},limit={limit}) -> {result}");
		return result;

	def get_user(self,
				 user_id = None,
				 system_id = None,
				 where = [],
				 limit = None):
		debug(1,f"get_user(user_id={user_id},system_id={system_id},where={where},limit={limit})");
		if user_id != None: where.append(["user_id","=",user_id]);
		if system_id != None: where.append(["system_id","=",system_id]);
		result = self.select(table="user",where=where,limit=limit);
		debug(1,f"get_user(user_id={user_id},system_id={system_id},where={where},limit={limit}) -> {result}");
		return result;

def extract(data,fields="*"):
	"""Extract fields from query data
	
	Parameters:
		data	query data
		fields	list of fields to extract, default is all fields ("*")
	
	Returns: list of matching fields in data
	
	If fields is a singleton, then the result is also a singleton.
	If data is a singleton and fields is a list, then the result is a list.
	If both data and fields are lists, then the result is list of lists.
	"""
	debug(1,f"extract(data={data},fields={fields})");
	result = [];
	if fields == "*" :
		fields = list(data[0].keys());
	if not type(fields) is list:
		singleton = True;
		fields = [fields];
	else:
		singleton = False;
		if type(data) is list:
			for n in range(len(data)):
				result.append([]);
	if singleton :
		for field in fields:
			if type(data) is list:
				for item in data:
					result.append(item[field]);
			else:
				result.append(data[field]);
	else:
		if type(data) is list:
			for field in fields:
				n = 0;
				for item in data:
					result[n].append(item[field]);
					n += 1;
		else:
			for field in fields:
				result.append(data[field]);
	if singleton:
		debug(1,f"  -> {result[0]}");
		return result[0];
	else:
		debug(1,f"  ->{result}");
		return result;

def index(data,fields=[],extract="*"):
	"""Index fields in query data
	
	Parameters:
		data	query data
		fields	fields to index/subindex, [] use extract()
		extract fields to extract, default is all ("*")
	
	Returns: dict of data indexed by fields
	"""
	debug(1,f"index(data={data},fields={fields},extract={extract})");
	if fields == []:
		return data;
	if not type(fields) is list:
		primary = fields;
		secondaries = [];
	else:
		primary = fields[0];
		secondaries = fields[1::];
	result = {};
	for row in data:
		key = row[primary];
		if not key in result.keys():
			result[key] = [];
		if secondaries == []:
			result[key].append(module.extract(data,extract));
		else:
			result[key].append(index(data,secondaries,extract));
	debug(1,f"  -> {result}");
	return result;

def selftest():
	information_schema = Tess(schema="information_schema");
	table_data = information_schema.select(table="columns",where=["table_schema","tess"]);
	# debug(0,extract(table_data[0],"TABLE_NAME"));
	# debug(0,extract(table_data,"TABLE_NAME"));
	# debug(0,extract(table_data[0],["TABLE_NAME","COLUMN_NAME"]));
	# debug(0,extract(table_data,["TABLE_NAME","COLUMN_NAME"]));
	debug(0,index(table_data,"TABLE_NAME","COLUMN_NAME"));
	# debug(0,index(table_data,"TABLE_NAME",["COLUMN_NAME"]));
	# debug(0,index(table_data,"TABLE_NAME",["COLUMN_NAME","DATA_TYPE"]));
	del information_schema;

	quit()

	# defaults tests
	tess = Tess(schema="tess");

	tess.get_config();
	tess.get_config(config_id=None);
	tess.get_config(config_id=1);
	tess.get_config(system_id=1);
	tess.get_config(where=["name","api-version"],limit=1);
	tess.get_config(where=["value"]);
	tess.get_config(where=["value",None]);
	tess.get_config(where=[["name","mechanism"],["value","auction"]]);

	tess.get_device();
	tess.get_device(device_id=1);
	tess.get_device(user_id=1);
	feeder = tess.get_device(where=["name","feeder"]);
	tess.get_device(unique_id=feeder["unique_id"]);

	tess.get_meter();
	tess.get_order();
	tess.get_preference();
	tess.get_price();
	tess.get_resource();
	tess.get_setting();
	tess.get_system();
	tess.get_token();
	tess.get_transaction();
	tess.get_user();

	# practical tests
	system_name = "HCE";
	systems = tess.get_system(where=["name","=",system_name])
	system_id = systems["system_id"];

	system_resources = tess.get_resource(system_id);
	quit()
	extract(system_resources,"name")
	index(system_resources,["system_id","resource_id"],["name"])

	system_config = tess.get_config(system_id=system_id);
	index(system_config,"name","value")

	del tess

selftest()