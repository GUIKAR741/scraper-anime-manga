"""."""
from kivy.uix.boxlayout import BoxLayout

from .popup import (PopupDownload,  # pylint: disable=relative-beyond-top-level
                    PopupProcura)
from kivy.properties import ObjectProperty  # pylint: disable=no-name-in-module


class Row(BoxLayout):
    """."""

    video = ObjectProperty()

    def procurar(self, titulo, link, rv):
        """."""
        if self.tipo == 'anime' or self.tipo == 'manga':
            pop = PopupProcura()
            pop.open()
            pop.procura(self.tipo, titulo, link, rv)
        elif self.tipo == 'episodio' or self.tipo == 'capitulo':
            pop = PopupDownload()
            pop.open()
            pop.baixar(self.tipo, link)
        elif self.tipo == 'video':
            pop = PopupDownload()
            pop.open()
            pop.baixar(self.tipo, self.video)
