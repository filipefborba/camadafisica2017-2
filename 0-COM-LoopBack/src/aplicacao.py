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
# serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM3"                  # Windows(variacao de)

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
        #Variável indicando que o servidor está pronto para receber arquivos
        serverReady = True

        #Objeto da classe que cuida dos pacotes
        fh = FileHandler()

        #Remove resquícios de comunicações antigas
        com.rx.clearBuffer()

        while serverReady:
            #Mostra na tela o seguinte texto
            screen.updateText('Aguardando dados...')
            print("Aguardando dados .... ")

            #Faz a recepção dos dados
            rxBuffer = com.getData()

            #Mostra na tela o seguinte texto
            screen.updateText('ARQUIVO RECEBIDO!')

            #Começa a calcular o tempo de recepção
            now = datetime.now().microsecond

            # Salva imagem recebida em arquivo
            received = fh.decode(rxBuffer)
            print('---------- RECEIVED DATA ----------')
            for i in received.keys():
                if i == 'payload':
                    print(' -> payload : {} ... '.format(received[i][:50]))
                else:
                    print(' -> {} : {} '.format(i,received[i]))
            
            #Tamanho do arquivo lido
            print ("Lido              {} bytes ".format(received['size']))
            
            # Endereco da imagem a ser salva
            imageW = "./recebidos/" + received['name'] + received['ext']

            #Gravação dos dados
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
