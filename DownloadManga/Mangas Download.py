# coding=utf-8
import requests as req
import unicodedata  # Python3
from bs4 import BeautifulSoup
import PIL.Image
from threading import *
# import time
import os
from tkinter import *


class MangasDownload:
    def __init__(self, tk):
        # Instancia Tkinter
        self.tk = tk
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
        self.rename.set(self.rena)
        self.x = IntVar()
        self.x.set(2)
        # Inicia aplicativo
        self.inicia()
        # cria Frames
        self.frames()
        # cria interface dentro dos frames
        self.criaInterfaceBaixar()
        self.criaInterfaceRenomear()

    def inicia(self):
        self.tk.geometry("600x450")
        self.tk.resizable(False, False)
        # self.icon = self.dir + '\\' + 'down.ico'
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
        Radiobutton(frameB, text="Re-Criar e Celular", variable=self.ren, value=3).pack(side=LEFT)
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
        return (("http://unionmangas." in url) or ("https://unionmangas." in url)) and ("leitor" in url)

    def download(self):
        url = self.link.get()
        self.link.set('')
        if url != '' and self.validUrl(url):
            newWindow = Toplevel(self.tk)
            DownloadWindow(newWindow, self.icon, url, self.dir, self.op.get(), self.x.get(), self.ini.get(),
                           self.fim.get())
        else:
            from tkinter import messagebox
            messagebox.showinfo("Mangás Downloader", "Insira uma url valída!")

    def renomear(self):
        esc = self.ren.get()
        Thread(target=self.renomearThread, args=[esc]).start()

    def renomearThread(self, esc):
        if esc == 1:
            self.frenomar(self.rena)
            self.frenomar(self.rena, col=True, mensagem=0)
        elif esc == 2:
            self.frenomar(self.rena)
            self.frenomar(self.rena, col=True)
            self.frenomar(self.rena, mensagem=0)
        elif esc == 3:
            self.frenomar(self.rena)
            self.frenomar(self.rena, r=False)
            # print("Renomeando...")
            # time.sleep(60)
            self.frenomar(self.rena, r=False, mensagem=0, colocaHifen=0)

    """def frenomar(self, caminho, col=False, r=True, t=1, m=1):
        from tkinter import messagebox
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
                            try:
                                im = PIL.Image.open(_ + "\\" + arq)
                                x, y = im.size
                                if m == 1:
                                    im.resize((x, y), PIL.Image.ANTIALIAS).save(_ + "\\-" + arq)
                                    os.remove(_ + "\\" + arq)
                                else:
                                    im.resize((x, y), PIL.Image.ANTIALIAS).save(_ + "\\" + arq.replace("-", ""))
                                    os.remove(_ + "\\" + arq)
                                print(' a ')
                            except PermissionError:
                                print()
                                # messagebox.showerror("Mangás Downloader", "Erro no Arquivo:\n" + _ + "\\" + arq)
                        else:
                            if not col:
                                aa = arq.split(".")
                                os.rename(_ + "\\" + arq,
                                          _ + "\\" + self.nomei(aa[aa.__len__() - 2], col=True) +
                                          '.' + aa[aa.__len__() - 1])
                            else:
                                aa = arq.split(".")
                                os.rename(_ + "\\" + arq,
                                          _ + "\\" + str(i) + '.' + aa[aa.__len__() - 1])
                                i += 1
        if t != 1:
            messagebox.showinfo("Mangás Downloader", "Arquivos Renomeados!")"""

    def frenomar(self, caminho, col=False, r=True, mensagem=1, colocaHifen=1):
        for _, __, arquivo in os.walk(caminho):
            if str(_).find(caminho) != -1 and str(_).find("pycache") == -1:
                tam = __.__len__()
                if tam == 0:
                    i = 1
                    arquivo.sort()
                    for arq in arquivo:
                        if not r:
                            # im = Image.open(_ + "\\" + arq)
                            # ima = im.copy()
                            # os.remove(_ + "\\" + arq)
                            # ima.save(_ + "\\-" + arq)
                            # C:/Users/Guilherme/Desktop/download mangas/img\BlackClover138\15.jpg
                            # C:/Users/Guilherme/Desktop/download mangas/img\BlackClover144\04.jpg
                            try:
                                if 'Thumbs' in arq:
                                    continue
                                im = PIL.Image.open(_ + "/" + arq)
                                x, y = im.size
                                if colocaHifen == 1:
                                    im.resize((x, y), PIL.Image.ANTIALIAS).save(_ + "/-" + arq)
                                    os.remove(_ + "/" + arq)
                                else:
                                    im.resize((x, y), PIL.Image.ANTIALIAS).save(_ + "/" + arq.replace("-", ""))
                                    os.remove(_ + "/" + arq)
                            except:
                                from tkinter import messagebox
                                messagebox.showerror("Mangás Downloader", "Erro no Arquivo:\n" + _ + "/" + arq)
                        else:
                            if not col:
                                aa = arq.split(".")
                                os.rename(_ + "/" + arq,
                                          _ + "/" + self.nomei(aa[aa.__len__() - 2], col=True) +
                                          '.' + aa[aa.__len__() - 1])
                            else:
                                aa = arq.split(".")
                                os.rename(_ + "/" + arq,
                                          _ + "/" + str(i) + '.' + aa[aa.__len__() - 1])
                                i += 1
        if mensagem != 1:
            from tkinter import messagebox
            messagebox.showinfo("Mangás Downloader", "Arquivos Renomeados!")

    @staticmethod
    def nomei(i, col=False):
        if (str(i).__len__() < 2) and col:
            i = '0' + str(i)
        return str(i)


