import os
os.chdir(os.path.abspath(os.getcwd()))

from flask import Flask, request, session, redirect, url_for, render_template, send_file, jsonify
from flask_mysqldb import MySQL
import json
import io
import os
import shutil           
import base64                  
from PIL import Image

import configparser as cp
filename = 'serverConfig.ini'
inifile = cp.ConfigParser()
inifile.read(filename,'UTF-8')

# Initialize the Flask application
app = Flask(__name__, template_folder='template')
app.secret_key = "super secret key"

app.config['MYSQL_HOST'] = inifile.get("db","host")
app.config['MYSQL_PORT'] = inifile.getint("db","port")
app.config['MYSQL_USER'] = inifile.get("db","user")
app.config['MYSQL_PASSWORD'] = inifile.get("db","password")
app.config['MYSQL_DB'] = inifile.get("db","database")

mysql = MySQL(app)


app.config['SERVER_PATH'] = os.getcwd()
app.config['SERVER_DATASETS'] = "datasets"


@app.route('/api/connect', methods=['GET'])
def connect():
    ip_address = request.remote_addr
    return "Server IP: " + ip_address + " -> Connected Successfully"

@app.route('/api/checkSum', methods=['GET'])
def checkSum():
    return str(len(os.listdir(app.config['SERVER_DATASETS'])))

@app.route('/api/currentDir', methods=['GET'])
def currentDir():
    return str(os.getcwd())

# route http posts to this methods
@app.route('/api/register', methods=['POST'])
def register():
    
    # get the base64 encoded string
    im_b64 = request.json['image']
    
    # convert it into bytes  
    img_bytes = base64.b64decode(im_b64.encode('utf-8'))

    # convert bytes data to PIL Image object
    img = Image.open(io.BytesIO(img_bytes))

    username = request.json['username']
    userid = request.json['userid']
    count = request.json['count']
    """
     --- Saving image in server database ---
     1. Create new folder with OID number if not exists
     2. Name the picture with employee name

    """

    # path to the server database for employee face images
    #parent_dir = "D:/JH/Face Recognition Project/CSC_Server/datasets"

    
    # --- Check whether the folder is exists. --- 
    # If not, Register new folder. Else replace existing image for modification
    path = os.path.join(app.config['SERVER_DATASETS'], str(userid))

    if request.json['modify']:
        if count == 0:
            shutil.rmtree(path)

    if os.path.isdir(path):
        img.save(path + '/' + username + "-" + str(count+1) +'.jpg', quality='keep') # More shaper image: subsampling=0, quality=100

    else:
        os.mkdir(path)
        img.save(path + '/' + username + "-" + str(count+1) + '.jpg', quality='keep') # More shaper image: subsampling=0, quality=100
   
    result_dict = {'Message': 'Image received'}
    
    return result_dict


# route http posts to this method
@app.route('/api/dataSync', methods=['GET'])
def dataSync():
    
    # parent_dir = 'D:/JH/Face Recognition Project/CSC_Server/datasets'

    # export directory to zip
    shutil.make_archive('datasets','zip',app.config['SERVER_DATASETS'])

    # passing zip file
    return send_file('datasets.zip', mimetype = 'zip', download_name= 'datasets.zip', as_attachment = True)

    # Delete the zip file if not needed
    os.remove("datasets.zip")

# route http posts to this method
@app.route('/api/delete', methods=['POST'])
def delete():
    
    userid = request.json['userid']

    path = os.path.join(app.config['SERVER_DATASETS'], str(userid))

    if os.path.isdir(path):
        shutil.rmtree(path)

    result_dict = {'Message': 'Employee {} is removed'.format(userid)}    
    
    return result_dict

# @app.route("/api/query")
# def query():
#     return "Query Received"

#https://hevodata.com/learn/flask-mysql/

# ====================================== API ============================================
class create_dict(dict): 

    # __init__ function 
    def __init__(self): 
        self = dict() 
        
    # Function to add key:value 
    def add(self, key, value): 
        self[key] = value

