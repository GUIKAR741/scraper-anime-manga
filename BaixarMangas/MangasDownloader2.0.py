from io import StringIO
import json
import PIL.Image
import unicodedata
from bs4 import BeautifulSoup
import requests as req
import os
from threading import Thread
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import re


class Manga:
    def __init__(self, tk, telaP, texto, nome="", url=""):
        self.master = tk
        self.telaP = telaP
        self.master.minsize(width=500, height=150)
        self.master.maxsize(width=500, height=150)
        # self.master.iconbitmap(icon)

        self.name = StringVar()
        self.speed = StringVar()
        self.eta = StringVar()

        Label(self.master, text=texto).pack(side=TOP, pady=15)

        self.framepart = Frame(tk)
        self.framepart.pack(pady=5)

        Label(self.master, textvariable=self.name).pack()

        self.framedt = Frame(tk, height=20, bd=1)
        self.framedt.pack(fill=X, padx=50, pady=10)

        Label(self.framedt, textvariable=self.speed).pack()
        Label(self.framedt, textvariable=self.eta).pack()
        from tkinter.ttk import Progressbar
        self.mpb = Progressbar(self.master, orient="horizontal", length=300, mode="determinate")
        self.mpb.pack(pady=5)
        self.tam = 0
        self.per = 0
        if texto == 'Atualizando...':
            Thread(target=self.selBusca).start()
        elif texto == "Procurando...":
            Thread(target=self.pegaCap, args=[nome, url]).start()

    def buscaPag(self, link, direcao=True, maximo=0):
        def reqLink(u):
            try:
                resul = req.get(u)
            except (Exception, req.RequestException):
                resul = reqLink(u)
            return resul

        num = int(re.compile('([0-9]+)').findall(link)[0])
        if not os.path.isfile("mangas/Pagina %s.json" % num):
            info = {'nome': [], 'link': []}
            r = reqLink(link)
            b = BeautifulSoup(r.text, 'html.parser')
            mangas = b.find_all('div', 'bloco-manga')
            for i in mangas:
                lin = i.find_all('a')[-1]
                info['nome'].append(DownloadWindow.sanitizestring(lin.get("href").split('/')[-1].replace('-', ' ').title()))
                # info['nome'].append(DownloadWindow.sanitizestring(lin.text))
                info['link'].append(lin.get("href"))
            io = StringIO()
            json.dump(info, io)
            jsonS = io.getvalue()
            arq = 'mangas/Pagina ' + str(num) + '.json'
            arq = open(arq, 'w')
            arq.write(jsonS)
            arq.close()
        if self.per < int(self.tam):
            self.per += 1
        self.mpb['value'] = self.per
        self.eta.set('Paginas Percorridas: %d' % self.per)
        link = "https://unionmangas.top/lista-mangas/a-z/%s/*"
        if direcao and num + 1 <= maximo:
            self.buscaPag((link % (int(num) + 1)), direcao, maximo)
        elif not direcao and num - 1 > 0:
            self.buscaPag((link % (int(num) - 1)), direcao, maximo)

    def selBusca(self):
        def reqLink(u):
            try:
                resul = req.get(u)
            except (Exception, req.RequestException):
                resul = reqLink(u)
            return resul

        r = reqLink("https://unionmangas.top/lista-mangas")
        b = BeautifulSoup(r.text, 'html.parser')
        paginacao = b.find("ul", "pagination").find_all('span', "sr-only")
        link = "https://unionmangas.top/lista-mangas/a-z/%s/*"
        fim = 0
        for i in paginacao:
            if i.text == 'End':
                fim = int(re.compile('([0-9]+)').findall(i.parent.get("href"))[0])
        self.mpb['maximum'] = self.tam = fim
        self.speed.set('Paginas: ' + str(self.tam))
        self.eta.set('Paginas Percorridas: %d' % 0)
        meio = fim // 2
        t = [Thread(target=self.buscaPag, args=[(link % 1), True, fim]),
             Thread(target=self.buscaPag, args=[(link % (meio - 1)), False, fim]),
             Thread(target=self.buscaPag, args=[(link % meio), True, fim]),
             Thread(target=self.buscaPag, args=[(link % fim), False, fim])]
        for i in t:
            i.start()
        for i in t:
            i.join()
        self.junta()
        self.telaP.voltar()
        self.master.destroy()
        messagebox.showinfo("Anime Downloader", "Atualização Finalizada!")

    def junta(self):
        dic = dict({'nome': [], 'link': []})
        for l, j, k in os.walk("mangas/"):
            lis = []
            for ll in k:
                s = re.compile('([0-9]+)').findall(ll)
                if os.path.isfile("mangas/Pagina " + (s[0] if len(s) else '') + ".json"):
                    lis.append(int(s[0]))
            lis.sort()
            for li in lis:
                if os.path.isfile("mangas/Pagina " + str(li) + ".json"):
                    arq = open("mangas/Pagina " + str(li) + ".json", 'r')
                    js = json.load(arq)
                    dic['nome'] += js['nome']
                    dic['link'] += js['link']
                    arq.close()
                    os.remove("mangas/Pagina " + str(li) + ".json")
        io = StringIO()
        json.dump(dic, io)
        jsonS = io.getvalue()
        arq = open("mangas/Paginas.json", 'w')
        arq.write(jsonS)
        arq.close()

    def pegaCap(self, nome, link):
        def reqLink(u):
            try:
                resul = req.get(u)
            except (Exception, req.RequestException):
                resul = reqLink(u)
            return resul

        info = {'cap': [], 'link': []}
        r = reqLink(link)
        b = BeautifulSoup(r.text, 'html.parser')
        cap = b.find_all('div', 'row lancamento-linha')
        for i in cap:
            info['cap'].append(i.a.text)
            info['link'].append(i.a.get("href"))
        io = StringIO()
        json.dump(info, io)
        jsonS = io.getvalue()
        arq = open(("mangas/%s.json" % nome), 'w')
        arq.write(jsonS)
        arq.close()
        self.master.destroy()
        self.telaP.mostraAni()

    def criaMan(self):
        abc = open("mangas/Paginas.json")
        man = json.load(abc)
        abc.close()
        for i in range(len(man['nome'])):
            self.pegaCap(str(i + 1) + " " + man['nome'][i], man['link'][i])


