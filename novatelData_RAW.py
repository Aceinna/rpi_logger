"""
Program to log raw measurements in binary from Novatel FlexPak6
Created on 2020-01-22
@author: xiankw
"""

import serial
import time
import datetime

# need to replace "RTKCASTER MNTPNT USERNAME PWD" with real values
# need to relace the setinstranslation with real lever arm values
def configNovatel(ser):

    setupcommands  = ['unlogall\r',\
                'serialconfig com1 460800 N 8 1 N OFF\r',\
                'ETHCONFIG ETHA AUTO AUTO AUTO AUTO\r',\
                'ntripconfig NCOM1 client v1 RTKCASTER MNTPNT USERNAME PWD\r',\
                'interfacemode ncom1 rtcmv3 novatel off\r',\
                'interfacemode com1 novatel novatel on\r',\
                'serialconfig com2 460800 N 8 1 N OFF\r',\
                'connectimu com2 IMU_IMAR_FSAS\r',\
                'alignmentmode automatic\r',\
                'setimutoantoffset -0.5521 1.8065 1.2614 0.0087 0.0102 0.0248\r',\
                'setinsoffset -0.5521 1.8065 1.2614\r',\
                'log ncom1 gpgga ontime 1\r',\
                'log versionb once\r',\
                'log rxconfigb once\r',\
                'log rxstatusb once\r',\
                'log thisantennatypeb once\r',\
                'log inspvaxb ontime 0.01\r',\
                'log bestposb ontime 0.05\r',\
                'log bestgnssposb ontime 0.05\r',\
                'log bestgnssvelb ontime 0.05\r',\
                'log timeb ontime 0.05\r',\
                'log rangecmpb ontime 0.05\r',\
                'log rawephemb onnew\r',\
                'log rawimusxb onnew\r',\
                'log setimuorientationb onchanged\r',\
                'log imutoantoffsetsb onchanged\r',\
                'log vehiclebodyrotationb onchanged\r',\
                'log insupdateb onchanged\r',\
                'saveconfig\r']
    for cmd in setupcommands:
        ser.write(cmd.encode())    
 

ser    = serial.Serial('/dev/ttyUSB0',460800,parity='N',bytesize=8,stopbits=1,timeout=None) # need to confirm port
while True:
    if ser.isOpen(): break
print ('\Port is open now\n')

fname  = './data/novatel_FLX6-'
fname += time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + '.bin'
fmode  = 'wb'

with open(fname,fmode) as outf:
    configNovatel(ser)
    ser.flushInput()
    while True:
        try:
            line = ser.readline()
            outf.write(bytes(line))

        except:
            break

    outf.close()

