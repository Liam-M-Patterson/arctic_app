import asyncio
import serial_asyncio
import sys
import db.db_connect as DB
import datetime 

# SOME ENV VARIABLES
from config import PI, ROOT_DIR

def writeToFile(data):
    
    num = '1\n' if data == 'HIGH' else '0\n'
    file = open(ROOT_DIR+'/arduino/led.txt', 'a')
    file.write(num)
    file.close()  


async def send(w):
    print('in send')
    
    msgs = DB.getArduinoMessages(datetime.datetime.utcnow())
    print(msgs)
    for msg in msgs:
        id, message, *_ = msg
        
        message += '\n'
        
        w.write(message.encode())
        DB.setArduinoMessageSent(id)
        # print(f'sent: {message.encode().rstrip()}')
        await asyncio.sleep(0.5)
    
    print('Done sending')
    


async def recv(r):
    
    msg = await r.readuntil(b'\n')
    if msg.rstrip() == b'DONE':
        print('Done receiving')
    
    data = msg.rstrip().decode()
    print(f'received: {data}')
    
    DB.updateLED(data)
        

async def main(port):
    
    reader, writer = await serial_asyncio.open_serial_connection(url=port, baudrate=9600)
    
    while True:
        
        # msgs = DB.getArduinoMessages(datetime.datetime.now())
        # if msgs:
        #     await send(writer)
        # else: 
        #     await asyncio.sleep(1)
        
        await send(writer)
        await recv(reader)        
        
    

def startLoop(port):
    # print('isPi in asyncSerialReader', isPi)
    
    # port = '/dev/ttyACM0' if isPi else './COM3'
    loop = asyncio.get_event_loop()
    
    loop.run_until_complete(main(port))
    loop.close()
    
if __name__ == '__main__':
    
    port = sys.argv[1]
    startLoop(port)