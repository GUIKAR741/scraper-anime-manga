import unicodedata
from io import StringIO
import json
import os
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import wget
from bs4 import BeautifulSoup
import requests as req
from threading import Thread
from operator import itemgetter


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
        def reqLink(u, dados):
            try:
                resul = req.post(u, data=dados)
            except (Exception, req.RequestException):
                resul = reqLink(u, dados)
            return resul

        if not os.path.isfile("animes/Paginas.json") or buscar:
            link = "http://www.superanimes.site/inc/paginator.inc.php"
            total = 99
            atual = 1
            ani = {'nome': [], 'link': []}
            listaAnimes = []
            self.tam = str(total)
            self.mpb['maximum'] = self.tam
            self.speed.set('Paginas: ' + self.tam)
            self.eta.set('Paginas Percorridas: %d' % 0)
            while atual <= total:
                data = {'type_url': "lista",
                        'page': atual,
                        'limit': 100,
                        'total_page': total,
                        'type': 'lista',
                        'filters': '{"filter_data":"filter_letter=0&filter_type_content=100&filter_genre_model=0'
                                   '&filter_order=0&filter_rank=0&filter_status=0&filter_idade=&filter_dub=0'
                                   '&filter_size_start=0&filter_size_final=0&filter_date=0&filter_viewed=0",'
                                   '"filter_genre_add":[],"filter_genre_del":[]}'}
                e = reqLink(link, data)
                body = json.loads(e.content)
                total = body['total_page']
                self.tam = str(total)
                self.mpb['maximum'] = self.tam
                self.speed.set('Paginas: ' + self.tam)
                self.eta.set('Paginas Percorridas: %d' % atual)
                self.mpb['value'] = atual
                atual += 1
                for I in range(len(body['body'])):
                    novoAni = dict(ani)
                    b = BeautifulSoup(body['body'][I], 'html.parser')
                    a = b.find('h1', 'grid_title').find('a')
                    novoAni['nome'] = a.text
                    novoAni['link'] = a.get('href') if ('http' or 'https') in a.get('href') else "https:" + a.get(
                        'href')
                    listaAnimes.append(novoAni)
            for I in sorted(listaAnimes, key=itemgetter('nome')):
                ani['nome'].append(I['nome'])
                ani['link'].append(I['link'])
            io = StringIO()
            json.dump(ani, io)
            jsonS = io.getvalue()
            arq = open("animes/Paginas.json", 'w')
            arq.write(jsonS)
            arq.close()
            self.telaP.voltar()
            self.master.destroy()
            messagebox.showinfo("Anime Downloader", "Atualização Finalizada!")
        else:
            self.master.destroy()
            messagebox.showinfo("Anime Downloader", "Lista já Atualizada!")

    """@staticmethod
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
        link=link if ('http' or 'https') in link else "https:"+link
        s = re.compile('([0-9]+)').findall(link)
        if not os.path.isfile("animes/Pagina " + (s[0] if len(s) else '1') + ".json"):
            r = reqLink(link)
            b = BeautifulSoup(r.content, 'html.parser')
            print(b)
            exit(0)
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
        t4.join()"""

    @staticmethod
    def sanitizestring(palavra):
        # Unicode normalize transforma um caracter em seu equivalente em latin.
        nfkd = unicodedata.normalize('NFKD', palavra)
        palavrasemacento = u"".join([c for c in nfkd if not unicodedata.combining(c)])
        # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
        return re.sub('[^a-zA-Z0-9 \\\]', '', palavrasemacento)

    def paginaAnime(self, nome, link):
        def reqLink(u):
            try:
                resul = req.get(u)
            except (Exception, req.RequestException):
                resul = reqLink(u)
            return resul

        def reqLinkPost(u, info):
            try:
                resul = req.post(u, data=info)
            except (Exception, req.RequestException):
                resul = reqLinkPost(u, info)
            return resul

        # try:
        dic = dict({'ep': [], 'link': []})
        link= link if ('http' or 'https') in link else "https:"+link
        r = reqLink(link)
        b = BeautifulSoup(r.content, 'html.parser')
        id_cat = b.find('div', attrs={"data-id-cat": True}).get("data-id-cat")
        self.name.set(nome)
        atual = 1
        self.tam = 99
        self.speed.set('Paginas: ' + str(self.tam))
        self.mpb['maximum'] = self.tam
        link = "https://www.superanimes.site/inc/paginatorVideo.inc.php"
        while atual <= self.tam:
            data = {'id_cat': id_cat,
                    'page': atual,
                    'limit': 100,
                    'total_page': self.tam,
                    'order_video': 'asc'}
            e = reqLinkPost(link, data)
            body = json.loads(e.content)
            self.tam = body['total_page']
            self.mpb['maximum'] = self.tam
            self.speed.set('Paginas: ' + str(self.tam))
            self.eta.set('Paginas Percorridas: %d' % atual)
            self.mpb['value'] = atual
            atual += 1
            if self.tam>0:
                for II in range(len(body['body'])):
                    bb = BeautifulSoup(body['body'][II], 'html.parser')
                    a = bb.find('div', 'epsBoxSobre').find('a')
                    dic['ep'].append(a.text)
                    dic['link'].append(
                        a.get('href') if ('http' or 'https') in a.get('href') else "https:" + a.get('href'))
        box=b.find_all("div", 'boxBarraInfo js_dropDownBtn active')
        if box:
            for K in box:
                par=K.parent
                ova=par.find_all('div', 'epsBox')
                if ova:
                    for K in ova:
                        dic['ep'].append("OVA: "+K.find("h3").a.text)
                        dic['link'].append(K.find("h3").a.get("href") if ('http' or 'https') in
                                           K.find("h3").a.get("href") else "https:" + K.find("h3").a.get("href"))
                fil=par.find_all('div', 'epsBoxFilme')
                if fil:
                    for L in fil:
                        dic['ep'].append("FILME: "+L.find("h4").text)
                        dic['link'].append(L.find("a").get("href") if ('http' or 'https') in L.find("a").get("href")
                                           else "https:" + L.find("a").get("href"))
        io = StringIO()
        json.dump(dic, io)
        jsonS = io.getvalue()
        arq = "animes/" + self.sanitizestring(nome) + ".json"
        arq = open(arq, 'w')
        arq.write(jsonS)
        arq.close()
        self.master.destroy()
        self.telaP.mostraAni()
        # except (Exception, AttributeError) as exception:
        #     print(link, exception)


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
        for III in range(len(self.ani['nome'])):
            self.mylist.insert(END, self.ani['nome'][III])
        self.scrollbar.config(command=self.mylist.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        # Buscar
        Label(self.fra1, text='Anime:').pack(side=LEFT)
        self.etProc = Entry(self.fra1, textvariable=self.busca, width=65)
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
            for IV in range(len(self.ani['nome'])):
                if buscar == self.ani['nome'][IV].lower():
                    ind = IV
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
            for V in range(len(self.ani['nome'])):
                if buscar in self.ani['nome'][V].lower():
                    ind.append(V)
            if ind is not []:
                for V in range(self.mylist.size()):
                    self.mylist.delete(0)
                for V in ind:
                    self.mylist.insert(END, self.ani['nome'][V])
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
        for VI in range(self.mylist.size()):
            self.mylist.delete(0)
        for VI in range(len(self.ani[campo])):
            self.mylist.insert(END, self.ani[campo][VI])

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
        Thread(target=self.downloadVideo, args=[conj['link'], True]).start()

    def testaCallback(self, current, total, width):
        width+1
        self.mpb['maximum'] = total
        self.mpb['value'] = current
        self.speed.set('Tamanho: %.2f Mbps' % ((total / 1024) / 1024))
        self.eta.set('Baixado: %.2lf Mbps' % ((current / 1024) / 1024))

    def downloadVideo(self, link, retorno=False):
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
            link=link if ('http' or 'https') in link else "https:"+link
            r = reqLink(link)
            b = BeautifulSoup(r.content, 'html.parser')
            nome=b.find("h1", itemprop='name').text.split()[-1]+'-'
            nome+=b.find("h2", itemprop='alternativeHeadline').text
            bb = b.find("source")
            nome = nome + ".mp4"
            self.name.set(nome)
            headers = {
                'Referer': link
            }
            if bb:
                ll = bb.get("src") if ('http' or 'https') in bb.get('src') else "https:"+bb.get('src')
                r = req.get(ll, allow_redirects=False, headers=headers)
                if retorno:
                    # print(r.headers['location'])
                    # print(nome)
                    wget.download(r.headers['location'], nome, bar=self.testaCallback)
                    """
                    rr=req.get(r.headers['location'], stream=True)
                    with open(nome, 'wb') as f:
                        aaa=rr.iter_content(chunk_size=1024*1024)
                        print(len(aaa))
                        c=0
                        for i in aaa:
                            if i:
                                print(c, "baixando")
                                f.write(i)
                                c+=1
                    """
                else:
                    return r.headers['location']
            else:
                bb = b.find('a', title="Baixar Video")
                if bb:
                    r = reqLink(bb.get("href") if ('http' or 'https') in bb.get('href') else "https:"+bb.get('href'))
                    b = BeautifulSoup(r.content, 'html.parser')
                    bb = b.find("a", "bt-download")
                    if bb:
                        head = pegaLink(bb.get("href") if ('http' or 'https') in bb.get('href') else
                                        "https:"+bb.get('href'), headers)
                        if retorno:
                            wget.download(head, nome, bar=self.testaCallback)
                        else:
                            return head
            self.master.destroy()
            messagebox.showinfo("Anime Downloader", "Download Concluido!")
        except (Exception, AttributeError) as exp:
            print(link, exp)


if __name__ == "__main__":
    for i in os.listdir('./'):
        if ".tmp" in i:
            os.remove(i)

    Tela()
