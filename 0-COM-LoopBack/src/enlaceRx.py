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
from datetime import datetime
from loader import Screen

# Threads
import threading

# Class
class RX(object):
    """ This class implements methods to handle the reception
        data over the p2p fox protocol
    """
    
    def __init__(self, fisica):
        """ Initializes the TX class
        """
        self.fisica      = fisica
        self.buffer      = bytes(bytearray())
        self.packetFound = False
        self.threadStop  = False
        self.threadMutex = True
        self.READLEN     = 1024
        self.label       = '[enlaceRx]'
        self.role        = None

    def thread(self):
        """ RX thread, to send data in parallel with the code
        """
        while not self.threadStop:
            if(self.threadMutex == True):
                rxTemp, nRx = self.fisica.read(self.READLEN)
                if (nRx > 0):
                    self.buffer += rxTemp
                time.sleep(0.001)

    def threadStart(self):
        """ Starts RX thread (generate and run)
        """
        self.thread = threading.Thread(target=self.thread, args=())
        self.thread.start()

    def threadKill(self):
        """ Kill RX thread
        """
        self.threadStop = True

    def threadPause(self):
        """ Stops the RX thread to run

        This must be used when manipulating the Rx buffer
        """
        self.threadMutex = False

    def threadResume(self):
        """ Resume the RX thread (after suspended)
        """
        self.threadMutex = True

    def setRole(self,role):
        self.role = role

    def getIsEmpty(self):
        """ Return if the reception buffer is empty
        """
        if(self.getBufferLen() == 0):
            return(True)
        else:
            return(False)

    def getBufferLen(self):
        """ Return the total number of bytes in the reception buffer
        """
        return(len(self.buffer))

    def getAllBuffer(self, len):
        """ Read ALL reception buffer and clears it
        """
        self.threadPause()
        b = self.buffer[:]
        self.clearBuffer()
        self.threadResume()
        return(b)

    def getBuffer(self):
        """ Remove n data from buffer
        """
        self.threadPause()
        b           = self.buffer[:]
        self.threadResume()
        return(b)

    def getNData(self, size):
        """ Read N bytes of data from the reception buffer
        This function blocks until the number of bytes is received
        """
        while(self.getBufferLen() < size):
            time.sleep(0.05)

        return(self.getBuffer(size))

    def getPacket(self):
        self.clearBuffer()
        startTime = time.time()
        while not self.packetFound:
            # self.threadPause()
            # print(self.getBuffer())
            # print('-------------------------------- \n ')
            runtime = time.time()
            eop = self.buffer.find(b'626f72626166726564')
            if eop != -1:
                self.packetFound = True
                startTime = time.time()
                # print('EOP ENCONTRADO:' , eop)
                head = self.buffer.find(0xFF)
                receivedbytes = self.buffer
                receivedbytes = receivedbytes[head:eop + 18]
                # print('RECEIVED BYTES : ', receivedbytes)
                # self.threadPause()
                self.packetFound = False
                return receivedbytes, False
            elif runtime - startTime >= 5:
                print('[enlaceRx] Tempo para recebimento de confirmação expirou.')
                if(self.getIsEmpty()) :
                    return False,True
                else :
                    self.clearBuffer()
                    return False,False

            else:
                time.sleep(0.1)


    def clearBuffer(self):
        """ Clear the reception buffer
        """
        self.buffer = b""


