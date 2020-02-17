
"""
Program to log USER com port data in binary from OpenRTK330
Created on 2020-02-13
@author: xiankw
"""

import serial
import time
import datetime
from azureSAStest import push2azure
                 
ser = serial.Serial('/dev/ttyUSB0',460800,parity='N',bytesize=8,stopbits=1,timeout=None) # need to confirm the port


while True:
    if ser.isOpen(): break

print ('\Port is open now\n')
ser.flushInput()


fname = './data/openRTK-U-'
fname += time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + '.bin'
fmode = 'wb'

with open(fname,fmode) as outf:
    while True:
        try:
            line = ser.readline()
            outf.write(bytes(line))

        except:
            break

    outf.close()

