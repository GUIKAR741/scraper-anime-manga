"""."""
from json import dump, load, loads  # pylint: disable=unused-import
from os import path

from kivy.app import App

from .popup import PopupProcura  # pylint: disable=relative-beyond-top-level
from .telaBase import Tela  # pylint: disable=relative-beyond-top-level


class Animes(Tela):
    """."""

    def on_enter(self, *args, **kwargs):
        """."""
        super().on_enter(*args, **kwargs)
        self.path = App.get_running_app().user_data_dir+'/'
        self._atualizar_lista()
        self.ids.texto.text = ''
        self.ids.texto.disable = False
        self.ids.buscar.text = 'Buscar'

    def _clear(self):
        """."""
        self.ids.rv.data = []

    def procurar(self):
        """."""
        if self.ids.buscar.text == 'Buscar':
            busca = self.ids.texto.text.lower()
            retorno = []
            for i in range(len(self.animes['nome'])):
                if busca in self.animes['nome'][i].lower():
                    retorno.append({'titulo': self.animes['nome'][i],
                                    'link': self.animes['link'][i],
                                    'tituloBotao': 'Ver Episodios',
                                    'tipo': 'anime'})
            self.ids.rv.data = retorno
            self.ids.texto.text = ''
            self.ids.buscar.text = 'Resetar'
            self.ids.texto.disabled = True
        else:
            self.ids.buscar.text = 'Buscar'
            self.ids.texto.disabled = False
            self._atualizar_lista()

    def atualizar(self):
        """."""
        p = PopupProcura()
        p.open()
        p.atualizar('animes', self._atualizar_lista)

    def _atualizar_lista(self):
        """."""
        if path.isfile(self.path+"PaginasAnimes.json"):
            self.animes = load(open(self.path+"PaginasAnimes.json"))
            self.ids.rv.data = [{'titulo': self.animes['nome'][i],
                                 'link': self.animes['link'][i],
                                 'tituloBotao': 'Ver Episodios',
                                 'tipo': 'anime'}
                                for i in range(len(self.animes['nome']))]
