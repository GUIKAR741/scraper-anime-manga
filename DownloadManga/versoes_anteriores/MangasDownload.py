import time
from typing import List, Union
import os
from tkinter import *
from scraper.manga.DownloadWindow import DownloadWindow


class MangasDownload:
    def __init__(self):
        # Instancia Tkinter
        self.tk = Tk()
        # Inicia variaveis
        self.frame1 = None  # frame baixar
        self.frame2 = None  # frame renomear
        self.icon = None
        self.op = IntVar()
        self.op.set(2)
        self.ren = IntVar()
        self.ren.set(1)
        self.link = StringVar()
        self.down = StringVar()
        self.ini = StringVar()
        self.fim = StringVar()
        self.rename = StringVar()
        self.dir = os.getcwd()
        self.rena = os.getcwd()
        self.down.set(self.dir)
        self.rename.set(self.dir)
        self.x = IntVar()
        self.x.set(2)
        # Inicia aplicativo
        self.inicia()
        # cria Frames
        self.frames()
        # cria interface dentro dos frames
        self.criaInterfaceBaixar()
        self.criaInterfaceRenomear()
        # Executa aplicativo
        self.executa()

    def inicia(self):
        self.tk.geometry("600x450")
        self.tk.resizable(False, False)
        self.icon = self.dir + '\\' + 'down.ico'
        self.tk.iconbitmap(self.icon)
        self.tk.title("Mangás Downloader")

    def frames(self):
        # Frame 1 - Baixar
        self.frame1 = Frame(self.tk, bd=1)
        self.frame1.pack()
        # Frame 1 - Renomear
        self.frame2 = Frame(self.tk, bd=1)
        self.frame2.pack()

    def criaInterfaceBaixar(self):
        # Frames Baixar
        frameA = Frame(self.frame1, bd=1)
        frameB = Frame(self.frame1, bd=1)
        frameC = Frame(self.frame1, bd=1, highlightbackground="gray", highlightcolor="gray",
                       highlightthickness=1)
        frameD = Frame(self.frame1, bd=1, highlightbackground="gray", highlightcolor="gray",
                       highlightthickness=1)
        frameE = Frame(self.frame1, bd=1)
        frameF = Frame(self.frame1, bd=1)
        frameG = Frame(self.frame1, bd=1)
        frameA.pack(fill=X)
        frameB.pack(pady=5)
        frameF.pack(pady=5)
        frameC.pack(pady=5)
        frameD.pack(pady=5)
        frameG.pack()
        ###
        Label(frameA, text='Mangás Download V1.0', width=100, font=("Helvetica", 14)).pack(side=TOP)
        Label(frameA, text='Baixar', font=("Helvetica", 14)).pack(side=LEFT)
        Label(frameB, text='Link:').pack(side=LEFT)
        Entry(frameB, textvariable=self.link, width=70).pack(side=LEFT)
        Label(frameF, text='Salvar:').pack(side=LEFT, padx=5)
        Entry(frameF, width=70, textvariable=self.down, state=DISABLED).pack(side=LEFT, padx=5)
        Button(frameF, text='Procurar', command=self.salvarArquivo).pack(side=LEFT, padx=5)
        Label(frameC, text='Baixar e Renomear:').pack(side=LEFT)
        Radiobutton(frameC, text="Sim", variable=self.op, value=1).pack(side=LEFT)
        Radiobutton(frameC, text="Não", variable=self.op, value=2).pack(side=LEFT)
        Label(frameD, text='Baixar entre Intervalo:').pack(side=LEFT)
        botao = Button(frameG, text='Download', command=self.download)
        botao.pack()
        Radiobutton(frameD, text="Sim", variable=self.x, command=lambda: self.mostraInter(frameE, frameG, botao,
                                                                                          self.x.get()),
                    value=1).pack(side=LEFT)
        Radiobutton(frameD, text="Não", variable=self.x, command=lambda: self.mostraInter(frameE, frameG, botao,
                                                                                          self.x.get()),
                    value=2).pack(side=LEFT)
        Label(frameE, text='Inicio:').pack(side=LEFT)
        Entry(frameE, textvariable=self.ini, width=5).pack(side=LEFT)
        Label(frameE, text='Fim:').pack(side=LEFT)
        Entry(frameE, textvariable=self.fim, width=5).pack(side=LEFT)

    def criaInterfaceRenomear(self):
        # Frames Baixar
        frameA = Frame(self.frame2, bd=1)
        frameB = Frame(self.frame2, bd=1, highlightbackground="gray", highlightcolor="gray",
                       highlightthickness=1)
        frameC = Frame(self.frame2, bd=1)
        frameD = Frame(self.frame2, bd=1)
        frameA.pack(fill=X)
        frameD.pack(pady=5)
        frameB.pack(pady=5)
        frameC.pack(pady=5)
        ###
        Label(frameA, text='Renomear', font=("Helvetica", 14)).pack(side=LEFT)
        Label(frameD, text='Pasta\nPara\nRenomear:').pack(side=LEFT, padx=5)
        Entry(frameD, width=70, textvariable=self.rename, state=DISABLED).pack(side=LEFT, padx=5)
        Button(frameD, text='Procurar', command=self.renomearArquivo).pack(side=LEFT, padx=5)
        Label(frameB, text='Quer Renomear?').pack(side=LEFT)
        Radiobutton(frameB, text="Normal", variable=self.ren, value=1).pack(side=LEFT)
        Radiobutton(frameB, text="Celular", variable=self.ren, value=2).pack(side=LEFT)
        # Radiobutton(frameB, text="Re-Criar e Celular", variable=self.ren, value=3).pack(side=LEFT)
        Button(frameC, text='Renomear', command=self.renomear).pack()

    def mostraInter(self, frame, g, botao, tipo):
        self.ini.set('')
        self.fim.set('')
        if tipo == 1:
            frame.pack(pady=5)
        elif tipo == 2:
            frame.forget()
        g.forget()
        g.pack()
        botao.pack(side=LEFT, padx=5)

    def executa(self):
        self.tk.mainloop()

    def salvarArquivo(self):
        from tkinter import filedialog
        browser = filedialog.askdirectory(initialdir=self.dir, title="Salvar arquivo")
        self.dir = browser
        self.down.set(browser)

    def renomearArquivo(self):
        from tkinter import filedialog
        browser = filedialog.askdirectory(initialdir=self.rena, title="Salvar arquivo")
        self.rena = browser
        self.rename.set(browser)

    @staticmethod
    def validUrl(url):
        ref = 'http://unionmangas.site/leitor/'
        return url.startswith(ref)

    def download(self):
        url = self.link.get()
        if url != '' and self.validUrl(url):
            newWindow = Toplevel(self.tk)
            DownloadWindow(newWindow, self.icon, url, self.dir, self.op.get(), self.x.get(), self.ini.get(),
                           self.fim.get(),)
        else:
            from tkinter import messagebox
            messagebox.showinfo("Mangás Downloader", "Insira uma url valída!")

    def renomear(self):
        esc = self.ren.get()
        if esc == 1:
            self.frenomar(self.rena)
            self.frenomar(self.rena, col=True, t=0)
        elif esc == 2:
            self.frenomar(self.rena)
            self.frenomar(self.rena, col=True)
            self.frenomar(self.rena, t=0)
        elif esc == 3:
            self.frenomar(self.rena)
            self.frenomar(self.rena, r=False)
            print("Renomeando...")
            time.sleep(60)
            self.frenomar(self.rena, r=False, t=0)  # m=0)

    def frenomar(self, caminho, col=False, r=True, t=1):  # , m=1):
        for _, __, arquivo in os.walk(caminho):
            if str(_).find(caminho) != -1 and str(_).find("pycache") == -1:
                tam = __.__len__()
                if tam == 0:
                    i = 1
                    for arq in arquivo:
                        if not r:
                            # im = Image.open(_ + "\\" + arq)
                            # ima = im.copy()
                            # os.remove(_ + "\\" + arq)
                            # ima.save(_ + "\\-" + arq)
                            """im = Image.open(_ + "\\" + arq)
                            x, y = im.size
                            if m == 1:
                                im.resize((x, y), Image.ANTIALIAS).save(_ + "\\-" + arq)
                                os.remove(_ + "\\" + arq)
                            else:
                                im.resize((x, y), Image.ANTIALIAS).save(_ + "\\" + arq.replace("-", ""))
                                os.remove(_ + "\\" + arq)"""
                        else:
                            if not col:
                                aa: Union[List[bytes], List[str]] = arq.split(".")
                                os.rename(_ + "\\" + arq,
                                          _ + "\\" + self.nomei(aa[aa.__len__() - 2], col=True) +
                                          '.' + aa[aa.__len__() - 1])
                            else:
                                aa: Union[List[bytes], List[str]] = arq.split(".")
                                os.rename(_ + "\\" + arq,
                                          _ + "\\" + str(i) + '.' + aa[aa.__len__() - 1])
                                i += 1
        if t != 1:
            from tkinter import messagebox
            messagebox.showinfo("Mangás Downloader", "Arquivos Renomeados!")

    @staticmethod
    def nomei(i, col=False):
        if (str(i).__len__() < 2) and col:
            i = '0' + str(i)
        return str(i)
