from interfaces import global_initialize as global_ini
from interfaces import database
import cv2
import os
import pandas as pd
import qimage2ndarray
import time
import requests
import base64
import json
from tqdm import tqdm
import re
import shutil

from src.commons import functions
from src.detectors import FaceDetector

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi


# --------------------------------------Modify Windows--------------------------------------

class modWindow(QDialog):
    def __init__(self):
        super(modWindow, self).__init__()
        loadUi("ui/modify.ui", self)
        self.setWindowIcon(QIcon('faceid.ico'))
        timer = QTimer(self)
        timer.timeout.connect(self.displayPre)
        timer.start(10)
        self.messlabel.setText("To modify the account, please MAKE SURE your face has a blue rectangle...")
        self.progressBar.setVisible(False)
        self.ModButton.clicked.connect(self.modify)
        self.RemButton.clicked.connect(self.removeAcc)
        self.TrainButton.clicked.connect(self.training)
        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)

    def displayPre(self):
        ret, img = global_ini.cap.read()
        img = cv2.flip(img,1)

        try:
            #faces store list of detected_face and region pair
            faces = FaceDetector.detect_faces(global_ini.face_detector, global_ini.detector_backend, img, align = True)
        except: #to avoid exception if no face detected
            faces = []

        for face, (x, y, w, h) in faces:
            if w > 130: #discard small detected faces

                cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2) #draw rectangle to main image

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image = qimage2ndarray.array2qimage(img)
        self.videolabel.setPixmap(QPixmap.fromImage(image))
        
    def modify(self):
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(int(global_ini.photo_num))
        
        user_id = (str(self.userID.text()))

        path = os.path.join(global_ini.parent_dir, str(user_id))


        if len(str(user_id)) == 0:
            self.progressBar.setVisible(False)
            self.messlabel.setText("Warning!!! Please fill in the user id...")

        elif os.path.isdir(path):
            
            user_name = re.sub('-[0-9]', '', os.listdir(path)[0].replace(".jpg", "")) # listdir inside /user_id/ folder and get image name
            
            msg = QMessageBox()
            msg.setWindowTitle("Confirm Modification")
            msg.setText("Are you sure you want to modify "+"<strong>\""+user_name+"\"</strong> ?")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
            msg.setDefaultButton(QMessageBox.Yes)

            x = msg.exec()
            
            if x == QMessageBox.Yes:
                
                shutil.rmtree(path) # remove whole /folder/image.jpg
                os.mkdir(path) # make whole /folder/
                
                self.progressBar.setVisible(True)
                
                count = 0
                while(True):
                    if count == 0:
                        QMessageBox.information(None, "Capture Face", "Ready to capture...")
                    elif count >= 1:
                        QMessageBox.information(None, "Capture Face", "Proceed to capture photo No. <strong>{}</strong> <br><br><strong>Noted:</strong> If you wear glasses, please take an extra photo with the glasses off.".format(count+1))
                    
                    ret, img = global_ini.cap.read()
                    img = cv2.flip(img,1)
                    
                    try:
                        #faces store list of detected_face and region pair
                        faces = FaceDetector.detect_faces(global_ini.face_detector, global_ini.detector_backend, img, align = True)
                    except: #to avoid exception if no face detected
                        faces = []
                        
                    if len(faces)==0:
                        QMessageBox.information(None, "Capture Face", "<strong>No face detected</strong>. Please try again.", QMessageBox.Retry)
                        continue
                    
                    elif len(faces)==1:
                        for face, (x, y, w, h) in faces:
                            if w > 130: #discard small detected faces                
                                
                                cv2.imwrite(path + '/' + str(user_name) + "-" + str(count+1) + ".jpg", img)
                                
                                # =============== Send image to server =======================
                                image_file = path + '/' + str(user_name) + "-" + str(count+1) + ".jpg"
                                
                                with open(image_file, 'rb') as f:
                                    img_bytes = f.read()
                                img_b64 = base64.b64encode(img_bytes).decode("utf8")
                                headers = {'content-type': 'application/json', 'Accept':'text/plain'}
                                payload = json.dumps({'image':img_b64, 'username':user_name, 'userid':user_id, 'count':count, 'modify':True})
                                # send http request with image and receive response
                                response = requests.post(global_ini.reg_url, data=payload, headers=headers)
                                print(response.text)
                                # ============================================================
                                count +=1
                                self.progressBar.setValue(count)
                                break

                        
                    if count >=int(global_ini.photo_num):
                        self.messlabel.setText("\""+user_name+"\" 's dataset had been successfully modify...")
                        self.TrainButton.setEnabled(True)
                        self.BackButton.setEnabled(False)
                        self.userID.clear()                        
                        break
                    
            else:
                self.messlabel.setText("Abort modifying...")
                self.userID.clear()

        elif not len(str(user_id)) == 6:
            self.messlabel.setText("Warning !!! The User ID should be 6 characters... Please Enter Again")
            self.userID.clear()

        else:
            self.messlabel.setText("Invalid User ID... Please enter again")
            self.userID.clear()
            
    def removeAcc(self):
        user_id = (str(self.userID.text()))
        
        path = os.path.join(global_ini.parent_dir, str(user_id))
        
        if len(str(user_id)) == 0:
            self.messlabel.setText("Warning!!! Please fill in the user id...")
        elif os.path.isdir(path):
            
            user_name = re.sub('-[0-9]', '', os.listdir(path)[0].replace(".jpg", "")) # listdir inside /user_id/ folder and get image name
            
            msg = QMessageBox()
            msg.setWindowTitle("Delete Account")
            msg.setText("Are you sure you want to delete "+"<strong>\""+user_name+"\"</strong> ? \nThis will permanently erase the account.")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
            msg.setDefaultButton(QMessageBox.Yes)

            x = msg.exec()
            
            if x == QMessageBox.Yes:
                # =================== Remove employee image in server ====================
                headers = {'content-type': 'application/json', 'Accept':'text/plain'}
                payload = json.dumps({'userid':user_id})
                # send http request with image and receive response
                response = requests.post(global_ini.del_url, data=payload, headers=headers)
                print(response.text)
                # ========================================================================
                
                shutil.rmtree(path)
                
                sql = "DELETE FROM employee WHERE user_id = %s"
                val = (user_id, )
                global_ini.mycursor.execute(sql, val)
                global_ini.mydb.commit()
                
                self.messlabel.setText("\""+user_name+"\" account had been successfully remove.")
                self.TrainButton.setEnabled(True)
                self.BackButton.setEnabled(False)
                self.userID.clear()
            else:
                self.messlabel.setText("Cancel deletion...")
                self.userID.clear()                
        elif os.path.isdir(path)!=True:
            try:
                global_ini.mycursor.execute("SELECT user_name FROM employee WHERE user_id = %s", (user_id,))
                checkUserOutput = global_ini.mycursor.fetchone()              
                if checkUserOutput is not None:
                    for n in checkUserOutput:
                        username = n
                    sql = "DELETE FROM employee WHERE user_id = %s"
                    val = (user_id, )
                    global_ini.mycursor.execute(sql, val)
                    global_ini.mydb.commit()
                    self.messlabel.setText("\""+username+"\" account had been successfully remove.")
                    self.userID.clear()
                else:
                    self.messlabel.setText("Invalid User ID... Please enter again")
                    self.userID.clear()                    
            except Exception as e:
                print(e)
                self.messlabel.setText("Invalid User ID... Please enter again")
                self.userID.clear()

        elif not len(str(user_id)) == 6:
            self.messlabel.setText("Warning !!! The User ID should be 6 characters... Please Enter Again")
            self.userID.clear()
        else:
            self.messlabel.setText("Invalid User ID... Please enter again")
            self.userID.clear()

    def training(self):
        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)   
                
        db_path="datasets"

        def findEmbeddings():
            #find embeddings for employee list
            tic = time.time()
            
            #-----------------------
            pbar = tqdm(range(0, len(employees)), desc='Finding embeddings')
            self.progressBar.setMaximum(len(employees))
            self.progressBar.setVisible(True)
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
            self.TrainButton.setEnabled(False)
            self.BackButton.setEnabled(True)
            self.messlabel.setText("No Account Registered...")
            print("WARNING: There is no image in this path ( ", db_path,") . Training will not be performed.")

        if len(employees) > 0:
            findEmbeddings()
            self.messlabel.setText("The Training Process Had Done...")
            self.TrainButton.setEnabled(False)
            self.BackButton.setEnabled(True)
        
    def closeEvent(self, event):
        if self.TrainButton.isEnabled():
            close = QMessageBox()
            close.setWindowTitle("Action Required!")
            close.setIcon(QMessageBox.Warning)
            close.setText("Please Press On The <strong>Perform Training</strong> Button...")
            close.setStandardButtons(QMessageBox.Ok)
            close = close.exec()

            if close == QMessageBox.Ok:
                event.ignore()

        else:
            event.accept()
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
