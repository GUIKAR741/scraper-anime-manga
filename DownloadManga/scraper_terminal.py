import time
import requests as req
import os
import unicodedata
import re
from bs4 import BeautifulSoup
from PIL import Image


def reqbeau(url):
    r = req.get(url)
    b = BeautifulSoup(r.content, 'html.parser')
    return b


def criapasta(pasta):
    if not os.path.isdir(pasta):
        os.mkdir(pasta)


def baixarimg(pasta, i, n, urlImg):
    rr = req.get(str(urlImg))
    with open(pasta + "/" + str(i) + "." + n[n.__len__() - 1], 'wb') as code:
        code.write(rr.content)
    Image.open(pasta + "/" + str(i) + "." + n[n.__len__() - 1]).save(pasta + "/" + str(i) + "." + n[n.__len__() - 1])


def nomei(i, col=False):
    if (str(i).__len__() < 2) and col:
        i = '0' + str(i)
    return str(i)


def sanitizestring(palavra):
    # Unicode normalize transforma um caracter em seu equivalente em latin.
    nfkd = unicodedata.normalize('NFKD', palavra)
    palavrasemacento = u"".join([c for c in nfkd if not unicodedata.combining(c)])
    # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
    return re.sub('[^a-zA-Z0-9 \\\]', '', palavrasemacento)


def fbaixar(url, ren=False):
    urls = url.split('/')
    st = sanitizestring(str(urls[urls.__len__() - 2]))
    pasta = './img/' + st + urls[urls.__len__() - 1]
    print("Requisitando dados da URL %s...\n" % url)
    bb = reqbeau(url)
    criapasta("./img/")
    criapasta(pasta)
    i = 1
    for node in bb.find_all('img', pag=True):
        img = 'http:' + node.get("src")
        n = str(img).split(".")
        if str(img).find("leitor") != -1:
            nome = nomei(i, ren)
            baixarimg(pasta, nome, n, img)
            print(pasta + "/" + nome + "." + n[n.__len__() - 1])
            i += 1


def ibaixar(ren=False):
    inter = int(input("Deseja Baixar Entre Intervalo?\n"
                      "1-Sim "
                      "2-Não "
                      "3-Menu "
                      "0-Sair\n"
                      "Selecione uma Opção:"))
    if inter == 1:
        url = input("Digite a URL:").strip()
        interin = int(input("Inicio do Intervalo:"))
        interend = int(input("Fim do Intervalo:"))
        for i in range(interin, interend + 1):
            fbaixar(url + str(nomei(i, True)), ren)
    elif inter == 2:
        url = input("Digite a URL:").strip()
        fbaixar(url, ren)
    elif inter == 3:
        menu()
    elif inter == 0:
        print("Obrigado por Utilizar o Script")
        exit()
    else:
        print("Opção Invalida")
        ibaixar()


def baixar():
    esc = int(input("Deseja Baixar e renomear?\n"
                    "1-Sim "
                    "2-Não "
                    "3-Menu "
                    "0-Sair\n"
                    "Selecione uma Opção:"))
    if esc == 1:
        ibaixar(ren=True)
    elif esc == 2:
        ibaixar()
    elif esc == 3:
        menu()
    elif esc == 0:
        print("Obrigado por Utilizar o Script")
        exit()
    else:
        print("Opção Invalida")
        baixar()
    input("...")
    menu()


def frenomar(col=False, r=True, t=1, m=1):
    for _, __, arquivo in os.walk('./'):
        if str(_).find("./img") != -1:
            tam = __.__len__()
            if tam == 0:
                i = 1
                for arq in arquivo:
                    if not r:
                        # im = Image.open(_ + "\\" + arq)
                        # ima = im.copy()
                        # os.remove(_ + "\\" + arq)
                        # ima.save(_ + "\\-" + arq)
                        im = Image.open(_ + "\\" + arq)
                        x, y = im.size
                        if m == 1:
                            im.resize((x, y), Image.ANTIALIAS).save(_ + "\\-" + arq)
                            os.remove(_ + "\\" + arq)
                        else:
                            im.resize((x, y), Image.ANTIALIAS).save(_ + "\\" + arq.replace("-", ""))
                            os.remove(_ + "\\" + arq)
                    else:
                        if not col:
                            aa = arq.split(".")
                            os.rename(_ + "\\" + arq,
                                      _ + "\\" + nomei(aa[aa.__len__() - 2], col=True) + '.' + aa[aa.__len__() - 1])
                        else:
                            aa = arq.split(".")
                            os.rename(_ + "\\" + arq,
                                      _ + "\\" + str(i) + '.' + aa[aa.__len__() - 1])
                            i += 1
    if t != 1:
        print("Arquivos Renomeados")


def renomear():
    esc = int(input("Deseja Renomear?\n"
                    "1-Normal "
                    "2-Celular "
                    "3-Re-Criar e Renomear Para o Celular(+60 Seg) "
                    "4-Menu "
                    "0-Sair\n"
                    "Selecione uma Opção:"))
    if esc == 1:
        frenomar()
        frenomar(col=True, t=0)
    elif esc == 2:
        frenomar()
        frenomar(col=True)
        frenomar(t=0)
    elif esc == 3:
        frenomar()
        frenomar(r=False)
        print("Renomeando...")
        time.sleep(60)
        frenomar(r=False, m=0, t=0)
    elif esc == 4:
        menu()
    elif esc == 0:
        print("Obrigado por Utilizar o Script")
        exit()
    else:
        print("Opção Invalida")
        frenomar()
    input("...")
    menu()


def menu():
    print("Baixar Mangas V1.0")
    print("Opções:")
    print("1 - Baixar 2 - Renomear 0 - Sair")
    op = int(input("Selecione uma Opção:"))
    if op == 1:
        baixar()
    elif op == 2:
        renomear()
    elif op == 0:
        print("Obrigado por Utilizar o Script")
        exit()
    else:
        print("Opção Invalida")
        menu()


menu()
