# -*- coding: utf-8 -*-
import Tkinter as tk
import time
from threading import Thread

class Screen:
    def __init__(self):
        self.btnfn = None
        self.startTrigger = False
        self.role = 'none'
        print('Screen Started')
        self.window = tk.Tk()
        self.window.geometry('250x175')
        self.window.title('Borbafred')
        self.window.resizable(0, 0)
        for i in range(2):
            self.window.rowconfigure(i, minsize=50)

        self.window.columnconfigure(0, minsize=250)
        self.title = tk.Label(self.window)
        self.title.configure(text='Borbafred',fg='white',bg='#a9a9a9')
        self.title.configure(font=('calibri', 15, 'bold'))
        self.title.grid(row=0, rowspan=1, column=0, sticky='nsew')
        self.title2 = tk.Label(self.window)
        self.title2.configure(text= 'Selecione sua role',fg='white',bg='#1e9622')
        self.title2.configure(font=('calibri', 15, 'bold'))
        self.title2.grid(row=1, rowspan=1, column=0, sticky='nsew')
        self.clientButton = tk.Button(self.window)
        self.clientButton.configure(text='SERVER', command=self.setClient)
        self.clientButton.configure(font=('pixelmix', 11))
        self.clientButton.grid(row=6, rowspan=1, column=0, sticky='nsew')
        self.serverButton = tk.Button(self.window)
        self.serverButton.configure(text='CLIENT', command=self.setServer)
        self.serverButton.configure(font=('pixelmix', 11))
        self.serverButton.grid(row=7, rowspan=1, column=0, sticky='nsew')

    def setClient(self):
        self.role = 'client'
        Thread(target=self.btnfn).start()

    def setServer(self):
        self.role = 'server'
        Thread(target=self.btnfn).start()

    def updateText(self,txt):
        self.infoLabel.configure(text=txt.upper())

    def getSelected(self):
        return self.role

    def setFn(self,fn):
        self.btnfn = fn

    def onScriptStopped(self):
        self.startTrigger = False

    def StartScript(self):
        if not self.startTrigger:
            self.startTrigger = True
            # mainThread = Thread(target=self.btnfn)
            self.btnfn()
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
