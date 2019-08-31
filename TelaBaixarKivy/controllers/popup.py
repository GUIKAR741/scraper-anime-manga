"""Controller dos Popups."""
from io import StringIO
from json import dump, loads
from operator import itemgetter
from os import path, mkdir, remove
from queue import Queue
from re import compile, sub
from threading import Thread, current_thread
from unicodedata import combining, normalize

from bs4 import BeautifulSoup as bs
from ffmpy import FFmpeg
from kivy.app import App
from kivy.metrics import dp
from kivy.properties import Property  # pylint: disable=no-name-in-module
from kivy.properties import StringProperty  # pylint: disable=no-name-in-module
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from PIL.Image import open as open_image
from requests import RequestException, get, post
from wget import download


class PopupDownload(Popup):
    """Componente Popup."""

    textoBotao = StringProperty('Fechar')

    titulo = StringProperty('Iniciando...')
    texto = StringProperty('Procurando Titulo')
    funcao = Property(lambda x: x.dismiss())

    def __init__(self, *args, **kwargs):
        """."""
        super().__init__(*args, **kwargs)
        self.pathDown = App.get_running_app().pathDown

    def _sanitizestring(self, palavra):
        """."""
        # Unicode normalize transforma um caracter em seu equivalente em latin.
        nfkd = normalize('NFKD', palavra)
        palavrasemacento = u"".join([c for c in nfkd if not combining(c)])
        # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
        return sub('[^a-zA-Z0-9 ]', '', palavrasemacento)

    def baixar(self, tipo, link):
        """."""
        if tipo == 'episodio':
            self.thr = Thread(target=self._download_video, args=[link])
        elif tipo == 'capitulo':
            self.thr = Thread(target=self._download_capitulo, args=[link])
        elif tipo == 'video':
            self.thr = Thread(target=self._download_video_youtube, args=[link])
        self.thr.parar = False
        self.thr.start()

    def _baixar_callback(self, current, total, width):
        """."""
        t = current_thread()
        if t.parar:
            exit(0)
        self.ids.barra.value = (current/total) * 100
        self.ids.tamanho.text = ('%.2f' % ((total / 1024) / 1024))
        self.ids.baixado.text = ('%.2lf' % ((current / 1024) / 1024))

    def _baixar_video_callback(self, total, recvd, ratio, rate, eta):
        """."""
        t = current_thread()
        if t.parar:
            exit(0)
        self.ids.barra.value = (recvd/total) * 100
        self.ids.tamanho.text = ('%.2f' % ((total / 1024) / 1024))
        self.ids.baixado.text = ('%.2lf' % ((recvd / 1024) / 1024))
        self.lvel1.text = ('%.2f' % (rate/1024))
        self.ltemp1.text = str(int(eta))

    def cancelar(self):
        """."""
        self.thr.parar = True
        self.dismiss()

    def _req_link(self, u):
        """."""
        try:
            resul = get(u)
        except (Exception, RequestException):
            resul = self._req_link(u)
        return resul

    def _pega_link(self, href, header):
        """."""
        s = get(href, allow_redirects=False, headers=header)
        return s.headers['location']

    def _download_video(self, link):
        """."""
        try:
            link = link if ('http' or 'https') in link else "https:"+link
            r = self._req_link(link)
            b = bs(r.content, 'html.parser')
            nome = b.find("h1", itemprop='name').text.split()[-1]+'-'
            nome += b.find("h2", itemprop='alternativeHeadline').text
            bb = b.find("source")
            nome = nome + ".mp4"
            self.texto = nome
            headers = {
                'Referer': link
            }
            if bb:
                ll = bb.get("src") if ('http' or 'https') in bb.get(
                    'src') else "https:"+bb.get('src')
                r = get(ll, allow_redirects=False, headers=headers)
                self.titulo = "Baixando..."
                download(r.headers['location'],
                         self.pathDown + "/" + nome,
                         bar=self._baixar_callback)
            else:
                bb = b.find('a', title="Baixar Video")
                if bb:
                    r = self._req_link(bb.get("href") if ('http' or 'https') in bb.get(
                        'href') else "https:"+bb.get('href'))
                    b = bs(r.content, 'html.parser')
                    bb = b.find("a", "bt-download")
                    if bb:
                        head = \
                            self._pega_link(
                                bb.get("href") if
                                ('http' or 'https') in bb.get('href') else
                                "https:" + bb.get('href'), headers)
                        self.titulo = "Baixando..."
                        download(head,
                                 self.pathDown + "/" + nome,
                                 bar=self._baixar_callback)
            self.titulo = "Download Concluido!"
            btn = Button()
            btn.size_hint_y = None
            btn.height = dp(50)
            btn.text = self.textoBotao
            btn.on_press = lambda: self.funcao(self)
            self.ids.box.remove_widget(self.ids.cancelar)
            self.ids.box.add_widget(btn)
        except (Exception, AttributeError) as exp:
            print(link, exp)

    def _download_video_youtube(self, video):
        """."""
        boxVel = BoxLayout()
        lvel = Label()
        lvel.text = 'Velocidade: '
        self.lvel1 = Label()
        self.lvel1.text = '0'
        lvel2 = Label()
        lvel2.text = 'Mbps'
        boxVel.add_widget(lvel)
        boxVel.add_widget(self.lvel1)
        boxVel.add_widget(lvel2)
        self.ids.down.add_widget(boxVel)
        boxTemp = BoxLayout()
        ltemp = Label()
        ltemp.text = 'Tempo Restante: '
        self.ltemp1 = Label()
        self.ltemp1.text = '0'
        ltemp2 = Label()
        ltemp2.text = 'Segundos'
        boxTemp.add_widget(ltemp)
        boxTemp.add_widget(self.ltemp1)
        boxTemp.add_widget(ltemp2)
        self.ids.down.add_widget(boxTemp)

        vInfo = video[0]
        vDown = video[1]
        arquivo = self.pathDown + "/" +\
            self._sanitizestring(vInfo.title) + "." +\
            vDown.extension
        self.titulo = "Baixando..."
        self.texto = vInfo.title[:50]
        if video[2].active:
            vDown.download(filepath=arquivo, quiet=True,
                           callback=self._baixar_video_callback)
            if vDown.mediatype == 'audio':
                self.ids.box.remove_widget(self.ids.cancelar)
                self.titulo = "Convertendo..."
                FFmpeg(global_options=['-v quiet'], inputs={arquivo: None},
                       outputs={self.pathDown + "/" +
                                self._sanitizestring(vInfo.title) +
                                '.mp3': None}).run()
                remove(arquivo)
        else:
            vDown = vInfo.getbestaudio()
            arquivo = self.pathDown + "/" + \
                self._sanitizestring(vInfo.title) + "."+vDown.extension
            vDown.download(filepath=arquivo, quiet=True,
                           callback=self._baixar_video_callback)
            self.ids.box.remove_widget(self.ids.cancelar)
            self.titulo = "Convertendo..."
            FFmpeg(global_options=['-v quiet'], inputs={arquivo: None},
                   outputs={self.pathDown + "/" +
                            self._sanitizestring(vInfo.title) +
                            '.mp3': None}).run()
            remove(arquivo)
        self.titulo = "Download Concluido!"
        btn = Button()
        btn.size_hint_y = None
        btn.height = dp(50)
        btn.text = self.textoBotao
        btn.on_press = lambda: self.funcao(self)
        self.ids.box.add_widget(btn)

    def _download_capitulo(self, url):
        """."""
        self.ids.box.remove_widget(self.ids.cancelar)
        self.ids.tamanho.text = ''
        self.ids.textoTamanho.text = ''
        self.ids.mb.text = ''
        self.ids.mbps.text = 'Paginas'
        caminho = self.pathDown
        urls = url.split('/')
        st = self._sanitizestring(str(urls[urls.__len__() - 2]))
        pasta = caminho + '/' + st + "_" + urls[urls.__len__() - 1]
        bb = bs(self._req_link(url).content, 'html.parser')
        self.criapasta(pasta)
        i = 1
        self.texto = st + "_" + urls[urls.__len__() - 1]
        imagens = bb.find_all('img', pag=True)
        for node in imagens:
            if str(node.get("src")).find("leitor") == -1:
                imagens.remove(node)
        self.titulo = "Baixando..."
        self.ids.baixado.text = "00/" + str(len(imagens))
        self.i = 1
        self.total = str(len(imagens))
        self.q = Queue()
        [
            self.q.put([
                pasta,
                '0'+str(i+1) if len(str(i+1)) < 2 else i+1,
                str(imagens[i].get('src')
                    if "http:" in imagens[i].get("src") or
                    "https:" in imagens[i].get("src")
                    else 'http:' + imagens[i].get("src")).split("."),
                imagens[i].get('src')
                if "http:" in imagens[i].get("src") or
                "https:" in imagens[i].get("src")
                else 'http:' + imagens[i].get("src")
            ]) for i in range(len(imagens))
        ]

        p = [Thread(target=self.baixarimg) for i in range(5)]
        [i.start() for i in p]
        [i.join() for i in p]
        # p = p.map_async(lambda x: self.baixarimg(*x), [
        #     [
        #         pasta,
        #         '0'+str(i+1) if len(str(i+1)) < 2 else i+1,
        #         str(imagens[i].get('src')
        #             if "http:" in imagens[i].get("src") or
        #             "https:" in imagens[i].get("src")
        #             else 'http:' + imagens[i].get("src")).split("."),
        #         imagens[i].get('src')
        #         if "http:" in imagens[i].get("src") or
        #         "https:" in imagens[i].get("src")
        #         else 'http:' + imagens[i].get("src")
        #     ] for i in range(len(imagens))
        # ])
        # p.wait()
        self.titulo = "Download Concluido!"
        btn = Button()
        btn.size_hint_y = None
        btn.height = dp(50)
        btn.text = self.textoBotao
        btn.on_press = lambda: self.funcao(self)
        self.ids.box.add_widget(btn)

    def criapasta(self, pasta):
        """."""
        if not path.isdir(pasta):
            mkdir(pasta)

    def baixarimg(self):
        """."""
        while not self.q.empty():
            pasta, i, n, url_img = self.q.get()
            rr = self._req_link(str(url_img))
            with open(pasta + "/" + str(i) + "." + n[n.__len__() - 1], 'wb') as code:
                code.write(rr.content)
            open_image(pasta + "/" + str(i) + "." + n[n.__len__() - 1]).save(
                pasta + "/" + str(i) + "." + n[n.__len__() - 1])
            self.ids.baixado.text = str('0'+str(self.i) if
                                        len(str(self.i)) < 2 else
                                        self.i) + \
                "/" + self.total
            self.ids.barra.value = self.i/int(self.total) * 100
            self.i += 1


