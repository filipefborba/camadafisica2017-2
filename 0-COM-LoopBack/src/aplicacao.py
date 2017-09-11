#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
# Prof. Rafael Corsi
#  Abril/2017
#  Aplicação
####################################################

from enlace import *
from packethandler import *
import time
from datetime import datetime
import os
import threading 

# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

# serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
# serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
# serialName = "COM3"                  # Windows(variacao de)
 

global label
label = '[MAIN]'

class Application:
    def __init__(self,role):
        if os.name == 'posix':
            self.serialName = "/dev/tty.usbmodem1421"
        else:
            self.serialName = "COM3"   
        
        self.role = role
        self.ph = PacketHandler()

        self.com = enlace(self)
        self.com.enable()
        #self.com.rx.clearBuffer()

        print(label,
        """
        Application iniciada
        Papel selecionado: {}
        """.format(self.role))
        
        if self.role == 'client':
            self.client = Client(self)
        elif self.role == 'server':
            self.server = Server(self)


    def main(self):
        print("Main thread Iniciada")
    
class Client:
    def __init__(self,app):  
        self.handshake = False
        self.state = 'INICIAL'
        self.app = app
        print('Classe Client Iniciada')

    def sendFile(self,filePath):
        if self.handshake:
            self.app.com.sendData(PacketHandler().buildPacket(filePath))
        else:
            self.app.com.connect(self)
            if self.handshake == True:
                time.sleep(0.1)
                self.app.com.sendData(PacketHandler().buildPacket(filePath))

    def getState(self):
        return self.state
    
    def setState(self,newState):
        print('[Client] State changed! ' + self.state + ' -> ' + newState )
        self.state = newState

class Server:
    def __init__(self,app):
        self.handshake = False
        self.state = 'INICIAL'
        self.app = app
        print('Classe Server Iniciada')
        self.getFile()
        
    def getFile(self):
        if self.handshake:
            self.app.com.getData()
        else:
            self.app.com.bind(self)
            if self.handshake == True:
                self.app.com.getData()

    def getState(self):
        return self.state
    
    def setState(self,newState):
        print('[Server] State changed! ' + self.state + ' -> ' + newState )
        self.state = newState