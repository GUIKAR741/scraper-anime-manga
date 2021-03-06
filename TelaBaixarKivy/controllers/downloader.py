"""."""
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.properties import StringProperty  # pylint: disable=no-name-in-module

from .telaBase import Tela  # pylint: disable=relative-beyond-top-level
from .popup import PopupFile  # pylint: disable=relative-beyond-top-level


class Downloader(Tela):
    """."""

    path = StringProperty('')

    def on_enter(self, *args, **kwargs):
        """."""
        super().on_enter(*args, **kwargs)
        self.path = App.get_running_app().pathDown

    def on_pre_enter(self, *args, **kwargs):
        """Executa antes de Entrar na Tela."""
        super().on_pre_enter(*args, **kwargs)
        Window.bind(on_request_close=self.confirmacao)

    def confirmacao(self, *args, **kwargs):
        """Popup de Confirmação de Saida."""
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        botoes = BoxLayout(padding=10, spacing=10)

        pop = Popup(title='Deseja mesmo sair?', content=box, size_hint=(None, None),
                    size=(300, 130))

        sim = Button(text='Sim', on_release=App.get_running_app().stop)
        nao = Button(text='Não', on_release=pop.dismiss)

        botoes.add_widget(sim)
        botoes.add_widget(nao)

        box.add_widget(botoes)

        pop.open()
        return True

    def procurar(self):
        """."""
        p = PopupFile()
        p._att_down(self._att_path)
        p.open()

    def _att_path(self, path):
        """."""
        self.path = path
