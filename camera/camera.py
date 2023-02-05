# SOME ENV VARIABLES
from config import PI

if PI:
    from picamera import PiCamera

def takePicture(dir='img.png', form='png'):
    
	if PI:
	# print('taking picture: ', dir)
		camera = PiCamera()
		# camera.resolution = (602, 452)
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

