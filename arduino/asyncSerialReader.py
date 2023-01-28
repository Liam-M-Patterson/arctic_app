import asyncio
import serial_asyncio
import sys
import db.db_connect as DB

# SOME ENV VARIABLES
from config import PI, ROOT_DIR

def writeToFile(data):
    
    num = '1\n' if data == 'HIGH' else '0\n'
    file = open(ROOT_DIR+'/arduino/led.txt', 'a')
    file.write(num)
    file.close()

async def main(port):
    reader, _ = await serial_asyncio.open_serial_connection(url=port, baudrate=9600)
    print('Reader created')
    # _, writer = await serial_asyncio.open_serial_connection(url='./writer', baudrate=115200)
    # print('Writer created')
    # messages = [b'foo\n', b'bar\n', b'baz\n', b'qux\n']
    # sent = send(writer, messages)
    received = recv(reader)
    await asyncio.wait([received])


# async def send(w, msgs):
#     for msg in msgs:
#         w.write(msg)
#         print(f'sent: {msg.decode().rstrip()}')
#         await asyncio.sleep(0.5)
#     w.write(b'DONE\n')
#     print('Done sending')


async def recv(r):
    while True:
        msg = await r.readuntil(b'\n')
        if msg.rstrip() == b'DONE':
            print('Done receiving')
            break
        data = msg.rstrip().decode()
        print(f'received: {data}')
        # writeToFile(data)
        DB.updateLED(data)
        
        

def startLoop(port):
    # print('isPi in asyncSerialReader', isPi)
    
    # port = '/dev/ttyACM0' if isPi else './COM3'
    loop = asyncio.get_event_loop()
    
    loop.run_until_complete(main(port))
    loop.close()
    
if __name__ == '__main__':
    port = sys.argv[1]
    print('starting async reading')
    startLoop(port)
    