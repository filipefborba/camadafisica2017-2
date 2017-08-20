#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
# Prof. Rafael Corsi
#  Abril/2017
#  Camada de Enlace
####################################################

# Importa pacote de tempo
import time
import hashlib
import os
import binascii

# Construct Struct
from construct import *


data = '/Users/fredcurti/Pictures/Arquivo Escaneado 1.jpeg'


class FileHandler(object):
    """ This class handles files to package and unpack them,
    adding necessary data for a successful file transfer
    """
    def __init__(self,dataPath):
        """ Initializes the filehandler class
        """
        self.filePath = dataPath
        self.data = open(dataPath,'rb')
        self.fileSize = os.path.getsize(dataPath)

    def buildHead(self):
        headSTART  = 0xFF
        fileExtension = self.filePath.split('.')
        fileExtension = fileExtension[len(fileExtension) - 1]
        # md5 = self.generate_md5()

        extArray = self.generate_extArr(fileExtension)

        headStruct = Struct(
                            "start" / Int8ub,
                            "size"  / Int16ub,
                            "type" / Array(5,Byte)
                            )                    
        
        head = headStruct.build(
            dict(
                start = headSTART,
                size = self.fileSize,
                type = extArray,
            )
        )

        print(head)
        print(headStruct.parse(head))
        return(head)

    # def generate_md5(self):
    #     hash_md5 = hashlib.md5()
    #     with open(self.filePath, "rb") as f:
    #         for chunk in iter(lambda: f.read(4096), b""):
    #             hash_md5.update(chunk)
    #     return hash_md5.hexdigest()

    def generate_extArr(self,fileExt):
        arr = []
        arr.append(len(fileExt))
        for i in range(len(fileExt)):
            arr.append( ord(fileExt[i]))
        
        if len(fileExt) != 4:
            arr.append(0)

        print(arr)
        return arr

    def 
    


fh = FileHandler(data)
fh.buildHead()



