from flask import Flask
from flask import send_file, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

import random
import time
import os
import subprocess
import threading
import base64 
import json
import requests
# import asyncio

#Custom scripts
import backend.myAPI as myAPI
import db.weather
import db.db_connect as DB


# only needed for demo with laptop
# import cv2

# SOME ENV VARIABLES
from config import PI, ROOT_DIR, GCLOUD_URL

if PI:
    import camera.camera as camera
else:
    def read():
        print('on windows')
        

CWD = os.getcwd()
app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secret!'
# CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
CORS(app)
# socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
socketio = SocketIO(app, cors_allowed_origins="*")

intrusionModel = 'yolov3'

@app.route('/')
def home():
    return myAPI.home()

@app.route('/liam')
def liamEmit():
    app.logger.info('this is the normal backend ')
    socketio.emit('liam', 'please')
    return 'this is working'
    
@app.route('/cloud')
def cloudHome():
    return requests.get(GCLOUD_URL)

# TEST API FOR NEW ENDPOINTS
@app.route('/api', methods=['GET'])
def index():
    
    # CHOOSE IMAGE TO SEND
    print('testing gcloud detection')
    filename = 'image.png'
    srcImage = ROOT_DIR+'camera/'+filename
    # srcImage = ROOT_DIR+'camera/img.png'
    
    # ENCODE IMAGE AS STRING TO POST
    with open(srcImage, 'rb') as f:
        encoded_string = base64.b64encode(f.read()).decode('utf-8')
        
    print('encoded image')
    # MAKE POST request, with the encoded image, and filename
    response = requests.post(GCLOUD_URL+'/api', 
                             json={'image': encoded_string, 'filename': 'image.png'}
                             ).json()
    
    print('got response')
    # decode the returned image
    decoded_image = base64.b64decode(response['image'].encode('utf-8'))
    
    print('decoded image')
    # write the decoded image to file
    detectImage = ROOT_DIR+'camera/output/det_'+filename
    with open(detectImage, 'wb') as f:
        f.write(decoded_image)
        
    print('about to return')
    return send_file(detectImage)
    
    
def packageImageData(imageFilename):
    # Encode image to send to the front end
    with open(imageFilename, 'rb') as f:
        encoded_string = base64.b64encode(f.read()).decode('utf-8')
    
    return {'image': encoded_string, 'filename': imageFilename}   

@app.route('/api/take/img', methods=["GET"])
def takeNewImage():
    
    filename = DB.createImageName()

    srcImage = ROOT_DIR+'camera/'+filename
    
    # TAKE IMAGE USING PI Camera
    if PI:
        camera.takePicture(srcImage)        
    
    imgData = packageImageData(srcImage)
    return jsonify(imgData)
    

def makeDetectImageRequest(requestDict):
    
    # Make filenames
    filename = requestDict['filename'].split('/')[-1]
    srcImage = ROOT_DIR+'camera/'+filename 
    detectImage = ROOT_DIR+'camera/output/det_'+filename
    
    # ENCODE IMAGE AS STRING TO POST
    with open(srcImage, 'rb') as f:
        encoded_string = base64.b64encode(f.read()).decode('utf-8')
         
    # MAKE POST request to Google VM, with the encoded image, and filename
    response = requests.post(GCLOUD_URL+'/api', 
                             json={
                                 'image': encoded_string,
                                 'filename': 'image.png',
                                 'model': intrusionModel
                                 }
                             ).json()
    
    # decode the returned image
    decoded_image = base64.b64decode(response['image'].encode('utf-8'))
    
    # write the decoded image to file
    with open(detectImage, 'wb') as f:
        f.write(decoded_image)
    
    return detectImage

@socketio.on('take/img') 
def socket_takeNewImage():
    
    print('socket_takeNewImage')
    # TAKE PICTURE, simulated with sending exisiting image
    if PI:
        filename = DB.createImageName()
        srcImage = ROOT_DIR+'camera/'+filename
        camera.takePicture(srcImage)
    else:
        filename = 'image.png'
        srcImage = ROOT_DIR+'camera/'+filename
        
    # TAKE IMAGE USING PI Camera
    # if PI:
    #     camera.takePicture(srcImage)    
    
    imgData = packageImageData(srcImage)
    socketio.emit('img', imgData)
    
    detectedImg = makeDetectImageRequest(imgData)
    imgData = packageImageData(detectedImg)
    socketio.emit('detected img', imgData)

    
@app.route('/api/detect/img', methods=["GET", "POST"])
def getDetectImage():
    print("going to detec")
    requestDict = json.loads(request.data.decode('utf-8'))     
    
    detectImage = makeDetectImageRequest(requestDict)
    
    return send_file(detectImage)

@app.route('/api/get/img', methods=["GET"])
async def getImage():
    
    filename = 'image.png'
    srcImage = ROOT_DIR+'camera/'+filename
        
    # Encode image to send to the front end
    with open(srcImage, 'rb') as f:
        encoded_string = base64.b64encode(f.read()).decode('utf-8')
    
    return jsonify({'image': encoded_string, 'filename': filename})
    
    
