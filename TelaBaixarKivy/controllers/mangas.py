"""."""
from json import dump, load, loads  # pylint: disable=unused-import
from os import path

from kivy.app import App

from .popup import PopupProcura  # pylint: disable=relative-beyond-top-level
from .telaBase import Tela  # pylint: disable=relative-beyond-top-level


class Mangas(Tela):
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
            for i in range(len(self.mangas['nome'])):
                if busca in self.mangas['nome'][i].lower():
                    retorno.append({'titulo': self.mangas['nome'][i],
                                    'link': self.mangas['link'][i]})
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
        p.atualizar('mangas', self._atualizar_lista)

    def _atualizar_lista(self):
        """."""
        if path.isfile(self.path + "PaginasMangas.json"):
            self.mangas = load(open(self.path + "PaginasMangas.json"))
            self.ids.rv.data = [{'titulo': self.mangas['nome'][i],
                                 'link': self.mangas['link'][i],
                                 'tituloBotao': 'Ver Capitulos',
                                 'tipo': 'manga'}
                                for i in range(len(self.mangas['nome']))]
