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

    def __init__(self, name):
        """ Initializes the enlace class
        """
        self.fisica      = fisica(name)
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
                print(self.label, "Enviando SYN...")
                self.sendSyn()
                client.setState('ENVIANDO_SYN')

            elif client.state == 'ENVIANDO_SYN':
                client.setState('AGUARDANDO_SYN')
                data = self.getData()
                if data != False:
                    p = self.ph.unpack(data)
                    if p['type'] == 'SYN':
                        client.setState('AGUARDANDO_ACK')
            
            elif client.state == 'AGUARDANDO_ACK':
                data = self.getData()
                if data != False:
                    p = self.ph.unpack(data)
                    if p['type'] == 'ACK':
                        client.setState('ENVIANDO_ACK')
                        self.sendAck()
                        client.setState('CONECTADO')
                        client.handshake = True
                


                # print(self.label, "SYN Enviado...")
    # def connect(self):
    #     """ Bloqueia a execução do programa até que uma conexão confiável
    #     com o servidor seja estabelecida """
    #     print(self.label, "Iniciando Handshake como Cliente")
    #     print(self.label, "Enviando SYN...")
    #     self.sendSyn()
    #     print(self.label, "SYN Enviado...")
    #     print(self.label, "Esperando pelo SYN+ACK do Servidor...")
    #     syn = waitForSyn()
    #     ack = waitforAck()
    #     if syn and ack:
    #         print(self.label, "SYN e ACK recebidos...")
    #         print(self.label, "Enviando ACK de Client...")
    #         self.sendAck()
    #         print(self.label, "ACK de Client enviado...")
    #         self.connected = True
    #         print(self.label, "Conectado!")
    #         return self.connected
    #     else:
    #         print(self.label, "[Connect] Handshake falhou!")
    #         return self.connected
    
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

                
        # if syn:
        #     print(self.label, '[DEBUG] Obtido {}'.format(received['type']))
        #     print(self.label, "Enviando SYN e ACK...")
        #     self.sendSyn()
        #     self.sendAck()
        #     print(self.label, "SYN e ACK enviados...")

        # ack = waitforAck()
        # if ack:
        #     print(self.label,"ACK recebido de volta")
        #     print(self.label,"Conectado!")
        #     self.connected = True
        #     return self.connected

        # else:
        #     print(self.label, "[Server] Handshake falhou!")
        #     print(self.label, "Enviando SYN e NACK...")
        #     self.sendSyn()
        #     self.sendNack()
        #     return self.connected

    
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
        print('Packet received @ getData',packet)

        if packet != False:
            p = PacketHandler().unpack(packet)
            print(p)
            if p['type'] == 'PAYLOAD' and p['size'] != len(p['payload']):
                print(self.label,'Pacote corrompido, enviando NACK')
                self.sendNack()
                return False
            return packet
        
        else:
            print(self.label,'Timeout! Enviando NACK')
            self.sendNack()
            return False
            
        # while notFound :
            # # pRaw, bufferEmpty = self.rx.getPacket()
            # # print(self.label,"GetPacket(): pRaw", pRaw,"\n BufferEmpty:", bufferEmpty)

            # if pRaw == False:
            #     print(self.label,"[getData] ", "Timeout: Buffer Empty")
            #     notFound = True

            # elif bufferEmpty == False:
            #     print(self.label,"[getData] ","Timeout: Buffer corrompido")
            #     self.sendNack()
            #     notFound = True

            # else:
            #     pDecoded = self.fh.decode(pRaw)

            #     if pDecoded["type"] == "PAYLOAD":
            #         if pDecoded['size'] != len(pDecoded['payload']):
            #             print(self.label,"[getData] ","Pacote corrompido... Enviando NACK...")
            #             self.sendNack()
            #         else:
            #             return pDecoded

            #     elif pDecoded["type"] == "ACK" or pDecoded["type"] == "SYN":
            #         return pDecoded
                
            #     else:
            #         print(self.label,"[getData] ","Nao é um payload ou comando... Enviado NACK")
            #         self.sendNack()
