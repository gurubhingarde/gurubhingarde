# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['nexaboot_tester.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['can', 'isotp', 'Crypto.Cipher.AES', 'Crypto.Util.Counter', 'can.interfaces.pcan', 'can.interfaces.socketcan', 'can.interfaces.kvaser', 'can.interfaces.vector', 'can.interfaces.virtual'],
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
    name='NexaBootTester',
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
