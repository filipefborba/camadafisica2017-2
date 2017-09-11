# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog
import time
from aplicacao import Application
from threading import Thread

class Screen:
    def __init__(self):
        self.btnfn = None
        self.startTrigger = False
        self.role = 'none'
        self.fileDir = None
        print('Screen Started')
        self.window = tk.Tk()
        self.window.geometry('250x200')
        self.window.title('Borbafred')
        self.window.resizable(0, 0)
        for i in range(2):
            self.window.rowconfigure(i, minsize=50)

        self.window.columnconfigure(0, minsize=250)
        self.window.configure(bg='#006400')

        self.title = tk.Label(self.window)
        self.title.configure(text='Borbafred',fg='white',bg='#a9a9a9')
        self.title.configure(font=('calibri', 15, 'bold'))
        self.title.grid(row=0, rowspan=1, column=0, sticky='nsew')

        self.title2 = tk.Label(self.window)
        self.title2.configure(text= 'Selecione sua role',fg='white',bg='#1e9622')
        self.title2.configure(font=('calibri', 13, 'bold'))
        self.title2.grid(row=1, rowspan=1, column=0, sticky='nsew')

        self.clientButton = tk.Button(self.window)
        self.clientButton.configure(text='Cliente', command=self.setClient,highlightbackground='#006400')
        self.clientButton.configure(font=('pixelmix', 11))
        # self.clientButton.grid(row=6, rowspan=1, column=0, sticky='nsew')
        self.clientButton.place(rely=1.0, relx=1.0, x=-35, y=-40, anchor='se')

        self.serverButton = tk.Button(self.window)
        self.serverButton.configure(text='Servidor', command=self.setServer)
        self.serverButton.configure(font=('pixelmix', 11),highlightbackground='#006400',padx=20)
        # self.serverButton.grid(row=7, rowspan=1, column=0, sticky='nsew')        
        self.serverButton.place(rely=1.0, relx=1.0, x=-225, y=-40, anchor='sw')

    def setClient(self):
        self.app = Application('client')
        # Thread(target=self.app.main).start()
        self.hideRoleButtons()
        self.role = 'client'
        self.insertButton = tk.Button(self.window, text='Escolher', command=self.askopenfile)
        self.insertButton.configure(fg='black',bg='#1e9622',highlightbackground='#006400')
        self.insertButton.grid(row=4, rowspan=1, column=0, sticky='nsew')

    def setServer(self):
        self.app = Application('server')
        # Thread(target=self.app.main).start()

        self.hideRoleButtons()
        self.role = 'server'

    def hideRoleButtons(self):
        self.serverButton.destroy()
        self.clientButton.destroy()
        self.window.geometry('250x175')

    # def showInsertBtn(self):
        
    def updateText(self,txt):
        self.title2.configure(text=txt.upper())

    def getRole(self):
        return self.role

    def setFn(self,fn):
        self.btnfn = fn

    def askopenfile(self):
        fileName = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("png files","*.png"),("all files","*.*")))
        self.fileDir = fileName
        split = fileName.split('/')
        self.insertButton.configure(text='Arquivo: ' + split[len(split) - 1])
        if fileName == '':
            self.fileDir = None
            print('Nenhum arquivo selecionado... Aguardando seleção')
        else:
            self.sendButton = tk.Button(self.window,command=lambda: self.app.client.onSendButtonClicked(self.fileDir))
            self.sendButton.configure(text='Enviar',fg='white',bg='#006400',highlightbackground='#006400',font=('calibri', 15, 'bold'))
            self.sendButton.place(rely=1.0, relx=1.0, x=-162.5, y=-5, anchor='sw')


    def getFileDirectory(self):
        while self.fileDir == None:
            time.sleep(1)
        return self.fileDir

        
    def onScriptStopped(self):
        self.startTrigger = False

    # def StartScript(self):
    #     if not self.startTrigger:
    #         self.startTrigger = True
    #         # mainThread = Thread(target=self.btnfn)
    #         self.btnfn()
            # mainThread.start()

		# self.infoLabel.configure(text='Click "Close Connection" to\n\nstop accepting new players'.upper())
		# self.infoLabel.configure(font=('pixelmix', 8))
        # self.infoLabel.grid(row=2, rowspan=2, column=0, sticky='nsew')

    def stopAcpt(self):
        self.server.stopAccepting()
        self.StartWindow()

    def StartWindow(self):
        self.infoLabel.configure(text='Good Luck'.upper())
        self.infoLabel.configure(font=('pixelmix', 12))
        self.infoLabel.grid(row=2, rowspan=2, column=0, sticky='nsew')

        self.bot_start = tk.Button(self.window)
        self.bot_start.configure(text='START GAME', command=self.CommandStart)
        self.bot_start.configure(font=('pixelmix', 11))
        self.bot_start.grid(row=4, rowspan=2, column=0, sticky='nsew')

    def CommandStart(self):
        self.server.startGame()
        self.window.destroy()

    def start(self):
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()

    def on_closing(self):
        self.window.destroy()
        raise SystemExit

Screen().start()
