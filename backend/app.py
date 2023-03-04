from flask import Flask
from flask import send_file, request, jsonify
from flask_cors import CORS

import random
import time
import os
import subprocess
import threading
import base64 
import json
import requests

#Custom scripts
import backend.myAPI as myAPI
import db.weather
import db.db_connect as DB


# only needed for demo with laptop
import cv2

# SOME ENV VARIABLES
from config import PI, ROOT_DIR, GCLOUD_URL

if PI:
    import camera.camera as camera
else:
    def read():
        print('on windows')
        
# def takePicture():
#     cam = cv2.VideoCapture(0)
    
#     cv2.namedWindow("test")
    
#     print('on windows')
CWD = os.getcwd()
# print(PI, ROOT_DIR)

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return myAPI.home()

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
    
    

@app.route('/api/take/img', methods=["GET"])
def takeNewImage():
    
    filename = DB.createImageName()

    srcImage = ROOT_DIR+'camera/'+filename
    
    # TAKE IMAGE USING PI Camera
    if PI:
        camera.takePicture(srcImage)        
        
    # Encode image to send to the front end
    with open(srcImage, 'rb') as f:
        encoded_string = base64.b64encode(f.read()).decode('utf-8')
    
    return jsonify({'image': encoded_string, 'filename': filename})
    
@app.route('/api/detect/img', methods=["GET", "POST"])
def getDetectImage():
    
    requestDict = json.loads(request.data.decode('utf-8'))
    # Make filenames
    filename = requestDict['filename']
    srcImage = ROOT_DIR+'camera/'+filename
    detectImage = ROOT_DIR+'camera/output/det_'+filename
    
    # ENCODE IMAGE AS STRING TO POST
    with open(srcImage, 'rb') as f:
        encoded_string = base64.b64encode(f.read()).decode('utf-8')
         
    # MAKE POST request to Google VM, with the encoded image, and filename
    response = requests.post(GCLOUD_URL+'/api', 
                             json={'image': encoded_string, 'filename': 'image.png'}
                             ).json()
    
    # decode the returned image
    decoded_image = base64.b64decode(response['image'].encode('utf-8'))
    
    # write the decoded image to file
    with open(detectImage, 'wb') as f:
        f.write(decoded_image)
    
    return send_file(detectImage)

@app.route('/api/get/img', methods=["GET"])
async def getImage():
    
    filename = 'image.png'
    srcImage = ROOT_DIR+'camera/'+filename
        
    # Encode image to send to the front end
    with open(srcImage, 'rb') as f:
        encoded_string = base64.b64encode(f.read()).decode('utf-8')
    
    return jsonify({'image': encoded_string, 'filename': filename})
    
    
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

    # return send_file(ROOT_DIR+'camera/image.png')
    # return jsonify({'image': ROOT_DIR+'camera/image.png', 'file': filename})
    # return jsonify({'image': send_file(ROOT_DIR+'camera/image.png'), 'file': filename})


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

@app.route('/api/liam', methods=["GET"])
def liam():
    
    return {'state': '2'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')