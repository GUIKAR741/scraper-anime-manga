"""."""
import kivy
from kivy.app import App
from controllers.downloader import Downloader  # pylint: disable=unused-import
from controllers.animes import Animes  # pylint: disable=unused-import
from controllers.mangas import Mangas  # pylint: disable=unused-import
from controllers.youtube import YouTube  # pylint: disable=unused-import
from controllers.gerenciadordetelas import GerenciadorDeTelas  # pylint: disable=unused-import
from controllers.row import Row  # pylint: disable=unused-import

kivy.require("1.11.0")


class Main(App):
    """Classe Principal do Aplicativo."""

    def build(self):
        """Construção do Aplicativo."""
        self.title = "Downloader"
        super().build()


Main().run()
