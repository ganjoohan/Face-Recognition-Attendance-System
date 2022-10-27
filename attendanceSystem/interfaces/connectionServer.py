import sys
import requests
from PyQt5.QtWidgets import *
import configparser as cp

filename = 'config.ini'
inifile = cp.ConfigParser()
inifile.read(filename,'UTF-8')

App = QApplication(sys.argv)

try:
    response = requests.get('http://{}:{}/api/connect'.format(inifile.get("server","ip"),inifile.get("server","port")), timeout=5)
    print(response.text)

except Exception as e:
    QMessageBox.critical(None, "Status", "Fail to connect to CSC server \nPlease check again")
    print(e)
    sys.exit("Fail to start application")
    
    