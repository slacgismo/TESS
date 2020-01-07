The `mysql` module provide low-level functions to access the TESS data tables needed for market, user, and control room operations.

# Local database
To test on a local database, you must install a MySQL server and set up the TESS users.  Then run the `create_users.sql` script as root:

~~~
bash$ mysql -uroot -p < create_users.sql
~~~

# Requirements
~~~
bash$ pip3 install cryptography, pymysql
~~~

# Unit test
Once the TESS users are created you can run the `test.py` script to run the unit tests.

~~~
bash$ python3 test.py
~~~

