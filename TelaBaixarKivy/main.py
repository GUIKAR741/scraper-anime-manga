"""."""
import kivy
from kivy.app import App
from kivy.lang.builder import Builder

from controllers.animes import Animes  # pylint: disable=unused-import
from controllers.downloader import Downloader  # pylint: disable=unused-import
from controllers.gerenciadordetelas import (  # pylint: disable=unused-import
    GerenciadorDeTelas
)
from controllers.mangas import Mangas  # pylint: disable=unused-import
from controllers.row import Row  # pylint: disable=unused-import
from controllers.youtube import YouTube  # pylint: disable=unused-import
from os import path, environ, mkdir


kivy.require("1.11.0")


class DownloaderApp(App):
    """Classe Principal do Aplicativo."""

    def build(self):
        """Construção do Aplicativo."""
        self.title = "Downloader"
        self.icon = "res/download.png"
        return Builder.load_string(
            "#: include views/popup.kv\n"
            "#: include views/downloader.kv\n"
            "#: include views/row.kv\n"
            "#: include views/animes.kv\n"
            "#: include views/youtube.kv\n"
            "#: include views/mangas.kv\n"
            "#: include views/gerenciadordetelas.kv\n"
            "GerenciadorDeTelas:"
            )


if __name__ == "__main__":
    app = DownloaderApp()
    app.pathDown = path.join(path.join(environ['HOME'], "Downloads"), 'Downloader')\
                       .replace('\\', '/')
    if not path.isdir(app.pathDown):
        mkdir(app.pathDown)
    app.run()
