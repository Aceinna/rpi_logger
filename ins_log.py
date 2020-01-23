
"""
Program to log data from two INSs
Created on 2020-01-22
@author: xiankw
"""

import serial
import time
import datetime
import json
import requests
import threading
import sys

# need to find something python3 compatible  
# import urllib2

from azure.storage.blob import AppendBlobService
from azure.storage.blob import ContentSettings
from azure.storage.blob import BlockBlobService

from azureSAStest import push2azure


class INSTestLog:
    
    def __init__(self, serialport, timestr, user = False): 
        '''Initialize and create a txt file
        '''
        self.ser  = 0
        if serialport == '/dev/NovatelFLX6':
            self.sensor = 'Novatel'
        elif serialport == '/dev/INS2000':
            self.sensor = 'INS2000'
        pass
        self.serialport = serialport
        self.name = self.sensor + '-' + timestr + '.bin' #'.dat'
    
        if user:
            self.user = user
            if self.user['fileName'] == '':
                self.user['fileName'] = self.name
            else:
                self.user['fileName'] += timestr + '.dat'
            self.file = open('data/' + self.user['fileName'], 'w')
        else:
            self.file = open('data/' + self.name, 'wb') #'wb'

        self.ws = True # imu.ws
        if  self.sensor=='Novatel':
            self.sn = '123456'
            self.pn = '78901'
            self.device_id = 'FLEX6-3456-0987'
            self.odr_setting = 0
            self.packet_type = 'Separate'
            self.imu_properties = ''
        elif self.sensor=='Frii':
            self.sn = '0005532319289999'
            self.pn = '0005532319289999'
            self.device_id = 'FRII6809999'
            self.odr_setting = 0
            self.packet_type = 'Integrated'
            self.imu_properties = ''
        elif self.sensor=='INS2000':
            self.sn = 'INS2000'
            self.pn = 'INS2000'
            self.device_id = 'INS2000'
            self.odr_setting = 0
            self.packet_type = 'Integrated'
            self.imu_properties = ''
        pass


    def openSerialPort(self):
        '''Open serial port for system configuration and data logging
        '''
        while True:
            self.ser = serial.Serial(self.serialport,230400,parity='N',bytesize=8,stopbits=1,timeout=None) #115200
            if self.ser.isOpen():
                print ('\Port is open now\n')
                break
            else:
                time.sleep(1)
            pass
        return True

    # need to replace "RTKCASTER MNTPNT USERNAME PWD" with real values
    # need to relace the setinstranslation with real lever arm values
    def sysconfig(self):
        '''configure the system
        '''
        if self.sensor == 'Novatel':
            setupcommands  = ['unlogall\r',\
                'serialconfig com1 230400 N 8 1 N OFF\r',\
                'ETHCONFIG ETHA AUTO AUTO AUTO AUTO\r',\
                'ntripconfig NCOM1 client v1 RTKCASTER MNTPNT USERNAME PWD\r',\
                'interfacemode ncom1 rtcmv3 novatel off\r',\
                'interfacemode com1 novatel novatel on\r',\
                'serialconfig com2 230400 N 8 1 N OFF\r',\
                'connectimu com2 IMU_IMAR_FSAS\r',\
                'alignmentmode automatic\r',\
                'setimutoantoffset -0.5507 1.7123 1.3175 0.0289 0.0290 0.0499\r',
                'log ncom1 gpgga ontime 1\r',\
                'log inspvaxb ontime 0.05\r',\
                'log bestgnssposb ontime 0.05\r',\
                'log bestleverarmb onchanged\r',\
                'log insconfig onchanged\r',\
                'saveconfig\r']
        elif self.sensor == 'INS2000':
            setupcommands  = ['unlogall\r',\
                'com com2 230400\r',\
                'ntripconfig DTU1 client v1 RTKCASTER MNTPNT USERNAME PWD\r',\
                'ntripconfig NCOM1 client v1 RTKCASTER MNTPNT USERNAME PWD\r',\
                'setinstranslation ANT1 -0.3507 1.7123 1.2575 0.10 0.10 0.10\r',\
                'setinstranslation DUALANT 0.8128 0 0\r',\
                'inscommand enable\r',\
                'log inspvaxb ontime 0.05\r',\
                'log bestgnssposb ontime 0.05\r',\
                'saveconfig\r']
        pass
        for cmd in setupcommands:
            self.ser.write(cmd.encode())
            print (cmd)
            response = self.ser.readline()
            while response.find(b'OK',0,len(response)) < 0 and response.find(b'INSPVAXA',0,len(response)) < 0 :
                response = self.ser.readline()
                print (response)
            self.ser.flushInput()

    def log_upload(self):
        ''' log the serial port stream into a file
        '''
        while self.ser.isOpen():
            try:
                line = self.ser.readline()
                self.file.write(bytes(line))

            except:
                print('Port disconnected')
                break
            
        self.close()
        
        time.sleep(30)
        print('Pushing to Azure ...')
        toCloud = push2azure()
        toCloud.push2AzureAsBlobs()

    def write_to_azure(self):
        # check for internet 
        # if not self.internet_on(): 
        #    return False

        # record file to cloud
        # f = open("data/" + self.name,"r")
        f = open("data/" + self.user['fileName'], "r")
        text = f.read()
       



        self.block_blob_service = BlockBlobService(account_name='navview',
                                                    sas_token=self.sas_token, # account_key
                                                    protocol='http')
        self.block_blob_service.create_blob_from_text(container_name='data',
                                                    blob_name=self.name,
                                                    text=text,
                                                    content_settings=ContentSettings(content_type='text/plain'))
        # self.block_blob_service.create_blob_from_text(container_name='data-1000',
        #                                             blob_name=self.name,
        #                                             text=text,
        #                                             content_settings=ContentSettings(content_type='text/plain'))


        # record record to ansplatform
        self.record_to_ansplatform()
        
        
    def record_to_ansplatform(self):
        # data = { "pn" : self.pn, "sn": self.sn, "fileName" : self.user['fileName'],  "url" : self.name, "imuProperties" : json.dumps(self.imu_properties),
        #          "sampleRate" : self.odr_setting, "packetType" : self.packet_type, "userId" : self.user['id'] }
        data = { 
                    "type":"INS", 
                    "fileName" : self.user['fileName'], 
                    "url" : self.name,
                    "userId" : self.user['id'], 
                    "model" : self.device_id,
                    "logInfo": {
                        "pn" : self.pn, 
                        "sn": self.sn, 
                        "sampleRate" : self.odr_setting, 
                        "packetType" : self.packet_type,
                        "appVersion" : self.imu_properties['appName'] if 'appName' in self.imu_properties else '',
                        "imuProperties" : json.dumps(self.imu_properties)
                    } 
                }
        # host_address='http://40.118.233.18:3000/'
        host_address='https://api.aceinna.com/'        
        url = host_address + "api/recordLogs/post" #"https://api.aceinna.com/api/datafiles/replaceOrCreate"
        data_json = json.dumps(data)
        headers = {'Content-type': 'application/json', 'Authorization' : self.user['access_token'] }
        response = requests.post(url, data=data_json, headers=headers)
        response = response.json()
       
        # clean up
        self.name = ''

        return  #ends thread

    def internet_on(self):
        try:
            urllib2.urlopen('https://ans-platform.azurewebsites.net', timeout=1)
            return True
        except urllib2.URLError as err: 
            return False


    def get_sas_token(self):
        print('user token',self.user['access_token'])
        try:
            # host_address='http://40.118.233.18:3000/'
            host_address='https://api.aceinna.com/'
            url = host_address+"token/storagesas"
            headers = {'Content-type': 'application/json', 'Authorization':  self.user['access_token']}
            response = requests.post(url, headers=headers)
            rev = response.json()
            if 'token' in rev:
                self.sas_token = rev['token']
            else:
                self.sas_token = ''
                print('Error: Get sas token failed!')
        except Exception as e:
            print('Exception when get_sas_token:', e)

    def close(self):
        time.sleep(0.1)
        if self.ws:
            self.file.close()
            #self.get_sas_token()
            #threading.Thread(target=self.write_to_azure).start()
        else:
            self.file.close()

        return

