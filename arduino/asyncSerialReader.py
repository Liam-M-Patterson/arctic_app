import asyncio
import serial_asyncio
import sys
import db.db_connect as DB
import datetime 
import aiohttp
import socketio
import arduino.sensorLogic as sensor
import random
import time
import math

from collections import deque

# SOME ENV VARIABLES
from config import PI, ROOT_DIR

DEBUG = False

def socketInit():
    sio = socketio.Client()
    server = 'http://localhost:5000'
    sio.connect(server)
    
    # print('done test client')
    return sio

async def sendLidar(lidar, msgs: deque):
    
    if len(msgs) > 0:
        
        msg = msgs.popleft()
        if DEBUG:
            print("sending lidar", msg)
        lidar.write(msg.encode())
        await asyncio.sleep(0.5)
        
        # make sure to set lidarReady to false
        return False
    
    return True
        
    
async def send(w1, w2=None):
    
    msgs = DB.getArduinoMessages(datetime.datetime.utcnow())
    
    for msg in msgs:
    
        if DEBUG:
            print('Sending', msg)
        id, message, *_ = msg
        
        message += '\n'
        
        w1.write(message)
        DB.setArduinoMessageSent(id)
        
        if DEBUG:
            print(f'added: {message.encode().rstrip()}')
        # await asyncio.sleep(0.5)
    # print('done sending')

async def addDBLidarMessagesToQueue(msgs: deque):
    # print('in db msgs')
    db_msgs = DB.getArduinoMessages(datetime.datetime.utcnow())
    
    if DEBUG and (len(db_msgs)):
        print("add msgs to queue")
        print('exisiting queue', msgs)    
        print('new msgs', db_msgs)
    
    for msg in db_msgs:
    
        id, message, *_ = msg
        
        message += '\n'
        
        msgs.append(message)
        DB.setArduinoMessageSent(id)
        
        if DEBUG:
            print(f'sent: {message.rstrip()}')
        await asyncio.sleep(0.5)
        
    # print('new queue length', len(msgs))

    
async def recv(r):
    
    msg = await r.readuntil(b'\n')
    if DEBUG and msg.rstrip() == b'DONE':
        print('Done receiving')
        
    try:
        data = msg.rstrip().decode()
    except: 
        print(msg, " is not encoded properly")
        data = ''
    
    # try:
    #     data = msg.rstrip().decode('utf-8')
    # except: 
    #     print(msg, " is not encoded properly")
    #     data = ''
    
    if DEBUG:    
        print(f'received: {data}')
    
    # DB.updateLED(data)
    return data

        
async def myReq():
            
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:5000/api/liam') as response:
            
            r =  await response.json()
            return r

async def sensorLogic(req):
    
    newReq = await myReq()
    if newReq['state'] != req['state']:
        
        if newReq['state'] == '1':
            DB.addMessagetoSendArduino('H2500\n')
            DB.addMessagetoSendArduino('L500\n')
        elif newReq['state'] == '2':
            DB.addMessagetoSendArduino('H500\n')
            DB.addMessagetoSendArduino('L4500\n')
        
    return newReq
    
async def updateWeather():
    
    sensor.makeRequest()
    # wind = sensor.getCurrentWind()
    wind = sensor.getWind4Day()
    print("new wind: ", wind)
    
def getLidarAngle(radarDistance, radarAngle):
    
    if radarAngle == 90:
        return 90
    
    if radarAngle <= 45:
        return radarAngle + 10
    
    elif radarAngle > 45 and radarAngle <=85:
        return radarAngle + 5
    
    elif radarAngle > 95 and radarAngle < 135:
        return radarAngle -5
    
    elif radarAngle >= 135:
        return radarAngle - 10
    
    
    # print("initial angle", radarAngle)
    # print("initial distance", radarDistance)
    
    # angleC = math.radians(90 + 180 - radarAngle)
    # distC = math.sqrt(radarDistance**2 + 10**2 - 2*radarDistance*10 *math.cos(angleC))
    
    # print("distC: ", distC)
    # angleA = math.asin( distC/radarDistance * math.sin(angleC))

    # print("lidar radians angle:", angleA)
    # angleA = math.degrees(angleA)
    
    # print("lidar angle:", angleA)
    # return angleA
    

async def main(port1, port2):
    
    try:

        reader, writer = await serial_asyncio.open_serial_connection(url=port1, baudrate=115200)
    except:
        print("Could not find device attached to port: ", port1)
    
    # reader, writer = await serial_asyncio.open_serial_connection(url=port1, baudrate=115200)
    print("in async main")
    
    lidarReady = False
    lidarQueue = deque()
    
    # await addDBLidarMessagesToQueue(lidarQueue)
    # print(lidarQueue)
    
    socket = socketInit()
    
    radarDetecting = False
    radarDetectStart = 0
    radarDetectEnd = 0
    prevTime = 0
    
    while True:
        
        if lidarReady:
            # pass
            lidarReady = await sendLidar(writer, lidarQueue)
        
        # msg = await asyncio.wait_for(recv(reader), timeout=1) 
        msg = await recv(reader)
        
        if lidarReady == False and msg == 'L,done':
            lidarReady = True
        
        if msg in ['Away', 'Towards']:
            print(msg)
            if msg == 'Towards':
                print("need to take picture")
                # if sensor.sendCamera():
                #     socket.emit("take img")
                # else:
                #     print("bad visibility")
                #     socket.emit("no vis")
                    
            lidarReady = True
        
        if msg[0] == 'R' or msg[0] == 'r':
            
            radar, radarDistance, radarAngle = msg.split(",")
            radarDistance = int(radarDistance)
            radarAngle = int(radarAngle)
            
            if not radarDetecting and radar == 'R':
                radarDetecting = True
                radarDetectStart = radarAngle
            elif radarDetecting and radar == 'r':
                radarDetecting = False
                radarDetectEnd = radarAngle
                print("detected object from ", radarDetectStart, " - ", radarDetectEnd)
                lidarAngle = (radarDetectEnd + radarDetectStart)/2
                
                lidarAngle = getLidarAngle(radarDistance, lidarAngle)
                lidarQueue.append(f"L,{lidarAngle},{0}")

        
        # await addDBLidarMessagesToQueue(lidarQueue)
        
        """
        currTime = round(time.time())
        # print(currTime)
        # print(prevTime)
        # print(currTime-prevTime)
        if currTime - prevTime >= 10:
            print('going to update')
            await updateWeather()    
            prevTime = round(time.time())
        
        await asyncio.sleep(1)
        """
        
        if DEBUG:
            print(len(lidarQueue))
            print('waiting...', lidarReady)    
        

async def _main(port1, port2):
   
    prevTime = 0
    
    while True: 
        
        
        currTime = round(time.time())
        print(currTime)
        print(prevTime)
        print(currTime-prevTime)
        if currTime - prevTime >= 1:
            print('going to update')
            updateWeather()    
            prevTime = round(time.time())
        


if __name__ == '__main__':
    print('starting to listen on serial ports')
    
    port1 = sys.argv[1]
    
    if len(sys.argv) >= 3:
        port2 = sys.argv[2]    
    else:
        port2 = './COM4'
        
    asyncio.run(main(port1, port2))