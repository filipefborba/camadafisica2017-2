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
                    "filename" / String(6, encoding="utf-8"),
                    "ext" / String(4, encoding="utf-8"),
                    "type" / String(7, encoding="utf-8")
                    # "checksum" / Int16ub
                    )        

    #Constroi o HEAD do Payload
    def buildHead(self):
        #'Start' do HEAD
        headSTART  = 0xFF

        #Tipo de Arquivo
        file = self.filePath.split('/')
        file = file[len(file) - 1]
        file = file.split(".")
        fileName = file[0]
        fileExtension = file[1]
        

        #Checksum
        #md5 = self.generate_md5()

        #Construção do HEAD
        head = self.headStruct.build(
            dict(
                start = headSTART,
                size = self.fileSize,
                filename = String(6, encoding="utf-8").build(fileName),
                ext = String(7, encoding="utf-8").build(fileExtension),
                type = String(7, encoding="utf-8").build("PAYLOAD")
                # checksum = md5
            )
        )
        print ('===== \nGENERATED HEAD:', head ,'LEN:', len(head))
        return head

    #Constroi o HEAD dos comandos SYN, ACK e NACK
    def buildCommandPacket(self, commandType):
        head = self.headStruct.build (
            dict(
                start = 0xFF,
                size = 0,
                filename = 0,
                ext = 0,
                type = String(7, encoding="utf-8").build(commandType.upper())
            ))
        print('===== \nGENERATED COMMAND HEAD:', head ,'LEN:', len(head))
        return head + self.buildEOP()

    #Gera o hash do Checksum
    # def generate_md5(self):
    #     hash_md5 = hashlib.md5()
    #     with open(self.filePath, "rb") as f:
    #         for chunk in iter(lambda: f.read(4096), b""):
    #             hash_md5.update(chunk)
    #     return hash_md5.hexdigest()
    
    #Constroi o End Of Package (EOP)
    def buildEOP(self):
        eop = b'borbafred'
        print ('GENERATED EOP : ',binascii.hexlify(eop), 'LEN : ', len(binascii.hexlify(eop)),'\n=====')
        return binascii.hexlify(eop)

    #Constroi o pacote do Payload
    def buildPacket(self,filePath):
        self.filePath = filePath
        self.data = open(self.filePath,'rb')
        self.fileSize = os.path.getsize(self.filePath)

        data = self.buildHead()
        data += open(self.filePath, 'rb').read()
        data += self.buildEOP()
        return data

    #Realiza o desempacotamento
    def decode(self,bincode):
        output = {}
        decoded = self.headStruct.parse(bincode)
        for each in decoded.items():
            output[each[0]] = each[1]
        extLen = output['ext'][0]
        # ext = ''
        # for i in range(extLen):
        #     ext += chr(output['ext'][i + 1])
        barr = bytearray(bincode)
        filebarr = barr[20:len(barr) - 18]

        # output['ext'] = ext
        output['payload'] = filebarr
        # print('[Filebarr] : {}'.format(filebarr))

        if output['type'] == "PAYLOAD":
            outputDir = "./received/{}.{}".format(output['filename'],output['ext'])
            f = open(outputDir, 'wb')
            f.write(bytes(filebarr))
            print('[INFO]: Arquivo escrito com sucesso no diretório ' + outputDir )

        # print(
        # """
        # -> OBTAINED HEAD : {}
        # -> OBTAINED BODY : {} ...
        # -> EOF AT POSITION : {}
        # """
        # .format(output,filebarr[:50],len(barr) - 18))
        #outputdir = './imgs/foi.png'
        return output




        

# fh = FileHandler()
# fh.decode(fh.buildPacket(dataPath))
# fh.decode(fh.buildPacket())






