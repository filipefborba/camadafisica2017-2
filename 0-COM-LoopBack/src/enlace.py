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
        print("Enviando SYN")
        inSync = False
        while not inSync:
            received = self.getData()
            self.sendData(FileHandler().buildCommandPacket("SYN"))
            print("SENT SYN")
            print("WAITING FOR SYN+ACK")
            handshake = self.fh.decode(self.getData())
            if handshake["type"] == "SYN+ACK":
                print("RECEIVED SYN+ACK")
                self.sendData(FileHandler().buildCommandPacket("ACK"))
                print("SENT ACK")
                inSync = True
            else:
                received = self.fh.decode(self.getData())
                time.sleep(0.25)
                self.sendData(FileHandler().buildCommandPacket("SYN"))
    
    def bind(self):
        inSync = False
        while not inSync:
            received = self.getData()
            if received["type"] == "SYN":
                print("RECEIVED SYN")
                self.sendData(self.fh.buildCommandPacket("SYN+ACK"))
                print("SENT SYN+ACK")
            elif received["type"] == "ACK":
                print("RECEIVED ACK BACK")
                inSync = True
            else:
                self.sendData(self.fh.buildCommandPacket("SYN+NACK"))


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


    

