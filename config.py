import sys

if sys.platform == 'win32':
    ROOT_DIR = 'C:/users/liamp/source/arctic_app/'
    PI = False
else:
    PI = True
    ROOT_DIR = '/home/liam/arctic_app/'
    