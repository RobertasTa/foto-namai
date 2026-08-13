# -*- mode: python ; coding: utf-8 -*-
# FotoNamai.spec - onedir build (PLANAS sprendimas 15: exe + DLL salia,
# zip -> flesiukas; NE onefile). Leisti is repo saknies PROJEKTO venv'e:
#   .venv\Scripts\python.exe -m PyInstaller FotoNamai.spec
# (venv shim'ai luze - visada python -m PyInstaller; OKF_PyInstaller guard.)

a = Analysis(
    ['foto_namai\\main.py'],
    pathex=['foto_namai'],
    binaries=[],
    datas=[('foto_namai\\ikona.ico', '.'),
           ('foto_namai\\ikona_256.png', '.'),
           ('foto_namai\\zinynas_vietos.json', '.'),
           ('foto_namai\\README.txt', '.'),
           ('foto_namai\\README-en.txt', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PhotoHome',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['foto_namai\\ikona.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PhotoHome',
)
