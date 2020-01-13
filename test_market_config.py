"""config.py

Configure the TESS operations

mechanism - string to select the market mechanism in use
Options:
  "auction" - periodic clearing
  "orderbook" - continuous clearing

interval - integer to set the period of the market interval in seconds

capacity - bool to indicate whether power capacity bids are allowed

ramping - bool to indicate whether ramp rate bids are allowed

storage - bool to indicate whether energy storage bids are allowed

power_unit - string to indicate the unit in which bids are submitted

time_unit - string to indicate the unit of time

currency_unit - string to indicate the unit of currency
"""
mechanism = "auction";
interval = 300;
capacity = True;
ramping = False;
storage = False;
power_unit = "MW";
time_unit = "h";
currency_unit = "$";

host = {
	'api' : "https://tess.slacgismo.io/",
	'www' : "https://tess.slacgismo.org/",
	'doc' : "http://docs.slacgismo.org/index.html?project=TESS",
	'dev' : "http://docs.slacgismo.org/index.html?project=TESS&doc=REST_API.md"
};

#
# database configuration
#
mysql = {
	'user' : "tess",
	'password' : "slacgismo",
	'host' : "localhost",
	'port' : 3306,
	'database' : "tess"
};

#
# Rate limits
#
limit = {
	'anonymous' : 60,
	'authenticated' : 3600
};
