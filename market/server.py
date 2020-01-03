import pymysql as my;
import config;
import json;

debug_level = 9;
def debug(level,message):
	if ( level <= debug_level ):
		print("DEBUG(server,{}): {}".format(level,message))

endpoints = {
	"config" : {
		"GET" : [
			"/{system}",
			"/{system}?setting={parameter}",
			"/{system}/{resource}"
		],
		"PUT" : [
			"/{system}?setting={parameter}"
		]
	},
	"order": {
		"GET" : [
			"/{system}/{resource}",
			"/{system}/{resource}/{order}"
		],
		"PUT" : [
			"/{system}/{resource}",
			"/{system}/{resource}/{order}"
		],
		"DELETE" : [
			"/{system}/{resource}/{order}"
		]
	},
	"price": {
		"GET" : [
			"/{system}/{resource}",
			"/{system}/{resource}?quantity={quantity}",
			"/{system}/{resource}?order={order}"
		]
	},
	"quantity" : {
		"GET" : [
			"/{system}/{resource}",
			"/{system}/{resource}?price={price}",
			"/{system}/{resource}?order={order}"
		]
	},
	"device" : {
		"GET" : [
			"/{user}",
			"/{user}/{parameter}"
		],
		"PUT" : [
			"/{user}/{parameter}"
		]
	},
	"user" : {
		"GET" : [
			"/{user}",
			"/{user}/{parameter}"
		],
		"PUT" : [
			"/{user}/{parameter}"
		]
	}
};

def endpoint_get_(db,**kwargs):
	return {
		"hostname" : config.host['api'],
		"systems" : endpoint_get_config(db),
		"limit" : config.limit,
		"endpoints" : endpoints
	};

def endpoint_get_config(db,**kwargs):
	# protip: items = None converts the result to a simple list, others result is a dict
	select = db.cursor();
	if "system" in kwargs :
		if "resource" in kwargs :
			items = ['name','quantity_unit','price_unit'];
			query = ("SELECT resource.name, resource.quantity_unit, resource.price_unit "
							"FROM tess.resource JOIN tess.system USING (system_id) "
							"WHERE system.name = '%s'") % kwargs['system'];
		else:
			items = ['name','quantity_unit','price_unit'];
			query = ("SELECT resource.name, resource.quantity_unit, resource.price_unit "
							"FROM tess.resource JOIN tess.system USING (system_id) "
							"WHERE system.name = '%s'") % kwargs['system'];
	else:
		items = None;
		query = "SELECT name FROM tess.system";
	debug(2,query);
	select.execute(query);
	result = [];
	for row in select:
		if items is None:
			if len(row) == 1:
				data = row[0]
			else:
				data = list(row)
		else:
			data = dict(zip(items,row));
		result.append(data);
	select.close();
	return result;

def endpoint_put_config(db,**kwargs):
	# protip: items = None converts the result to a simple list, others result is a dict
	return {}

def endpoint_get_order(db,**kwargs):
	# protip: items = None converts the result to a simple list, others result is a dict
	return {}

def endpoint_put_order(db,**kwargs):
	# protip: items = None converts the result to a simple list, others result is a dict
	return {}

def endpoint_delete_order(db,**kwargs):
	# protip: items = None converts the result to a simple list, others result is a dict
	return {}

def endpoint_get_price(db,**kwargs):
	# protip: items = None converts the result to a simple list, others result is a dict
	return {}

def endpoint_get_quantity(db,**kwargs):
	# protip: items = None converts the result to a simple list, others result is a dict
	return {}

def endpoint_get_device(db,**kwargs):
	# protip: items = None converts the result to a simple list, others result is a dict
	return {}

def endpoint_put_device(db,**kwargs):
	# protip: items = None converts the result to a simple list, others result is a dict
	return {}

def endpoint_get_user(db,**kwargs):
	# protip: items = None converts the result to a simple list, others result is a dict
	return {}

def endpoint_put_user(db,**kwargs):
	# protip: items = None converts the result to a simple list, others result is a dict
	return {}

def response(target,**kwargs):
	debug(1,"mysql connection - config={}, target={}, kwargs={}".format(config.mysql,target,kwargs))
	db = my.connect(**config.mysql);
	result = target(db,**kwargs);
	db.close();
	return json.dumps(result,indent=4);

def process_request(verb,query,attributes=None,body=None) :
	#print("%s %s?%s\n\n%s"%(verb,query,attributes,body));
	specs = query.split("/")
	if len(specs) <= 1:
		raise Exception("query '%s' is not valid" % query);
	endpoint = specs[1]
	target = "_".join(["endpoint",verb.lower(),endpoint]);
	# TODO replace {} terms
	kwargs = {}
	items = specs[2::]
	if endpoint != '':
		for pattern in endpoints[endpoint][verb]:
			keys = pattern.split('/')[1::]
			if len(keys) != len(items):
				continue;
			for n in range(len(keys)):
				key = keys[n]
				if len(key) > 0 and key[0] == '{' and key[-1] == '}':
					kwargs[key[1:-1]] = items[n]
	print("response(target='%s',kwargs=%s) -> " % (target,kwargs))
	return response(eval(target),**kwargs)


specs = process_request("GET","/");
for system in specs["systems"]:
	resources = endpoint_get_
	for endpoint,actions in specs[""].items():

