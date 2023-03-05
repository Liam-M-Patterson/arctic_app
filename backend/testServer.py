import socketio

sio = socketio.Server()
# server = 'http://localhost:5000'
# val = sio.connect(server)

# socket_server = socketio.Server()

@sio.on('connect')
def connect():
    print('connected to my socket')
    sio.emit('connect done')
# sio.emit('liam')

@sio.on('liam')
def connect_done():
    print('test client done connecting')
    sio.emit('liam')