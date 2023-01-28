import asyncio
import serial_asyncio
import os
from functools import partial


BAUDRATE = 9600
PORT = 'COM3'

class Reader(asyncio.Protocol):
    """Receives newline-terminated messages and places them on a queue.
    """
    def __init__(self, queue):
        super().__init__()
        self.transport = None
        self.queue = queue

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        """Store received messages on the queue.
        """
        self.buf += data
        if b'\n' in self.buf:
            lines = self.buf.split(b'\n')
            self.buf = lines[-1]  # whatever was left over
            for line in lines[:-1]:
                asyncio.ensure_future(self.queue.put(line))

class InputChunkProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        print('data received', repr(data))
        
        # stop callbacks again immediately
        self.pause_reading(repr(data))

    def pause_reading(self, data):
        file = open(os.getcwd()+'/arduino/led.txt', 'a')
        file.write(data+'\n')
        file.close()
        # This will stop the callbacks to data_received
        self.transport.pause_reading()

    def resume_reading(self):
        # This will start the callbacks to data_received again with all data that has been received in the meantime.
        
        self.transport.resume_reading()

async def reader( baudrate, port):
    
    transport, protocol = await serial_asyncio.create_serial_connection(loop, InputChunkProtocol, port, baudrate=baudrate)

    while True:
        await asyncio.sleep(0.3)

        protocol.resume_reading()
    
# if __name__ == '__main__':
    
my_queue = asyncio.Queue()
reader_with_queue = partial(Reader, my_queue)

loop = asyncio.get_event_loop()
reader = serial_asyncio.create_serial_connection(loop, reader_with_queue, PORT, baudrate=BAUDRATE)
asyncio.ensure_future(reader)
print('Reader Scheduled')

loop.call_later(10, loop.stop)
loop.run_forever()
# loop.run_until_complete(reader(BAUDRATE, 'COM3'))
loop.close()
