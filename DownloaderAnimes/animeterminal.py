import re
import unicodedata
import requests as req
import wget
import os
import json
from io import StringIO
from threading import Thread
from bs4 import BeautifulSoup


def sanitizestring(palavra):
    # Unicode normalize transforma um caracter em seu equivalente em latin.
    nfkd = unicodedata.normalize('NFKD', palavra)
    palavrasemacento = u"".join([c for c in nfkd if not unicodedata.combining(c)])
    # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
    return re.sub('[^a-zA-Z0-9 \\\]', '', palavrasemacento)


def downloadVideo(link, retorno=False, num=""):
    def reqLink(u):
        try:
            resul = req.get(u)
        except (Exception, req.RequestException):
            resul = reqLink(u)
        return resul

    def pegaLink(href):
        s = req.get(href, allow_redirects=False)
        return s.headers['location']

    try:
        r = reqLink(link)
        b = BeautifulSoup(r.content, 'html.parser')
        bb = b.find("source")
        if bb:
            r = req.get(bb.get("src"), allow_redirects=False)
            if retorno:
                wget.download(r.headers['location'],
                              str(num) + sanitizestring(b.find("h2", itemprop="alternativeHeadline").text) + ".mp4")
            else:
                return r.headers['location']
        else:
            bb = b.find('a', title="Baixar Video")
            if bb:
                r = reqLink(bb.get("href"))
                b = BeautifulSoup(r.content, 'html.parser')
                bb = b.find("a", "bt-download")
                if bb:
                    head = pegaLink(bb.get("href"))
                    if retorno:
                        wget.download(head,
                                      str(num) + sanitizestring(b.find("h2", itemprop="alternativeHeadline").text) +
                                      ".mp4")
                    else:
                        return head

    except (Exception, AttributeError) as exp:
        print(link, exp)


def paginaAnime(nome, link):
    def reqLink(u):
        try:
            resul = req.get(u)
        except (Exception, req.RequestException):
            resul = reqLink(u)
        return resul

    try:
        dic = dict({'ep': [], 'link': []})
        if os.path.isfile("animes/" + sanitizestring(nome) + ".json"):
            arq = open("animes/" + sanitizestring(nome) + ".json", 'r')
            dic = json.load(arq)
            arq.close()
        r = reqLink(link)
        b = BeautifulSoup(r.content, 'html.parser')
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
        arq = "animes/" + sanitizestring(nome) + ".json"
        # print(arq)
        arq = open(arq, 'w')
        arq.write(jsonS)
        arq.close()
        a = b.find("a", title="Próxima Pagina")
        if a:
            paginaAnime(nome, a.get("href"))
    except (Exception, AttributeError) as exception:
        print(link, exception)
        paginaAnime(nome, link)


