"""."""
from .telaBase import Tela  # pylint: disable=relative-beyond-top-level
# from .popup import PopupDownload  # pylint: disable=relative-beyond-top-level


class Downloader(Tela):
    """."""

    def on_enter(self, *args, **kwargs):
        """."""
        super().on_enter(*args, **kwargs)
        # p = PopupDownload()
        # p.open()
        # p.baixar("https://www.superanimes.site/cartoon/a-formiga-atomica/51653")
