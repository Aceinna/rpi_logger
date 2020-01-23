"""
Program to log INSPVAXA from FRII
Created on 2020-01-22
@author: xiankw
"""

import serial
import math
import time
import datetime

def getweeknum(weekseconds):
    return math.floor(weekseconds/(7*24*3600))

def getweeksec(weekseconds):
    return weekseconds - getweeknum(weekseconds)*(7*24*3600)

def yearfour(year):
    if year<=80:
        year += 2000
    elif year<1990 and year>80:
        year += 1900
    return year

def isleapyear(year):
    return (yearfour(year)%4==0 and yearfour(year)%100!=0) or yearfour(year)%400==0
                 
def timefromGPS(weeknum,weeksec):
    year = 0
    month = 0
    day = 0
    hour = 0
    minute = 0
    second = 0
    doy = 0
    daypermon = [31,28,31,30,31,30,31,31,30,31,30,31]

    weeknum += getweeknum(weeksec)
    weeksec  = getweeksec(weeksec)
    
    weekmin  = math.floor(weeksec/60.0)
    second   = weeksec - weekmin*60.0
    weekhour = math.floor(weekmin/60)
    minute   = weekmin - weekhour*60
    weekday  = math.floor(weekhour/24)
    hour     = weekhour - weekday*24

    totalday = weekday+weeknum*7
    if totalday<360:
        year = 1980
    else:
        year = 1981
        totalday -= 360
        while True:
            if totalday<365:
                break
            if isleapyear(year): totalday -= 1
            totalday -= 365
            year += 1
    doy = totalday

    if totalday <= daypermon[0]:
        month = 1
    else:
        totalday -= daypermon[0]
        if isleapyear(year): totalday -= 1
        month = 2
        while True:
            if totalday<=daypermon[month-1]:
                break
            else:
                totalday -= daypermon[month-1]
                month += 1
    if month==2 and isleapyear(year): totalday += 1
    day = totalday
    return [year,month,day,hour,minute,second,doy]

# need to replace "RTKCASTER MNTPNT USERNAME PWD" with real values
# need to relace the setinstranslation with real lever arm values
def configFRII(ser):

    setupcommands  = ['unlogall\r',\
                'com com2 230400\r',\
                'setinsrotation rbv 0 0 -90\r',\
                'ntripconfig DTU1 client v1 RTKCASTER MNTPNT USERNAME PWD\r',\
                'ntripconfig NCOM1 client v1 RTKCASTER MNTPNT USERNAME PWD\r',\
                'setinstranslation ANT1 -0.04 1.8782 1.032\r',\
                'set dynalign 5.0\r',\
                'log inspvaxa 0.05\r',\
                'saveconfig\r']
    for cmd in setupcommands:
        ser.write(cmd.encode())
        response = ser.readline()
        while response.find(b'OK',0,len(response)) < 0 and response.find(b'INSPVAXA',0,len(response)) < 0 :
            response = ser.readline()
            print (response)
        ser.flushInput()
                 
ser = serial.Serial('/dev/ttyUSB0',115200,parity='N',bytesize=8,stopbits=1,timeout=None) # need to confirm port
fname = 'frii-'

fmode = 'w'

while True:
    if ser.isOpen(): break

print ('\Port is open now\n')
configFRII(ser)
ser.flushInput()


fname += time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + '.txt'

with open(fname,fmode) as outf:
    while True:
        try:
            line = ser.readline()
            print (line, end='\r\n')
            outf.write(line.decode('utf-8'))

        except:
            break

    outf.close()
