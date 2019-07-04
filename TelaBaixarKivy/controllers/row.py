"""."""
from kivy.uix.boxlayout import BoxLayout

from .popup import (PopupDownload,  # pylint: disable=relative-beyond-top-level
                    PopupProcura)


class Row(BoxLayout):
    """."""

    def procurar(self, titulo, link, rv):
        """."""
        if self.tipo == 'anime':
            pop = PopupProcura()
            pop.open()
            pop.procura(titulo, link, rv)
        else:
            pop = PopupDownload()
            pop.open()
            pop.baixar(link)
