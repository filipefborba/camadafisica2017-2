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

    def conect(self):
        """ Bloqueia a execução do programa até que uma conexão confiável
        com o servidor seja estabelecida """
        print(self.label, "Iniciando Handshake como Cliente")
        while not self.connected:
            print(self.label, "Enviando SYN...")
            self.sendSyn()
            print(self.label, "SYN Enviado...")
            print(self.label, "Esperando pelo SYN+ACK do Servidor...")
            handshake = self.fh.decode(self.getData())
            if handshake != 'TIMEOUT':
                if handshake["type"] == "SYN":
                    handshake = self.fh.decode(self.getData())
                    print(self.label, "SYN recebido...")
                    if handshake["type"] == "ACK":
                        print(self.label, "ACK recebido...")
                        self.sendAck()
                        print(self.label, "Enviado ACK de Client...")
                        self.connected = True
                        return self.connected
                    else:
                        print(self.label, "Erro no conect, SYN+ACK")
                        pass
            else:
                print(self.label,'Tempo para handshake expirou!')
                return handshake
                break
    
    def bind(self):
        """ Bloqueia a execução do programa até que uma conexão confiável
        com o cliente seja estabelecida """
        print(self.label, "Iniciando Handshake como Servidor")
        while not self.connected:
            print(self.label, 'Aguardando pedidos SYN...')
            received = self.fh.decode(self.getData())
            try:
                print(self.label, 'Obtido {}'.format(received['type']))
                if received["type"] == "SYN":
                    self.sendSyn()
                    self.sendAck()
                    print(self.label, "Enviado SYN+ACK")
                elif received["type"] == "ACK":
                    print(self.label,"ACK recebido de volta")
                    self.connected = True
                else:
                    print(self.label, "Ocorreu um erro... Enviando SYN+NACK")
                    self.sendSyn()
                    self.sendNack()
            except:
                pass

    
    def sendSyn(self):
        p = self.fh.buildCommandPacket("SYN")
        self.sendData(p)

    def sendAck(self):
        p = self.fh.buildCommandPacket("ACK")
        self.sendData(p)

    def sendNack(self):
        p = self.fh.buildCommandPacket("NACK")
        self.sendData(p)
    

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
        while(notFound):
            pRaw, bufferEmpty = self.rx.getPacket()
            print(self.label,"GetPacket(): pRaw", pRaw,"\n BufferEmpty:", bufferEmpty)
            if(pRaw == False):
                print(self.label,"Timeout: Buffer Empty")
                notFound = True
            elif(bufferEmpty == False):
                print("Timeout: Buffer corrompido")
                self.sendNack()
                notFound = True   
            else:
                pDecoded = self.fh.decode(pRaw)
                if(pDecoded["type"] == "PAYLOAD"):
                    if(pDecoded['size'] != len(pDecoded['payload'])):
                        print("Pacote corrompido... Enviando NACK")
                        self.sendNack()
                    else:
                        return pDecoded
                elif(pDecoded["type"] == "ACK" && "SYN"):
                    return pDecoded
                else:
                    print("Nao é um payload ou comando... Enviado NACK")
                    self.sendNack()
