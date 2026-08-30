# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

datas = [
    ('/home/jmc/Source/romcat/templates', 'templates'),
    ('/home/jmc/Source/romcat/static/css', 'static/css'),
    ('/home/jmc/Source/romcat/static/icons', 'static/icons'),
    ('/home/jmc/Source/romcat/static/favicon.png', 'static'),
    ('/home/jmc/Source/romcat/config.example.yaml', '.'),
]

a = Analysis(
    ['desktop.py'],
    pathex=['/home/jmc/Source/romcat'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'ujson',
        'yaml',
        'webview',
        'PIL',
        'PIL.Image',
        'requests',
        'gi',
        'gi.repository.Gtk',
        'gi.repository.WebKit2',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch', 'torchvision', 'torchaudio', 'tensorflow', 'scipy',
        'matplotlib', 'pandas', 'numpy', 'pygame', 'PyQt5', 'PyQt6',
        'PySide6', 'PySide2', 'cv2', 'sklearn', 'tkinter', 'IPython',
        'jupyter', 'notebook', 'sqlite3', '_sqlite3', 'unittest',
        'pydoc', 'doctest', 'test', 'pdb', 'curses', 'xmlrpc',
        'multiprocessing.test'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Strip out unnecessary OS icon themes/locales/fonts
a.datas = [
    d for d in a.datas
    if not (
        d[1].startswith('/usr/share/icons')
        or d[1].startswith('/usr/share/locale')
        or d[1].startswith('/usr/share/fonts')
        or d[1].startswith('/usr/share/doc')
    )
]

# Exclude unnecessary heavy shared libraries
excluded_bin_patterns = (
    'libsqlite3',
    'libxml2',
    'libsystemd',
    'libreadline',
    'libtinfo',
    'libdbus',
    'fips.so',
)
a.binaries = [
    b for b in a.binaries
    if not any(p in b[0] for p in excluded_bin_patterns)
]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ROMCat',
    icon='/home/jmc/Source/romcat/static/favicon.png',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[
        'libgnutls.so.30',
        'libgmp.so.10',
        'libhogweed.so.6',
        'libnettle.so.8',
        'libcrypto.so.3',
        'libssl.so.3'
    ],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
)
