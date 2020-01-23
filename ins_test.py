
"""
Program to log data from two INSs
Created on 2020-01-22
@author: xiankw
"""

import serial
import serial.tools.list_ports
import string
import time
import datetime
import sys
import os
from   ins_log import INSTestLog
#import collections
#import glob
#import struct
import json
import threading
from pathlib import Path
from openimu import OpenIMU
#from imu_input_packet import InputPacket
#from bootloader_input_packet import BootloaderInputPacket
from azure.storage.blob import BlockBlobService



class INS_Test:
    def __init__(self, ws=False):
        '''Initialize and then start ports search and autobaud process
        '''
        self.novatelport       = '/dev/ttyUSB0' # need to confirm port
        self.friiport          = '/dev/ttyUSB3'
        self.reConfigReceivers = True
        self.recordFrii        = True
        self.recordOpenIMUdata = False        

        # find serial ports
        while True:
            portlist = self.find_ports()
            for port in portlist:
                print (port)
            if self.novatelport in portlist:# and self.friiport in portlist:
                break
            else:
                time.sleep(10)
            pass
            
        self.timestr = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        print(self.timestr)
        #if no data folder, then creat one
        if not os.path.isdir("data"):
            print('creat data folder for store measure data in future')
            os.makedirs("data")

        # to log OpenIMU data
        if self.recordOpenIMUdata:
            self.imu = OpenIMU()
            self.imu.find_device()
            self.imu.openimu_get_all_param()
            time.sleep(30)
            
    def find_ports(self):
        ''' Lists serial port names. Code from
            https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
            Successfully tested on Windows 8.1 x64, Windows 10 x64, Mac OS X 10.9.x / 10.10.x / 10.11.x and Ubuntu 14.04 / 14.10 / 15.04 / 15.10 with both Python 2 and Python 3.
            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        '''
        print('scanning ports')

        #find system available ports
        portList = list(serial.tools.list_ports.comports())
        ports = [ p.device for p in portList]
        result = []
        for port in ports:
            if "Bluetooth" in port:
                continue
            else:
                print('Testing port ' + port)
                s = None
                try:
                    s = serial.Serial(port)
                    if s:
                        s.close()
                        result.append(port)
                # except:
                except Exception as e:
                    # print(e)                    
                    if sys.version_info[0] > 2:
                        if e.args[0].find('WindowsError') >= 0:
                            try:
                                if s:
                                    s.close()
                            except Exception as ee:
                                print (ee)
                                # self.disconnect()
                            
                    else:   
                        if e.message.find('Error') >= 0:
                            try:
                                if s:
                                    s.close()
                            except Exception as ee:
                                print (ee)
                                # self.disconnect()
                    pass
        return result
    
    def removeOldlogs(self):
        ''' remove files are more than 7 days old
        '''
        path = './data'

        now = time.time()
        for f in os.listdir(path):
            pathf = os.path.join(path, f)
            if os.stat(pathf).st_mtime < now - 7 * 86400:
                if os.path.isfile(pathf):
                    print('To be deleted: '+pathf+'\n')
                    os.remove(pathf)

    def start_log(self, data = False):
        '''log serial port streams and upload to Azure 
        '''
        novatellog = INSTestLog(self.novatelport,self.timestr)
        if self.recordFrii:
            friilog = INSTestLog(self.friiport,self.timestr)

        if self.recordFrii:
            if novatellog.openSerialPort() and friilog.openSerialPort():
                if self.reConfigReceivers:
                    novatellog.sysconfig()
                    friilog.sysconfig()
                print('Start logging ...')
                threading.Thread(target=novatellog.log_upload).start()
                threading.Thread(target=friilog.log_upload).start()
                # log OpenIMU data
                if self.recordOpenIMUdata:
                    threading.Thread(target=self.imu.start_log).start()
        else:
            if novatellog.openSerialPort():
                if self.reConfigReceivers:
                    novatellog.sysconfig()
                print('Start logging ...')
                threading.Thread(target=novatellog.log_upload).start()
                # log OpenIMU data
                if self.recordOpenIMUdata:
                    threading.Thread(target=self.imu.start_log).start()
                     

#####       

if __name__ == "__main__":
    ins = INS_Test()
    ins.removeOldlogs()
    ins.start_log()
