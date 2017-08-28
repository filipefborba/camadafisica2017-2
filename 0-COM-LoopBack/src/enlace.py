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

    def conecta(self):
        """ Bloqueia a execução do programa até que uma conexão confiável
        com o servidor seja estabelecida """
        print(self.label, "Iniciando Handshake como Cliente")
        inSync = False
        while not inSync:
            print(self.label, "Enviando SYN...")
            self.sendData(FileHandler().buildCommandPacket("SYN"))
            print(self.label, "SYN Enviado...")
            print(self.label, "Esperando pelo SYN+ACK do Servidor...")
            handshake = self.fh.decode(self.getData())

            if handshake != 'TIMEOUT':
                if handshake["type"] == "SYN+ACK":
                    print(self.label, "SYN+ACK recebido...")
                    self.sendData(FileHandler().buildCommandPacket("ACK"))
                    print(self.label, "Enviado ACK de Client...")
                    inSync = True
            else:
                print(self.label,'Tempo para handshake expirou!')

            #  FIX ----------------------------------------------------
            # else:
            #     time.sleep(0.25)
            #     print("Reenviando SYN após 0.25s ...")
            #     self.sendData(FileHandler().buildCommandPacket("SYN"))
    
    def bind(self):
        """ Bloqueia a execução do programa até que uma conexão confiável
        com o cliente seja estabelecida """
        print(self.label, "Iniciando Handshake como Servidor")
        inSync = False

        while not inSync:
            print(self.label, 'Aguardando pedidos SYN...')
            received = self.fh.decode(self.getData())
            if received != 'TIMEOUT':
                print(self.label, 'Obtido {}'.format(received['type']))
                if received["type"] == "SYN":
                    self.sendData(self.fh.buildCommandPacket("SYN+ACK"))
                    print(self.label, "Enviado SYN+ACK")
                elif received["type"] == "ACK":
                    # print(self.label,"RECEIVED ACK BACK")
                    inSync = True
                else:
                    print(self.label, "Ocorreu um erro... Enviando SYN+NACK")
                    self.sendData(self.fh.buildCommandPacket("SYN+NACK"))
            else:
                print(self.label,'Tempo de handshake expirou')

    ################################
    # Application  interface       #
    ################################
    def sendData(self, data):
        """ Send data over the enlace interface
        """
        self.tx.sendBuffer(data)

    def getData(self):
        """ Get n data over the enlace interface
        Return the byte array and the size of the buffer
        """
        return self.rx.getPacket()


    

