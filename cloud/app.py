from flask import Flask
from flask import send_file, request, jsonify
from flask_cors import CORS

import time
import os
import subprocess
import threading
import base64 
import json


# SOME ENV VARIABLES
from config import ROOT_DIR

CWD = os.getcwd()

app = Flask(__name__)
CORS(app)
@app.route('/', methods=["GET"])
def home():
    return "THE new CLOUD"

# original function for just yolov3
@app.route('/api', methods=["GET", "POST"])
def index():
    app.logger.info('got request')
    
    requestDict = json.loads(request.data.decode('utf-8'))
    currModel = requestDict['model'] 
    
    decoded_image = base64.b64decode(requestDict['image'].encode('utf-8'))
    filename = requestDict['filename']
    
    srcImage = ROOT_DIR+'backend/input/'+filename
    dstDetectDir = ROOT_DIR+'backend/output'
    dstDetectImage = dstDetectDir+'/det_'+filename
        
    with open(srcImage, 'wb') as f:
        f.write(decoded_image)
        
    print(currModel)
    
    if currModel == 'yolov3':
            
        cmds = ['python3', ROOT_DIR+"intrusion/detect.py", 
                                    '--images', srcImage, 
                                    '--det', dstDetectDir,
                                    '--root_dir', ROOT_DIR]
    elif currModel == 'yolov5l':
        
        cmds = ['python3', ROOT_DIR+"yolov5/detect.py", 
                                    '--source', srcImage, 
                                    '--weights', ROOT_DIR+"yolov5/weights/yolov5l.pt"]
    
    def detect_object():
        process = subprocess.Popen(cmds).wait()
    
    print('about to start thread')
    thread = threading.Thread(target=detect_object)
    thread.start()  
    thread.join()
    print('done thread')
    
    with open(dstDetectImage, 'rb') as f:
        encoded_string = base64.b64encode(f.read()).decode('utf-8')
    
    print('going to return')
    return {'image': encoded_string, 'filename': dstDetectImage, 'data': 'coming from THE CLOUD'}
    
        
    
    
@app.route('/api/take/img', methods=["GET"])
def takeNewImage():
    print("api/take/img")    
    
    srcImage, dstDetectImage = 1, 2 
        
    with open(srcImage, 'rb') as f:
        encoded_string = base64.b64encode(f.read()).decode('utf-8')
    return jsonify({'image': encoded_string, 'filename': dstDetectImage})


@app.route('/api/detect/img', methods=["GET"])
def getDetectImage():
    print("/api/detect/img")
    requestDict = json.loads(request.data.decode('utf-8'))
    
    # app.logger.info('POST FILENAME: ', requestDict['filename'])
    # file = ROOT_DIR+'camera/output/det_image.png'
    file = requestDict['filename']
    while not os.path.exists(file):
        # app.logger.info('detection not available')
        time.sleep(5)
    return send_file(file)
    
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
