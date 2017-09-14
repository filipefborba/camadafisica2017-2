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
        self.idle        = True

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
                        print(self.label,'\n ~~~ HANDSHAKE EFETUADO ~~~ \n')
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
                time.sleep(0.05)
                server.setState('ENVIANDO_ACK')
    
            elif server.state == 'ENVIANDO_ACK':
                self.sendAck()
                time.sleep(0.05)
                server.setState('AGUARDANDO_ACK')

            elif server.state == 'AGUARDANDO_ACK':
                data = self.getData()
                if data:
                    p = self.ph.unpack(data)
                    if p['type'] == 'ACK':
                        print(self.label,'\n ~~~ HANDSHAKE EFETUADO ~~~ \n')
                        server.setState('CONECTADO')
                        server.handshake = True


    def startServerStateMachine(self,server):
        """Máquina de Estados para envio de ACK e NACK ao receber payloads"""
        currentSize = 0

        while server.stateMachineRunning:
            # Checa se o handshake já foi efetuado, caso contrário, o faz
            if server.handshake == False:
                server.setState('INICIAL')
                server.app.com.bind(server)
            
            elif server.state == 'CONECTADO':
                time.sleep(0.05)
                server.setState('AGUARDANDO_PACOTE')

            elif server.state == 'AGUARDANDO_PACOTE':
                file = self.getData()
                if file != False:
                    self.idle = False
                    p = server.ph.unpack(file)
                    headchecksum = server.ph.generateHeadChecksum(p['head'])
                    payloadchecksum = server.ph.generatePayloadChecksum(p['payload'])
                    # print('HOLYYYYYYYYY', p['headchecksum'],'\n',headchecksum)
                    if (p['headchecksum'] == headchecksum) and (p['payloadchecksum'] == payloadchecksum):
                        index = p['index']
                        currentSize += p['slicesize']
                        print('[ServerStateMachine] Recebido pacote {}/{} com {} bytes | Recebido : {}/{} bytes'
                            .format(index[0],index[1],p['slicesize'],currentSize,p['size']))

                        server.setState('ENVIANDO_ACK')

                        if index[0] == index[1] and currentSize == p['size']:
                            self.sendAck()
                            currentSize = 0
                            print('[ServerStateMachine] Arquivo recebido com sucesso! ')
                            server.ph.writeFile()
                            self.idle = True
                            server.setState('CONECTADO')

                    else:
                        server.setState('ENVIANDO_NACK')

                else:
                    server.setState('ENVIANDO_NACK')
            
            elif server.state == 'ENVIANDO_ACK':
                self.sendAck()
                server.setState('AGUARDANDO_PACOTE')

            elif server.state == 'ENVIANDO_NACK':
                self.sendNack()
                server.setState('AGUARDANDO_PACOTE')

    def startClientStateMachine(self,client):
        """Máquina de Estados para envio e recepcao de ACKS e NACKS ao enviar
        payloads"""

        packets = client.filePackets
        currentPacket = 0

        while client.stateMachineRunning:
            # Checa se o handshake já foi efetuado, caso contrário, o faz
            if client.handshake == False:
                client.setState('INICIAL')
                client.app.com.connect(client)
            
            elif client.state == 'CONECTADO':
                time.sleep(0.05)
                client.setState('ENVIANDO_PACOTE')

            elif client.state == 'ENVIANDO_PACOTE':
                print('[ClientStateMachine] Enviando pacote {}/{} com {} bytes'
                    .format(currentPacket + 1,len(packets), packets[currentPacket]['packetSize']))

                self.sendData(packets[currentPacket]['packet'])
                client.setState('AGUARDANDO_ACK')
            
            elif client.state == 'AGUARDANDO_ACK':
                data = client.app.com.getData()
                if data != False:
                    p = client.app.ph.unpack(data)
                    if p['type'] == 'ACK':
                        print('[ClientStateMachine] -> Pacote {}/{} -> ACK'.format(currentPacket + 1,len(packets)))
                        currentPacket += 1
                        if currentPacket == len(packets):
                            client.setState('ENCERRANDO_COMUNICACAO')
                        else:
                            client.setState('ENVIANDO_PACOTE')

                    elif p['type'] == 'NACK':
                        print('[ClientStateMachine] -> Pacote {}/{} -> NACK !!!'.format(currentPacket + 1,len(packets)))
                        client.setState('ENVIANDO_PACOTE')

                else:
                    print('[ClientStateMachine] -> Pacote {}/{} -> TIMEOUT !!!'.format(currentPacket + 1,len(packets)))
                    client.setState('ENVIANDO_PACOTE')

            elif client.state == 'ENCERRANDO_COMUNICACAO':
                print('[Client] Sucesso no envio, encerrando comunicação')
                print('Fim de Transmissão. Arquivo enviado com sucesso!')
                client.setState('CONECTADO')
                currentPacket = 0
                client.stateMachineRunning = False
        
    def sendSyn(self):
        p = self.ph.buildCommandPacket("SYN")
        self.sendData(p)

    def sendAck(self):
        p = self.ph.buildCommandPacket("ACK")
        self.sendData(p)

    def sendNack(self):
        p = self.ph.buildCommandPacket("NACK")
        if self.app.role == 'server' and self.idle == False:
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
        packet = self.rx.getPacket()
        # print('--> DATA RECEIVED : ', packet)

        if packet != False:
            p = PacketHandler().unpack(packet)
            # if p['type'] == 'PAYLOAD' and p['slicesize'] != len(p['payload']):
            #     print(self.label,'Pacote corrompido, enviando NACK')
            #     self.sendNack()
            #     return False
            return packet
        
        else:
            return False

        # else:

        #     if self.app.role == 'server' and self.currentSize != 0:
        #         print(self.label,'Timeout! Enviando NACK')
        #         self.sendNack()
        #         return False



