# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

datas = [
    ('templates', 'templates'),
    ('static/css', 'static/css'),
    ('static/icons', 'static/icons'),
    ('static/favicon.png', 'static'),
    ('config.example.yaml', '.'),
]

a = Analysis(
    ['desktop.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'webview.platforms.winforms',
        'clr',
        'pythonnet',
        'ujson',
        'yaml',
        'PIL',
        'PIL.Image',
        'requests',
        'flask',
        'jinja2',
        'werkzeug',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'gi', 'gi.repository', 'gtk', 'Gtk',
        'torch', 'torchvision', 'torchaudio', 'tensorflow', 'scipy',
        'matplotlib', 'pandas', 'numpy', 'pygame', 'PyQt5', 'PyQt6',
        'PySide6', 'PySide2', 'cv2', 'sklearn', 'tkinter', 'IPython',
        'jupyter', 'notebook'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ROMCat',
    icon='icon.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
)
