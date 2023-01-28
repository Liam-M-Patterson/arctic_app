from flask import Flask
from flask import send_file
from flask_cors import CORS
import random
# from flask_sqlalchemy import SQLAlchemy
import time
import os
import asyncio
import sys

#Custom scripts
import backend.myAPI as myAPI


PI = False
if sys.platform != 'win32':
    import camera.camera as camera
    PI = True
else:
    def camera():
        def takePicture():
            print('on windows')
    def read():
        print('on windows')

CWD = os.getcwd()

app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return myAPI.home()

@app.route('/api', methods=['GET'])
def index():
    return {
        'channel': "THE ARCTIC SURVEILLENCE OPERATION",
        "tutorial": "This is using React Docker and Flask",
        'another': 'Liam Patterson',
    }
    
@app.route('/api/take/img', methods=["GET"])
def takeNewImage():
    app.logger.info('new image')
    app.logger.info(CWD)
    app.logger.info('going to take new image')
    file = 'image.png'
    dir = CWD+'/camera/'+file
    camera.takePicture(dir)
    return send_file(dir)
    
@app.route('/api/img', methods=["GET"])
def getImage():
    return send_file(CWD+'/camera/img.png')


@app.route('/api/status/solar', methods=["GET"])
def statusSolar():
    
    dataPoints = [random.randint(0, 100) for i in range(9)]
    labels = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'August']
    return {
        "direction": 'top',
        "icon": "default",
        'title': 'Solar Energy',
        'dataPoints': dataPoints,
        'labels': labels,
    }

@app.route('/api/status/wind', methods=["GET"])
def statusWind():
    dataPoints = [ random.randint(37, 100) for i in range(9)]
    labels = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'August']
    return {
        "direction": 'top',
        "icon": "default",
        'title': 'Wind Energy',
        'dataPoints': dataPoints,
        'labels': labels,
    }

@app.route('/api/status/battery', methods=["GET"])
def statusBattery():
    dataPoints = [ random.randint(37, 100) for i in range(9)]
    labels = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'August']
    return {
        "direction": 'top',
        "icon": "default",
        'title': 'Battery Reserve',
        'dataPoints': dataPoints,
        'labels': labels,
    }

    
@app.route('/api/status/led', methods=["GET"])
def getSerial():
    
    dir = CWD+'/arduino/led.txt'
    f = open(dir)
    content = f.read()
    
    dataPoints = [int(i) for i in content.split()]
    labels = ['High' if i == 1 else 'Low' for i in dataPoints]
    
    return {
        "direction": 'top',
        "icon": "default",
        'title': 'Battery Reserve',
        'dataPoints': dataPoints,
        'labels': labels,
    }


# @app.route('/api/db', methods=["GET"])
# def dbTest():
    
#     db_name = 'sensor'
#     db_user = 'root'
#     db_pass = 'password'
#     db_host = 'postgres_db'
#     db_port = '5432'

#     # Connecto to the database
#     db_string = 'postgres://{}:{}@{}:{}/{}'.format(db_user, db_pass, db_host, db_port, db_name)
#     db = SQLAlchemy.create_engine(db_string)
    
#     def add_new_row(n):
#         # Insert a new number into the 'numbers' table.
#         db.execute("INSERT INTO numbers (number,timestamp) "+"VALUES ("+str(n) + "," + str(int(round(time.time() * 1000))) + ");")

#     def get_last_row():
#         # Retrieve the last number inserted inside the 'numbers'
#         query = "" + "SELECT number " + "FROM numbers " + "WHERE timestamp >= (SELECT max(timestamp) FROM numbers)" + "LIMIT 1"

#         result_set = db.execute(query)  
#         for (r) in result_set:  
#             return r[0]
        
#     # while True:
#     add_new_row(random.randint(1,100000))
#     print('The last value insterted is: {}'.format(get_last_row()))
#         # time.sleep(5)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
