
"""
Program to push files to Microsoft Azure
Created on 2020-01-22
@author: xiankw
"""

import mimetypes
mimetypes.init()
import time
from   datetime import datetime, timedelta

import requests
from   azure.storage.blob import BlockBlobService, ContainerPermissions, ContentSettings

import os
import numpy as np
import copy

# need to replace account information in __init__
class push2azure:
    ''' push the test data files of specific types in a folder to a contanier on Azure
    '''
    def __init__(self):
        ''' initialize the class
        '''
        self.account_name    = 'yourAccount'
        self.account_key     = 'yourKeyString'
        self.container_name  = 'yourContainer'
        self.datafolder      = 'yourFolder'
    
        
    def getfilelist(self):
        ''' get the log files of the current directory and subdirectory
        '''
        mypath  = self.datafolder # folder with logged data
        result  = []
        for r, d, f in os.walk(mypath):
            for file in f:
                if (file.endswith(".ASC") or file.endswith(".asc") or file.endswith(".txt") or file.endswith(".csv") or file.endswith(".bin")): 
                    result.append(os.path.join(r, file))
                    
        logfiles = []
        logfiles = copy.deepcopy(np.array(result))
        return logfiles


    def push2AzureAsBlobs(self):
        ''' push the files to azure
        '''
        service         = BlockBlobService(account_name=self.account_name, account_key=self.account_key)
        permission      = ContainerPermissions(read=True, write=True)
        sas             = service.generate_container_shared_access_signature(container_name=self.container_name,
                                permission=permission, protocol='https',
                                start=datetime.now(), expiry=datetime.now() + timedelta(days=1))

        service         = BlockBlobService(account_name=self.account_name, sas_token=sas)

        logfiles        = self.getfilelist()
        for insfile in logfiles:            
            print(insfile)
            basename    = os.path.basename(insfile)
            if service.exists(container_name=self.container_name, blob_name=basename):
                print('File '+ basename + ' has been uploaded before.')
            else:
                service.create_blob_from_path(
                        container_name=self.container_name,
                        blob_name=basename,
                        file_path=insfile,
                        content_settings=ContentSettings(content_type=mimetypes.guess_type(basename)[0]),
                        validate_content=False) 

 #####
if __name__ == "__main__":
    uploaddata = push2azure()
    uploaddata.push2AzureAsBlobs()
