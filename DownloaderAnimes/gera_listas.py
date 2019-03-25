"""Gerar Listas de Desenhos."""
from json import loads, load, dump
from multiprocessing.dummy import Pool
from operator import itemgetter
from io import StringIO

from bs4 import BeautifulSoup as Bs
from requests import RequestException, get, post


def busca_pag() -> list:
    """Busca os Desenhos."""
    def req_link(u, dados):
        try:
            resul = post(u, data=dados)
        except (Exception, RequestException):
            resul = req_link(u, dados)
        return resul

    link = f"{base}inc/paginator.inc.php"
    total = 99
    atual = 1
    ani = {'nome': [], 'link': [], 'img': []}
    lista_animes = []
    while atual <= total:
        data = {'type_url': "lista",
                'page': atual,
                'limit': 100,
                'total_page': total,
                'type': 'lista',
                'filters': '{"filter_data":"filter_display_view=grade&filter_letter=0&'
                           'filter_type_content=4&filter_genre_model=0&filter_order=a-z&'
                           'filter_rank=0&filter_status=0&filter_idade=&filter_dub=0&'
                           'filter_size_start=0&filter_size_final=0&filter_date=0&'
                           'filter_viewed=0","filter_genre_add":[],"filter_genre_del":[]}'}
        e = req_link(link, data)
        body = loads(e.content)
        total = body['total_page']
        atual += 1
        for I in range(len(body['body'])):
            novo_ani = dict(ani)
            b = Bs(body['body'][I], 'html.parser')
            a = b.find('h1', 'grid_title').find('a')
            img = b.find('img').get('src')
            novo_ani['nome'] = a.text
            novo_ani['link'] = a.get('href') if ('http' or 'https') in a.get(
                'href') else "https:" + a.get('href')
            novo_ani['img'] = img
            lista_animes.append(novo_ani)
    # for I in sorted(lista_animes, key=itemgetter('nome')):
    #     ani['nome'].append(I['nome'])
    #     ani['link'].append(I['link'])
    ani = sorted(lista_animes, key=itemgetter('nome'))
    return ani


def download_video(link):
    """Pega o Link."""
    def req_link(u):
        try:
            resul = get(u, stream=True)
        except (Exception, RequestException):
            resul = req_link(u)
        return resul

    def down(link_, max: int = 1):
        try:
            if max > 5:
                return
            print(link_[0])
            link_down = link_[1]
            link_down = link_down if (
                'http' or 'https') in link_down else "https:" + link_down
            r = req_link(link_down)
            b = Bs(r.content, 'html.parser')
            nome = b.find("h1", itemprop='name').text.split()[-1] + '-'
            nome += b.find("h2", itemprop='alternativeHeadline').text
            bb = b.find("source")
            if bb:
                ll = bb.get("src") if ('http' or 'https') in bb.get(
                    'src') else "https:" + bb.get('src')
                r = ll
                return {nome: r}
            else:
                bb = b.find('a', title="Baixar Video")
                if bb:
                    r = req_link(bb.get("href") if ('http' or 'https') in bb.get(
                        'href') else "https:" + bb.get('href'))
                    b = Bs(r.content, 'html.parser')
                    bb = b.find("a", "bt-download")
                    if bb:
                        head = bb.get("href") if ('http' or 'https') in bb.get(
                            'href') else "https:" + bb.get('href')
                        return {nome: head}
        except Exception as e:
            print("Down", link_[0], e)
            return down(link_, max+1)

    try:
        node = Pool(10)
        espera = node.map_async(down, link['episodios'])
        espera.wait()
        link['episodios'] = espera.get()
        return link
    except (Exception, AttributeError) as exp:
        print("Download", link['nome'], exp)
        return download_video(link)


def pagina_anime(ani: dict):
    """Pega os Episodios."""
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
    print(ani['nome'])
    link = ani['link']
    link = link if ('http' or 'https') in link else "https:" + link
    r = req_link(link)
    b = Bs(r.content, 'html.parser')
    id_cat = b.find('div', attrs={"data-id-cat": True}).get("data-id-cat")
    atual = 1
    tam = 99
    link = f"{base}inc/paginatorVideo.inc.php"
    ani['episodios'] = []
    while atual <= tam:
        data = {'id_cat': id_cat,
                'page': atual,
                'limit': 100,
                'total_page': tam,
                'order_video': 'asc'}
        e = req_link_post(link, data)
        body = loads(e.content)
        tam = body['total_page']
        atual += 1
        if tam > 0:
            for II in range(len(body['body'])):
                bb = Bs(body['body'][II], 'html.parser')
                a = bb.find('div', 'epsBoxSobre').find('a')
                ani['episodios'].append((a.text, a.get('href') if ('http' or 'https') in
                                         a.get('href')
                                         else "https:" + a.get('href')))
    box = b.find_all("div", 'boxBarraInfo js_dropDownBtn active')
    if box:
        for K in box:
            par = K.parent
            ova = par.find_all('div', 'epsBox')
            if ova:
                for kk in ova:
                    ani['episodios'].append((str("OVA: " + kk.find("h3").a.text),
                                             kk.find("h3").a.get("href")
                                             if ('http' or 'https') in kk.find("h3").a.get("href")
                                             else "https:" + kk.find("h3").a.get("href")))
            fil = par.find_all('div', 'epsBoxFilme')
            if fil:
                for L in fil:
                    ani['episodios'].append((str("FILME: " + L.find("h4").text),
                                             L.find("a").get("href")
                                             if ('http' or 'https') in L.find("a").get("href")
                                             else "https:" + L.find("a").get("href")))
    return ani


def m3u(animes_parse: dict):
    """Gera a Lista."""
    m3u8 = '#EXTM3U\n'
    for i in animes_parse:
        for j in i['episodios']:
            nome = ' '.join(i['nome'].replace(
                ',', '').replace('-', ' ').split())
            if j is not None:
                k = [*j.keys()][0]
                m3u8 += '#EXTINF:-1 tvg-id="' + nome + '" tvg-name="' + nome + '" logo="' \
                        + i['img'].replace(',', '%2C') + '", ' + nome + " " \
                        + ' '.join(k.replace(',', ' ').replace('-',
                                                               ' ').split()) + '\n'
                m3u8 += j[k] + "\n"
    arq = open('listas/listaDesenho.m3u', 'w')
    arq.write(m3u8)
    arq.close()


def salvar_arq(arq: dict, nome: str):
    """Salva o arquivo json."""
    io = StringIO()
    dump(arq, io)
    json_s = io.getvalue()
    arq = open(f'{pasta}/{nome}.json', 'w')
    arq.write(json_s)
    arq.close()


def ler_arq(nome: str) -> dict:
    """Abre o arquivo json."""
    return load(open(f'{pasta}/{nome}.json'))


print("Procurar Episodios")
base = "https://www.superanimes.com/"
pasta = "listas"
# animes = busca_pag()
# salvar_arq(animes, "desenho")
# print("Pegar Links")
# no = Pool(100)
# animes = no.map_async(pagina_anime, animes)
# animes.wait()
# animes = animes.get()
# salvar_arq(animes, "desenho")
animes = ler_arq("desenho")
print("Alterar Links")
no = Pool(2)
animes = no.map_async(download_video, animes)
animes.wait()
animes = animes.get()
salvar_arq(animes, "desenho")
print("Gera Lista")
m3u(animes)
print("fim")
