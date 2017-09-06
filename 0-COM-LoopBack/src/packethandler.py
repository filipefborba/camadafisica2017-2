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

class PacketHandler(object):
    """ This class handles files to package and unpack them,
    adding necessary data for a successful file transfer
    """
    def __init__(self):
        """ Initializes the filehandler class
        """
        self.label = '[FileHandler]'
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
        "Constrói o HEAD para pacotes com payload"
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
                ext = String(4, encoding="utf-8").build(fileExtension),
                type = String(7, encoding="utf-8").build("PAYLOAD")
                # checksum = md5
            )
        )
        return head

    def buildEOP(self):
        "Constrói o EOP Padrão"
        eop = b'borbafred'
        return binascii.hexlify(eop)

    
    def buildCommandPacket(self, commandType):
        "Constroi o HEAD dos comandos SYN, ACK e NACK"
        head = self.headStruct.build(
            dict(
                start = 0xFF,
                size = 0x00,
                filename = String(6, encoding="utf-8").build("NULL"),
                ext = String(4, encoding="utf-8").build("NULL"),
                type = String(7, encoding="utf-8").build(commandType.upper())
            )
        )
        return head + self.buildEOP()

    #Gera o hash do Checksum
    # def generate_md5(self):
    #     hash_md5 = hashlib.md5()
    #     with open(self.filePath, "rb") as f:
    #         for chunk in iter(lambda: f.read(4096), b""):
    #             hash_md5.update(chunk)
    #     return hash_md5.hexdigest()


    #Constroi o pacote do Payload
    def buildPacket(self,filePath):
        "Retorna um pacote com payload pronto para ser enviado"
        self.filePath = filePath
        self.data = open(self.filePath,'rb')
        self.fileSize = os.path.getsize(self.filePath)
        return self.buildHead() + open(self.filePath, 'rb').read() + self.buildEOP()

    #Realiza o desempacotamento
    def decode(self,bincode):

        if bincode == False:
            return 'TIMEOUT'

        output = {}
        decoded = self.headStruct.parse(bincode)

        # print('[PARSE]',decoded)

        # Constroi um dicionário normal com as informações do HEAD obtido
        for each in decoded.items():
            output[each[0]] = each[1]

        # Faz slice dos bytes para separar o payload
        barray = bytearray(bincode)
        filebarray = barray[20:len(barray) - 18]
        output['payload'] = filebarray
        
        # Escreve o arquivo na pasta received caso haja um payload
        if output['type'] == "PAYLOAD":
            outputDir = "./received/{}.{}".format(output['filename'],output['ext'])
            f = open(outputDir, 'wb')
            f.write(bytes(filebarray))
            print(self.label, 'Arquivo escrito com sucesso no diretório ' + outputDir )

        return output
