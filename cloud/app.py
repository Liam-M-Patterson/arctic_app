from flask import Flask
from flask import request
from flask_cors import CORS

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
    return "THE CLOUD"

@app.route('/api', methods=["GET", "POST"])
def index():
    
    requestDict = json.loads(request.data.decode('utf-8'))
    
    decoded_image = base64.b64decode(requestDict['image'].encode('utf-8'))
    filename = requestDict['filename']
    
    srcImage = ROOT_DIR+'backend/input/'+filename
    dstDetectDir = ROOT_DIR+'backend/output'
    dstDetectImage = dstDetectDir+'/det_'+filename
    
    with open(srcImage, 'wb') as f:
        f.write(decoded_image)
        
    pythonCmd = 'python3'
    
    def detect_object():
        process = subprocess.Popen([pythonCmd, ROOT_DIR+"intrusion/detect.py", 
                                    '--images', srcImage, 
                                    '--det', dstDetectDir,
                                    '--root_dir', ROOT_DIR]
                                   ).wait()
    
    thread = threading.Thread(target=detect_object)
    thread.start()  
    thread.join()
    
    with open(dstDetectImage, 'rb') as f:
        encoded_string = base64.b64encode(f.read()).decode('utf-8')
    
    return {'image': encoded_string, 'filename': dstDetectImage, 'data': 'coming from THE CLOUD'}
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
