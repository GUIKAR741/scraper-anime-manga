import requests as req
import os
import unicodedata
from bs4 import BeautifulSoup
import PIL.Image
from threading import *
from tkinter import *


class DownloadWindow:
    def __init__(self, tk, icon, url, path, ren, inter, iniInter, fimInter):
        from tkinter.ttk import Progressbar
        self.master = tk
        self.master.minsize(width=500, height=200)
        self.master.maxsize(width=500, height=200)
        self.master.iconbitmap(icon)

        self.name = StringVar()
        self.speed = StringVar()
        self.eta = StringVar()
        self.current = StringVar()
        self.total = StringVar()

        Label(self.master, text='Baixando...').pack(side=TOP, pady=15)

        self.framepart = Frame(tk)
        self.framepart.pack(pady=5)
        Label(self.framepart, textvariable=self.current).pack(side=LEFT)
        Label(self.framepart, textvariable=self.total).pack(side=LEFT)

        Label(self.master, textvariable=self.name).pack()

        self.framedt = Frame(tk, height=20, bd=1)
        self.framedt.pack(fill=X, padx=50, pady=10)

        Label(self.framedt, textvariable=self.speed).pack()
        Label(self.framedt, textvariable=self.eta).pack()
        self.mpb = Progressbar(self.master, orient="horizontal", length=300, mode="determinate")
        self.mpb.pack(pady=5)
        ren = True if ren == 1 else False
        if inter == 1:
            Thread(target=self.baixarInter, args=[path, url, ren, iniInter, fimInter]).start()
        elif inter == 2:
            Thread(target=self.fbaixar, args=[path, url, ren]).start()
        #     http://unionmangas.site/leitor/Nanatsu_no_Taizai(Pt-Br)/275

    def fbaixar(self, caminho, url, ren=False):
        urls = url.split('/')
        st = self.sanitizestring(str(urls[urls.__len__() - 2]))
        pasta = caminho + '\\' + st + urls[urls.__len__() - 1]
        bb = self.reqbeau(url)
        self.criapasta(pasta)
        i = 1
        self.name.set(url)
        imagens = bb.find_all('img', pag=True)
        for node in imagens:
            if str(node.get("src")).find("leitor") == -1:
                imagens.remove(node)
        self.mpb["maximum"] = len(imagens) - 1
        self.mpb["value"] = 0
        for node in imagens:
            img = 'http:' + node.get("src")
            n = str(img).split(".")
            nome = self.nomei(i, ren)
            self.baixarimg(pasta, nome, n, img)
            # self.eta.set("Ultimo arquivo baixado " + nome + "." + n[n.__len__() - 1])
            self.speed.set("Paginas " + nome + "/" + str(len(imagens)))
            i += 1
            self.mpb["value"] += 1
        from tkinter import messagebox
        messagebox.showinfo("Mangás Downloader", "Download Concluido!")
        self.master.destroy()

    def baixarInter(self, path, url, ren=False, ini=0, fim=0):
        ini = int(ini)
        fim = int(fim)
        for i in range(ini, fim + 1):
            self.current.set(str(ini) + '/' + str(fim))
            ini += 1
            # Thread(target=self.fbaixar, args=[path, url, ren]).start()
            # print(url + str(self.nomei(i, True)))
            self.ffbaixar(path, url + str(self.nomei(i, True)), ren)
        from tkinter import messagebox
        messagebox.showinfo("Mangás Downloader", "Download Concluido!")
        self.master.destroy()

    def ffbaixar(self, caminho, url, ren=False):
        urls = url.split('/')
        st = self.sanitizestring(str(urls[urls.__len__() - 2]))
        pasta = caminho + '\\' + st + urls[urls.__len__() - 1]
        bb = self.reqbeau(url)
        self.criapasta(pasta)
        i = 1
        self.name.set(url)
        imagens = bb.find_all('img', pag=True)
        for node in imagens:
            if str(node.get("src")).find("leitor") == -1:
                imagens.remove(node)
        self.mpb["maximum"] = len(imagens) - 1
        self.mpb["value"] = 0
        for node in imagens:
            img = 'http:' + node.get("src")
            n = str(img).split(".")
            nome = self.nomei(i, ren)
            self.baixarimg(pasta, nome, n, img)
            # self.eta.set("Ultimo arquivo baixado " + nome + "." + n[n.__len__() - 1])
            self.speed.set("Paginas " + nome + "/" + str(len(imagens)))
            i += 1
            self.mpb["value"] += 1

    @staticmethod
    def sanitizestring(palavra):
        # Unicode normalize transforma um caracter em seu equivalente em latin.
        nfkd = unicodedata.normalize('NFKD', palavra)
        palavrasemacento = u"".join([c for c in nfkd if not unicodedata.combining(c)])
        # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
        return re.sub('[^a-zA-Z0-9 \\\]', '', palavrasemacento)

    @staticmethod
    def criapasta(pasta):
        if not os.path.isdir(pasta):
            os.mkdir(pasta)

    @staticmethod
    def nomei(i, col=False):
        if (str(i).__len__() < 2) and col:
            i = '0' + str(i)
        return str(i)

    @staticmethod
    def reqbeau(url):
        r = req.get(url)
        b = BeautifulSoup(r.content, 'html.parser')
        return b

    @staticmethod
    def baixarimg(pasta, i, n, urlImg):
        rr = req.get(str(urlImg))
        with open(pasta + "/" + str(i) + "." + n[n.__len__() - 1], 'wb') as code:
            code.write(rr.content)
        PIL.Image.open(pasta + "/" + str(i) + "." + n[n.__len__() - 1]).save(
            pasta + "/" + str(i) + "." + n[n.__len__() - 1])
