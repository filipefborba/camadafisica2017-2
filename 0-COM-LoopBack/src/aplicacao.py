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
        # self.com.rx.clearBuffer()

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
        self.stateMachineRunning = False
        self.app = app
        print('Classe Client Iniciada')

    # def sendFile(self,filePath):
    #     if self.handshake:
    #         self.app.com.sendData(PacketHandler().buildPacket(filePath))
    #     else:
    #         self.app.com.connect(self)
    #         if self.handshake == True:
    #             time.sleep(0.1)
    #             self.app.com.sendData(PacketHandler().buildPacket(filePath))

    def sendFile(self):
        self.app.com.sendData(PacketHandler().buildPacket(self.fileDir))

    def onSendButtonClicked(self,fileDir):
        self.stateMachineRunning = True
        self.fileDir = fileDir
        self.startClientStateMachine()

    def startClientStateMachine(self):
        """Máquina de Estados para envio e recepcao de ACKS e NACKS ao enviar
        payloads"""

        while self.stateMachineRunning == True:
            # Checa se o handshake já foi efetuado, caso contrário, o faz
            if self.handshake == False:
                self.setState('INICIAL')
                self.app.com.connect(self)
            
            elif self.state == 'CONECTADO':
                time.sleep(0.1)
                self.setState('ENVIANDO_PACOTE')

            elif self.state == 'ENVIANDO_PACOTE':
                self.sendFile()
                self.setState('AGUARDANDO_ACK')
            
            elif self.state == 'AGUARDANDO_ACK':
                data = self.app.com.getData()
                if data != False:
                    p = self.app.ph.unpack(data)
                    if p['type'] == 'ACK':
                        print('[Client] Sucesso no envio, encerrando comunicação')
                        self.setState('ENCERRANDO_COMUNICACAO')
                        self.stateMachineRunning = False
                    else:
                        self.setState('ENVIANDO_PACOTE')
                else:
                    self.setState('ENVIANDO_PACOTE')

            else:
                print('[Client] Fim da maquina de estados por algum motivo')

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
                filePacket = self.app.com.getData()
                if filePacket != False:
                    print('[SERVER] File written successfully')
                    

    def getState(self):
        return self.state
    
    def setState(self,newState):
        print('[Server] State changed! ' + self.state + ' -> ' + newState )
        self.state = newState
