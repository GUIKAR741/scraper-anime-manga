"""."""
from .telaBase import Tela  # pylint: disable=relative-beyond-top-level
import pafy
from kivy.properties import StringProperty  # pylint: disable=no-name-in-module
from .popup import PopupProcura  # pylint: disable=relative-beyond-top-level
from threading import Thread


class YouTube(Tela):
    """."""

    info = StringProperty('')

    def on_enter(self, *args, **kwargs):
        """."""
        super().on_enter(*args, **kwargs)
        self.ids.videoV.active = True
        self.ids.videoS.active = True
        self.ids.texto.text = ''
        self.ids.rv.data = []
        self.info = ''

    def buscar(self):
        """."""
        p = PopupProcura()
        p.open()
        Thread(target=self._busca, args=[p]).start()

    def _busca(self, pop):
        """."""
        busca = self.ids.texto.text
        if self.ids.videoV.active:
            video = pafy.new(busca)
            self.info = video.title+"\nDuração: "+video.duration
            ordena = {}
            for i in video.allstreams:
                if not (i.mediatype in ordena.keys()):
                    ordena[i.mediatype] = [i]
                else:
                    ordena[i.mediatype].append(i)
            for i in ordena.items():
                ordena[i[0]] = i[1][::-1]
            if 'video' in ordena.keys():
                del ordena['video']
            orden = []
            for i in sorted(ordena.items(), key=lambda x: x[0], reverse=True):
                orden += i[1]
            retorno = [{'titulo': 'Qualidade: ' + i.quality +
                                  '  Mediatype: ' + i.mediatype +
                                  '\nExtensão: ' + i.extension +
                                  '  Tamanho: '+('%.2f MB' %
                                                 ((i.get_filesize()/1024)/1024)),
                        'link': i.url,
                        'tipo': 'video',
                        'video': (video, i, self.ids.videoS),
                        'tituloBotao': 'Baixar'}
                       for i in orden]
            self.ids.rv.data = retorno
        else:
            playlist = pafy.get_playlist(busca)
            self.info = playlist['title']
            retorno = [{'titulo': i['pafy'].title,
                        'link': i['pafy'].title,
                        'tipo': 'video',
                        'video': (i['pafy'], i['pafy'].getbest(), self.ids.videoS),
                        'tituloBotao': 'Baixar'}
                       for i in playlist['items']]
            self.ids.rv.data = retorno
        pop.dismiss()
