"""
Program to log solution in binary from Novatel FlexPak6 and then push to Azure after data collection
Created on 2020-01-22
@author: xiankw
"""

import serial
import math
import time
import datetime
from azureSAStest import push2azure

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
def configNovatel(ser):

    setupcommands  = ['unlogall\r',\
                'serialconfig com1 230400 N 8 1 N OFF\r',\
                'ETHCONFIG ETHA AUTO AUTO AUTO AUTO\r',\
                'ntripconfig NCOM1 client v1 RTKCASTER MNTPNT USERNAME PWD\r',\
                'interfacemode ncom1 rtcmv3 novatel off\r',\
                'interfacemode com1 novatel novatel on\r',\
                'serialconfig com2 230400 N 8 1 N OFF\r',\
                'connectimu com2 IMU_IMAR_FSAS\r',\
                'alignmentmode automatic\r',\
                'setimutoantoffset -0.5521 1.8065 1.2614 0.0087 0.0102 0.0248\r',
                'log ncom1 gpgga ontime 1\r',\
                'log inspvaxb ontime 0.05\r',\
                'log bestgnssposb ontime 0.05\r',\
                'saveconfig\r']
    for cmd in setupcommands:
        ser.write(cmd.encode())    
 

ser = serial.Serial('/dev/ttyUSB0',230400,parity='N',bytesize=8,stopbits=1,timeout=None) # need to confirm port
fname = './data/novatel_FLX6-'
ser.flushInput()

fmode = 'wb'

while True:
    if ser.isOpen(): break

print ('\Port is open now\n')


if False:
    while True:
        line = ser.readline().decode('utf-8')
        if line.find('#INSPVAXA', 0, len(line)) >= 0:
            info = line.split(',')
            gpsweek = int(info[5])
            sow     = float(info[6])
            startime = timefromGPS(gpsweek,sow)
            fname += '_%4d%02d%02d_%02d%02d%02d.bin' % (startime[0],startime[1],startime[2],startime[3],startime[4],startime[5])
            print(fname)
            break
else:
    fname += time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + '.bin'



with open(fname,fmode) as outf:
    configNovatel(ser)
    ser.flushInput()
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

