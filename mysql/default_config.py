"""config.py

Configure the TESS database operations
"""
debug_level = None; # None, or <int> >= 0
schema_name = "tess";
system_name = "HCE";

#
# database configurations
#
root = {
	'user' : "root",
	'password' : "slacgismo",
	'host' : "localhost",
	'port' : 3306,
}
user = {
	'user' : "tess",
	'password' : "slacgismo",
	'host' : "localhost",
	'port' : 3306,
}
admin = {
	'user' : "tess_a",
	'password' : "slacgismo",
	'host' : "localhost",
	'port' : 3306,
}
