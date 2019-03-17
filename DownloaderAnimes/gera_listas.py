from requests import get, RequestException, post
from bs4 import BeautifulSoup as bs
from json import load, loads, dump
from io import StringIO
from multiprocessing.dummy import Pool


def download_video(link):
    def req_link(u):
        try:
            resul = get(u, stream=True)
        except (Exception, RequestException):
            resul = req_link(u)
        return resul

    def pega_link(href, header):
        s = get(href, stream=True, allow_redirects=False, headers=header)
        return s.headers['location']

    try:
        link = link[1]
        link = link if ('http' or 'https') in link else "https:" + link
        r = req_link(link)
        b = bs(r.content, 'html.parser')
        nome = b.find("h1", itemprop='name').text.split()[-1] + '-'
        nome += b.find("h2", itemprop='alternativeHeadline').text
        bb = b.find("source")
        headers = {
            'Referer': link
        }
        if bb:
            ll = bb.get("src") if ('http' or 'https') in bb.get('src') else "https:" + bb.get('src')
            r = get(ll, stream=True, allow_redirects=False, headers=headers)
            return nome, r.headers['location']
        else:
            bb = b.find('a', title="Baixar Video")
            if bb:
                r = req_link(bb.get("href") if ('http' or 'https') in bb.get('href') else "https:" + bb.get('href'))
                b = bs(r.content, 'html.parser')
                bb = b.find("a", "bt-download")
                if bb:
                    head = pega_link(bb.get("href") if ('http' or 'https') in bb.get('href') else "https:" +
                                                                                                  bb.get('href'),
                                     headers)
                    return nome, head
    except (Exception, AttributeError) as exp:
        print(link, exp)


def pagina_anime(self, nome, link):
    def req_link(u):
        try:
            resul = get(u)
        except (Exception, RequestException):
            resul = req_link(u)
        return resul

    def req_link_post(u, info):
        try:
            resul = post(u, data=info)
        except (Exception, RequestException):
            resul = req_link_post(u, info)
        return resul

    # try:
    dic = dict({'ep': [], 'link': []})
    link = link if ('http' or 'https') in link else "https:"+link
    r = req_link(link)
    b = bs(r.content, 'html.parser')
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
        e = req_link_post(link, data)
        body = loads(e.content)
        self.tam = body['total_page']
        self.mpb['maximum'] = self.tam
        self.speed.set('Paginas: ' + str(self.tam))
        self.eta.set('Paginas Percorridas: %d' % atual)
        self.mpb['value'] = atual
        atual += 1
        if self.tam > 0:
            for II in range(len(body['body'])):
                bb = bs(body['body'][II], 'html.parser')
                a = bb.find('div', 'epsBoxSobre').find('a')
                dic['ep'].append(a.text)
                dic['link'].append(
                    a.get('href') if ('http' or 'https') in a.get('href') else "https:" + a.get('href'))
    box = b.find_all("div", 'boxBarraInfo js_dropDownBtn active')
    if box:
        for K in box:
            par = K.parent
            ova = par.find_all('div', 'epsBox')
            if ova:
                for kk in ova:
                    dic['ep'].append("OVA: "+kk.find("h3").a.text)
                    dic['link'].append(kk.find("h3").a.get("href") if ('http' or 'https') in
                                       kk.find("h3").a.get("href") else "https:" + kk.find("h3").a.get("href"))
            fil = par.find_all('div', 'epsBoxFilme')
            if fil:
                for L in fil:
                    dic['ep'].append("FILME: "+L.find("h4").text)
                    dic['link'].append(L.find("a").get("href") if ('http' or 'https') in L.find("a").get("href")
                                       else "https:" + L.find("a").get("href"))
    io = StringIO()
    dump(dic, io)
    json_s = io.getvalue()
    arq = "animes/" + self.sanitizestring(nome) + ".json"
    arq = open(arq, 'w')
    arq.write(json_s)
    arq.close()
    # except (Exception, AttributeError) as exception:
    #     print(link, exception)


knd = load(open("animes/1250 KND  A Turma Do Bairro.json"))
du = load(open("animes/664 Du Dudu E Edu.json"))
arqknd = list((zip(knd['ep'], knd['link'])))
arqdu = (zip(du['ep'], du['link']))
kndimg = 'https://img.superanimes.site/img/animes/gyv7-large.jpg'
duimg = "https://img.superanimes.site/img/animes/HtmX-large.jpg"
no = Pool(10)
esp = no.map_async(download_video, arqknd)
esp.wait()
kndep = esp.get()
no = Pool(10)
esp = no.map_async(download_video, arqdu)
esp.wait()
duep = esp.get()
m3u = '#EXTM3U\n'
for i in kndep:
    m3u += '#EXTINF:-1 tvg-id="' + i[0] + '" tvg-name="' \
           + i[0] + '" logo="' + kndimg + '", KND - A Turma do Bairo ' + i[0] + '\n'
    m3u += i[1] + "\n"
for i in duep:
    m3u += '#EXTINF:-1 tvg-id="' + i[0] + '" tvg-name="' \
           + i[0] + '" logo="' + duimg + '", Du, Dudu e Edu ' + i[0] + '\n'
    m3u += i[1] + "\n"

arq = open('listaDesenho.m3u', 'w')
arq.write(m3u)
arq.close()