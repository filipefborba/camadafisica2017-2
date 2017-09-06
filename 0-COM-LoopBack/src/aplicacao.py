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
import threading 

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

global label
label = '[MAIN]'

def main():
    # Inicializa enlace
    com = enlace(serialName)

    # Ativa comunicacao
    com.enable()

    # Define a role selecionada na GUI
    role = screen.getSelected()
    print(label, 'Papel selecionado:',role)

    # Programa para o cliente
    if role == 'client':
        com.rx.setRole('client')
        # Endereco da imagem a ser transmitida
        print("""--------- CLIENTE ------------
        Comunicação inicializada 
        porta : {}"
        """.format(com.fisica.name))
        screen.updateText('Insira o arquivo abaixo')
        print(label,'Aguardando a inserção de um arquivo')
        
        # Checa se o cliente selecionou um arquivo para ser enviado
        if screen.getImageDir() != None:
            imageR = screen.getImageDir()
            print(label, "Endereço da Imagem Selecionada: " + imageR)

            #Aguardando Handshake com o servidor
            response = com.conect()
            if response == 'TIMEOUT':
                print(label,'TIMEOUT!')
                screen.updateText('TIMEOUT')
                com.disable()
                return
        
            print("Handshake efetuado!")
            time.sleep(2)

            # Carrega imagem
            print (label, "Carregando imagem para transmissão :")
            print (label, " - {}".format(imageR))
            # print("-------------------------")
            txBuffer = open(imageR, 'rb').read()
            txLen    = len(txBuffer)

            print(label, "Transmitindo .... {} bytes".format(txLen))

            # Transmite a imagem e marca o tempo
            now = datetime.now().microsecond
            com.sendData(FileHandler().buildPacket(imageR))

            # espera o fim da transmissão
            while(com.tx.getIsBussy()):
                pass

            # Atualiza dados da transmissão
            txSize = com.tx.getStatus()

            #Calcula o tempo de transmissão
            finished = datetime.now().microsecond
            delta = now - finished
            print (label,"Transmitido       {} bytes ".format(txSize))
            print (label,"Processo finalizado em ",delta," ms")
            print (label,"Envio realizado, cliente pronto para enviar novamente")
            com.disable()
        else:
            print(label, 'Nenhuma imagem selecionada, tente novamente')


    elif role == 'server':
        com.rx.setRole('server')
        #Variável indicando que o servidor está pronto para receber arquivos
        serverReady = True

        #Objeto da classe que cuida dos pacotes
        fh = FileHandler()

        #Remove resquícios de comunicações antigas
        com.rx.clearBuffer()

        # fh.decode(fh.buildPacket('./imgs/imageC.png'))

        while serverReady:
            #Mostra na tela o seguinte texto
            screen.updateText('Aguardando conexão...')
            print(label,"Aguardando dados .... ")

            #Faz a recepção dos dados
            # rxBuffer = com.getData()

            response = com.bind()
            
            #Começa a calcular o tempo de recepção
            now = datetime.now().microsecond
            
            # Salva imagem recebida em arquivo
            received = fh.decode(com.getData())
            if received == 'TIMEOUT':
                print(label,'TIMEOUT')
                
            outputDir = "./received/{}.{}".format(received['filename'],received['ext'])

            print(label, '---------- RECEIVED DATA ----------')
    
            for i in received.keys():
                if i == 'payload':
                    print(' -> payload : {} ... '.format(received[i][:15]))
                else:
                    print(' -> {} : {} '.format(i,received[i]))
            
            #Tamanho do arquivo lido
            print (label, "Lido {} bytes ".format(received['size']))
    
            print(label, """
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

            print("----------------------------\n[INFO] Servidor pronto \n")

    else:
        print('Ocorreu um erro...')


# if __name__ == "__main__":
#     main()

screen = Screen()
screen.setFn(main)
screen.start()
