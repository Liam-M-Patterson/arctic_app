import socketio
import asyncio
from multiprocessing.pool import ThreadPool

def f(thread):
    sio = socketio.Client()
    server = 'http://127.0.0.1:5000'
    sio.connect(server)
    # sio.emit('liam', {'Hello': thread})
    sio.emit('liam')


async def init():
    sio = socketio.AsyncClient()
    server = 'http://127.0.0.1:5000'
    print('initing connection')
    
    await sio.connect(server)
    print('done awaiting')
    return sio

async def main():
    print("IN MAIN")
    sio = await init()
    print('socket is connected - CLIENT')
    await sio.emit('take img')
    # sio.emit('liam')
    # sio.disconnect()
    # print('done test client')

    @sio.img
    def gotImage(data):
        print('got raw img')
        print(data)
    # @sio.on('img')
    # async def gotImage(data):
    #     print('got raw img')
    #     print(data)
        
    @sio.on('detected img')
    def gotDetectedImg(data):
        print('detected the image', data)

    @sio.on('message')
    def connect_done(msg):
        print('test client done connecting')
        print(msg)
        sio.emit('liam')

if __name__ == '__main__':
    print('MAIN')
    asyncio.run(main())