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


dataPath = 'imgs/imageC.png'
# dataPath = '/Users/fredcurti/Pictures/Arquivo Escaneado 3.jpeg'

class FileHandler(object):
    """ This class handles files to package and unpack them,
    adding necessary data for a successful file transfer
    """
    def __init__(self):
        """ Initializes the filehandler class
        """

        self.headStruct = Struct(
                    "start" / Int8ub,
                    "size"  / Int16ub,
                    "ext" / Array(5,Byte),
                    "type" / Int16ub
                    # "checksum" / Int16ub
                    )        


    def buildHead(self):
        headSTART  = 0xFF
        fileExtension = self.filePath.split('.')
        fileExtension = fileExtension[len(fileExtension) - 1]
        
        #Tipo de imagem
        extArray = self.generate_extArr(fileExtension)

        #Checksum
        md5 = self.generate_md5()

        head = self.headStruct.build(
            dict(
                start = headSTART,
                size = self.fileSize,
                ext = extArray,
                type = "PAYLOAD".encode()
                # checksum = md5
            )
        )
        print ('===== \nGENERATED HEAD:', head ,'LEN:', len(head))
        return head

    def buildCommandPacket(self, commandType):
        head = self.headStruct.buid (
            dict(
                start = 0xFF,
                size = 0,
                ext = [0]*5,
                type = commandType.upper()
            )
        )
        print ('===== \nGENERATED COMMAND HEAD:', head ,'LEN:', len(head))
        return head

    def generate_md5(self):
        hash_md5 = hashlib.md5()
        with open(self.filePath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def generate_extArr(self,fileExt):
        arr = []
        arr.append(len(fileExt))
        for i in range(len(fileExt)):
            arr.append( ord(fileExt[i]))
        
        if len(fileExt) != 4:
            arr.append(0)

        return arr

    def buildEOP(self):
        eop = b'borbafred'
        print ('GENERATED EOP : ',binascii.hexlify(eop), 'LEN : ', len(binascii.hexlify(eop)),'\n=====')
        return binascii.hexlify(eop)

    def buildPacket(self,filePath):
        self.filePath = filePath
        self.data = open(self.filePath,'rb')
        self.fileSize = os.path.getsize(self.filePath)


        data = self.buildHead()
        data += open(self.filePath, 'rb').read()
        data += self.buildEOP()
        return data

    def decode(self,bincode):
        output = {}
        decoded = self.headStruct.parse(bincode)
        for each in decoded.items():
            output[each[0]] = each[1]
        extLen = output['ext'][0]
        ext = ''
        for i in range(extLen):
            ext += chr(output['ext'][i + 1])
        barr = bytearray(bincode)
        filebarr = barr[8:len(barr) - 18]

        output['ext'] = ext
        output['payload'] = filebarr
        print(
        """
        -> OBTAINED HEAD : {}
        -> OBTAINED BODY : {} ...
        -> EOF AT POSITION : {}
        """
        .format(output,filebarr[:50],len(barr) - 18))
        return output


        

# fh = FileHandler()
# fh.decode(fh.buildPacket(dataPath))

# fh.decode(fh.buildPacket())






