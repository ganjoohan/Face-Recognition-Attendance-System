# Face-Recognition-Attendance-System
A project that utilizes deepface and deep learning techniques to recognize human faces to facilitate attendance records.


## Set up Database server
Step to Set Up XAMPP for MariaDB database. MariaDB is very similar to MySQL but they are not the same. 

Step 1: Download XAMPP https://www.apachefriends.org/index.html


Step 2: Apache -> config -> Apache (httpd-xampp.conf)   
Change Require local -> Require all granted


Step 3: Change the bind address to "0.0.0.0", allow for "remote access"


Step 4:  
  
Username: admin  
Password: admin  
Host name: % (actually is your local device name, can check using mysql workbench)  


Step 5: Create database & data table
```sql
CREATE DATABASE face_recognition_system;

CREATE TABLE IF NOT EXISTS employee(
	user_id varchar(6) NOT NULL, 
	user_name varchar(25) NOT NULL, 
	user_ic varchar(12) NOT NULL,
	PRIMARY KEY (user_id)
);
TRUNCATE TABLE employee;

CREATE TABLE IF NOT EXISTS admin(
	id INT NOT NULL AUTO_INCREMENT,
	username VARCHAR(100) NOT NULL, 
	password VARCHAR(100) NOT NULL, 
	PRIMARY KEY (id)
);
TRUNCATE TABLE admin;

CREATE TABLE IF NOT EXISTS attendance(
	user_id varchar(6) NOT NULL, 
	user_name varchar(25) NOT NULL, 
	sign_in DATETIME NOT NULL,
	machine varchar(1) NOT NULL,
);
TRUNCATE TABLE attendance;

INSERT INTO admin(username , password) values ('admin', 'admin123');
INSERT INTO admin(username , password) values ('admin2', 'admin456');
INSERT INTO admin(username , password) values ('admin3', 'admin789');

INSERT INTO employee(user_id , user_name, user_ic) values ('1', 'GAN JOO HAN', '001207040021');
```
***   

![image](https://user-images.githubusercontent.com/57710546/198226559-d20b3264-520d-4a0f-a08d-b1710d966096.png)
