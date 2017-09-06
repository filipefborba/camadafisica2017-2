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
        while not self.connected:
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
                    self.connected = True
                    return self.connected
            else:
                print(self.label,'Tempo para handshake expirou!')
                return handshake
                break

            #  FIX ----------------------------------------------------
            # else:
            #     time.sleep(0.25)
            #     print("Reenviando SYN após 0.25s ...")
            #     self.sendData(FileHandler().buildCommandPacket("SYN"))
    
    def bind(self):
        """ Bloqueia a execução do programa até que uma conexão confiável
        com o cliente seja estabelecida """
        
        if self.connected:
            print(self.label,"Handshake já está estabelecido")
            return True
        else:
            while not self.connected:
                print(self.label, "Iniciando Handshake como Servidor")
                print(self.label, 'Aguardando pedidos SYN...')
                received = self.fh.decode(self.getData())
                try:
                    print(self.label, 'Obtido {}'.format(received['type']))
                    if received["type"] == "SYN":
                        self.sendData(self.fh.buildCommandPacket("SYN+ACK"))
                        print(self.label, "Enviado SYN+ACK")
                    elif received["type"] == "ACK":
                        # print(self.label,"RECEIVED ACK BACK")
                        self.connected = True
                        return self.connected
                    else:
                        print(self.label, "Ocorreu um erro... Enviando NACK")
                        self.sendData(self.fh.buildCommandPacket("NACK"))
                except:
                    pass
        

    ################################
    # Application  interface       #
    ################################
    def sendData(self, data):
        """ Send data over the enlace interface
        """
        self.tx.sendBuffer(data)

    def getData(self):
        """ Get n data over the enla`e interface
        Return the byte array and the size of the buffer
        """
        nAchei = True
        while(nAchei):
            pRaw, bufferEmpty = self.rx.getPacket()
            print("GETDATA",pRaw,bufferEmpty)
            if(pRaw == False):
                print("Timeout: buffer empty")
                nAchei = True
            elif(bufferEmpty == False):
                print("Timeout: Buffer corrompido")
                self.sendData(self.fh.buildCommandPacket("NACK"))    
                nAchei = True   
            else :
                pDecode = FileHandler().decode(p)
                if(pDecode["type"] == "PAYLOAD"):
                    if(pDecode['size'] != len(pDecode['payload'])):
                        print("Pacote corrompido")
                        self.sendData(self.fh.buildCommandPacket("NACK"))
                    else:
                        return(pDecode)
                else :
                    print("Nao é um payload")
                    self.sendData(self.fh.buildCommandPacket("NACK"))


                    




    

