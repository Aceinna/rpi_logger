"""
Program to log soluton in binary from Aceinna INS2000 and push to Azure after data collection
Created on 2020-01-22
@author: xiankw
"""

import serial
import time
import datetime
from azureSAStest import push2azure

# need to replace "RTKCASTER MNTPNT USERNAME PWD" with real values
# need to relace the setinstranslation with real lever arm values
def configFRII(ser):

    setupcommands  = ['unlogall\r',\
                'com com2 460800\r',\
                'setinsrotation rbv 0 0 90 0.0 0.0 0.0\r',\
                'ntripconfig DTU1 client v1 RTKCASTER MNTPNT USERNAME PWD\r',\
                'ntripconfig NCOM1 client v1 RTKCASTER MNTPNT USERNAME PWD\r',\
                'setinstranslation ANT1 -1.8065 -0.3521 1.3214\r',\
                'setinstranslation DUALANT 0.0 0.8128 0.0\r',\
                'inscommand enable\r',\
                'log version\r',\
                'log inspvaxb ontime 0.1\r',\
                'log bestgnssposb ontime 0.1\r',\
                'saveconfig\r']
    for cmd in setupcommands:
        ser.write(cmd.encode())
        print(cmd)
                 
ser = serial.Serial('/dev/ttyUSB0',460800,parity='N',bytesize=8,stopbits=1,timeout=None)  # need to confirm port


while True:
    if ser.isOpen(): break

print ('\Port is open now\n')
configFRII(ser)
ser.flushInput()


fname = './data/ins2000-'
fname += time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + '.bin'
fmode = 'wb'

with open(fname,fmode) as outf:
    while True:
        try:
            line = ser.readline()
            outf.write(bytes(line))

        except:
            print('Port disconnected')
            break

    outf.close()

time.sleep(30)
print('Pushing to Azure ...')
toCloud = push2azure()
toCloud.push2AzureAsBlobs()
