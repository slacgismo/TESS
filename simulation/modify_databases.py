import pandas as pd
import mysql.connector
from datetime import datetime
import numpy as np

mydb = mysql.connector.connect(
            host='192.168.1.67', #'192.168.1.67', #SLAC #'192.168.1.67', #zu Hause '192.168.1.67', #'10.21.152.169', #'198.129.217.106', #network ip
            user='gridlabd', #'root',
            port='3306',
            passwd='gridlabd',
            database='TESS' #'gridlabd'
        )

print('Connected!')

# mydb = mysql.connector.connect(
#             host='192.168.1.67',
#             #service=mysql
#             #port=3306
#             user='root',
#             port='3306',
#             passwd='gridlabd',
#             database='gridlabd'
#         )

# mydb = mysql.connector.connect(
#             host='127.0.0.1',
#             #service=mysql
#             #port=3306
#             user='root',
#             port='3306',
#             passwd='gridlabd',
#             database='gridlabd'
#         )

mycursor = mydb.cursor(buffered = True)

import pdb; pdb.set_trace()

#cursor.execute("ALTER TABLE table_name ADD email VARCHAR(100) NOT NULL")
mycursor.execute('SET FOREIGN_KEY_CHECKS = 0')

sql = "DROP TABLE market_EV" #not needed
mycursor.execute(sql) 

    # Table with pv specification
try:
    mycursor.execute('CREATE TABLE market_EV (id INT AUTO_INCREMENT PRIMARY KEY, house_name VARCHAR(255), appliance_name VARCHAR(255), appliance_id VARCHAR(255), SOC_max FLOAT, u_max FLOAT, eff FLOAT, charging_type VARCHAR(255), k FLOAT)')
except Exception as e:
    print('error')

mycursor.execute('SET FOREIGN_KEY_CHECKS = 1')

#mydb.commit()
#mydb.close()