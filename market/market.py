"""
Implements the TESS market operations

Concept of Operations
=====================

There are two types of market mechanisms, "auction" and "orderbook".

Auction
-------

An auction is a periodic market that clear every `config.interval` seconds.  
Bids are submitted at any time and cleared together at once.  The resulting
price determines which bids are awarded.

Orderbook
---------

An orderbook is a continuous market that clears whenever an order can be
immediately filled.  There are two types of orders.

1. Limit orders are for resources that can run at a reservation price.

2. Market orders are for resources that will run at any price.

"""

import datetime, uuid

def get_valid_resources():
	"""Get the list of valid resources
	Returns:
	  list - string names of valid resources
	"""
	valid = []
	if ( config.capacity ):
		valid.append("capacity")
	if ( config.ramping ):
		valid.append("ramping")
	if ( config.storage ):
		valid.append("storage")
	return valid

def is_valid_resource(resource):
	return resource in get_valid_resources()

def get_time_unit():
	"""Get the units for time"""
	return config.time_unit

def get_currency_unit():
	"""Get the units for currency"""
	return config.currency_unit

def get_resource_unit(resource):
	"""Get the units for a resource
	Parameters:
	  resource (string) - specifies the resource type -- see get_valid_resources()
	Returns:
	  string - the resource price units
	"""
	if ( resource == "capacity" and  config.power ):
		return config.power_unit
	elif ( resource == "ramping" and config.ramping ):
		return config.power_unit + "/" + config.time_unit
	elif ( resource == "storage" ):
		return config.power_unit + config.time_unit
	else:
		raise Exception("resource '%s' is not valid" % (resource))

def get_cost_unit():
	"""Get the units for costs"""
	return config.currency_unit + "/" + time_unit

def get_price_unit(resource):
	"""Get the units of price for a resource
	Parameters:
	  resource (string) - specifies the resource type, see get_resources()
	Returns:
	  string - the resource price units
	"""
	if ( resource == "capacity" and  config.power ):
		return config.currency_unit + "/" + config.power_unit + config.time_unit
	elif ( resource == "ramping" and config.ramping ):
		return config.currency_unit + "/" + config.power_unit
	elif ( resource == "storage" ):
		return config.currency_unit + "/" + config.power_unit + config.time_unit+"^2"
	else:
		raise Exception("resource '%s' is not valid" % (resource))

def open_market():
	"""Get access to the configured market
	"""
	print("TODO")

def get_next_clearing_datetime():
	"""Get the datetime of the next market clearing
	Returns:
	  datetime - date and time when price will be available, None if price is already available
	"""
	if config.mechanism == "auction":
		timestamp = datetime.datetime.utcnow().timestamp()
		return datetime.datetime.utcfromtimestamp((int(timestamp/config.interval)+1)*config.interval)
	elif config.mechanism == "orderbook":
		return None
	else:
		raise Exception("market mechanism '%s' is not valid" % (config.mechanism))

def log_market_action(message):
	"""Log a market action for current mechanism
	Parameters:
	  message (string) - message to write to market log
	"""
	with open(config.mechanism+".log","a") as fh:
		print("%s: %s" % (datetime.datetime.utcnow(),message),file=fh)
		fh.close()

def submit_bid(resource,device,quantity,price,current,replace=None):
	"""Submit a bid to the market
	Parameters:
	  resource (string) - resource type -- see get_valid_resources()
	  device (number)   - device id
	  quantity (double) - the bid quantity, negative is sell ask, positive is buy offer
	  price (double)    - the bid price, +inf for must trade, -inf for must not trade, 0.0 for take any
	  current (double)  - the current quantity, zero if none, nan if unknown
	  replace (integer) - order id to replace or delete (use price=-inf) a previous trade
	Returns:
	  integer - the order id -- see 'replace' parameters
	"""
	if is_valid_resource(resource):
		timestamp = datetime.datetime.utcnow().timestamp()
		salt = uuid.uuid4()
		ident = "%.0f/%s-%08d-%s-%s" % (get_next_clearing_datetime().timestamp(),resource,device,timestamp,salt.hex)
		log_market_action("submit_bid(resource='%s',device=%d,quantity=%g,price=%g,current=%g,replace=%s) -> order_id = '%s'" % (resource,device,quantity,price,current,replace,ident))
		return ident
	else:
		raise Exception("resouce '%s' is not valid" % (resource))

def clear_market():
	"""Clears the market
	Returns:
	  bool - status of market clearing -- True if price is valid, False if no price found
	"""
	print("TODO")

def get_price(order):
	"""Get the market price of a resource
	Parameters:
	  order (string) - order id -- see submit_bid()
	Returns:
	  double - the resource price, or nan if none -- see get_resource_price(resource) for units of prices
	"""
	print("TODO")
