import json
import mysql.tess as mysql
import test_mysql_config
import random

mysql.use_config(test_mysql_config)

from user import *
mysql.set_debug(None)

# get system
system_id = mysql.find_system(name=test_mysql_config.system_name)

# create a new user
rand = int(random.random()*1e12)
name = f"test{rand}"
email = f"test{rand}@tess.org"
password = "slacgismo"
role = "TEST"
a = user(database=mysql,request='create',system_id=system_id,name=name,role=role,email=email,password=password)

# check user
# name = "dchassin"
# email = "dchassin@slac.stanford.edu"
# password = "slacgismo"
# role = "ADMINISTRATOR"
a = user(database=mysql,request='get',name=name,use_throw=True)
assert(a.name == name)
assert(a.system_id == system_id)
assert(a.email == email)
assert(a.role == role)
user_id = a.user_id
sha1pwd = a.sha1pwd

# authenticate user
a = user(database=mysql,request='check',name=name,password=password,use_throw=True)
assert(a.name == name)
assert(a.system_id == system_id)
assert(a.user_id == user_id)
assert(a.email == email)
assert(a.role == role)
assert(a.is_authenticated == True)

# authentication failure using return
a = user(database=mysql,request='check',name=name,password=password+"bad")
assert(a.is_authenticated == False)

# authentication failure using exception
try:
	a = user(database=mysql,request='check',name=name,password=password+"bad",use_throw=True)
	ok = True
except:
	ok = False
assert(ok == False)

# change the password
a.change(password=password+"new",use_throw=True)

# change the email
a.change(email="new-email@tess.org",use_throw=True)

# delete user
a.delete()
