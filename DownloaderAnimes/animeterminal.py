from re import sub, compile
from unicodedata import normalize, combining
from requests import get, post, RequestException
from wget import download
from os import path, mkdir, walk, remove
from json import load, dump, decoder, loads
from io import StringIO
from threading import Thread
from bs4 import BeautifulSoup


def sanitizestring(palavra):
    # Unicode normalize transforma um caracter em seu equivalente em latin.
    nfkd = normalize('NFKD', palavra)
    palavrasemacento = u"".join([c for c in nfkd if not combining(c)])
    # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
    return sub('[^a-zA-Z0-9 \\\]', '', palavrasemacento)


def download_video(link_down, retorno=False, num=""):
    def req_link(u):
        try:
            resul = get(u)
        except (Exception, RequestException):
            resul = req_link(u)
        return resul

    def pega_link(href):
        s = get(href, allow_redirects=False)
        return s.headers['location']

    try:
        requi = req_link(link_down)
        beaut = BeautifulSoup(requi.content, 'html.parser')
        bb = beaut.find("source")
        if bb:
            requi = get(bb.get("src"), allow_redirects=False)
            if retorno:
                download(requi.headers['location'], str(num) +
                         sanitizestring(beaut.find("h2", itemprop="alternativeHeadline").text) + ".mp4")
            else:
                return requi.headers['location']
        else:
            bb = beaut.find('a', title="Baixar Video")
            if bb:
                requi = req_link(bb.get("href"))
                beaut = BeautifulSoup(requi.content, 'html.parser')
                bb = beaut.find("a", "bt-download")
                if bb:
                    head = pega_link(bb.get("href"))
                    if retorno:
                        download(head, str(num) +
                                 sanitizestring(beaut.find("h2", itemprop="alternativeHeadline").text) + ".mp4")
                    else:
                        return head

    except (Exception, AttributeError) as exp:
        print(link_down, exp)


def pagina_anime(nome, link_page):
    def req_link(u):
        try:
            resul = get(u)
        except (Exception, RequestException):
            resul = req_link(u)
        return resul

    try:
        dic = dict({'ep': [], 'link': []})
        if path.isfile("animes/" + sanitizestring(nome) + ".json"):
            arq = open("animes/" + sanitizestring(nome) + ".json", 'r')
            dic = load(arq)
            arq.close()
        reques = req_link(link_page)
        b_page = BeautifulSoup(reques.content, 'html.parser')
        eps = b_page.find("div", itemprop="episode")
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
            ova = b_page.find("div", "js_dropDownView")
            if ova:
                box_ov = ova.find_all("div", "epsBox")
                if box_ov:
                    for ii in box_ov:
                        ov = ii.find("h3")
                        num = compile('([0-9]+)').findall(str(ov.a.get("title")))[0]
                        dic['ep'].append(num + ' - ' + ov.text)
                        dic['link'].append(ov.a.get('href'))
                        # dic['download'].append("")
                fil = ova.find_all("div", "epsBoxFilme")
                if fil:
                    for o in fil:
                        num = compile('([0-9]+)').findall(str(o.find("h3").text))[0]
                        dic['ep'].append(num + ' - ' + o.find("h4").text)
                        dic['link'].append(o.find("a").get("href"))
                        # dic['download'].append("")
        io = StringIO()
        dump(dic, io)
        json_s = io.getvalue()
        arq = "animes/" + sanitizestring(nome) + ".json"
        # print(arq)
        arq = open(arq, 'w')
        arq.write(json_s)
        arq.close()
        prox = b_page.find("a", title="Próxima Pagina")
        if prox:
            pagina_anime(nome, prox.get("href"))
    except (Exception, AttributeError) as exception:
        print(link_page, exception)
        pagina_anime(nome, link_page)