@app.route('/api/set/model', methods=["GET", "POST"])
def changeIntrusionModel():
    
    global intrusionModel
    requestDict = json.loads(request.data.decode('utf-8'))
    intrusionModel = requestDict['intrusionModel']
    return jsonify({'model': intrusionModel})
    

# TEST ROUTES FOR WIN DEV 
@app.route('/api/test/img', methods=["GET"])
def createImageName():
    
    filename = 'image.png'
    return captureImage(filename)

def captureImage(filename):

    srcImage = ROOT_DIR+'camera/'+filename
    dstDetectDir = ROOT_DIR+'camera/output'
    dstDetectImage = dstDetectDir+'/det_'+filename
    
    def detect_object():
        
        pythonCmd = 'python3.7' if PI else 'python'
        
        process = subprocess.Popen([pythonCmd, ROOT_DIR+"intrusion/detect.py", 
                                    '--images', srcImage,
                                    '--det', dstDetectDir, 
                                    '--root_dir', ROOT_DIR]
                                   )
        # process = subprocess.Popen(['sh', ROOT_DIR+"intrusion/detect.sh"])
    
    thread = threading.Thread(target=detect_object)
    thread.start()  
        
    with open(srcImage, 'rb') as f:
        encoded_string = base64.b64encode(f.read()).decode('utf-8')
    return jsonify({'image': encoded_string, 'filename': dstDetectImage})


@app.route('/api/test/detect', methods=["POST"])
def getDetectedImage():
    
    requestDict = json.loads(request.data.decode('utf-8'))
    
    # app.logger.info('POST FILENAME: ', requestDict['filename'])
    # file = ROOT_DIR+'camera/output/det_image.png'
    file = requestDict['filename']
    while not os.path.exists(file):
        # app.logger.info('detection not available')
        time.sleep(5)
    return send_file(file)
    
    

# Socket Hooks
@socketio.on('connect')
def handle_connect():
    print('socket connected in flask app')
    # socketio.emit('liam', 'Hello from Socket')
    socketio.emit('done connect')
    # return

@socketio.on('disconnect')
def disconnect():
    print('socket disconnected')
    
@socketio.on('connected')
def handleLiam():
    print('socket is listening ')
    socketio.emit('message', 'THIS IS FROM FLASK!!')
    
solarData = []
solarLabels = []
@socketio.on('update/solar')
def updatesolar(data):
    # socketio.emit("solar", data)
    print("new solar", data)
    solarData.append(data['value'])
    solarLabels.append(data['time'])
    
    if len(solarData) > 15:
        solarData.pop(0)
        solarLabels.pop(0)
        
    socketio.emit('solar', {
        "msg": 'Too Dark for Solar Cells' if data['msg'] != 0 else '',
        "icon": "default",
        'title': 'Solar Energy',
        'dataPoints': solarData,
        'labels': solarLabels,
        'tooltipLabel': 'km/h',
    })

windData = []
windLabels = []
@socketio.on('update/wind')
def updateWind(data):
    # socketio.emit("wind", data)
    windData.append(data['value'])
    windLabels.append(data['time'])
    
    if len(windData) > 15:
        windData.pop(0)
        windLabels.pop(0)
        
    socketio.emit('wind', {
        "msg": 'Too Windy For Wind Turbine. Turn on Brakes.' if data['msg'] != 0 else '',
        "icon": "default",
        'title': 'Wind Energy',
        'dataPoints': windData,
        'labels': windLabels,
        'tooltipLabel': 'km/h',
    })
    
@socketio.on('update/radar')
def updateRadar(data):
    # print(data)
    socketio.emit('radar', data)

@app.route('/api/status/solar', methods=["GET"])
def statusSolar():
    
    # dataPoints = [random.randint(0, 100) for i in range(9)]
    # labels = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'August']
    
    dataPoints = []
    return {
        "msg": '',
        "icon": "default",
        'title': 'Solar Energy',
        'dataPoints': solarData,
        'labels': solarLabels,
        'tooltipLabel': 'UV Index',
    }

@app.route('/api/status/wind', methods=["GET"])
def statusWind():
    # dataPoints = [ random.randint(37, 100) for i in range(9)]
    # labels = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'August']
    
    return {
        "msg": '',
        "icon": "default",
        'title': 'Wind Energy',
        'dataPoints': windData,
        'labels': windLabels,
        'tooltipLabel': 'km/h',
    }

"""
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

"""

@app.route('/api/liam', methods=["GET"])
def liam():
    
    return {'state': '23'}

if __name__ == '__main__':
    # tracemalloc.start()
    # app.run(debug=True, host='0.0.0.0')
    socketio.run(app, port=5000)
    # socketio.run(app, port=5000, websocket=True)
    
    
    
    