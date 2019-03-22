from io import StringIO
from json import dump, load
from os import getcwd, mkdir, path, remove, rename, walk
from re import sub, compile
from threading import Thread
from tkinter import (BOTH, DISABLED, END, LEFT, NORMAL, RIGHT, TOP, VERTICAL,
                     Button, Entry, Frame, Label, Listbox, StringVar, Tk,
                     Toplevel, X, Y, messagebox, ttk)
from unicodedata import combining, normalize

from bs4 import BeautifulSoup
from PIL.Image import ANTIALIAS
from PIL.Image import open as open_image
from requests import RequestException, get


class Manga:
    def __init__(self, tk, tela_p, texto, nome="", url=""):
        self.master = tk
        self.telaP = tela_p
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
        self.mpb = ttk.Progressbar(
            self.master, orient="horizontal", length=300, mode="determinate")
        self.mpb.pack(pady=5)
        self.tam = 0
        self.per = 0
        if texto == 'Atualizando...':
            Thread(target=self.sel_busca).start()
        elif texto == "Procurando...":
            Thread(target=self.pega_cap, args=[nome, url]).start()

    def busca_pag(self, link, direcao=True, maximo=0):
        def req_link(u):
            try:
                resul = get(u)
            except (Exception, RequestException):
                resul = req_link(u)
            return resul

        num = int(compile('([0-9]+)').findall(link)[0])
        if not path.isfile("mangas/Pagina %s.json" % num):
            info = {'nome': [], 'link': []}
            r = req_link(link)
            b = BeautifulSoup(r.text, 'html.parser')
            mangas = b.find_all('div', 'bloco-manga')
            for i in mangas:
                lin = i.find_all('a')[-1]
                info['nome'].append(DownloadWindow.sanitizestring(
                    lin.get("href").split('/')[-1].replace('-', ' ').title()))
                # info['nome'].append(DownloadWindow.sanitizestring(lin.text))
                info['link'].append(lin.get("href"))
            io = StringIO()
            dump(info, io)
            json_s = io.getvalue()
            arq = 'mangas/Pagina ' + str(num) + '.json'
            arq = open(arq, 'w')
            arq.write(json_s)
            arq.close()
        if self.per < int(self.tam):
            self.per += 1
        self.mpb['value'] = self.per
        self.eta.set('Paginas Percorridas: %d' % self.per)
        link = "https://unionmangas.top/lista-mangas/a-z/%s/*"
        if direcao and num + 1 <= maximo:
            self.busca_pag((link % (int(num) + 1)), direcao, maximo)
        elif not direcao and num - 1 > 0:
            self.busca_pag((link % (int(num) - 1)), direcao, maximo)

    def sel_busca(self):
        def req_link(u):
            try:
                resul = get(u)
            except (Exception, RequestException):
                resul = req_link(u)
            return resul

        r = req_link("https://unionmangas.top/lista-mangas")
        b = BeautifulSoup(r.text, 'html.parser')
        paginacao = b.find("ul", "pagination").find_all('span', "sr-only")
        link = "https://unionmangas.top/lista-mangas/a-z/%s/*"
        fim = 0
        for i in paginacao:
            if i.text == 'End':
                fim = int(compile(
                    '([0-9]+)').findall(i.parent.get("href"))[0])
        self.mpb['maximum'] = self.tam = fim
        self.speed.set('Paginas: ' + str(self.tam))
        self.eta.set('Paginas Percorridas: %d' % 0)
        meio = fim // 2
        t = [Thread(target=self.busca_pag, args=[(link % 1), True, fim]),
             Thread(target=self.busca_pag, args=[
                    (link % (meio - 1)), False, fim]),
             Thread(target=self.busca_pag, args=[(link % meio), True, fim]),
             Thread(target=self.busca_pag, args=[(link % fim), False, fim])]
        for i in t:
            i.start()
        for i in t:
            i.join()
        self.junta()
        self.telaP.voltar()
        self.master.destroy()
        messagebox.showinfo("Anime Downloader", "Atualização Finalizada!")

    @staticmethod
    def junta():
        dic = dict({'nome': [], 'link': []})
        for k in walk("mangas/"):
            lis = []
            for ll in k[2]:
                s = compile('([0-9]+)').findall(ll)
                if path.isfile("mangas/Pagina " + (s[0] if len(s) else '') + ".json"):
                    lis.append(int(s[0]))
            lis.sort()
            for li in lis:
                if path.isfile("mangas/Pagina " + str(li) + ".json"):
                    arq = open("mangas/Pagina " + str(li) + ".json", 'r')
                    js = load(arq)
                    dic['nome'] += js['nome']
                    dic['link'] += js['link']
                    arq.close()
                    remove("mangas/Pagina " + str(li) + ".json")
        io = StringIO()
        dump(dic, io)
        json_s = io.getvalue()
        arq = open("mangas/Paginas.json", 'w')
        arq.write(json_s)
        arq.close()

    def pega_cap(self, nome, link):
        def req_link(u):
            try:
                resul = get(u)
            except (Exception, RequestException):
                resul = req_link(u)
            return resul

        info = {'cap': [], 'link': []}
        r = req_link(link)
        b = BeautifulSoup(r.text, 'html.parser')
        cap = b.find_all('div', 'row lancamento-linha')
        for i in cap:
            info['cap'].append(i.a.text)
            info['link'].append(i.a.get("href"))
        io = StringIO()
        dump(info, io)
        json_s = io.getvalue()
        arq = open(("mangas/%s.json" % nome), 'w')
        arq.write(json_s)
        arq.close()
        self.master.destroy()
        self.telaP.mostra_ani()

    def cria_man(self):
        abc = open("mangas/Paginas.json")
        man = load(abc)
        abc.close()
        for i in range(len(man['nome'])):
            self.pega_cap(str(i + 1) + " " + man['nome'][i], man['link'][i])


