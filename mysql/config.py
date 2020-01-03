"""config.py

Configure the TESS database operations
"""
debug_level = None; # None, or <int> >= 0
schema_name = "tess";
system_name = "HCE";

#
# database configurations
#
local = {
	'user' : "tess",
	'password' : "slacgismo",
	'host' : "localhost",
	'port' : 3306,
};
local_a = {
	'user' : "tess_a",
	'password' : "slacgismo",
	'host' : "localhost",
	'port' : 3306,
};
remote = {
	'user' : "tess",
	'password' : "slacgismo",
	'host' : "localhost",
	'port' : 3306,
}
remote_a = {
	'user' : "tess_a",
	'password' : "slacgismo",
	'host' : "localhost",
	'port' : 3306,
}
