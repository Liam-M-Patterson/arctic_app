from flask import Flask, render_template
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)
CORS(app, origins="http://localhost:5000")
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/home')
def home():
    return {
        'title': 'ARCTIC SURVEILLENCE OPERATION LANDING PAGE!', 
    }

@socketio.on('liam')
def handle_connect():
    app.logger.info('socket is listening myAPI')
    # socketio.emit('message', 'Hello from Socket')
    
if __name__ == '__main__':
    socketio.run(app, port='2000')
    