class Tela:
    def __init__(self):
        self.nomeApp="Mangás Downloader"
        self.tk = Tk()
        self.tk.geometry("600x500")
        self.tk.resizable(False, False)
        if not os.path.isdir('mangas'):
            os.mkdir('mangas')
        if os.path.isfile("mangas/Paginas.json"):
            self.ani = json.load(open("mangas/Paginas.json"))
        else:
            self.ani = {'nome': [], 'link': []}
        self.mylist = None
        self.scrollbar = None
        self.fra1 = None
        self.fra2 = None
        self.bt1 = None
        self.bt2 = None
        self.bt3 = None
        self.bt4 = None
        self.ren1 = None
        self.ren2 = None
        self.ren3 = None
        self.btProc = None
        self.etProc = None
        self.isVoltar = False
        self.dir = os.getcwd()
        self.busca = StringVar()
        self.inicia()
        self.tk.title(self.nomeApp)
        self.selecionado = -1
        # self.icon = self.dir + '\\' + 'down.ico'
        # self.tk.iconbitmap(self.icon)
        self.tk.mainloop()

    def inicia(self):
        self.fra1 = Frame(self.tk, bd=1)
        fra3 = Frame(self.tk, bd=1)
        self.fra2 = Frame(self.tk, bd=1)
        self.scrollbar = ttk.Scrollbar(self.tk, orient=VERTICAL)
        self.mylist = Listbox(self.tk, yscrollcommand=self.scrollbar.set)
        for i in range(len(self.ani['nome'])):
            self.mylist.insert(END, self.ani['nome'][i])
        self.scrollbar.config(command=self.mylist.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        # Buscar
        Label(self.fra1, text='Anime:').pack(side=LEFT)
        self.etProc = Entry(self.fra1, textvariable=self.busca, width=65)
        self.etProc.pack(side=LEFT)
        self.btProc = Button(self.fra1, text='Procurar', command=self.procura)
        self.ren1 = Button(fra3, text="Renomear Normal", command=lambda: self.renomear(1))
        self.ren2 = Button(fra3, text="Renomear Celular", command=lambda: self.renomear(2))
        self.ren3 = Button(fra3, text="Renomear Re-Criar e Celular", command=lambda: self.renomear(3))
        self.btProc.pack(side=LEFT)
        self.fra1.pack(fill=X)
        fra3.pack()
        # Lista
        self.mylist.pack(fill=BOTH, expand=True)
        # Botoes
        self.bt1 = Button(self.fra2, text="Pegar valor", command=self.li)
        self.bt2 = Button(self.fra2, text="Voltar", command=self.voltar)
        self.bt3 = Button(self.fra2, text="Baixar", command=self.baixar)
        self.bt4 = Button(self.fra2, text="Atualizar Base", command=self.buscaP)
        self.ren1.pack(side=LEFT)
        self.ren2.pack(side=LEFT)
        self.ren3.pack(side=LEFT)
        self.bt4.pack(side=LEFT)
        self.bt1.pack(side=LEFT)
        self.fra2.pack()

    def li(self):
        if self.mylist.curselection():
            buscar = self.mylist.get(self.mylist.curselection()).lower()
            ind = -1
            for i in range(len(self.ani['nome'])):
                if buscar in self.ani['nome'][i].lower():
                    ind = i
                    break
            self.selecionado = ind
            url = self.ani['link'][ind]
            nome = str(ind + 1) + " " + DownloadWindow.sanitizestring(self.ani['nome'][ind])
            newWindow = Toplevel(self.tk)
            Thread(target=Manga, args=[newWindow, self, 'Procurando...', nome, url]).start()

    def mostraAni(self):
        self.ani = json.load(open("mangas/" + str(self.selecionado + 1) + " "
                                  + DownloadWindow.sanitizestring(
            self.ani['nome'][self.selecionado]) + ".json"))
        self.atualiza("cap")
        self.bt1.forget()
        self.bt4.forget()
        self.isVoltar=True
        self.bt2.pack(side=LEFT)
        self.bt3.pack(side=LEFT)

    def procura(self):
        buscar = self.busca.get().lower()
        self.busca.set('')
        if self.btProc['text'] == 'Procurar':
            self.btProc['text'] = 'Resetar'
            self.etProc['state'] = DISABLED
            ind = []
            for i in range(len(self.ani['nome'])):
                if buscar in self.ani['nome'][i].lower():
                    ind.append(i)
            if ind is not []:
                for i in range(self.mylist.size()):
                    self.mylist.delete(0)
                for i in ind:
                    self.mylist.insert(END, self.ani['nome'][i])
            else:
                messagebox.showerror("Anime Downloader", "Anime não Encontrado!")
        else:
            self.btProc['text'] = 'Procurar'
            self.etProc['state'] = NORMAL
            if self.isVoltar:
                self.voltar()
            else:
                self.atualiza('nome')
            self.isVoltar=False

    def voltar(self):
        self.ani = json.load(open("mangas/Paginas.json"))
        self.atualiza("nome")
        self.bt2.forget()
        self.bt3.forget()
        self.bt4.pack(side=LEFT)
        self.bt1.pack(side=LEFT)

    def atualiza(self, campo):
        for i in range(self.mylist.size()):
            self.mylist.delete(0)
        for i in range(len(self.ani[campo])):
            self.mylist.insert(END, self.ani[campo][i])

    def baixar(self):
        if self.mylist.curselection():
            url = self.ani['link'][self.mylist.curselection()[0]]
            newWindow = Toplevel(self.tk)
            Thread(target=DownloadWindow, args=[newWindow, url, self.dir]).start()

    def buscaP(self):
        newWindow = Toplevel(self.tk)
        Thread(target=Manga, args=[newWindow, self, 'Atualizando...']).start()

    def renomear(self, esc):
        # esc = self.ren.get()
        Thread(target=self.renomearThread, args=[esc]).start()

    def renomearThread(self, esc):
        if esc == 1:
            self.frenomar(self.dir)
            self.frenomar(self.dir, col=True, mensagem=0)
        elif esc == 2:
            self.frenomar(self.dir)
            self.frenomar(self.dir, col=True)
            self.frenomar(self.dir, mensagem=0)
        elif esc == 3:
            self.frenomar(self.dir)
            self.frenomar(self.dir, r=False)
            # print("Renomeando...")
            # time.sleep(60)
            self.frenomar(self.dir, r=False, mensagem=0, colocaHifen=0)

    def frenomar(self, caminho, col=False, r=True, mensagem=1, colocaHifen=1):
        for _, __, arquivo in os.walk(caminho):
            if str(_).find(caminho) != -1 and str(_).find("pycache") == -1 and str(_).find(caminho+"/mangas") == -1:
                tam = __.__len__()
                if tam == 0:
                    i = 1
                    arquivo.sort()
                    for arq in arquivo:
                        if not r:
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
    def __init__(self, tk, url, path):
        self.master = tk
        self.master.minsize(width=500, height=200)
        self.master.maxsize(width=500, height=200)
        # self.master.iconbitmap(icon)

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
        Thread(target=self.fbaixar, args=[path, url]).start()

    def fbaixar(self, caminho, url, ren=False):
        urls = url.split('/')
        self.mpb["value"] = 0
        st = self.sanitizestring(str(urls[urls.__len__() - 2]))
        pasta = caminho + '/' + st +"_"+ urls[urls.__len__() - 1]
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
            n = str(img).split(".")
            nome = self.nomei(i, ren)
            self.baixarimg(pasta, nome, n, img)
            self.speed.set("Paginas " + nome + "/" + str(len(imagens)))
            i += 1
            self.mpb["value"] += 1
        from tkinter import messagebox
        self.master.destroy()
        messagebox.showinfo("Mangás Downloader", "Download Concluido!")

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
        try:
            r = req.get(url)
            b = BeautifulSoup(r.content, 'html.parser')
        except (Exception, req.RequestException):
            b = DownloadWindow.reqbeau(url)
        return b

    @staticmethod
    def baixarimg(pasta, i, n, urlImg):
        rr = req.get(str(urlImg))
        with open(pasta + "/" + str(i) + "." + n[n.__len__() - 1], 'wb') as code:
            code.write(rr.content)
        PIL.Image.open(pasta + "/" + str(i) + "." + n[n.__len__() - 1]).save(
            pasta + "/" + str(i) + "." + n[n.__len__() - 1])


if __name__ == "__main__":
    Tela()