# 1
@app.route('/api/query/employees/$<user_id>')
def employee(user_id):
    user_id=user_id
    try:
        myArray = []
        mydict = create_dict()
        cursor = mysql.connection.cursor()
        sql = "SELECT user_id, user_name, sign_in, machine FROM attendance WHERE user_id = %s ORDER BY sign_in DESC"
        val = (str(user_id), )
        cursor.execute(sql, val)
        output = cursor.fetchall()
        cursor.close()

        # ================================================================
        # for index, row in enumerate(output):
        #     mydict.add(index,({"OID":row[0],"Name":row[1],"Attendance":row[2]}))
        # stud_json = json.dumps(mydict, indent=2, sort_keys=False, default=str)
        # stud_json = jsonify(mydict)
        # print(stud_json)   
        # =================================================================

        for row in output:
            myArray.append({"OID":row[0],"Name":row[1],"Attendance":row[2],"Machine No.":row[3]})
        
        mydict.add("Records",myArray)
        stud_json = json.dumps(mydict, indent=2, sort_keys=False, default=str)
        
        # print(stud_json)
        return stud_json
            
    except Exception as e:
        return str(e)

# 2
@app.route('/api/query/employees')
def employees():

    try:
        myArray = []
        mydict = create_dict()
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT user_id, user_name, sign_in, machine FROM attendance ORDER BY sign_in DESC", )
        output = cursor.fetchall()
        cursor.close()

        for row in output:
            myArray.append({"OID":row[0],"Name":row[1],"Attendance":row[2],"Machine No.":row[3]})
        mydict.add("Records",myArray)
        stud_json = json.dumps(mydict, indent=2, sort_keys=False, default=str)
        
        # print(stud_json)
        return stud_json
            
    except Exception as e:
        return str(e)

# 3
@app.route('/api/query/employees/start=<start_date>')
def employees_date1(start_date):

    try:
        myArray = []
        mydict = create_dict()
        cursor = mysql.connection.cursor()
        sql = "SELECT user_id, user_name, sign_in, machine FROM attendance WHERE sign_in >= %s ORDER BY sign_in DESC"
        val = (start_date,)
        cursor.execute(sql, val)
        output = cursor.fetchall()
        cursor.close()

        for row in output:
            myArray.append({"OID":row[0],"Name":row[1],"Attendance":row[2],"Machine No.":row[3]})
        mydict.add("Records",myArray)
        stud_json = json.dumps(mydict, indent=2, sort_keys=False, default=str)
        
        # print(stud_json)
        return stud_json
            
    except Exception as e:
        return str(e)

# 4 
@app.route('/api/query/employees/start=<start_date>&end=<end_date>')
def employees_date2(start_date,end_date):

    try:
        myArray = []
        mydict = create_dict()
        cursor = mysql.connection.cursor()
        sql = "SELECT user_id, user_name, sign_in, machine FROM attendance WHERE sign_in BETWEEN %s AND %s ORDER BY sign_in DESC"
        val = (start_date, end_date)
        cursor.execute(sql, val)
        output = cursor.fetchall()
        cursor.close()

        for row in output:
            myArray.append({"OID":row[0],"Name":row[1],"Attendance":row[2],"Machine No.":row[3]})
        mydict.add("Records",myArray)
        stud_json = json.dumps(mydict, indent=2, sort_keys=False, default=str)
        
        # print(stud_json)
        return stud_json
            
    except Exception as e:
        return str(e)

# 5
@app.route('/api/query/employees/$<user_id>/start=<start_date>')
def employees_date3(user_id,start_date):

    try:
        myArray = []
        mydict = create_dict()
        cursor = mysql.connection.cursor()
        sql = "SELECT user_id, user_name, sign_in, machine FROM attendance WHERE (user_id = %s AND sign_in >= %s) ORDER BY sign_in DESC"
        val = (str(user_id),start_date)
        cursor.execute(sql, val)
        output = cursor.fetchall()
        cursor.close()

        for row in output:
            myArray.append({"OID":row[0],"Name":row[1],"Attendance":row[2],"Machine No.":row[3]})
        mydict.add("Records",myArray)
        stud_json = json.dumps(mydict, indent=2, sort_keys=False, default=str)
        
        # print(stud_json)
        return stud_json
            
    except Exception as e:
        return str(e)

