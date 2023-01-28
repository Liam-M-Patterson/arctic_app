import sys

PI = False
if sys.platform != 'win32':
	from picamera import PiCamera
	PI = True
from time import sleep

def takePicture(dir='img.png', form='png'):
    
	if PI:
	# print('taking picture: ', dir)
		camera = PiCamera()
		camera.start_preview()
		camera.capture(dir, format=form)
		camera.stop_preview()
		camera.close()
	else:
		print('cannot access pi camera')
	# print('closed camera')

if __name__ == '__main__':
    takePicture()
    print('done main')

