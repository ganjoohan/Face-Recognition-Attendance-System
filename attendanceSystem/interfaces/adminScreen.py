from interfaces import global_initialize as global_ini
import configparser as cp
import os
import time
from tqdm import tqdm
import pandas as pd
import shutil
import requests
import mysql.connector

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import QDateTime, QDate, QTime, Qt
from PyQt5.uic import loadUi

from src.commons import functions, distance as dst
from src import DeepFace

counter = 0
# ======================== Admin Login ==================================
class adminLoginWindow(QDialog):
    def __init__(self):
        super(adminLoginWindow, self).__init__()
        loadUi("ui/adminLogin.ui", self)
        self.setWindowIcon(QIcon('faceid.ico'))

# ======================== Admin Screen ==================================
class adminWindow(QDialog):
    def __init__(self):
        super(adminWindow, self).__init__()
        loadUi("ui/adminScreen.ui", self)
        self.setWindowIcon(QIcon('faceid.ico'))

# ======================== Splash Screen for Sync ==================================
class adminSyncWindow(QDialog):
    
    def __init__(self):
        super(adminSyncWindow, self).__init__()
        loadUi("ui/adminSync.ui", self)
        self.setWindowIcon(QIcon('faceid.ico'))
        
        ## REMOVE TITLE BAR
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)


        ## DROP SHADOW EFFECT
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.dropShadowFrame.setGraphicsEffect(self.shadow)


        # =================== Sync employee face image from server ====================
        # REMOVE 'DATASETS' WHOLE FOLDER
        shutil.rmtree('datasets', ignore_errors=False)
        
        with open('datasets.zip', 'wb+') as file:
            file.write(requests.get(global_ini.sync_url).content)
        shutil.unpack_archive('datasets.zip', 'datasets')
        os.remove('datasets.zip')
        
        # TO PREVENT SYSTEM BUG: if datasets.zip is empty, datasets folder will be deleted, so need to create new empty folder
        if not os.path.exists('datasets'):
            os.makedirs('datasets')
        # =============================================================================
        
        self.progressBar.setMaximum(50)

        self.timer = QTimer()
        self.timer.timeout.connect(self.progress)
        # TIMER IN MILLISECONDS
        self.timer.start(10)
        
        # Initial Text
        self.label_description.setText("<strong>LOADING</strong> DATABASE")


    ########################################################################
    def progress(self):
     
        global counter
        # SET VALUE TO PROGRESS BAR
        self.progressBar.setValue(counter)

        # CLOSE SPLASH SCREE AND OPEN APP
        if counter > 50:
            
            # RESET COUNTER
            counter = 0
            
            # STOP TIMER
            self.timer.stop()
            self.label_description.setText("<strong>BUILDING</strong> & <strong>TRAINING</strong> MODEL")
            self.training()
            
            # SHOW COMPLETE SIGNAL
            QMessageBox.information(None, "Status", "Sync & Training completed.")

            # CLOSE SPLASH SCREEN
            self.close()

        # INCREASE COUNTER
        counter += 1

    def training(self):   
        
        self.progressBar.setValue(0)
        
        db_path="datasets"

        # ========================== Training Embeddings Function ===============================
        def findEmbeddings():
            #find embeddings for employee list
            tic = time.time()
            
            #-----------------------
            pbar = tqdm(range(0, len(employees)), desc='Finding embeddings')
            self.progressBar.setMaximum(len(employees))
            embeddings = []
            #for employee in employees:
            for index in pbar:
                self.progressBar.setValue(index)
                
                employee = employees[index]
                pbar.set_description("Finding embedding for %s" % (employee.split("/")[-1]))
                
                embedding = []
                #preprocess_face returns single face. this is expected for source images in db.
                img = functions.preprocess_face(img = employee, target_size = (global_ini.input_shape_y, global_ini.input_shape_x), enforce_detection = False, detector_backend = global_ini.detector_backend)
                img_representation = global_ini.model.predict(img)[0,:]

                embedding.append(employee)
                embedding.append(img_representation)
                embeddings.append(embedding)

            self.progressBar.setValue(index+1)
            
            df = pd.DataFrame(embeddings, columns = ['employee', 'embedding'])
            df['distance_metric'] = global_ini.distance_metric

            toc = time.time()

            print("Embeddings found for given data set in ", toc-tic," seconds")
            
            # print(type(embeddings)) # Embedding 是一个list，一张image一个位，# print(embeddings) #jh

            # jh - save embeddings to prevent training everytime
            df.to_pickle("trainer/face_embeddings.pkl")
        # =====================================================================================
        
        employees = []
        #check passed db folder exists
        if os.path.isdir(db_path) == True:
            for r, d, f in os.walk(db_path): # r=root, d=directories, f = files
                for file in f:
                    if ('.jpg' in file):
                        #exact_path = os.path.join(r, file)
                        exact_path = r + "/" + file
                        #print(exact_path)
                        employees.append(exact_path)
    
        if len(employees) == 0:
            QMessageBox.warning(None, "Status", "No Account Registered...")
            print("WARNING: There is no image in this path ( ", db_path,") . Training will not be performed.")

        if len(employees) > 0:
            findEmbeddings() 

