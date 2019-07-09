#!/bin/sh

rm ./appimagetool-x86_64.AppImage

wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

export ARCH=x86_64

./appimagetool-x86_64.AppImage dist Downloader.AppImage
