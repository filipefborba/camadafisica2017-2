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

    ################################
    # Application  interface       #
    ################################
    def sendData(self, data):
        """ Send data over the enlace interface
        """
        
        print(data)
        self.tx.sendBuffer(data)

    def getData(self, size):
        """ Get n data over the enlace interface
        Return the byte array and the size of the buffer
        """
        data = self.rx.getNData(size)
        return(data, len(data))


# class FileHandler(object):
#     """ This class handles files to package and unpack them,
#     adding necessary data for a successful file transfer
#     """
#     def __init__(self, name):
#         """ Initializes the enlace class
#         """
#         self.fisica      = fisica(name)
#         self.
#         #Construção do HEAD
#         headSTART  = 0xFF 
#         headStruct = Struct("start" / Int8ub, "size"  / Int16ub )

#         def buildHead(self, dataLen):
#             head = headStruct.build(dict(start = self.headSTART, size = dataLen))
#             return(head)

#         def buildEOF(self, dataLen):
#             eof = 
    


    

