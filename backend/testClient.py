import socketio
import asyncio
import db.db_connect as DB
import arduino.sensorLogic as sensor
import datetime 
import sys

async def init():
    sio = socketio.AsyncClient()
    server = 'http://127.0.0.1:5000'
       
    await sio.connect(server)
    
    return sio

async def main():
    
    sio = await init()
    
    await sio.emit('take img')
    

    # @sio.img
    # def gotImage(data):
    #     print('got raw img')
    #     print(data)
        
    # @sio.on('detected img')
    # def gotDetectedImg(data):
    #     print('detected the image', data)

    # @sio.on('message')
    # def connect_done(msg):
    #     print('test client done connecting')
    #     print(msg)
    #     sio.emit('liam')

if __name__ == '__main__':
    # asyncio.run(main())
    
    angle = sys.argv[1]
    
    
    msgs = DB.getLidarMessages(datetime.datetime.utcnow())
    print(msgs)
    
    DB.addMessagetoSendArduino(sensor.sendLidar(10, angle))
    
    msgs = DB.getLidarMessages(datetime.datetime.utcnow())
    for msg in msgs:
        print(msg[1])