class Tela:
    def __init__(self):
        self.nomeApp = "Mangás Downloader"
        self.tk = Tk()
        self.tk.geometry("600x500")
        self.tk.resizable(False, False)
        if not path.isdir('mangas'):
            mkdir('mangas')
        if path.isfile("mangas/Paginas.json"):
            self.ani = load(open("mangas/Paginas.json"))
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
        self.dir = getcwd()
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
        self.ren1 = Button(fra3, text="Renomear Normal",
                           command=lambda: self.renomear(1))
        self.ren2 = Button(fra3, text="Renomear Celular",
                           command=lambda: self.renomear(2))
        self.ren3 = Button(
            fra3, text="Renomear Re-Criar e Celular", command=lambda: self.renomear(3))
        self.btProc.pack(side=LEFT)
        self.fra1.pack(fill=X)
        fra3.pack()
        # Lista
        self.mylist.pack(fill=BOTH, expand=True)
        # Botoes
        self.bt1 = Button(self.fra2, text="Pegar valor", command=self.li)
        self.bt2 = Button(self.fra2, text="Voltar", command=self.voltar)
        self.bt3 = Button(self.fra2, text="Baixar", command=self.baixar)
        self.bt4 = Button(self.fra2, text="Atualizar Base",
                          command=self.busca_p)
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
            nome = str(ind + 1) + " " + \
                DownloadWindow.sanitizestring(self.ani['nome'][ind])
            new_window = Toplevel(self.tk)
            Thread(target=Manga, args=[
                   new_window, self, 'Procurando...', nome, url]).start()

    def mostra_ani(self):
        self.ani = load(open("mangas/" + str(self.selecionado + 1) + " " +
                             DownloadWindow.sanitizestring(self.ani['nome'][self.selecionado]) + ".json"))
        self.atualiza("cap")
        self.bt1.forget()
        self.bt4.forget()
        self.isVoltar = True
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
                messagebox.showerror("Anime Downloader",
                                     "Anime não Encontrado!")
        else:
            self.btProc['text'] = 'Procurar'
            self.etProc['state'] = NORMAL
            if self.isVoltar:
                self.voltar()
            else:
                self.atualiza('nome')
            self.isVoltar = False

    def voltar(self):
        self.ani = load(open("mangas/Paginas.json"))
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
            new_window = Toplevel(self.tk)
            Thread(target=DownloadWindow, args=[
                   new_window, url, self.dir]).start()

    def busca_p(self):
        new_window = Toplevel(self.tk)
        Thread(target=Manga, args=[new_window, self, 'Atualizando...']).start()

    def renomear(self, esc):
        # esc = self.ren.get()
        Thread(target=self.renomear_thread, args=[esc]).start()

    def renomear_thread(self, esc):
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
            self.frenomar(self.dir, r=False, mensagem=0, coloca_hifen=0)

    def frenomar(self, caminho, col=False, r=True, mensagem=1, coloca_hifen=1):
        for _, __, arquivo in walk(caminho):
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
                                im = open_image(_ + "/" + arq)
                                x, y = im.size
                                if coloca_hifen == 1:
                                    im.resize((x, y), ANTIALIAS).save(
                                        _ + "/-" + arq)
                                    remove(_ + "/" + arq)
                                else:
                                    im.resize((x, y), ANTIALIAS).save(
                                        _ + "/" + arq.replace("-", ""))
                                    remove(_ + "/" + arq)
                            except (ValueError, IOError):
                                from tkinter import messagebox
                                messagebox.showerror(
                                    "Mangás Downloader", "Erro no Arquivo:\n" + _ + "/" + arq)
                        else:
                            if not col:
                                aa = arq.split(".")
                                rename(_ + "/" + arq, _ + "/" + self.nomei(aa[aa.__len__() - 2], col=True) + '.' +
                                       aa[aa.__len__() - 1])
                            else:
                                aa = arq.split(".")
                                rename(_ + "/" + arq, _ + "/" +
                                       str(i) + '.' + aa[aa.__len__() - 1])
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
    def __init__(self, tk, url, pathdown):
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
        self.mpb = ttk.Progressbar(
            self.master, orient="horizontal", length=300, mode="determinate")
        self.mpb.pack(pady=5)
        Thread(target=self.fbaixar, args=[pathdown, url]).start()

    def fbaixar(self, caminho, url, ren=False):
        urls = url.split('/')
        self.mpb["value"] = 0
        st = self.sanitizestring(str(urls[urls.__len__() - 2]))
        pasta = caminho + '/' + st + "_" + urls[urls.__len__() - 1]
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
        nfkd = normalize('NFKD', palavra)
        palavrasemacento = u"".join([c for c in nfkd if not combining(c)])
        # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
        return sub("[^a-zA-Z0-9 ]", '', palavrasemacento)

    @staticmethod
    def criapasta(pasta):
        if not path.isdir(pasta):
            mkdir(pasta)

    @staticmethod
    def nomei(i, col=False):
        if (str(i).__len__() < 2) and col:
            i = '0' + str(i)
        return str(i)

    @staticmethod
    def reqbeau(url):
        try:
            r = get(url)
            b = BeautifulSoup(r.content, 'html.parser')
        except (Exception, RequestException):
            b = DownloadWindow.reqbeau(url)
        return b

    @staticmethod
    def baixarimg(pasta, i, n, url_img):
        rr = get(str(url_img))
        with open(pasta + "/" + str(i) + "." + n[n.__len__() - 1], 'wb') as code:
            code.write(rr.content)
        open_image(pasta + "/" + str(i) + "." + n[n.__len__() - 1]).save(
            pasta + "/" + str(i) + "." + n[n.__len__() - 1])


if __name__ == "__main__":
    Tela()
