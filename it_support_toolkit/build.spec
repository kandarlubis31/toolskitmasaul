# -*- mode: python ; coding: utf-8 -*-
#
# IT Support Toolkit — PyInstaller build spec
# 1-file EXE with UPX compression, admin manifest, dark/light themes.

import os

block_cipher = None

# ── Hidden imports ────────────────────────────────────
# PyInstaller can't detect lazy imports inside try/except blocks,
# so we declare them here explicitly.

hidden_imports = [
    # pywin32
    'win32api', 'win32con', 'win32service', 'win32serviceutil',
    'win32evtlog', 'win32com', 'pythoncom', 'win32com.client',
    # stdlib
    'ctypes', 'socket', 'subprocess', 'shutil', 'json',
    'logging', 'csv', 'winreg',
    # third-party
    'psutil',
]

# ── Data files ────────────────────────────────────────
# QSS theme files and icon bundled into the EXE.

datas = [
    ('ui/styles.qss', 'ui'),
    ('ui/styles_light.qss', 'ui'),
]

icon_path = 'assets/icon.ico'
if os.path.exists(icon_path):
    datas.append((icon_path, 'assets'))

# ── Analysis ──────────────────────────────────────────

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Unnecessary Qt modules — saves ~10 MB
        'PyQt6.QtBluetooth', 'PyQt6.Qt3D*', 'PyQt6.QtQuick*',
        'PyQt6.QtMultimedia*', 'PyQt6.QtXml*', 'PyQt6.QtSql',
        'PyQt6.QtSvg*', 'PyQt6.QtQml*', 'PyQt6.QtTest',
        'PyQt6.QtWebEngine*', 'PyQt6.QtWebChannel*',
        'PyQt6.QtPositioning', 'PyQt6.QtLocation',
        'PyQt6.QtSensors', 'PyQt6.QtSerialPort',
        'PyQt6.QtNetwork*', 'PyQt6.QtDBus',
        'PyQt6.QtPrintSupport', 'PyQt6.QtQuickWidgets',
        # Unnecessary tkinter
        'tkinter',
        # Unnecessary matplotlib / numpy (not used)
        'matplotlib', 'numpy',
        # Unnecessary pywin32 modules
        'win32clipboard', 'win32print', 'win32file',
        'win32pipe', 'win32process', 'win32security',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ── Single-file EXE ───────────────────────────────────
# No COLLECT — everything goes into one .exe for portability.

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,           # DLLs and compiled extensions
    a.zipfiles,
    a.datas,              # Themes + icon
    [],
    name='ITSupportToolkit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        'api-ms-win-*.dll',
        'ext-ms-win-*.dll',
    ],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
    icon=icon_path if os.path.exists(icon_path) else None,
)
