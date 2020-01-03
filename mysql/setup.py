import pymysql as mysql;
try:
	import config;
except:
	import mysql.config as config;	

root = mysql.connect(**config.root);
with open("create_users.sql","r") as f:
	script = f.readlines();
	command = "";
	for line in script:
		line = line.strip();
		if len(line) == 0 or line[0] == '#':
			continue;
		command += f" {line}";
		if line[-1] == ';':
			cursor = root.cursor();
			cursor.execute(command);
			cursor.close();
			command = "";
