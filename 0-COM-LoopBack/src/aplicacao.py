#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
# Prof. Rafael Corsi
#  Abril/2017
#  Aplicação
####################################################

from enlace import *
from filehandler import *
import time
from loader import Screen
from datetime import datetime
import os

# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

# serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
# serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
# serialName = "COM3"                  # Windows(variacao de)

if os.name == 'posix':
    serialName = "/dev/tty.usbmodem1411"
else:
    serialName = "COM3"     

def main():
    # Inicializa enlace
    com = enlace(serialName)

    # Ativa comunicacao
    com.enable()

    # Define a role selecionada na GUI
    print('OBTAINED CHOICE: ',screen.getSelected())
    role = screen.getSelected()

    if role == 'client':
        print('ROLE : CLIENT')
        # Endereco da imagem a ser transmitida
        screen.updateText('Insira o arquivo abaixo')
        if screen.getImageDir() != None:
            imageR = screen.getImageDir()
            print("Endereço da Imagem Selecionada: " + imageR)

            # Log
            print("-------------------------")
            print("Comunicação inicializada")
            print("  porta : {}".format(com.fisica.name))
            print("-------------------------")

            #Aguardando Handshake com o servidor
            print("Enviando SYN")
            inSync = False
            while not inSync:
                com.sendData(buildCommandPacket(self, "SYN"))
                print("Aguardando SYN+ACK")
                handshake = fh.decode(com.getData())
                if handshake["type"] == "SYN+ACK":
                    com.sendData(buildCommandPacket(self, "ACK")
                    inSync = True
                else:
                    time.sleep(0.25)
                    com.sendData(buildCommandPacket(self,"SYN"))

            # Carrega imagem
            print ("Carregando imagem para transmissão :")
            print (" - {}".format(imageR))
            print("-------------------------")
            txBuffer = open(imageR, 'rb').read()
            txLen    = len(txBuffer)

            # Transmite imagem
            now = datetime.now().microsecond
            print("Transmitindo .... {} bytes".format(txLen))
            com.sendData(FileHandler().buildPacket(imageR))

            # espera o fim da transmissão
            while(com.tx.getIsBussy()):
                pass

            # Atualiza dados da transmissão
            txSize = com.tx.getStatus()

            #Calcula o tempo de transmissão
            finished = datetime.now().microsecond
            delta = now - finished
            print ("Transmitido       {} bytes ".format(txSize))
            print ("Processo finalizado em ",delta," ms")
            inSync = False
            com.disable()
        else:
            print('Nenhuma imagem selecionada')


    elif role == 'server':
        #Variável indicando que o servidor está pronto para receber arquivos
        serverReady = True

        #Objeto da classe que cuida dos pacotes
        fh = FileHandler()

        #Remove resquícios de comunicações antigas
        com.rx.clearBuffer()

        # fh.decode(fh.buildPacket('./imgs/imageC.png'))

        while serverReady:
            #Mostra na tela o seguinte texto
            screen.updateText('Aguardando dados...')
            print("Aguardando dados .... ")

            #Faz a recepção dos dados
            # rxBuffer = com.getData()


            #Mostra na tela o seguinte texto
            screen.updateText('ARQUIVO RECEBIDO!')

            #Começa a calcular o tempo de recepção
            now = datetime.now().microsecond

            # Salva imagem recebida em arquivo
            received = fh.decode(com.getData())
            print('---------- RECEIVED DATA ----------')
            inSync = False
            while not inSync:
                if received["type"] == "SYN":
                    com.sendData(buildCommandPacket(self, "SYN+ACK"))
                elif received["type"] == "ACK":
                    inSync = True
                else:
                    com.sendData(buildCommandPacket(self,"SYN+NACK"))


            for i in received.keys():
                if i == 'payload':
                    print(' -> payload : {} ... '.format(received[i][:50]))
                else:
                    print(' -> {} : {} '.format(i,received[i]))
            
            #Tamanho do arquivo lido
            print ("Lido              {} bytes ".format(received['size']))
        
            # Endereco da imagem a ser salva
            outputDir = "./received/{}.{}".format(received['filename'],received['ext'])

            #Gravação dos dados
            #outputDir = './imgs/foi.png'

            print("""
            -------------------------
            Salvando dados no arquivo : - {}
            FILE LEN : {}
            """.format(outputDir,len(received['payload'])))

            #outputDir = "./received/{}.{}".format(received['filename'],received['ext'])
            # print( 'NAME JOINED ' + outputDir)
            # f = open(outputDir, 'wb')
            # f.write(bytes(received['payload']))
            # print('[INFO]: Arquivo escrito com sucesso no diretório ' + outputDir )
            # print()
            #Calcula o tempo de recepção
            finished = datetime.now().microsecond
            delta = now - finished
            print ("Processo finalizado em ",delta," ms")
            time.sleep(2)

            # Encerra comunicação
            print("-------------------------")
            print("Comunicação encerrada")
            print("-------------------------")
            inSync = False

    else:
        print('Ocorreu um erro...')


# if __name__ == "__main__":
#     main()

screen = Screen()
screen.setFn(main)
screen.start()
