# casa_di_polizia

The aim of this project is to develop an online police database management system which can be easily accessed  by the police personnel to manage crime and criminal records. 
The system allows the admin to create police records and allows them to set an unique police ID and password. Using these credentials the police can add, delete or update crime and criminal records. This project aims to make the process of record management in a police station streamlined and efficient.
Our project provides CRUD functionalities like adding, deleting and editing criminal and case records. In addition to this, we have also included some analysis based on the locality of crime report, active criminals and a timeline to help the police identify crime prone areas and make necessary changes.
We used PostgreSQL, Python Flask framework, HTML, CSS, JavaScript to develop this responsive website.

ER diagram of the database
![image](https://user-images.githubusercontent.com/77486930/203808600-e4c49a97-49e8-4537-bf5c-1c58ab794fb7.png)


# How to use

Download postgresql and create a database : https://www.youtube.com/watch?v=tu7zuv6aMug

Create tables with sql queries in the queries.txt file

Download the required pacakges using the following command: 
pip install -r requirements.txt

Run using: 
python crimeDB.py
