"""Controller dos Popups."""
from io import StringIO
from json import dump, loads
from operator import itemgetter
from re import sub
from threading import Thread, current_thread
from unicodedata import combining, normalize

from bs4 import BeautifulSoup as bs
from kivy.metrics import dp
from kivy.properties import Property  # pylint: disable=no-name-in-module
from kivy.properties import StringProperty  # pylint: disable=no-name-in-module
from kivy.uix.button import Button
from kivy.uix.popup import Popup
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

    def baixar(self, link):
        """."""
        self.thr = Thread(target=self._download_video, args=[link])
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
                download(r.headers['location'], nome, bar=self._baixar_callback)
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
                        download(head, nome, bar=self._baixar_callback)
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


class PopupProcura(Popup):
    """Componente Popup."""

    textoBotao = StringProperty('Fechar')

    titulo = StringProperty('Procurando...')
    texto = StringProperty('Procurando Titulo')
    funcao = Property(lambda x: x.dismiss())

    def __init__(self, *args, **kwargs):
        """."""
        super().__init__(*args, **kwargs)
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

    def procura(self, nome, link, rv):
        """."""
        Thread(target=self._pagina_anime, args=[nome, link, rv]).start()

    def atualizar(self, func):
        """."""
        self.titulo = 'Atualizando...'
        self.texto = ''
        Thread(target=self._atualizar_pagina, args=[func]).start()

    def _atualizar_pagina(self, func):
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
        arq = open("res/Paginas.json", 'w')
        arq.write(json_s)
        arq.close()
        self.dismiss()
        func()

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