class PopupProcura(Popup):
    """Componente Popup."""

    textoBotao = StringProperty('Fechar')

    titulo = StringProperty('Procurando...')
    texto = StringProperty('Procurando Titulo')
    funcao = Property(lambda x: x.dismiss())

    def __init__(self, *args, **kwargs):
        """."""
        super().__init__(*args, **kwargs)
        self.path = App.get_running_app().user_data_dir+'/'
        self.base = "https://www.superanimes.site/"

    def _req_link(self, u, dados={}):
        try:
            resul = get(u, data=dados)
        except (Exception, RequestException):
            resul = self._req_link(u, dados)
        return resul

    def _req_link_post(self, u, info):
        try:
            resul = post(u, data=info)
        except (Exception, RequestException):
            resul = self._req_link_post(u, info)
        return resul

    def _sanitizestring(self, palavra):
        """."""
        # Unicode normalize transforma um caracter em seu equivalente em latin.
        nfkd = normalize('NFKD', palavra)
        palavrasemacento = u"".join([c for c in nfkd if not combining(c)])
        # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
        return sub('[^a-zA-Z0-9 ]', '', palavrasemacento)

    def procura(self, tipo, nome, link, rv):
        """."""
        if tipo == 'anime':
            Thread(target=self._pagina_anime, args=[nome, link, rv]).start()
        else:
            Thread(target=self._pagina_manga, args=[nome, link, rv]).start()

    def atualizar(self, tipo, func):
        """."""
        self.titulo = 'Atualizando...'
        self.texto = ''
        if tipo == 'animes':
            Thread(target=self._atualizar_pagina_animes, args=[func]).start()
        else:
            Thread(target=self._atualizar_pagina_mangas, args=[func]).start()

    def _atualizar_pagina_animes(self, func):
        """."""
        link = f"{self.base}inc/paginator.inc.php"
        total = 99
        atual = 1
        ani = {'nome': [], 'link': []}
        lista_animes = []
        self.tam = str(total)
        while atual <= total:
            data = {'type_url': "lista",
                    'page': atual,
                    'limit': 1000,
                    'total_page': total,
                    'type': 'lista',
                    'filters': '{"filter_data":"filter_letter=0&filter_type_content=100'
                               '&filter_genre_model=0&filter_order=0&filter_rank=0'
                               '&filter_status=0&filter_idade=&filter_dub=0'
                               '&filter_size_start=0&filter_size_final=0&filter_date=0'
                               '&filter_viewed=0",'
                               '"filter_genre_add":[],"filter_genre_del":[]}'}
            e = self._req_link_post(link, data)
            body = loads(e.content)
            total = body['total_page']
            self.tam = str(total)
            self.ids.paginas.text = (self.tam)
            self.ids.procuradas.text = ('%d' % atual)
            self.ids.barra.value = atual/total * 100
            atual += 1
            for I in range(len(body['body'])):
                novo_ani = dict(ani)
                b = bs(body['body'][I], 'html.parser')
                a = b.find('h1', 'grid_title').find('a')
                novo_ani['nome'] = a.text
                novo_ani['link'] = (a.get('href') if ('http' or 'https') in a.get('href') else
                                    "https:" + a.get('href'))
                lista_animes.append(novo_ani)
        for I in sorted(lista_animes, key=itemgetter('nome')):
            ani['nome'].append(I['nome'])
            ani['link'].append(I['link'])
        io = StringIO()
        dump(ani, io)
        json_s = io.getvalue()
        arq = open(self.path+"PaginasAnimes.json", 'w')
        arq.write(json_s)
        arq.close()
        self.dismiss()
        func()

    def _atualizar_pagina_mangas(self, func):
        """Refatorar essa Merda."""
        r = self._req_link("https://unionmangas.top/lista-mangas")
        b = bs(r.text, 'html.parser')
        paginacao = b.find("ul", "pagination").find_all('span', "sr-only")
        link = "https://unionmangas.top/lista-mangas/a-z/%s/*"
        self.tam = 0
        self.per = 1
        for i in paginacao:
            if i.text == 'End':
                self.tam = int(compile(
                    '([0-9]+)').findall(i.parent.get("href"))[0])
        self.ids.paginas.text = str(self.tam)
        self.q = Queue()
        [self.q.put(link % i) for i in range(1, self.tam+1)]
        self.resQ = []
        p = [Thread(target=self._busca_pag, args=[self.q]) for i in range(5)]
        [i.start() for i in p]
        [i.join() for i in p]
        self._junta([i[1] for i in sorted(self.resQ, key=lambda x: x[0])])
        self.dismiss()
        func()

    def _junta(self, paginas):
        """."""
        dic = dict({'nome': [], 'link': []})
        for i in paginas:
            js = i
            dic['nome'] += js['nome']
            dic['link'] += js['link']
        io = StringIO()
        dump(dic, io)
        json_s = io.getvalue()
        arq = open(self.path + "PaginasMangas.json", 'w')
        arq.write(json_s)
        arq.close()

    def _busca_pag(self, fila, direcao=True, maximo=0):
        """."""
        while not fila.empty():
            link = fila.get()
            info = {'nome': [], 'link': []}
            r = self._req_link(link)
            b = bs(r.text, 'html.parser')
            mangas = b.find_all('div', 'bloco-manga')
            for i in mangas:
                lin = i.find_all('a')[-1]
                info['nome'].append(self._sanitizestring(
                    lin.get("href").split('/')[-1].replace('-', ' ').title()))
                info['link'].append(lin.get("href"))
            self.ids.barra.value = self.per/self.tam * 100
            self.ids.procuradas.text = ('%d' % self.per)
            self.per += 1
            self.resQ.append((int(compile('([0-9]+)').findall(link)[0]), info))

    def _pagina_anime(self, nome, link, rv):
        """."""
        try:
            dic = dict({'ep': [], 'link': []})
            link = link if ('http' or 'https') in link else "https:"+link
            r = self._req_link(link)
            b = bs(r.content, 'html.parser')
            id_cat = b.find(
                'div', attrs={"data-id-cat": True}).get("data-id-cat")
            self.texto = nome
            atual = 1
            self.tam = 20
            link = f"{self.base}inc/paginatorVideo.inc.php"
            while atual <= self.tam:
                data = {'id_cat': int(id_cat),
                        'page': int(atual),
                        'limit': 100,
                        'total_page': int(self.tam),
                        'order_video': 'asc'}
                e = self._req_link_post(link, data)
                body = loads(e.content)
                self.tam = body['total_page']
                self.ids.paginas.text = str(self.tam)
                self.ids.procuradas.text = ('%d' % atual)
                self.ids.barra.value = atual/self.tam * 100
                atual += 1
                if self.tam > 0:
                    for II in range(len(body['body'])):
                        bb = bs(body['body'][II], 'html.parser')
                        a = bb.find('div', 'epsBoxSobre').find('a')
                        dic['ep'].append(a.text)
                        dic['link'].append(
                            a.get('href') if ('http' or 'https') in a.get('href') else
                            "https:" + a.get('href')
                        )
            box = b.find_all("div", 'boxBarraInfo js_dropDownBtn active')
            if box:
                for K in box:
                    par = K.parent
                    ova = par.find_all('div', 'epsBox')
                    if ova:
                        for kk in ova:
                            dic['ep'].append("OVA: "+kk.find("h3").a.text)
                            dic['link'].append(kk.find("h3").a.get("href") if ('http' or 'https') in
                                               kk.find("h3").a.get("href") else "https:" +
                                               kk.find("h3").a.get("href"))
                    fil = par.find_all('div', 'epsBoxFilme')
                    if fil:
                        for L in fil:
                            dic['ep'].append("FILME: "+L.find("h4").text)
                            dic['link'].append(L.find("a").get("href") if ('http' or 'https') in
                                               L.find("a").get("href")
                                               else "https:" + L.find("a").get("href"))
            self.dismiss()
            rv.data = [{'titulo': dic['ep'][i],
                        'link': dic['link'][i],
                        'tituloBotao': 'Baixar',
                        'tipo': 'episodio'}
                       for i in range(len(dic['ep']))]
        except (Exception, AttributeError) as exception:
            print(link, exception)

    def _pagina_manga(self, nome, link, rv):
        """."""
        info = {'titulo': [], 'link': []}
        r = self._req_link(link)
        b = bs(r.text, 'html.parser')
        cap = b.find_all('div', 'row lancamento-linha')
        for i in cap:
            info['titulo'].append(i.a.text)
            info['link'].append(i.a.get("href"))
        self.dismiss()
        rv.data = [{'titulo': info['titulo'][i],
                    'link': info['link'][i],
                    'tituloBotao': 'Baixar',
                    'tipo': 'capitulo'}
                   for i in range(len(info['titulo']))]


class PopupFile(Popup):
    """Componente Popup."""

    textoBotao = StringProperty('Fechar')
    textoBotaoSel = StringProperty('Selecionar')

    titulo = StringProperty('Procurar:')
    funcao = Property(lambda x: x.dismiss())

    path = StringProperty('')

    def __init__(self, *args, **kwargs):
        """."""
        super().__init__(*args, **kwargs)
        self.path = App.get_running_app().pathDown

    def _att_down(self, func):
        self.func = func

    def selecionar(self):
        """."""
        App.get_running_app().pathDown = self.ids.fc.path
        self.func(self.ids.fc.path)
        self.dismiss()