# 6
@app.route('/api/query/employees/$<user_id>/start=<start_date>&end=<end_date>')
def employees_date4(user_id,start_date,end_date):

    try:
        myArray = []
        mydict = create_dict()
        cursor = mysql.connection.cursor()
        sql = "SELECT user_id, user_name, sign_in, machine FROM attendance WHERE (user_id = %s AND sign_in BETWEEN %s AND %s) ORDER BY sign_in DESC"
        val = (str(user_id),start_date, end_date)
        cursor.execute(sql, val)
        output = cursor.fetchall()
        cursor.close()

        for row in output:
            myArray.append({"OID":row[0],"Name":row[1],"Attendance":row[2],"Machine No.":row[3]})
        mydict.add("Records",myArray)
        stud_json = json.dumps(mydict, indent=2, sort_keys=False, default=str)
        
        # print(stud_json)
        return stud_json
            
    except Exception as e:
        return str(e)

# 7
@app.route('/api/query/registeredEmployees')
def registeredEmployees():

    try:
        myArray = []
        mydict = create_dict()
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT user_id, user_name, user_ic FROM employee ORDER BY user_id+0", )
        output = cursor.fetchall()
        cursor.close()

        for row in output:
            myArray.append({"OID":row[0],"Name":row[1],"IC Number":row[2]})

        mydict.add("Employees",myArray)
        stud_json = json.dumps(mydict, indent=2, sort_keys=False)
        
        # print(stud_json)
        return stud_json
            
    except Exception as e:
        return str(e)

# ========================== Login Flask Web Attendance ============================
@app.route('/')
def index():
   return render_template('login.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    msg=""
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']

        if len(username)==0 or len(password)==0:
            msg = "Please fill in all required fields"
            return render_template('login.html',info=msg)

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s",(username,password,))
        output = cursor.fetchone()
        cursor.close()
        if output:
            session['loggedin']=True
            session['username']=output[1]
            return redirect(url_for('home'))
        else:
            msg = "Invalid username or password"
    return render_template('login.html',info=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('username',None)
    return redirect(url_for('login'))

@app.route('/home')
def home():
    return render_template('home.html', username=session['username'])

### Result checker html page 
@app.route('/home/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        if request.form['two_buttons']=='Show All Attendances':
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT user_id, user_name, sign_in, machine FROM attendance", )
            output = cursor.fetchall()
            cursor.close()
            return render_template('home.html', data=output, queryType=1, username=session['username']) 
        elif request.form['two_buttons']=='Show All Employees':
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT user_id, user_name, user_ic FROM employee ORDER BY user_id+0", )
            output = cursor.fetchall()
            cursor.close()
            return render_template('home.html', data=output, queryType=2, username=session['username']) 
        else:    
            user_id = request.form['user_id']
            if len(user_id) == 0:
                user_id=0 
        res=""
        return redirect(url_for('user_id',user_id=str(user_id)))


@app.route('/home/submit/$<user_id>') #<string:> <int:>
def user_id(user_id):
    user_id= user_id
    try:
        cursor = mysql.connection.cursor()
        sql = "SELECT user_id, user_name, sign_in, machine FROM attendance WHERE user_id = %s ORDER BY sign_in ASC"
        val = (str(user_id), )
        cursor.execute(sql, val)
        output = cursor.fetchall()
        cursor.close()

        return render_template('home.html', data=output, queryType=1, username=session['username'])
            
    except Exception as e:
        return ()

# import logging
# import sys
# # logging.basicConfig(filename='record.log', level=logging.DEBUG, format=f'%(message)s')
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# app.run(host="192.168.217.29")

app.run(host="0.0.0.0", port=5000,threaded=True)