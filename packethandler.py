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
        self.label = '[PacketHandler]'
        self.maxPacketSize = 2048
        self.outputDir = ''
        self.fileBuffer = bytearray()
        self.headStruct = Struct(
                    "start" / Int8ub,
                    "size"  / Int64ub,
                    "slicesize" / Int16ub,
                    "filename" / String(16, encoding="utf-8"),
                    "ext" / String(4, encoding="utf-8"),
                    "type" / String(7, encoding="utf-8"),
                    "index" / Array(2, Int32ub)
                    )

    #Constroi o HEAD do Payload
    def buildHead(self,currentIndex,total,sliceSize):
        "Constrói o HEAD para pacotes com payload"
        #'Start' do HEAD
        headSTART  = 0xFF
        #Tipo de Arquivo
        file = self.filePath.split('/')
        file = file[len(file) - 1]
        file = file.split(".")
        fileName = file[0]
        fileExtension = file[1]

        #Construção do HEAD
        headData = dict(
                start = headSTART,
                size = self.fileSize,
                slicesize = sliceSize,
                filename = String(16, encoding="utf-8").build(fileName),
                ext = String(4, encoding="utf-8").build(fileExtension),
                type = String(7, encoding="utf-8").build("PAYLOAD"),
                index = [currentIndex,total]
            )
        head = self.headStruct.build(headData)
        # print(headData)
        # print(len(head))
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
                slicesize = 0x00,
                filename = String(16, encoding="utf-8").build("NULL"),
                ext = String(4, encoding="utf-8").build("NULL"),
                type = String(7, encoding="utf-8").build(commandType.upper()),
                index = [0,0]
            )
        )
        return head + self.buildEOP()

    #Gera o hash do Checksum
    def generateFileChecksum(self, filePath):
        hash_md5 = hashlib.md5()
        with open(filePath, "rb") as f:
            for chunk in iter(lambda: f.read(maxPacketSize), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def generatePayloadChecksum(self, bytes):
        hash_md5 = hashlib.md5()
        hash_md5.update(bytes)
        hash_md5 = hash_md5.hexdigest()
        return self.stringToHex(hash_md5)

    def generateHeadChecksum(self, head):
        hash_md5 = hashlib.md5()
        hash_md5.update(head)
        hash_md5 = hash_md5.hexdigest()
        return self.stringToHex(hash_md5)

    def stringToHex(self, string):
        stringToByte = bytearray(string, encoding = "ascii")
        return binascii.hexlify(stringToByte)

    #Constroi o pacote do Payload
    def buildPacket(self,filePath):
        "Retorna um pacote com payload pronto para ser enviado"
        self.filePath = filePath
        self.data = open(self.filePath,'rb').read()
        self.fileSize = os.path.getsize(self.filePath)
        filePackets = []

        remaining = self.fileSize % self.maxPacketSize

        if remaining > 0:
            packetCount = self.fileSize // self.maxPacketSize + 1
        else:
            packetCount = self.fileSize // self.maxPacketSize
        
        print(""" 
        ------- PACKET SPLITTER ------
        Filesize : {}
        Number of packets expected : {}
        """.format(self.fileSize,packetCount))

        for i in range(packetCount):
            slice = self.data[i*self.maxPacketSize:self.maxPacketSize*(i+1)]
            #Checksum
            head = self.buildHead(i+1,packetCount,len(slice))
            headChecksum = self.generateHeadChecksum(head)
            payloadChecksum = self.generatePayloadChecksum(slice)
            print("""
            HeadChecksum : {}
            HeadChecksum len : {}
            PayloadChecksum : {}
            PayloadChecksum len : {}
            """.format(headChecksum, len(headChecksum), payloadChecksum, len(payloadChecksum)))
            filePackets.append({
                'status'    : 'READY',
                'packet'    :  head + headChecksum + slice + payloadChecksum + self.buildEOP(),
                'packetSize': len(slice)
            })

        # print(filePackets)

        print('------- ------ ------- ------')
        return filePackets

    #Realiza o desempacotamento
    def unpack(self,bincode):
        output = {}
        decoded = self.headStruct.parse(bincode)

        # print('[PARSE] Received packet',decoded['type'])   

        # Constroi um dicionário normal com as informações do HEAD obtido
        for each in decoded.items():
            output[each[0]] = each[1]
        
        # Escreve o arquivo na pasta received caso haja um payload
        if output['type'] == "PAYLOAD":
            barray = bytearray(bincode)
            filebarray = barray[46+64:len(barray) - (18+64)]
            head = barray[:46]
            headChecksum = barray[46:110]
            payloadChecksum = barray[len(barray) - (18+64):len(barray) - 18]
            print("""
            headChecksum: {}
            payloadChecksum: {}
            """.format(headChecksum, payloadChecksum))
            self.fileBuffer += filebarray
            self.outputDir = "./received/{}.{}".format(output['filename'],output['ext'])
            output['payload'] = filebarray
            output['head'] = head
            output['payloadchecksum'] = payloadChecksum
            output['headchecksum'] = headChecksum

        return output

    def writeFile(self):
        f = open(self.outputDir, 'wb')
        f.write(bytes(self.fileBuffer))
        self.fileBuffer = b''
        print(self.label, 'Arquivo escrito com sucesso no diretório ' + self.outputDir )
    
    def printHead(self,packet):
        print("----------- head ----------")
        for k in packet.keys():
            if k != 'payload':
                print('[{}]'.format(k),packet[k])
        print("---------------------------")
        