# -*- mode: python -*-

block_cipher = None

data = [
    ('views/*', 'views'),
    ('res/*', 'res'),
]
tree = [
    # Tree('/home/guilherme/anaconda3/envs/kivyenv/lib/'),
    Tree('/home/guilherme/anaconda3/envs/kivyenv/include'),
    # Tree('/home/guilherme/anaconda3/envs/kivyenv/include/gstreamer-1.0'),
    # Tree('/home/guilherme/anaconda3/envs/kivyenv/include/glib-2.0')
]
a = Analysis(['main.py'],
             pathex=['/mnt/8A5492C05492AF07/Programação/Python/scraper/TelaBaixarKivy'],
             binaries=[],
             datas=data,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Downloader',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               *tree,
               strip=False,
               upx=True,
               name='Downloader')
