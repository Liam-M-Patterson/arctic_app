import socketio
import asyncio

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
    asyncio.run(main())