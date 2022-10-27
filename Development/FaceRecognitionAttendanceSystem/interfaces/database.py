import sys
import mysql.connector
#from mysql.connector import pooling
from PyQt5.QtWidgets import *

import configparser as cp
import os

filename = 'config.ini'
inifile = cp.ConfigParser()
inifile.read(filename,'UTF-8')

App = QApplication(sys.argv)

try:

    
    mydb = mysql.connector.connect(
        host=inifile.get("db","host"),
        port=inifile.get("db","port"),
        user=inifile.get("db","user"),
        password=inifile.get("db","password"),
        database=inifile.get("db","database")
    )
    
    # connection_pool = pooling.MySQLConnectionPool(
    #     pool_name="sql_pool",
    #     pool_size=5,
    #     pool_reset_session=True,
    #     host="F300-NB11",
    #     port="3306",
    #     user="admin",
    #     password="admin",
    #     database="face_recognition"
    # )

    # Get connection object from a pool
    # connection_object = connection_pool.get_connection()

except Exception as e:
    QMessageBox.critical(None, "Status", str(os.getcwd())+" Fail to connect to database <br>"+str(repr(e)))
    print(repr(e))
    sys.exit("Fail to start application")
    
    