def alterar_todos():
    def inifim(h, g):
        for o in range(len(h)):
            if not h[o] in g:
                print(h[o], len(g))
                alterar_download(h[o])
                g.append(h[o])
                # print(len(g))
            else:
                print("está", h[o])

    def meioinicio(h, g):
        for o in range(len(h) // 2 - 1, 0, -1):
            if not h[o] in g:
                print(h[o], len(g))
                alterar_download(h[o])
                g.append(h[o])
                # print(len(g))
            else:
                print("está", h[o])

    def meiofim(h, g):
        for o in range(len(h) // 2, len(h), 1):
            if not h[o] in g:
                print(h[o], len(g))
                alterar_download(h[o])
                g.append(h[o])
                # print(len(g))
            else:
                print("está", h[o])

    def fimini(h, g):
        for o in range(len(h) - 1, 0, -1):
            if not h[o] in g:
                print(h[o], len(g))
                alterar_download(h[o])
                g.append(h[o])
                # print(len(g))
            else:
                print("está", h[o])

    lis = []
    lis_c = []
    for l, j, k in walk("animes/"):
        for iI in k:
            try:
                abc = open("animes/" + iI)
                dicio = load(abc)
                abc.close()
                if "" in dicio["download"]:
                    lis.append("animes/" + iI)
                else:
                    lis_c.append(iI)
            except (Exception, decoder.JSONDecodeError) as err:
                print(iI, err)
    Thread(target=inifim, args=[lis, lis_c]).start()
    Thread(target=fimini, args=[lis, lis_c]).start()
    Thread(target=meiofim, args=[lis, lis_c]).start()
    Thread(target=meioinicio, args=[lis, lis_c]).start()


def alterar_download(dicio):
    def altera(dicionario, ind):
        dicionario['download'][ind] = download_video(dicionario['link'][ind])

    dd = arq = dicio
    try:
        print(dicio)
        abc = open(arq)
        dicio = load(abc)
        abc.close()
        li = []
        j = 0
        for I in range(len(dicio['ep'])):
            th = Thread(target=altera, args=[dicio, I])
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
        dump(dicio, io)
        json_s = io.getvalue()
        arq = open(arq, 'w')
        arq.write(json_s)
        arq.close()
    except (Exception, decoder.JSONDecodeError) as err:
        print(dicio, err)
        alterar_download(dd)


def pesquisa_animes():
    def b_p1(part1):
        for q in range(len(part1['nome'])):
            if not path.isfile("animes/" + str(q + 1) + " " + sanitizestring(part1['nome'][q]) + ".json"):
                print(str(q + 1) + " " + part1['nome'][q] + ".json")
                thread = Thread(target=pagina_anime, args=[str(q + 1) + " " + part1['nome'][q], part1['link'][q]])
                thread.start()
                thread.join()

    def b_p2(part2):
        for p2 in range(len(part2['nome']) - 1, 0, -1):
            if not path.isfile("animes/" + str(p2 + 1) + " " + sanitizestring(part2['nome'][p2]) + ".json"):
                print(str(p2 + 1) + " " + part2['nome'][p2] + ".json")
                thread = Thread(target=pagina_anime, args=[str(p2 + 1) + " " + part2['nome'][p2], part2['link'][p2]])
                thread.start()
                thread.join()

    def b_p3(part3):
        for p3 in range(len(part3['nome']) // 2 - 1, 0, -1):
            if not path.isfile("animes/" + str(p3 + 1) + " " + sanitizestring(part3['nome'][p3]) + ".json"):
                print(str(p3 + 1) + " " + part3['nome'][p3] + ".json")
                thread = Thread(target=pagina_anime, args=[str(p3 + 1) + " " + part3['nome'][p3], part3['link'][p3]])
                thread.start()
                thread.join()

    def b_p4(part4):
        for p4 in range(len(part4['nome']) // 2, len(part4['nome'])):
            if not path.isfile("animes/" + str(p4 + 1) + " " + sanitizestring(part4['nome'][p4]) + ".json"):
                print(str(p4 + 1) + " " + part4['nome'][p4] + ".json")
                thread = Thread(target=pagina_anime, args=[str(p4 + 1) + " " + part4['nome'][p4], part4['link'][p4]])
                thread.start()
                thread.join()

    abc = open("animes/Paginas.json")
    animes = load(abc)
    abc.close()
    t1 = Thread(target=b_p1, args=[animes])
    t2 = Thread(target=b_p2, args=[animes])
    t3 = Thread(target=b_p3, args=[animes])
    t4 = Thread(target=b_p4, args=[animes])
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()


def busca_pagina(buscar=False):
    def req_link(u):
        try:
            resul = get(u)
        except (Exception, RequestException):
            resul = req_link(u)
        return resul

    if not path.isfile("animes/Paginas.json") or buscar:
        link_lista = "https://www.superanimes.site/lista"
        rlink = req_link(link_lista)
        blink = BeautifulSoup(rlink.content, 'html.parser')
        tam = str(len(blink.find("select", "pageSelect").find_all("option")))
        meio = str(int(tam) // 2)
        t1 = Thread(target=todos_animes, args=[link_lista])
        t2 = Thread(target=todos_animes, args=[link_lista + "?pagina=" + meio, False])
        t3 = Thread(target=todos_animes, args=[link_lista + "?pagina=" + meio])
        t4 = Thread(target=todos_animes, args=[link_lista + "?pagina=" + tam, False])
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t1.join()
        t2.join()
        t3.join()
        t4.join()
        transforma_json()


def todos_animes(linkanimes, direcao=True):
    def req_link(u):
        try:
            resul = get(u)
        except (Exception, RequestException):
            resul = req_link(u)
        return resul

    dic = dict({'nome': [], 'link': []})
    s = compile('([0-9]+)').findall(linkanimes)
    if not path.isfile("animes/Pagina " + (s[0] if len(s) else '1') + ".json"):
        rget = req_link(linkanimes)
        bget = BeautifulSoup(rget.content, 'html.parser')
        anime = bget.find("div", "boxConteudo").find_all("div", "boxLista2")
        for j in anime:
            j = j.find("a", title=True)
            dic["nome"].append(j.img.get("title"))
            dic["link"].append(j.get("href"))
        io = StringIO()
        dump(dic, io)
        json_s = io.getvalue()
        arq = 'animes/' + \
              sanitizestring(bget.find("select", "pageSelect").find("option", selected=True).text) + '.json'
        arq = open(arq, 'w')
        arq.write(json_s)
        arq.close()
        dire = bget.find("a", title="Próxima Pagina") if direcao else bget.find("a", title="Pagina Anterior")
        if dire:
            todos_animes(dire.get("href"), direcao)


def transforma_json():
    dic = dict({'nome': [], 'link': []})
    for l, j, k in walk("animes/"):
        lis = []
        for ll in k:
            s = compile('([0-9]+)').findall(ll)
            if path.isfile("animes/Pagina " + (s[0] if len(s) else '') + ".json"):
                lis.append(int(s[0]))
        lis.sort()
        for li in lis:
            arq = open("animes/Pagina " + str(li) + ".json", 'r')
            js = load(arq)
            dic['nome'] += js['nome']
            dic['link'] += js['link']
            arq.close()
            remove("animes/Pagina " + str(li) + ".json")
    io = StringIO()
    dump(dic, io)
    json_s = io.getvalue()
    arq = open("animes/Paginas.json", 'w')
    arq.write(json_s)
    arq.close()


if __name__ == "__main__":
    if not path.isdir("animes"):
        mkdir("animes")
    # print(downloadVideo("https://www.superanimes.site/ova/hellsing-the-dawn/episodio-1"))
    # paginaAnime("885 Goblin Slayer", "https://www.superanimes.site/anime/goblin-slayer")
    # print("buscapagina")
    # buscaPagina()
    # print("pequisaanimes")
    # pesquisaAnimes()
    # print("alterartodos")
    link = "https://www.superanimes.site/inc/paginatorVideo.inc.php"
    linkAni = "https://www.superanimes.site/anime/black-clover"
    r = get(linkAni)
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
        e = post(link, data=data)
        body = loads(e.content)
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
