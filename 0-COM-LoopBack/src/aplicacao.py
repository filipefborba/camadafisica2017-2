#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
# Prof. Rafael Corsi
#  Abril/2017
#  Aplicação
####################################################

from enlace import *
import time
from loader import Screen

# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

# serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
#serialName = "COM3"                  # Windows(variacao de)

def main():
    # Inicializa enlace
    com = enlace(serialName)

    # Ativa comunicacao
    com.enable()

    # Define a role selecionada na GUI
    print('OBTAINED CHOICE: ',screen.getSelected())
    role = screen.getSelected()

    if role == 'client':
        # Endereco da imagem a ser transmitida
        imageR = "./imgs/imageC.png"
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
        print(txLen)

        # Transmite imagem
        print("Transmitindo .... {} bytes".format(txLen))
        com.sendData(txBuffer)

        # espera o fim da transmissão
        while(com.tx.getIsBussy()):
            pass

        # Atualiza dados da transmissão
        txSize = com.tx.getStatus()
        print ("Transmitido       {} bytes ".format(txSize))

    elif role == 'server':
        # Endereco da imagem a ser salva
        imageW = "./imgs/recebida.png"
        # Faz a recepção dos dados
        print ("Recebendo dados .... ")
        rxBuffer, nRx = com.getData(txLen)

        # log
        print ("Lido              {} bytes ".format(nRx))

        # Salva imagem recebida em arquivo
        print("-------------------------")
        print ("Salvando dados no arquivo :")
        print (" - {}".format(imageW))
        f = open(imageW, 'wb')
        f.write(rxBuffer)
        # Fecha arquivo de imagem
        f.close()

        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com.disable()

    else:
        print('Ocorreu um erro wtf dude')
    

# if __name__ == "__main__":
#     main()

screen = Screen()
screen.setFn(main)
screen.start()



