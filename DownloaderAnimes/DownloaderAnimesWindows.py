import unicodedata
from io import StringIO
from tkinter import *
import json
import os
from tkinter import messagebox
import wget
from bs4 import BeautifulSoup
import requests as req
from tkinter import ttk
from threading import Thread


class Anime:
    def __init__(self, tk, telaP, texto, nome="", url=""):
        self.master = tk
        self.telaP = telaP
        self.master.minsize(width=500, height=200)
        self.master.maxsize(width=500, height=200)
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
            Thread(target=self.buscaPagina, args=[True]).start()
        elif texto == "Procurando...":
            Thread(target=self.paginaAnime, args=[nome, url]).start()

    def buscaPagina(self, buscar=False):
        def reqLink(u):
            try:
                resul = req.get(u)
            except (Exception, req.RequestException):
                resul = reqLink(u)
            return resul

        if not os.path.isfile("animes/Paginas.json") or buscar:
            link = "https://www.superanimes.site/lista"
            r = reqLink(link)
            b = BeautifulSoup(r.content, 'html.parser')
            self.tam = str(len(b.find("select", "pageSelect").find_all("option")))
            self.mpb['maximum'] = self.tam
            self.speed.set('Paginas: ' + self.tam)
            self.eta.set('Paginas Percorridas: %d' % 0)
            meio = str(int(self.tam) // 2)
            t1 = Thread(target=self.todosAnimes, args=[link])
            t2 = Thread(target=self.todosAnimes, args=[link + "?pagina=" + meio, False])
            t3 = Thread(target=self.todosAnimes, args=[link + "?pagina=" + str(int(meio) + 1)])
            t4 = Thread(target=self.todosAnimes, args=[link + "?pagina=" + self.tam, False])
            t1.start()
            t2.start()
            t3.start()
            t4.start()
            t1.join()
            t2.join()
            t3.join()
            t4.join()
            self.transformaJson()
            # self.pesquisaAnimes()
            self.telaP.voltar()
            self.master.destroy()
            messagebox.showinfo("Anime Downloader", "Atualização Finalizada!")
        else:
            self.master.destroy()
            messagebox.showinfo("Anime Downloader", "Lista já Atualizada!")

    @staticmethod
    def transformaJson():
        dic = dict({'nome': [], 'link': []})
        for l, j, k in os.walk("animes/"):
            lis = []
            for ll in k:
                s = re.compile('([0-9]+)').findall(ll)
                if os.path.isfile("animes/Pagina " + (s[0] if len(s) else '') + ".json"):
                    lis.append(int(s[0]))
            lis.sort()
            for li in lis:
                if os.path.isfile("animes/Pagina " + str(li) + ".json"):
                    arq = open("animes/Pagina " + str(li) + ".json", 'r')
                    js = json.load(arq)
                    dic['nome'] += js['nome']
                    dic['link'] += js['link']
                    arq.close()
                    os.remove("animes/Pagina " + str(li) + ".json")
        io = StringIO()
        json.dump(dic, io)
        jsonS = io.getvalue()
        arq = open("animes/Paginas.json", 'w')
        arq.write(jsonS)
        arq.close()

    def todosAnimes(self, link, direcao=True):
        def reqLink(u):
            try:
                resul = req.get(u)
            except (Exception, req.RequestException):
                resul = reqLink(u)
            return resul

        dic = dict({'nome': [], 'link': []})
        s = re.compile('([0-9]+)').findall(link)
        if not os.path.isfile("animes/Pagina " + (s[0] if len(s) else '1') + ".json"):
            r = reqLink(link)
            b = BeautifulSoup(r.content, 'html.parser')
            animes = b.find("div", "boxConteudo").find_all("div", "boxLista2")
            for j in animes:
                j = j.find("a", title=True)
                dic["nome"].append(j.img.get("title"))
                dic["link"].append(j.get("href"))
            io = StringIO()
            json.dump(dic, io)
            jsonS = io.getvalue()
            arq = 'animes/' + self.sanitizestring(
                b.find("select", "pageSelect").find("option", selected=True).text) + '.json'
            arq = open(arq, 'w')
            arq.write(jsonS)
            arq.close()
            if self.per < int(self.tam):
                self.per += 1
            self.mpb['value'] = self.per
            self.eta.set('Paginas Percorridas: %d' % self.per)
            if direcao:
                a = b.find("a", title="Próxima Pagina")
            else:
                a = b.find("a", title="Pagina Anterior")
            if a:
                self.todosAnimes(a.get("href"), direcao)

    @staticmethod
    def sanitizestring(palavra):
        # Unicode normalize transforma um caracter em seu equivalente em latin.
        nfkd = unicodedata.normalize('NFKD', palavra)
        palavrasemacento = u"".join([c for c in nfkd if not unicodedata.combining(c)])
        # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
        return re.sub('[^a-zA-Z0-9 \\\]', '', palavrasemacento)

    def pesquisaAnimes(self):
        def bP1(a):
            for q in range(len(a['nome'])):
                if not os.path.isfile("animes/" + str(q + 1) + " " + self.sanitizestring(a['nome'][q]) + ".json"):
                    # print(str(q + 1) + " " + a['nome'][q] + ".json")
                    thread = Thread(target=self.paginaAnime, args=[str(q + 1) + " " + a['nome'][q], a['link'][q]])
                    thread.start()
                    thread.join()

        def bP2(a):
            for i in range(len(a['nome']) - 1, 0, -1):
                if not os.path.isfile("animes/" + str(i + 1) + " " + self.sanitizestring(a['nome'][i]) + ".json"):
                    # print(str(i + 1) + " " + a['nome'][i] + ".json")
                    thread = Thread(target=self.paginaAnime, args=[str(i + 1) + " " + a['nome'][i], a['link'][i]])
                    thread.start()
                    thread.join()

        def bP3(a):
            for i in range(len(a['nome']) // 2 - 1, 0, -1):
                if not os.path.isfile("animes/" + str(i + 1) + " " + self.sanitizestring(a['nome'][i]) + ".json"):
                    # print(str(i + 1) + " " + a['nome'][i] + ".json")
                    thread = Thread(target=self.paginaAnime, args=[str(i + 1) + " " + a['nome'][i], a['link'][i]])
                    thread.start()
                    thread.join()

        def bP4(a):
            for i in range(len(a['nome']) // 2, len(a['nome'])):
                if not os.path.isfile("animes/" + str(i + 1) + " " + self.sanitizestring(a['nome'][i]) + ".json"):
                    # print(str(i + 1) + " " + a['nome'][i] + ".json")
                    thread = Thread(target=self.paginaAnime, args=[str(i + 1) + " " + a['nome'][i], a['link'][i]])
                    thread.start()
                    thread.join()

        abc = open("animes/Paginas.json")
        ani = json.load(abc)
        abc.close()
        self.tam = len(ani['nome'])
        self.per = 0
        self.mpb['maximum'] = self.tam
        self.speed.set('Animes: ' + str(self.tam))
        self.eta.set('Animes Percorridas: %d' % 0)
        t1 = Thread(target=bP1, args=[ani])
        t2 = Thread(target=bP2, args=[ani])
        t3 = Thread(target=bP3, args=[ani])
        t4 = Thread(target=bP4, args=[ani])
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t1.join()
        t2.join()
        t3.join()
        t4.join()

    def paginaAnime(self, nome, link):
        def reqLink(u):
            try:
                resul = req.get(u)
            except (Exception, req.RequestException):
                resul = reqLink(u)
            return resul

        try:
            dic = dict({'ep': [], 'link': []})
            if os.path.isfile("animes/" + self.sanitizestring(nome) + ".json"):
                arq = open("animes/" + self.sanitizestring(nome) + ".json", 'r')
                dic = json.load(arq)
                arq.close()
            r = reqLink(link)
            b = BeautifulSoup(r.content, 'html.parser')
            self.name.set(nome)
            tam = len(b.find_all("option"))
            self.tam = len(b.find_all("option")) - 1 if tam > 0 else 1
            self.mpb['maximum'] = self.tam
            eps = b.find("div", itemprop="episode")
            if eps:
                num = eps.find_all("span", itemprop='episodeNumber')
                eps = eps.find_all("h3", itemprop="name")
                for ii in range(len(eps)):
                    name = (num[ii].text + ' - ' + eps[ii].a.text)
                    if not (name in dic['ep']):
                        dic['ep'].append(name)
                        dic['link'].append(eps[ii].a.get("href"))
                        # dic['download'].append("")
                    # else:
                    #     # print((num[ii].text + ' - ' + eps[ii].a.text))
                    #     dic['ep'].append(num[ii].text + ' - ' + eps[ii].a.text)
                    #     dic['link'].append(eps[ii].a.get("href"))
                    #     dic['download'].append("")
            else:
                ova = b.find("div", "js_dropDownView")
                if ova:
                    boxOv = ova.find_all("div", "epsBox")
                    if boxOv:
                        for ii in boxOv:
                            ov = ii.find("h3")
                            num = re.compile('([0-9]+)').findall(str(ov.a.get("title")))[0]
                            dic['ep'].append(num + ' - ' + ov.text)
                            dic['link'].append(ov.a.get('href'))
                            # dic['download'].append("")
                    fil = ova.find_all("div", "epsBoxFilme")
                    if fil:
                        for o in fil:
                            num = re.compile('([0-9]+)').findall(str(o.find("h3").text))[0]
                            dic['ep'].append(num + ' - ' + o.find("h4").text)
                            dic['link'].append(o.find("a").get("href"))
                            # dic['download'].append("")
            io = StringIO()
            json.dump(dic, io)
            jsonS = io.getvalue()
            arq = "animes/" + self.sanitizestring(nome) + ".json"
            # print(arq)
            arq = open(arq, 'w')
            arq.write(jsonS)
            arq.close()
            a = b.find("a", title="Próxima Pagina")
            self.per += 1
            self.eta.set('Paginas Percorridas: %d' % self.per)
            self.mpb['value'] = self.per
            if a:
                self.paginaAnime(nome, a.get("href"))
            else:
                self.master.destroy()
                self.telaP.mostraAni()
        except (Exception, AttributeError) as exception:
            print(link, exception)
            # Exception.__traceback__
            self.paginaAnime(nome, link)


class Tela:
    def __init__(self):
        self.tk = Tk()
        self.tk.geometry("600x400")
        self.tk.resizable(False, False)
        if not os.path.isdir("animes"):
            os.mkdir("animes")
        if os.path.isfile("animes/Paginas.json"):
            self.ani = json.load(open("animes/Paginas.json"))
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
        self.btProc = None
        self.etProc = None
        self.isVoltar = False
        self.dir = os.getcwd()
        self.busca = StringVar()
        self.inicia()
        self.tk.title("Anime Downloader")
        self.selecionado = -1
        # self.icon = self.dir + '\\' + 'down.ico'
        # self.tk.iconbitmap(self.icon)
        self.tk.mainloop()

    def inicia(self):
        self.fra1 = Frame(self.tk, bd=1)
        self.fra2 = Frame(self.tk, bd=1)
        self.scrollbar = ttk.Scrollbar(self.tk, orient=VERTICAL)
        self.mylist = Listbox(self.tk, yscrollcommand=self.scrollbar.set)
        for i in range(len(self.ani['nome'])):
            self.mylist.insert(END, self.ani['nome'][i])
        self.scrollbar.config(command=self.mylist.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        # Buscar
        Label(self.fra1, text='Anime:').pack(side=LEFT)
        self.etProc = Entry(self.fra1, textvariable=self.busca, width=79)
        self.etProc.pack(side=LEFT)
        self.btProc = Button(self.fra1, text='Procurar', command=self.procura)
        self.btProc.pack(side=LEFT)
        self.fra1.pack(fill=X)
        # Lista
        self.mylist.pack(fill=BOTH, expand=True)
        # Botoes
        self.bt1 = Button(self.fra2, text="Pegar valor", command=self.li)
        self.bt2 = Button(self.fra2, text="Voltar", command=self.voltar)
        self.bt3 = Button(self.fra2, text="Baixar", command=self.baixar)
        self.bt4 = Button(self.fra2, text="Atualizar Base", command=self.buscaP)
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
            nome = str(ind + 1) + " " + Anime.sanitizestring(self.ani['nome'][ind])
            newWindow = Toplevel(self.tk)
            Thread(target=Anime, args=[newWindow, self, 'Procurando...', nome, url]).start()

    def mostraAni(self):
        self.ani = json.load(open("animes/" + str(self.selecionado + 1) + " "
                                  + Anime.sanitizestring(
            self.ani['nome'][self.selecionado]) + ".json"))
        self.atualiza("ep")
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
        self.ani = json.load(open("animes/Paginas.json"))
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
            nome = self.ani['ep'][self.mylist.curselection()[0]]
            conjunto = {'ep': nome, 'link': url}
            newWindow = Toplevel(self.tk)
            Thread(target=DownloadWindow, args=[newWindow, None, conjunto]).start()

    def buscaP(self):
        newWindow = Toplevel(self.tk)
        Thread(target=Anime, args=[newWindow, self, 'Atualizando...']).start()


class DownloadWindow:
    def __init__(self, tk, icon, conj):
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
        Thread(target=self.downloadVideo, args=[conj['link'], True, conj['ep']]).start()

    def testaCallback(self, current, total, width):
        self.mpb['maximum'] = total
        self.mpb['value'] = current
        self.speed.set('Tamanho: %.2f Mbps' % ((total / 1024) / 1024))
        self.eta.set('Baixado: %.2lf Mbps' % ((current / 1024) / 1024))

    def downloadVideo(self, link, retorno=False, nome=""):
        def reqLink(u):
            try:
                resul = req.get(u)
            except (Exception, req.RequestException):
                resul = reqLink(u)
            return resul

        def pegaLink(href, header):
            s = req.get(href, allow_redirects=False, headers=header)
            return s.headers['location']

        try:
            r = reqLink(link)
            b = BeautifulSoup(r.content, 'html.parser')
            bb = b.find("source")
            nome = nome + ".mp4"
            self.name.set(nome)
            headers = {
                'Referer': link
            }
            if bb:
                r = req.get(bb.get("src"), allow_redirects=False, headers=headers)
                if retorno:
                    wget.download(r.headers['location'], nome, bar=self.testaCallback)
                else:
                    return r.headers['location']
            else:
                bb = b.find('a', title="Baixar Video")
                if bb:
                    r = reqLink(bb.get("href"))
                    b = BeautifulSoup(r.content, 'html.parser')
                    bb = b.find("a", "bt-download")
                    if bb:
                        head = pegaLink(bb.get("href"), headers)
                        if retorno:
                            wget.download(head, nome, bar=self.testaCallback)
                        else:
                            return head
            self.master.destroy()
            messagebox.showinfo("Anime Downloader", "Download Concluido!")
        except (Exception, AttributeError) as exp:
            print(link, exp)


if __name__ == "__main__":
    Tela()
