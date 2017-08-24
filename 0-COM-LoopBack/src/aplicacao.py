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

# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

# serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
# serialName = "COM3"                  # Windows(variacao de)

def main():
    # Inicializa enlace
    com = enlace(serialName)

    # # Ativa comunicacao
    
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
            print(imageR)
            # txBuffer = open(imageR, 'rb').read()
            # txlalala  = hex(1312321321)
            # txlalala += txBuffer
            # print(txlalala)
        
            #print(txBuffer)
            # Log
            print("-------------------------")
            print("Comunicação inicializada")
            print("  porta : {}".format(com.fisica.name))
            print("-------------------------")

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
            com.disable()
        else:
            print('Nenhuma imagem selecionada')


    elif role == 'server':
        serverReady = True
        #Tamanho em bytes do arquivo que está sendo recebido
        # txLen = 2076
        fh = FileHandler()
        com.rx.clearBuffer()
        
        # Endereco da imagem a ser salva
        imageW = "./imgs/recebida.png"

        while serverReady:
            # Faz a recepção dos dados
            screen.updateText('Aguardando dados...')
            print ("Aguardando dados .... ")
            rxBuffer = com.getData()

            screen.updateText('ARQUIVO RECEBIDO!')


            print('OBTAINED RX BUFFER', rxBuffer)

            # # log
            # print ("Lido              {} bytes ".format(nRx))

            #Começa a calcular o tempo de recepção
            now = datetime.now().microsecond

            # Salva imagem recebida em arquivo

            received = fh.decode(rxBuffer)
            print (received)
            f = open(imageW, 'wb')

            print("-------------------------")
            print ("Salvando dados no arquivo :")
            print (" - {}".format(imageW))
            f.write(received['payload'])
            print('[INFO]: Arquivo escrito com sucesso no diretório ' + imageW )

            #Calcula o tempo de recepção
            finished = datetime.now().microsecond
            delta = now - finished
            print ("Processo finalizado em ",delta," ms")
            time.sleep(2)

            # Encerra comunicação
            print("-------------------------")
            print("Comunicação encerrada")
            print("-------------------------")

    else:
        print('Ocorreu um erro...')


# if __name__ == "__main__":
#     main()

screen = Screen()
screen.setFn(main)
screen.start()
