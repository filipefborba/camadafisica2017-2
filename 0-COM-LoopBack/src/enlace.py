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
from filehandler import FileHandler
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
        self.fh          = FileHandler()
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

    def connect(self):
        """ Bloqueia a execução do programa até que uma conexão confiável
        com o servidor seja estabelecida """
        print(self.label, "Iniciando Handshake como Cliente")
        print(self.label, "Enviando SYN...")
        self.sendSyn()
        print(self.label, "SYN Enviado...")
        print(self.label, "Esperando pelo SYN+ACK do Servidor...")
        syn = waitForSyn()
        ack = waitforAck()
        if syn and ack:
            print(self.label, "SYN e ACK recebidos...")
            print(self.label, "Enviando ACK de Client...")
            self.sendAck()
            print(self.label, "ACK de Client enviado...")
            self.connected = True
            print(self.label, "Conectado!")
            return self.connected
        else:
            print(self.label, "[Connect] Handshake falhou!")
            return self.connected
    
    def bind(self):
        """ Bloqueia a execução do programa até que uma conexão confiável
        com o cliente seja estabelecida """
        print(self.label, "Iniciando Handshake como Servidor")
        print(self.label, 'Aguardando pedidos SYN...')

        syn = waitForSyn()
        if syn:
            print(self.label, '[DEBUG] Obtido {}'.format(received['type']))
            print(self.label, "Enviando SYN e ACK...")
            self.sendSyn()
            self.sendAck()
            print(self.label, "SYN e ACK enviados...")

        ack = waitforAck()
        if ack:
            print(self.label,"ACK recebido de volta")
            print(self.label,"Conectado!")
            self.connected = True
            return self.connected

        else:
            print(self.label, "[Server] Handshake falhou!")
            print(self.label, "Enviando SYN e NACK...")
            self.sendSyn()
            self.sendNack()
            return self.connected

    
    def sendSyn(self):
        p = self.fh.buildCommandPacket("SYN")
        self.sendData(p)

    def sendAck(self):
        p = self.fh.buildCommandPacket("ACK")
        self.sendData(p)

    def sendNack(self):
        p = self.fh.buildCommandPacket("NACK")
        self.sendData(p)

    def waitForSyn(self):
        handshake = self.fh.decode(self.getData())
        if handshake["type"] == "SYN":
            return True
        else:
            return False

    def waitForAck(self):
        handshake = self.fh.decode(self.getData())
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
        notFound = True
        while notFound :
            pRaw, bufferEmpty = self.rx.getPacket()
            print(self.label,"GetPacket(): pRaw", pRaw,"\n BufferEmpty:", bufferEmpty)

            if pRaw == False:
                print(self.label,"[getData] ", "Timeout: Buffer Empty")
                notFound = True

            elif bufferEmpty == False:
                print(self.label,"[getData] ","Timeout: Buffer corrompido")
                self.sendNack()
                notFound = True

            else:
                pDecoded = self.fh.decode(pRaw)

                if pDecoded["type"] == "PAYLOAD":
                    if pDecoded['size'] != len(pDecoded['payload']):
                        print(self.label,"[getData] ","Pacote corrompido... Enviando NACK...")
                        self.sendNack()
                    else:
                        return pDecoded

                elif pDecoded["type"] == "ACK" or pDecoded["type"] == "SYN":
                    return pDecoded
                
                else:
                    print(self.label,"[getData] ","Nao é um payload ou comando... Enviado NACK")
                    self.sendNack()
