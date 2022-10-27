from interfaces import global_initialize as global_ini
import cv2
import os
import pandas as pd
import qimage2ndarray
import time
import requests
import base64
import json
from tqdm import tqdm

from src.commons import functions
from src.detectors import FaceDetector

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi


# ----------------------------------Registration Windows-----------------------------------
class regWindow(QDialog):
    def __init__(self):
        super(regWindow, self).__init__()
        loadUi("ui/reg.ui", self)
        self.setWindowIcon(QIcon('faceid.ico'))
        timer = QTimer(self)
        timer.timeout.connect(self.displayPre)
        timer.start(1)
        self.messlabel.setText("Before pressing capture button, please MAKE SURE your face has a blue rectangle...")
        self.RegButton.clicked.connect(self.datasets)
        self.CaptureButton.clicked.connect(self.capture)
        self.TrainButton.clicked.connect(self.training)
        self.progressBar.setVisible(False)
        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)
    
    # Left-hand side video frame

    
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
        
    
    def datasets(self):
        self.progressBar.setVisible(False)
        self.progressBar.setMaximum(int(global_ini.photo_num)) # Number of images capture
        self.progressBar.setValue(0)

        user_id = self.userID.text()
        user_name = self.userName.text()
        user_ic = self.userIC.text()

        # Consistency to keep all name upper case
        user_name = user_name.upper()
        
        directory = str(user_id)
        expath = os.path.join(global_ini.parent_dir, directory)
        
        if len(str(user_name)) == 0 or len(str(user_id)) == 0  or len(str(user_ic)) == 0:
            self.messlabel.setText("Warning !!! Please fill in all the information required...")
        # -------------------------------- Maybe Need Modify ----------------------------    
        elif os.path.isdir(expath): # use parent dir to justify whether ID has been created
            self.messlabel.setText("Warning !!! This User ID has been used... Please Enter Again")
            self.userID.clear()
        # --------------------------------------------------------------------------------
        elif not len(str(user_id)) == 6 :
            self.messlabel.setText("Warning !!! The User ID should be 6 characters... Please Enter Again")
            self.userID.clear()
        elif not(user_ic.isnumeric()) or len(str(user_ic)) != 12:
            self.messlabel.setText("Warning !!! The User IC is Invalid... Please Enter Again")
            self.userIC.clear()
        else:
            sql = "INSERT INTO employee (user_id, user_name, user_ic) VALUES (%s, %s, %s)"
            val = (user_id, user_name, user_ic)

            try:
                global_ini.mycursor.execute(sql, val)
            except Exception as e:
                QMessageBox.critical(None, "Error", str(repr(e)+"<br><br> Please contact Admin to delete this user."))
                return

            global_ini.mydb.commit()

            # r = request.put()

            self.messlabel.setText("Please process to capture image...")
            self.RegButton.setEnabled(False)
            self.CaptureButton.setEnabled(True)
            self.BackButton.setEnabled(False)

    def capture(self):
        self.progressBar.setVisible(True)

        user_id = (str(self.userID.text()))
        user_name = (str(self.userName.text()))
        user_name = user_name.upper()

        path = os.path.join(global_ini.parent_dir, str(user_id))
        os.mkdir(path)
        
        count = 0

        while(True):
            
            if count >= 1:
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
                        payload = json.dumps({'image':img_b64, 'username':user_name, 'userid':user_id, 'count':count, 'modify':False})
                        # send http request with image and receive response
                        response = requests.post(global_ini.reg_url, data=payload, headers=headers)
                        print(response.text)
                        # ============================================================
                        count +=1
                        self.progressBar.setValue(count)
                        break

                
            if count >=int(global_ini.photo_num):
                break
            
        self.messlabel.setText("You Had Successfully Register...")
        self.RegButton.setEnabled(True)
        self.CaptureButton.setEnabled(False)
        self.TrainButton.setEnabled(True)
        self.userID.clear()
        self.userName.clear()
        self.userIC.clear()
        
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
            print("WARNING: There is no image in this path ( ", db_path,") . Training will not be performed.")
            self.TrainButton.setEnabled(False)
            self.BackButton.setEnabled(True)
            self.messlabel.setText("No Account Registered...")

        if len(employees) > 0:
            findEmbeddings()
            self.messlabel.setText("The Training Process Had Done...")
            self.TrainButton.setEnabled(False)
            self.BackButton.setEnabled(True)

       
    def closeEvent(self, event):
        if self.CaptureButton.isEnabled():
            close = QMessageBox()
            close.setWindowTitle("Action Required!")
            close.setIcon(QMessageBox.Warning)
            close.setText("Please Press On The <strong>Capture Image</strong> Button...")
            close.setStandardButtons(QMessageBox.Ok)
            close = close.exec()

            if close == QMessageBox.Ok:
                event.ignore() 

        elif self.TrainButton.isEnabled():
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