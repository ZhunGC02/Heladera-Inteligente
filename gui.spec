# -*- mode: python ; coding: utf-8 -*-
import flet as ft
import os

flet_path = os.path.dirname(ft.__file__)

a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=[(flet_path, 'flet')],
    hiddenimports=['flet_desktop'],  # 👈 AGREGAMOS ESTA LÍNEA AQUÍ
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
    a.binaries,
    a.datas,
    [],
    name='HeladeraInteligente',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)