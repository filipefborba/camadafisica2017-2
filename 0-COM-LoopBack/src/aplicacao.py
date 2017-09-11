#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
# Prof. Rafael Corsi
#  Abril/2017
#  Aplicação
####################################################

from enlace import *
from packethandler import *
import time
from datetime import datetime
import os
import threading 

# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

# serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
# serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
# serialName = "COM3"                  # Windows(variacao de)
 

global label
label = '[MAIN]'

class Application:
    def __init__(self,role):
        if os.name == 'posix':
            self.serialName = "/dev/tty.usbmodem1421"
        else:
            self.serialName = "COM3"    
        self.com = enlace(self.serialName)
        self.role = role
        self.fh = PacketHandler()
        self.com.enable()
        print(label,
        """
        Application iniciada
        Papel selecionado: {}
        """.format(self.role))
        
        if self.role == 'client':
            self.client = Client(self)
        elif self.role == 'server':
            self.server = Server(self)


    def main(self):
        print("Main thread Iniciada")


# def main():
#     global com
#     global fh

#     # Inicializa enlace e o fileHandler
#     com = enlace(serialName)
#     fh = 
#     # Ativa comunicacao
#     com.enable()
#     # Define a role selecionada na GUI
#     role = ui.getRole()
    
class Client:
    def __init__(self,app):  
        self.handshake = False
        self.state = 'INICIAL'
        self.app = app
        print('Classe Client Iniciada')

    def sendFile(self,filePath):
        file = open(filePath, 'rb').read()
        if self.handshake:
            self.app.com.sendData(PacketHandler().buildPacket(file))
        else:
            self.app.com.connect(self)
            if self.handshake == True:
                self.app.com.sendData(PacketHandler().buildPacket(file))

    def getState(self):
        return self.state
    
    def setState(self,newState):
        print('[Client] State changed! ' + self.state + ' -> ' + newState )
        self.state = newState

    # # Endereco da imagem a ser transmitida
    # print("""
    # --------- CLIENTE ------------
    # Comunicação inicializada 
    # porta : {}"
    # """.format(com.fisica.name))
    # ui.updateText('Insira o arquivo abaixo')
    # print(label,'Aguardando a inserção de um arquivo')
    
    # # Checa se o cliente selecionou um arquivo para ser enviado
    # fileDir = ui.getFileDirectory()
    # print(label, "Endereço do Arquivo Selecionado: " + fileDir)

    # #Aguardando Handshake com o servidor
    # response = com.connect()
    # if response == 'TIMEOUT':
    #     print(label,'TIMEOUT!')
    #     ui.updateText('TIMEOUT')
    #     com.disable()
        

    # print("Handshake efetuado!")
    # time.sleep(2)

    # # Carrega imagem
    # print (label, "Carregando imagem para transmissão :")
    # print (label, " - {}".format(imageR))
    # # print("-------------------------")
    # txBuffer = open(imageR, 'rb').read()
    # txLen    = len(txBuffer)

    # print(label, "Transmitindo .... {} bytes".format(txLen))

    # # Transmite a imagem e marca o tempo
    # now = datetime.now().microsecond
    # com.sendData(FileHandler().buildPacket(imageR))

    # # espera o fim da transmissão
    # while(com.tx.getIsBussy()):
    #     pass

    # # Atualiza dados da transmissão
    # txSize = com.tx.getStatus()

    # #Calcula o tempo de transmissão
    # finished = datetime.now().microsecond
    # delta = now - finished
    # print (label,"Transmitido       {} bytes ".format(txSize))
    # print (label,"Processo finalizado em ",delta," ms")
    # print (label,"Envio realizado, cliente pronto para enviar novamente")
    # com.disable()

class Server:
    def __init__(self,app):
        self.handshake = False
        self.state = 'INICIAL'
        self.app = app
        print('Classe Server Iniciada')
        self.getFile()
        
    def getFile(self):
        if self.handshake:
            self.app.com.getData()
        else:
            self.app.com.bind(self)
            if self.handshake == True:
                self.app.com.getData()

    def getState(self):
        return self.state
    
    def setState(self,newState):
        print('[Server] State changed! ' + self.state + ' -> ' + newState )
        self.state = newState


    # #Objeto da classe que cuida dos pacotes

    # #Remove resquícios de comunicações antigas
    # com.rx.clearBuffer()

    # # fh.decode(fh.buildPacket('./imgs/imageC.png'))


    # #Mostra na tela o seguinte texto
    # ui.updateText('Aguardando conexão...')
    # print(label,"Aguardando dados .... ")

    # #Faz a recepção dos dados
    # # rxBuffer = com.getData()

    # response = com.bind()
    
    # #Começa a calcular o tempo de recepção
    # now = datetime.now().microsecond
    
    # # Salva imagem recebida em arquivo
    # received = fh.decode(com.getData())
    # if received == 'TIMEOUT':
    #     print(label,'TIMEOUT')
        
    # outputDir = "./received/{}.{}".format(received['filename'],received['ext'])

    # print(label, '---------- RECEIVED DATA ----------')

    # for i in received.keys():
    #     if i == 'payload':
    #         print(' -> payload : {} ... '.format(received[i][:15]))
    #     else:
    #         print(' -> {} : {} '.format(i,received[i]))
    
    # #Tamanho do arquivo lido
    # print (label, "Lido {} bytes ".format(received['size']))

    # print(label, """
    # Salvando dados no arquivo : - {}
    # FILE LEN : {}
    # """.format(outputDir,len(received['payload'])))

    # #outputDir = "./received/{}.{}".format(received['filename'],received['ext'])
    # # print( 'NAME JOINED ' + outputDir)
    # # f = open(outputDir, 'wb')
    # # f.write(bytes(received['payload']))
    # # print('[INFO]: Arquivo escrito com sucesso no diretório ' + outputDir )
    # # print()
    # #Calcula o tempo de recepção
    # finished = datetime.now().microsecond
    # delta = now - finished
    # print ("Processo finalizado em ",delta," ms")
    # time.sleep(2)

    # print("----------------------------\n[INFO] Servidor pronto \n")


# if __name__ == "__main__":
#     main()

# ui = Screen()
# ui.setFn(main)
# ui.start()
