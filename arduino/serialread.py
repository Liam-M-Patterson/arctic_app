#!/usr/bin/env python3
import serial
import time

def read():
	ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
	ser.reset_input_buffer()
	while True:
		if ser.in_waiting > 0:
			line = ser.readline().decode('utf-8').rstrip()
			return line

def readSub(params):
    
    print('read sub: ', str(params))
    # file = open(params['dir'], 'r+')
    i = 0
    port = '/dev/ttyAMC0' if params['PI'] else 'COM3'
    print('port: ', port)
    
    ser = serial.Serial(port=port, baudrate=9600, timeout=1)
    
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)
            ser.flush()
    # while i < readings:
        
    #     file.write('val: '+ str(i))
    #     i += 1
    #     time.sleep(10)
    # file.close() 



def _readSub(dir, readings=10):
    
    file = open(dir, 'r+')
    i = 0
    while i < readings:
        
        file.write('val: '+ str(i))
        i += 1
        time.sleep(10)
    file.close() 

if __name__ == '__main__':
	params = { 'PI': False, 'dir': 'led.txt'}
    
	print(readSub(params))
	print('done reading')
#	print('going to read')
#	ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
#	ser.reset_input_buffer()
#	print('ser', ser)
#	while True:
#		if ser.in_waiting > 0:
#			line = ser.readline().decode('utf-8').rstrip()
#			print(line)



