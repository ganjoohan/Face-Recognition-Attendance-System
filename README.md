# Face-Recognition-Attendance-System
A project that utilizes deepface and deep learning techniques to recognize human faces to facilitate attendance records.

## Demo - Youtube Video
Link to video: https://youtu.be/PIPWR7Ub3TQ  
<a href="https://youtu.be/PIPWR7Ub3TQ">
  <img src="https://img.youtube.com/vi/PIPWR7Ub3TQ/hqdefault.jpg" alt="Rick Astley - Never Gonna Give You Up music video" />
</a>




## Some Screencaps


![image](https://user-images.githubusercontent.com/57710546/211441183-2f326942-f83c-49ca-b576-c2a5f30d35bd.png)  
*Figure 1: Main Screen*   
&nbsp;
  
![image](https://user-images.githubusercontent.com/57710546/211441445-bf40ed95-370f-47f8-a5e2-1ed8906e3319.png)  
*Figure 2: Face Recognition record attendance Screen*   
&nbsp;

![image](https://user-images.githubusercontent.com/57710546/211441206-a67428a4-a457-4b3c-89e3-e2a983761e94.png)   
*Figure 3: Admin Login Screen*     
&nbsp;

![image](https://user-images.githubusercontent.com/57710546/211441240-f5723031-754d-46d2-acde-ea411c635505.png)   
*Figure 4: Admin Screen*  
&nbsp;

![image](https://user-images.githubusercontent.com/57710546/211441373-a7584585-6a12-45a0-9663-86a69d723493.png)  
*Figure 5: Registration Screen*  
&nbsp;

![image](https://user-images.githubusercontent.com/57710546/211441152-3d223547-09bd-466b-8a21-5927c0f84701.png)   
*Figure 6: Logging feature of Recognition Error in Excel file*   
&nbsp;

#### Webpage
![image](https://user-images.githubusercontent.com/57710546/211443272-ffa3ff9e-2076-407e-b01b-ef79fe3fc81c.png)
*Figure 7: Web App Login Screen*  
&nbsp;

![image](https://user-images.githubusercontent.com/57710546/211443425-148a1f8e-aaa1-47c9-b6ff-521afc60a198.png)
*Figure 8: Web App Home Screen*  
&nbsp;

![image](https://user-images.githubusercontent.com/57710546/211443531-ee8eda89-1938-4d7f-a32c-608312fb0148.png)
*Figure 9: Query Attendance from Web App*  
&nbsp;

![image](https://user-images.githubusercontent.com/57710546/211443611-bdcafa67-3bcb-49f0-81c3-eb82939ef89a.png)
*Figure 10: Webhook feature*  
&nbsp;

![image](https://user-images.githubusercontent.com/57710546/211443771-6a28e685-9164-4a5a-bae8-65b1a0ab6601.png)
*Figure 11: Hosting Server by Flask*
&nbsp;

## Set up Database server
Step to Set Up XAMPP for MariaDB database. MariaDB is very similar to MySQL but they are not the same. 

Step 1: Download XAMPP & Install. You can choose to install Apache and MySQL only.
https://www.apachefriends.org/index.html   

Step 2: Type in “XAMPP” in your Windows search and open the application. 
Click Apache -> Config -> Apache (httpd-xampp.conf) 
Change Require local -> Require all granted
  
Step 3: Allow “remote access” for the database server so that other devices which operates at the same network can access to the database. 
Click Config -> my.ini
Change the bind address from “127.0.0.1” to "0.0.0.0", to allow for remote access in the same network. 
  
Step 4: Config Apache (config.inc.php) and add line "$cfg['Servers'][$i]['port'] = '3306';" according to your define port. If your port is '5100', then change '3306' to '5100'. Alert: Please choose a valid port to serve the database server. By default, is 3306, but some might had used 3306.
 
Step 5: Start up the Apache and MySQL server. Click MySQL -> Admin to open phpMyAdmin. You can create, modify, delete the database in this interface. 
   
Step 6: Go to User Accounts to add new username and password for database host in XAMPP so other devices in the same network can access.
Username: admin
Password: admin
Host name: % (actually is your local device name, can check using mysql workbench)

Step 7: Create database & data table (Go to SQL, paste below query, click Go)

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
	machine varchar(1) NOT NULL
);
TRUNCATE TABLE attendance;

CREATE TABLE IF NOT EXISTS webhook_table(
	url varchar(2083) NOT NULL UNIQUE, 
	status varchar(25) NOT NULL, 
	event varchar(25) NOT NULL,
	created date NOT NULL,
	updated date NOT NULL
);
TRUNCATE TABLE webhook_table;

INSERT INTO admin(username , password) values ('admin', 'admin123');
INSERT INTO admin(username , password) values ('admin2', 'admin456');
INSERT INTO admin(username , password) values ('admin3', 'admin789');

INSERT INTO employee(user_id , user_name, user_ic) values ('A22801', 'GAN JOO HAN', '123456789012');
INSERT INTO employee(user_id , user_name, user_ic) values ('A22802', 'SON HEUNG-MIN', '940424040023');
INSERT INTO employee(user_id , user_name, user_ic) values ('A22803', 'WANG JUN KAI', '991011037891');
INSERT INTO employee(user_id , user_name, user_ic) values ('A22804', 'ARTETA', '740425090231');
```

***   

![image](https://user-images.githubusercontent.com/57710546/198935580-0bfd3fae-b1f6-4edd-9510-9608b5b5d78a.png)