# ======================== Admin Settings ==================================
class adminSettings(QDialog):
    
    def __init__(self):
        super(adminSettings, self).__init__()
        loadUi("ui/adminSettings.ui", self)
        self.setWindowIcon(QIcon('faceid.ico'))
        
        ipRange = "(([ 0]+)|([ 0]*[0-9] *)|([0-9][0-9] )|([ 0][0-9][0-9])|(1[0-9][0-9])|([2][0-4][0-9])|(25[0-5]))"
        ipRegex = QRegExp("^" + ipRange
                        + "\\." + ipRange
                        + "\\." + ipRange
                        + "\\." + ipRange + "$")
        ipValidator = QRegExpValidator(ipRegex, self)
        self.server_ip.setValidator(ipValidator)
        self.server_ip.setInputMask("000.000.000.000")
        self.server_ip.setCursorPosition(0)

        self.server_port.setValidator(QRegExpValidator(QRegExp("[0-9]*"), self))
        self.db_port.setValidator(QRegExpValidator(QRegExp("[0-9]*"), self))

        # ==========================================================
        self.label_5.setEnabled(False);self.label_6.setEnabled(False);self.label_7.setEnabled(False)
        self.label_8.setEnabled(False);self.label_9.setEnabled(False);self.db_host.setEnabled(False)
        self.db_port.setEnabled(False);self.db_user.setEnabled(False);self.db_password.setEnabled(False)
        self.db_password.setEchoMode(QLineEdit.Password);self.db_database.setEnabled(False)

        self.db_host.setText(global_ini.db_host)
        self.db_port.setText(global_ini.db_port)
        self.db_user.setText(global_ini.db_user)
        self.db_password.setText(global_ini.db_password)
        self.db_database.setText(global_ini.db_database)
        self.checkBox_db.stateChanged.connect(self.db_method)
        # ===========================================================
        self.label_14.setEnabled(False);self.label_10.setEnabled(False)
        self.server_ip.setEnabled(False);self.server_port.setEnabled(False)
        self.server_ip.setText(global_ini.ip)
        self.server_port.setText(global_ini.port)
        self.checkBox_server.stateChanged.connect(self.server_method)


        self.comboBox_model.setCurrentText(global_ini.model_name)
        self.threshold_label.setValue(float(global_ini.threshold))
        self.comboBox_model.currentIndexChanged.connect(self.threshold_changed)
        
        # setting tool tip to each model
        self.comboBox_model.setItemData(0, "Google researchers: (99.20%) [128 dimensions]", Qt.ToolTipRole)
        self.comboBox_model.setItemData(1, "Google researchers: (99.65%) [512 dimensions]", Qt.ToolTipRole)
        self.comboBox_model.setItemData(2, "University of Oxford researchers: (98.78%)", Qt.ToolTipRole)
        self.comboBox_model.setItemData(3, "Facebook researchers: (97.53%)", Qt.ToolTipRole)
        self.comboBox_model.setItemData(4, "Imperial College London and InsightFace researchers: (99.40%)", Qt.ToolTipRole)
        self.comboBox_model.setItemData(5, "Sigmoid-Constrained Hypersphere Loss for Robust Face Recognition (99.40%)", Qt.ToolTipRole)
  
        self.num_photo.setValue(int(global_ini.photo_num))
        
        self.checkBox_logging.setChecked(global_ini.checkBox_logging)
        self.comboBox_machine.setCurrentText(global_ini.machine_code)

        self.save_button.clicked.connect(self.save_settings)
    
    def db_method(self):

        if self.checkBox_db.isChecked():
            self.label_5.setEnabled(True);self.label_6.setEnabled(True);self.label_7.setEnabled(True)
            self.label_8.setEnabled(True);self.label_9.setEnabled(True);self.db_host.setEnabled(True)
            self.db_port.setEnabled(True);self.db_user.setEnabled(True);self.db_password.setEnabled(True)
            self.db_database.setEnabled(True)

        elif self.checkBox_db.isChecked() == False:
            self.db_host.setText(global_ini.db_host)
            self.db_port.setText(global_ini.db_port)
            self.db_user.setText(global_ini.db_user)
            self.db_password.setText(global_ini.db_password)
            self.db_database.setText(global_ini.db_database)
            self.label_5.setEnabled(False);self.label_6.setEnabled(False);self.label_7.setEnabled(False)
            self.label_8.setEnabled(False);self.label_9.setEnabled(False);self.db_host.setEnabled(False)
            self.db_port.setEnabled(False);self.db_user.setEnabled(False);self.db_password.setEnabled(False)
            self.db_database.setEnabled(False)

    def server_method(self):

        if self.checkBox_server.isChecked():
            self.label_14.setEnabled(True);self.label_10.setEnabled(True)
            self.server_ip.setEnabled(True);self.server_port.setEnabled(True)

        elif self.checkBox_server.isChecked() == False:
            self.server_ip.setText(global_ini.ip)
            self.server_port.setText(global_ini.port)
            self.label_14.setEnabled(False);self.label_10.setEnabled(False)
            self.server_ip.setEnabled(False);self.server_port.setEnabled(False)
    
    def threshold_changed(self):

        if global_ini.model_name == self.comboBox_model.currentText():
            self.threshold_label.setValue(global_ini.threshold)
        else:
            threshold_temp = dst.findThreshold(self.comboBox_model.currentText(), global_ini.distance_metric)
            self.threshold_label.setValue(threshold_temp)

    def save_settings(self):
        # Path to config file
        filename = 'config.ini'
        inifile = cp.ConfigParser()
        inifile.read(filename,'UTF-8')

        if self.checkBox_db.isChecked():
            try:
                test_mydb = mysql.connector.connect(
                    host=self.db_host.text(),
                    port=self.db_port.text(),
                    user=self.db_user.text(),
                    password=self.db_password.text(),
                    database=self.db_database.text()
                )
                global_ini.mydb = test_mydb
                global_ini.mycursor = test_mydb.cursor()

            except Exception as e:
                QMessageBox.critical(None, "Database Connection Error", str(repr(e)))
                return

        if self.checkBox_server.isChecked():
            try:
                response = requests.get('http://{}:{}/api/connect'.format(self.server_ip.text(),self.server_port.text()), timeout=5)
                global_ini.addr = 'http://{}:{}'.format(self.server_ip.text(),self.server_port.text())
                global_ini.reg_url = global_ini.addr + '/api/register'
                global_ini.sync_url = global_ini.addr + '/api/dataSync'
                global_ini.del_url = global_ini.addr + '/api/delete'
                global_ini.checksum_url = global_ini.addr + '/api/checkSum'

            except Exception as e:
                QMessageBox.critical(None, "Server Connection Error", str(repr(e)))
                return

        # If user choose a new model
        if global_ini.model_name != self.comboBox_model.currentText():
            msg = QMessageBox()
            msg.setWindowTitle("Changing New Recognition Model")
            msg.setText("Are you sure you want to change recognition model from <strong>"+global_ini.model_name+"</strong> to <strong>"+self.comboBox_model.currentText()+"</strong>?")
            msg.setInformativeText("Warning:New model required to perform new training and embeddings.")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
            msg.setDefaultButton(QMessageBox.Yes)
            x = msg.exec()
                
            if x == QMessageBox.Yes:
                # [db]
                inifile["db"]["host"]=str(self.db_host.text())
                inifile["db"]["port"]=str(self.db_port.text())
                inifile["db"]["user"]=str(self.db_user.text())
                inifile["db"]["password"]=str(self.db_password.text())
                inifile["db"]["database"]=str(self.db_database.text())

                # [server]
                inifile["server"]["ip"]=str(self.server_ip.text())
                inifile["server"]["port"]=str(self.server_port.text())

                # [detection]
                # inifile["detection"]["detector"]=self.detector.text()
                inifile["detection"]["model"]=str(self.comboBox_model.currentText())
                inifile["detection"]["threshold"]=str(self.threshold_label.text()) #return <int> type

                # [photo]
                inifile["photo"]["number"]=str(self.num_photo.text()) #return <int> type

                # [logging]
                inifile["logging"]["logging_status"]=str(self.checkBox_logging.isChecked())

                # [machine]
                inifile["machine"]["machine_code"]=str(self.comboBox_machine.currentText())

                with open(filename, 'w') as configfile:
                    inifile.write(configfile)

                global_ini.db_host = self.db_host.text()
                global_ini.db_port = self.db_port.text()
                global_ini.db_user = self.db_user.text()
                global_ini.db_password = self.db_password.text()
                global_ini.db_database = self.db_database.text()
                global_ini.ip = self.server_ip.text()
                global_ini.port = self.server_port.text()
                global_ini.photo_num = self.num_photo.text()

                global_ini.model_name = self.comboBox_model.currentText()
                global_ini.threshold = float(self.threshold_label.text())

                global_ini.checkBox_logging = self.checkBox_logging.isChecked()
                global_ini.machine_code = self.comboBox_machine.currentText()
                
                #======================= Build DL Face Recognition Model ==========================
                start = time.time()
                global_ini.model = DeepFace.build_model(global_ini.model_name)
                end = time.time()
                print("Face Recognition Model: ", global_ini.model_name," is built. | Time Taken: ", (end-start))


                #========================= Find Model Input Shape =================================
                global_ini.input_shape = functions.find_input_shape(global_ini.model)
                global_ini.input_shape_x = global_ini.input_shape[0]
                global_ini.input_shape_y = global_ini.input_shape[1]

                class changeModel(QDialog):
                    
                    def __init__(self):
                        super(changeModel, self).__init__()
                        loadUi("ui/adminSync.ui", self)
                        self.setWindowIcon(QIcon('faceid.ico'))
                        
                        ## REMOVE TITLE BAR
                        self.setWindowFlag(Qt.FramelessWindowHint)
                        self.setAttribute(Qt.WA_TranslucentBackground)

                        ## DROP SHADOW EFFECT
                        self.shadow = QGraphicsDropShadowEffect(self)
                        self.shadow.setBlurRadius(20)
                        self.shadow.setXOffset(0)
                        self.shadow.setYOffset(0)
                        self.shadow.setColor(QColor(0, 0, 0, 60))
                        self.dropShadowFrame.setGraphicsEffect(self.shadow)
                        
                        self.progressBar.setMaximum(50)

                        self.timer = QTimer()
                        self.timer.timeout.connect(self.progress)
                        # TIMER IN MILLISECONDS
                        self.timer.start(10)
                        
                        # Initial Text
                        self.label_description.setText("<strong>LOADING</strong> DATABASE")


                    ########################################################################
                    def progress(self):
                        global counter
                        # SET VALUE TO PROGRESS BAR
                        self.progressBar.setValue(counter)

                        # CLOSE SPLASH SCREE AND OPEN APP
                        if counter > 50:
                            # RESET COUNTER
                            counter = 0
                            # STOP TIMER
                            self.timer.stop()
                            self.label_description.setText("<strong>BUILDING</strong> & <strong>TRAINING</strong> MODEL")
                            self.training()
                            # SHOW COMPLETE SIGNAL
                            QMessageBox.information(None, "Status", "Training completed.")
                            # CLOSE SPLASH SCREEN
                            self.close()
                        # INCREASE COUNTER
                        counter += 1

                    def training(self):   
                        self.progressBar.setValue(0)
                        db_path = global_ini.parent_dir
                        # ========================== Training Embeddings Function ===============================
                        def findEmbeddings():
                            #find embeddings for employee list
                            tic = time.time()
                            #-----------------------
                            pbar = tqdm(range(0, len(employees)), desc='Finding embeddings')
                            self.progressBar.setMaximum(len(employees))
                            embeddings = []
                            #for employee in employees:
                            for index in pbar:
                                self.progressBar.setValue(index)
                                
                                employee = employees[index]
                                pbar.set_description("Finding embedding for %s" % (employee.split("/")[-1]))
                                
                                embedding = []
                                #preprocess_face returns single face. this is expected for source images in db.
                                img = functions.preprocess_face(img = employee, target_size = (global_ini.input_shape_y, global_ini.input_shape_x), enforce_detection = False, detector_backend = global_ini.detector_backend)
                                img_representation = global_ini.model.predict(img)[0,:]

                                embedding.append(employee)
                                embedding.append(img_representation)
                                embeddings.append(embedding)

                            self.progressBar.setValue(index+1)
                            
                            df = pd.DataFrame(embeddings, columns = ['employee', 'embedding'])
                            df['distance_metric'] = global_ini.distance_metric

                            toc = time.time()
                            print("Embeddings found for given data set in ", toc-tic," seconds")
                            df.to_pickle("trainer/face_embeddings.pkl")
                        # =====================================================================================
                        
                        employees = []
                        #check passed db folder exists
                        if os.path.isdir(db_path) == True:
                            for r, d, f in os.walk(db_path): # r=root, d=directories, f = files
                                for file in f:
                                    if ('.jpg' in file):
                                        #exact_path = os.path.join(r, file)
                                        exact_path = r + "/" + file
                                        #print(exact_path)
                                        employees.append(exact_path)
                    
                        if len(employees) == 0:
                            QMessageBox.warning(None, "Status", "No Account Registered...")
                            print("WARNING: There is no image in this path ( ", db_path,") . Training will not be performed.")

                        if len(employees) > 0:
                            findEmbeddings()

                # ------ Run Training child-class        
                self._train_window = changeModel()
                self._train_window.show()

        else:            
            # [db]
            inifile['db']['host']=str(self.db_host.text())
            inifile["db"]["port"]=str(self.db_port.text())
            inifile["db"]["user"]=str(self.db_user.text())
            inifile["db"]["password"]=str(self.db_password.text())
            inifile["db"]["database"]=str(self.db_database.text())

            # [server]
            inifile["server"]["ip"]=str(self.server_ip.text())
            inifile["server"]["port"]=str(self.server_port.text())

            # [detection]
            inifile["detection"]["threshold"]=str(self.threshold_label.text()) #return <int> type

            # [photo]
            inifile["photo"]["number"]=str(self.num_photo.text()) #return <int> type

            # [logging]
            inifile["logging"]["logging_status"]=str(self.checkBox_logging.isChecked())

            # [machine]
            inifile["machine"]["machine_code"]=str(self.comboBox_machine.currentText())

            with open(filename, 'w') as configfile:
                inifile.write(configfile)
            
            
            global_ini.db_host = self.db_host.text()
            global_ini.db_port = self.db_port.text()
            global_ini.db_user = self.db_user.text()
            global_ini.db_password = self.db_password.text()
            global_ini.db_database = self.db_database.text()
            global_ini.threshold = float(self.threshold_label.text())
            global_ini.ip = self.server_ip.text()
            global_ini.port = self.server_port.text()
            global_ini.photo_num = self.num_photo.text()
            global_ini.checkBox_logging = self.checkBox_logging.isChecked()
            global_ini.machine_code = self.comboBox_machine.currentText()

        self.close()


 