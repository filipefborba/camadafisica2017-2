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

# Construct Struct
from construct import *
from packethandler import PacketHandler
# Interface Física
from interfaceFisica import fisica

# enlace Tx e Rx
from enlaceRx import RX
from enlaceTx import TX

class enlace(object):
    """ This class implements methods to the interface between Enlace and Application
    """

    def __init__(self, app):
        """ Initializes the enlace class
        """
        self.app         = app
        self.fisica      = fisica(app.serialName)
        self.rx          = RX(self.fisica)
        self.tx          = TX(self.fisica)
        self.connected   = False
        self.ph          = PacketHandler()
        self.label       = '[ENLACE]'

    def enable(self):
        """ Enable reception and transmission
        """
        self.fisica.open()
        self.rx.threadStart()
        self.tx.threadStart()

    def disable(self):
        """ Disable reception and transmission
        """
        self.rx.threadKill()
        self.tx.threadKill()
        time.sleep(1)
        self.fisica.close()

    def connect(self,client):
        """ Bloqueia a execução do programa até que uma conexão confiável
        com o servidor seja estabelecida """
        print(self.label, "Iniciando Handshake como Cliente")
        while client.handshake == False:
            if client.state == 'INICIAL':
                client.setState('ENVIANDO_SYN')

            elif client.state == 'ENVIANDO_SYN':
                self.sendSyn()
                client.setState('AGUARDANDO_SYN')
                
            elif client.state == 'AGUARDANDO_SYN':
                data = self.getData()
                if data != False:
                    p = self.ph.unpack(data)
                    if p['type'] == 'SYN':
                        client.setState('AGUARDANDO_ACK')
                    else:
                        client.setState('ENVIANDO_SYN')
                else:
                    client.setState('ENVIANDO_SYN')
            
            elif client.state == 'AGUARDANDO_ACK':
                data = self.getData()
                if data != False:
                    p = self.ph.unpack(data)
                    if p['type'] == 'ACK':
                        client.setState('ENVIANDO_ACK')
                        self.sendAck()
                        client.setState('CONECTADO')
                        client.handshake = True
                else:
                    client.setState('INICIAL')
                
    def bind(self,server):
        """ Bloqueia a execução do programa até que uma conexão confiável
        com o cliente seja estabelecida """
        print(self.label, "Iniciando Handshake como Servidor")
        while server.handshake == False:
            if server.state == 'INICIAL':
                server.setState('AGUARDANDO_SYN')
            
            elif server.state == 'AGUARDANDO_SYN':
                print(self.label, 'Aguardando pedidos SYN...')
                data = self.getData()
                if data:
                    p = self.ph.unpack(data)
                    if p['type'] == 'SYN':
                        server.setState('ENVIANDO_SYN')

            elif server.state == 'ENVIANDO_SYN':
                self.sendSyn()
                time.sleep(0.1)
                server.setState('ENVIANDO_ACK')
    
            elif server.state == 'ENVIANDO_ACK':
                self.sendAck()
                server.setState('AGUARDANDO_ACK')

            elif server.state == 'AGUARDANDO_ACK':
                data = self.getData()
                if data:
                    p = self.ph.unpack(data)
                    if p['type'] == 'ACK':
                        server.setState('CONECTADO')
                        server.handshake = True
    
    def sendSyn(self):
        p = self.ph.buildCommandPacket("SYN")
        self.sendData(p)

    def sendAck(self):
        p = self.ph.buildCommandPacket("ACK")
        self.sendData(p)

    def sendNack(self):
        p = self.ph.buildCommandPacket("NACK")
        self.sendData(p)

    def waitForSyn(self):
        handshake = self.ph.unpack(self.getData())
        if handshake["type"] == "SYN":
            return True
        else:
            return False

    def waitForAck(self):
        handshake = self.ph.unpack(self.getData())
        if handshake["type"] == "ACK":
            return True
        else:
            return False

    

    ################################
    # Application  interface       #
    ################################
    def sendData(self, data):
        """ Send data over the enlace interface
        """
        self.tx.sendBuffer(data)

    def getData(self):
        """ Get n data over the enlace interface
        """
        packet = self.rx.getPacket()
        print('Packet received @ getData', packet[0:20], '.....')

        if packet != False:
            p = PacketHandler().unpack(packet)
            if p['type'] == 'PAYLOAD' and p['size'] != len(p['payload']):
                print(self.label,'Pacote corrompido, enviando NACK')
                self.sendNack()
                return False
            
            return packet

        else:

            if self.app.role == 'server':
                print(self.label,'Timeout! Enviando NACK')
                self.sendNack()
                return False

            else:
                return False
                