def alterarTodos():
    def inifim(h, g):
        for o in range(len(h)):
            if not h[o] in g:
                print(h[o], len(g))
                alterarDownload(h[o])
                g.append(h[o])
                # print(len(g))
            else:
                print("está", h[o])

    def meioinicio(h, g):
        for o in range(len(h) // 2 - 1, 0, -1):
            if not h[o] in g:
                print(h[o], len(g))
                alterarDownload(h[o])
                g.append(h[o])
                # print(len(g))
            else:
                print("está", h[o])

    def meiofim(h, g):
        for o in range(len(h) // 2, len(h), 1):
            if not h[o] in g:
                print(h[o], len(g))
                alterarDownload(h[o])
                g.append(h[o])
                # print(len(g))
            else:
                print("está", h[o])

    def fimini(h, g):
        for o in range(len(h) - 1, 0, -1):
            if not h[o] in g:
                print(h[o], len(g))
                alterarDownload(h[o])
                g.append(h[o])
                # print(len(g))
            else:
                print("está", h[o])

    lis = []
    lisC = []
    for l, j, k in os.walk("animes/"):
        for i in k:
            try:
                abc = open("animes/" + i)
                dicio = json.load(abc)
                abc.close()
                if "" in dicio["download"]:
                    lis.append("animes/" + i)
                else:
                    lisC.append(i)
            except (Exception, json.decoder.JSONDecodeError) as err:
                print(i, err)
    Thread(target=inifim, args=[lis, lisC]).start()
    Thread(target=fimini, args=[lis, lisC]).start()
    Thread(target=meiofim, args=[lis, lisC]).start()
    Thread(target=meioinicio, args=[lis, lisC]).start()


def alterarDownload(dicio):
    def altera(dicionario, ind):
        dicionario['download'][ind] = downloadVideo(dicionario['link'][ind])

    dd = arq = dicio
    try:
        print(dicio)
        abc = open(arq)
        dicio = json.load(abc)
        abc.close()
        li = []
        j = 0
        for i in range(len(dicio['ep'])):
            th = Thread(target=altera, args=[dicio, i])
            li.append(th)
            th.start()
            j += 1
            if j == 10:
                for k in li:
                    k.join()
                j = 0
            # altera(dicio, i)
        if j > 0:
            for k in li:
                k.join()
        # print(dicio)
        # exit(0)
        io = StringIO()
        json.dump(dicio, io)
        jsonS = io.getvalue()
        arq = open(arq, 'w')
        arq.write(jsonS)
        arq.close()
    except (Exception, json.decoder.JSONDecodeError) as err:
        print(dicio, err)
        alterarDownload(dd)


def pesquisaAnimes():
    def bP1(a):
        for q in range(len(a['nome'])):
            if not os.path.isfile("animes/" + str(q + 1) + " " + sanitizestring(a['nome'][q]) + ".json"):
                print(str(q + 1) + " " + a['nome'][q] + ".json")
                thread = Thread(target=paginaAnime, args=[str(q + 1) + " " + a['nome'][q], a['link'][q]])
                thread.start()
                thread.join()

    def bP2(a):
        for i in range(len(a['nome']) - 1, 0, -1):
            if not os.path.isfile("animes/" + str(i + 1) + " " + sanitizestring(a['nome'][i]) + ".json"):
                print(str(i + 1) + " " + a['nome'][i] + ".json")
                thread = Thread(target=paginaAnime, args=[str(i + 1) + " " + a['nome'][i], a['link'][i]])
                thread.start()
                thread.join()

    def bP3(a):
        for i in range(len(a['nome']) // 2 - 1, 0, -1):
            if not os.path.isfile("animes/" + str(i + 1) + " " + sanitizestring(a['nome'][i]) + ".json"):
                print(str(i + 1) + " " + a['nome'][i] + ".json")
                thread = Thread(target=paginaAnime, args=[str(i + 1) + " " + a['nome'][i], a['link'][i]])
                thread.start()
                thread.join()

    def bP4(a):
        for i in range(len(a['nome']) // 2, len(a['nome'])):
            if not os.path.isfile("animes/" + str(i + 1) + " " + sanitizestring(a['nome'][i]) + ".json"):
                print(str(i + 1) + " " + a['nome'][i] + ".json")
                thread = Thread(target=paginaAnime, args=[str(i + 1) + " " + a['nome'][i], a['link'][i]])
                thread.start()
                thread.join()

    abc = open("animes/Paginas.json")
    ani = json.load(abc)
    abc.close()
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


def buscaPagina(buscar=False):
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
        tam = str(len(b.find("select", "pageSelect").find_all("option")))
        meio = str(int(tam) // 2)
        t1 = Thread(target=todosAnimes, args=[link])
        t2 = Thread(target=todosAnimes, args=[link + "?pagina=" + meio, False])
        t3 = Thread(target=todosAnimes, args=[link + "?pagina=" + meio])
        t4 = Thread(target=todosAnimes, args=[link + "?pagina=" + tam, False])
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t1.join()
        t2.join()
        t3.join()
        t4.join()
        transformaJson()


def todosAnimes(link, direcao=True):
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
        anime = b.find("div", "boxConteudo").find_all("div", "boxLista2")
        for j in anime:
            j = j.find("a", title=True)
            dic["nome"].append(j.img.get("title"))
            dic["link"].append(j.get("href"))
        io = StringIO()
        json.dump(dic, io)
        jsonS = io.getvalue()

        arq = 'animes/' + sanitizestring(b.find("select", "pageSelect").find("option", selected=True).text) + '.json'
        arq = open(arq, 'w')
        arq.write(jsonS)
        arq.close()
        if direcao:
            a = b.find("a", title="Próxima Pagina")
        else:
            a = b.find("a", title="Pagina Anterior")
        if a:
            todosAnimes(a.get("href"), direcao)


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


if __name__ == "__main__":
    if not os.path.isdir("animes"):
        os.mkdir("animes")
    # print(downloadVideo("https://www.superanimes.site/ova/hellsing-the-dawn/episodio-1"))
    # paginaAnime("885 Goblin Slayer", "https://www.superanimes.site/anime/goblin-slayer")
    # print("buscapagina")
    # buscaPagina()
    # print("pequisaanimes")
    # pesquisaAnimes()
    # print("alterartodos")
    link = "https://www.superanimes.site/inc/paginatorVideo.inc.php"
    linkAni = "https://www.superanimes.site/anime/black-clover"
    r = req.get(linkAni)
    b = BeautifulSoup(r.content, 'html.parser')
    id_cat = b.find('div', id='listaDeConteudo').get("data-id-cat")
    total = 99
    atual = 1
    ani = {'ep': [], 'link': []}
    while atual <= total:
        data = {'id_cat': id_cat,
                'page': atual,
                'limit': 25,
                'total_page': total,
                'order_video': 'asc'}
        e = req.post(link, data=data)
        body = json.loads(e.content)
        total = body['total_page']
        atual += 1
        for i in range(len(body['body'])):
            b = BeautifulSoup(body['body'][i], 'html.parser')
            a = b.find('div', 'epsBoxSobre').find('a')
            ani['ep'].append(a.text)
            ani['link'].append(a.get('href') if ('http' or 'https') in a.get('href') else "https:" + a.get('href'))
    print(ani)
    # for i in sorted(listaAnimes, key=itemgetter('nome')):
    #     ani['nome'].append(i['nome'])
    #     ani['link'].append(i['link'])
    # print(ani)
    # alterarTodos()
    # alterarDownload("animes/1813 One Piece.json")
# downloadVideo("https://www.superanimes.site/anime/overlord-iii/episodio-11",True)