class DownloadWindow:
    def __init__(self, tk, icon, url, path, ren, inter, iniInter, fimInter):
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
        from tkinter.ttk import Progressbar
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
        self.mpb["value"] = 0
        st = self.sanitizestring(str(urls[urls.__len__() - 2]))
        pasta = caminho + '/' + st + urls[urls.__len__() - 1]
        bb = self.reqbeau(url)
        self.criapasta(pasta)
        i = 1
        self.name.set(url)
        imagens = bb.find_all('img', pag=True)
        self.speed.set("")
        for node in imagens:
            if str(node.get("src")).find("leitor") == -1:
                imagens.remove(node)
        self.mpb["maximum"] = len(imagens)
        for node in imagens:
            if "http:" in node.get("src"):
                img = node.get("src")
            elif 'https:' in node.get("src"):
                img = node.get("src")
            else:
                img = 'http:' + node.get("src")
            # img = 'http:' + node.get("src") if ('http:' not in node.get("src")) or ('https:' not in node.get(
            # "src")) else node.get("src")
            n = str(img).split(".")
            nome = self.nomei(i, ren)
            self.baixarimg(pasta, nome, n, img)
            self.speed.set("Paginas " + nome + "/" + str(len(imagens)))
            i += 1
            self.mpb["value"] += 1
        from tkinter import messagebox
        self.master.destroy()
        messagebox.showinfo("Mangás Downloader", "Download Concluido!")

    def baixarInter(self, path, url, ren=False, ini=0, fim=0):
        ini = int(ini)
        fim = int(fim)
        for i in range(ini, fim + 1):
            self.current.set(self.nomei(ini, True) + '/' + self.nomei(fim, True))
            ini += 1
            self.ffbaixar(path, url + str(self.nomei(i, True)), ren)
        from tkinter import messagebox
        self.master.destroy()
        messagebox.showinfo("Mangás Downloader", "Download Concluido!")

    def ffbaixar(self, caminho, url, ren=False):
        self.speed.set("")
        self.mpb["value"] = 0
        urls = url.split('/')
        st = self.sanitizestring(str(urls[urls.__len__() - 2]))
        pasta = caminho + '/' + st + urls[urls.__len__() - 1]
        bb = self.reqbeau(url)
        self.criapasta(pasta)
        i = 1
        self.name.set(url)
        imagens = bb.find_all('img', pag=True)
        for node in imagens:
            if str(node.get("src")).find("leitor") == -1:
                imagens.remove(node)
        self.mpb["maximum"] = len(imagens)
        for node in imagens:
            img = 'http:' + node.get("src") if 'http:' not in node.get("src") else node.get("src")
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
        return re.sub("[^a-zA-Z0-9 \\\]", '', palavrasemacento)

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


def main():
    root = Tk()
    MangasDownload(root)
    # icon = os.getcwd() + '/' + 'down.ico'
    # root.wm_iconbitmap('down.ico')
    root.mainloop()


if __name__ == '__main__':
    main()
