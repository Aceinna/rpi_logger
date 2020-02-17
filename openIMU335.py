
"""
Program to log OpenRTK335 data
Created on 2020-02-14
@author: xiankw
"""

import serial
import time
import datetime
from azureSAStest import push2azure
import glob
                 
ser = serial.Serial('/dev/ttyUSB0',115200,parity='N',bytesize=8,stopbits=1,timeout=None) # need to confirm port


while True:
    if ser.isOpen(): break

print ('\Port is open now\n')
#configFRII(ser)
ser.flushInput()


fname = './data/OpenIMU335-'
fname += time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + '.bin'
fmode = 'wb'

with open(fname,fmode) as outf:
    while True:
        try:
            line = ser.readline()
            print(bytes(line))
            outf.write(bytes(line))

        except:
            break

    outf.close()

#time.sleep(60)
#print('Pushing to Azure ...')
#toCloud = push2azure()
#toCloud.push2AzureAsBlobs()