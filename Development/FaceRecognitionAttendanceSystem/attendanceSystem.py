#! /usr/bin/python3
import warnings
warnings.filterwarnings("ignore")
import os
os.chdir(os.path.abspath(os.getcwd()))
# os.chdir('/home/pi/Documents/MaskedFaceRecognitionSystem1')

from interfaces import database
from interfaces import connectionServer
import sys


from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi

import requests

from interfaces.adminScreen import adminLoginWindow, adminWindow, adminSyncWindow, adminSettings
from interfaces.mainWindow import mainWindow
from interfaces.regWindow import regWindow
from interfaces.modWindow import modWindow

from interfaces import global_initialize as global_ini


class Window(QDialog):
    def __init__(self):
        super(Window, self).__init__()
        loadUi("ui/start.ui", self)
        self.setWindowIcon(QIcon('faceid.ico'))
        
        if not os.path.exists('datasets'):
            os.makedirs('datasets')
            
        if not os.listdir("datasets"): 
            self.startButton.setEnabled(False)
        else:
            self.startButton.setEnabled(True)
        self.startButton.clicked.connect(self.syncSlot)
        self.logButton.clicked.connect(self.runSlot2)
        
        self._new_window = None
        self._new_window2 = None
        self._new_window3 = None
    
    # 1: main window (Face Detection Attendance)
    def syncSlot(self):
        response = requests.get(global_ini.checksum_url)
        server_sum = int(response.text)

        client_sum = len(os.listdir('datasets'))

        if server_sum == client_sum:
            print('Equal')
            self.runSlot()
            
        else:
            print('Not Equal')
            msg = QMessageBox()
            msg.setWindowTitle("DATABASE NOT SYNC")
            msg.setText("System detects that local database is not sync with the database stored in Server")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Cancel|QMessageBox.Ignore)
            msg.setDefaultButton(QMessageBox.Ignore)
            buttonY = msg.button(QMessageBox.Ignore)
            buttonY.setText('Launch anyway')
            msg.setInformativeText("If you launch the application now, you may not able to detect some newly registered user. Contact Admin to perform synchronization.")
            
            x = msg.exec()
            
            if x == QMessageBox.Ignore:
                print("Continue Launching")
                self.runSlot()
                     
            else:
                print("Abort launching")
    
    
    def runSlot(self):
        self.close() 
        self.outputWindow_()
        
    def outputWindow_(self):
        self._new_window = mainWindow()
        self._new_window.show()
        self._new_window.exitButton.clicked.connect(self.backMenu)
        
    def backMenu(self):
        self.close()
        self._new_window = Window()
        self._new_window.show()
        
    # 2: admin Login screen
    def runSlot2(self):
        self.close()
        self.outputWindow2_()
    
    def outputWindow2_(self):
        self._new_window = adminLoginWindow()
        self._new_window.show()
        self._new_window.passwordField.setEchoMode(QLineEdit.Password)
        self._new_window.signButton.clicked.connect(self.loginfunction)
        self._new_window.backButton.clicked.connect(self.backMenu)


    def loginfunction(self):
        username = self._new_window.usernameField.text()
        password = self._new_window.passwordField.text()
        
        if len(username)==0 or len(password)==0:
            self._new_window.error.setText("Please input all required field")
        else:
            query = 'SELECT password FROM admin WHERE username = \''+username+"\'"

            try:
                global_ini.mycursor.execute(query)
            except Exception as e:
                QMessageBox.critical(None, "Error", str(repr(e)))
                return
                      
            try:
                result_pass = global_ini.mycursor.fetchone()[0]
                if result_pass == password:
                    #login to admin screen
                    self._new_window.error.setText("Login Successfully")
                    self.runSlot3()
                else:
                    self._new_window.error.setText("Invalid username or password")
                    self._new_window.passwordField.clear()

            except TypeError as e:
                print(e)
                self._new_window.error.setText("Invalid username and password")
                self._new_window.usernameField.clear()
                self._new_window.passwordField.clear()

    # 3: admin screen  
    def runSlot3(self):
        self.close()
        self.outputWindow3_()
    
    def outputWindow3_(self):
        self._new_window = adminWindow()
        self._new_window.show()
        self._new_window.regButton.clicked.connect(self.runSlot4)
        self._new_window.modButton.clicked.connect(self.runSlot5)
        self._new_window.syncButton.clicked.connect(self.runSlot6)
        self._new_window.settingsButton.clicked.connect(self.runSlot7)
        self._new_window.logout.clicked.connect(self.backMenu)
    
    # 4: registration screen    
    def runSlot4(self):
        self.close()
        self.outputWindow4_()
    
    def outputWindow4_(self):
        self._new_window = regWindow()
        self._new_window.show()
        self._new_window.BackButton.clicked.connect(self.runSlot3)
    
    # 5: modifying screen
    def runSlot5(self):
        self.close()
        self.outputWindow5_()
    
    def outputWindow5_(self):
        self._new_window = modWindow()
        self._new_window.show()
        self._new_window.BackButton.clicked.connect(self.runSlot3)
        
    # 6: Sync Server Database
    def runSlot6(self):
        msg = QMessageBox()
        msg.setWindowTitle("Sync Server Database")
        msg.setText("Are you sure you want to sync Server Database?")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        buttonY = msg.button(QMessageBox.Ignore)
        
        x = msg.exec()
            
        if x == QMessageBox.Yes:
            self.outputWindow6_()
            
    
    def outputWindow6_(self):
        self._new_window2 = adminSyncWindow()
        self._new_window2.show()        

    # 7: settings screen
    def runSlot7(self):
        self.outputWindow7_()
    
    def outputWindow7_(self):
        self._new_window3 = adminSettings()
        self._new_window3.show()
        self._new_window3.cancel_button.clicked.connect(self._new_window3.close)


def main():
    App = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(App.exec_())

if __name__ == '__main__':
    main()