# -*- mode: python ; coding: utf-8 -*-
#
# Minimal PyInstaller spec for JSW FlashXpert.
#
# The app only imports stdlib modules (tkinter, ctypes, threading, subprocess,
# zlib, os, sys, traceback) plus the small pure-Python "intelhex" package.
# PCANBasic.dll itself is loaded at runtime via ctypes and is NOT bundled - it
# must already be installed on the target machine (PEAK PCAN driver package).
#
# A build from a clean venv (see README.md) should produce an exe in the
# 15-25 MB range. If your exe is much bigger than that, PyInstaller is
# almost certainly picking up unrelated packages (numpy/pandas/matplotlib/
# PyQt/etc.) from a non-isolated interpreter - use a fresh venv, not your
# system/Anaconda Python.

EXCLUDES = [
    # Heavy scientific / GUI / notebook stacks that have no reason to be
    # imported by this app; excluding them is a safety net in case a
    # non-clean environment pulls one in as a transitive/hidden import.
    "numpy", "pandas", "matplotlib", "scipy",
    "PIL", "Pillow",
    "PyQt5", "PyQt6", "PySide2", "PySide6", "wx",
    "IPython", "jupyter", "notebook", "nbconvert", "nbformat",
    "pytest", "nose",
    "torch", "tensorflow", "sklearn", "cv2",
    "lxml", "docutils", "babel", "jedi",
    "setuptools", "pip", "wheel",
]

a = Analysis(
    ["jsw_gui.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("favicon.ico", "."),
        ("Group_Logo.png", "."),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=EXCLUDES,
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
    name="JSW_FlashXpert",
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
    icon="favicon.ico",
)
