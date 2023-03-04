import asyncio
import serial_asyncio
import sys
import db.db_connect as DB
import datetime 
import aiohttp

# SOME ENV VARIABLES
from config import PI, ROOT_DIR

# def writeToFile(data):
    
#     num = '1\n' if data == 'HIGH' else '0\n'
#     file = open(ROOT_DIR+'/arduino/led.txt', 'a')
#     file.write(num)
#     file.close()  

# Need to process the msg before sending to send to the right arudino
async def send(w1, w2):
    
    msgs = DB.getArduinoMessages(datetime.datetime.utcnow())
    
    for msg in msgs:
        
        print('Sending', msg)
        id, message, *_ = msg
        
        message += '\n'
        
        w1.write(message.encode())
        DB.setArduinoMessageSent(id)
        # print(f'sent: {message.encode().rstrip()}')
        await asyncio.sleep(0.5)

async def recv(r):
    
    msg = await r.readuntil(b'\n')
    if msg.rstrip() == b'DONE':
        print('Done receiving')
        
    print(msg)
    try:
        data = msg.rstrip().decode()
    except: 
        print(msg, " is not encoded properly")
        data = ''
        
    print(f'received: {data}')
    
    DB.updateLED(data)
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

async def main(port1, port2):
    
    reader, writer = await serial_asyncio.open_serial_connection(url=port1, baudrate=9600)
    try:
        reader2, writer2 = await serial_asyncio.open_serial_connection(url=port2, baudrate=9600)
    except:
        print('Could not find device attached to ', port2)
        reader2, writer2 = reader, writer
    myAPI = {'state': '0'}
    
    while True:
        
        
        await send(writer, writer2)
        msg = await recv(reader)    
        msg = await recv(reader2)    
        
        # if msg == 'HIGH':
        #     myAPI = await sensorLogic(myAPI)
        
    

def startLoop(port):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(port))
    loop.close()


    
if __name__ == '__main__':
    print('starting to listen')
    
    port1 = sys.argv[1]
    if len(sys.argv) >= 3:
        port2 = sys.argv[2]    
    else:
        port2 = './COM4'
    
    # startLoop(port)
    asyncio.run(main(port1, port2))