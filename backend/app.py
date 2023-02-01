from flask import Flask
from flask import send_file, request, jsonify
from flask_cors import CORS
import random
# from flask_sqlalchemy import SQLAlchemy
import time
import os
import asyncio
import sys

#Custom scripts
import backend.myAPI as myAPI
import db.weather
import db.db_connect as DB


# SOME ENV VARIABLES
from config import PI, ROOT_DIR

if PI:
    import camera.camera as camera
else:
    def camera():
        def takePicture():
            print('on windows')
    def read():
        print('on windows')

CWD = os.getcwd()
print(PI, ROOT_DIR)

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
    app.logger.info(ROOT_DIR)
    app.logger.info('going to take new image')
    
    dir = ROOT_DIR+'camera/image.png'
    app.logger.info(dir)
    camera.takePicture(dir)
    return send_file(dir)
    
@app.route('/api/img', methods=["GET"])
def getImage():
    return send_file(ROOT_DIR+'camera/image.png')


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
        'tooltipLabel': 'UV Index',
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
        'tooltipLabel': 'km/h',
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
        'tooltipLabel': '%',
    }

    
@app.route('/api/status/led', methods=["GET"])
def getSerial():
    
    data = DB.getLED()
    app.logger.warn(data)
    
    labels = ['High' if i == 1 else 'Low' for i in data]
    
    return {
        "direction": 'top' if data[-1] == 1 else 'bottom',
        "icon": "default",
        'title': 'LED LIGHT',
        'dataPoints': data,
        'labels': labels,
        'tooltipLabel': 'State',
    }

    
@app.route('/api/status/ledTime', methods=["GET"])
def getLedTime():
    
    data = DB.getLED()
    app.logger.warn(data)
    
    labels = ['Higher' if i == 1 else 'Lower' for i in data]
    
    return {
        "direction": 'top' if data[-1] == 1 else 'bottom',
        "icon": "default",
        'title': 'LED LIGHT',
        'dataPoints': data,
        'labels': labels,
        'tooltipLabel': 'State',
    }

@app.route('/api/update/led', methods=["GET"])
def updateLED():
    
    data = request.args.get('message')
    DB.addMessagetoSendArduino(data)
    
    return {'data': data}
    
@app.route('/api/weather', methods=["GET"])
def weather():
    return db.weather.getWeather()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')