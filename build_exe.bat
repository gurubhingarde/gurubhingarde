@echo off
title JSW FlashXpert - Build EXE
color 1F
echo.
echo ============================================================
echo   JSW FlashXpert - PyInstaller Build Script
echo   Builds a portable single-file EXE for Windows
echo ============================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+ and add to PATH.
    pause
    exit /b 1
)
echo [OK] Python found:
python --version

echo.
echo [1/4] Installing / upgrading required packages...
pip install --upgrade pyinstaller python-can intelhex can-isotp >nul 2>&1
echo [OK] Packages ready.

echo.
echo [2/4] Cleaning previous build...
if exist build   rmdir /s /q build
if exist dist    rmdir /s /q dist
if exist jsw_gui.spec del /q jsw_gui.spec
echo [OK] Clean done.

echo.
echo [3/4] Building EXE with PyInstaller...

:: Check if logo exists
set LOGO_ARG=
if exist Group_Logo.png (
    set LOGO_ARG=--add-data "Group_Logo.png;."
    echo [INFO] Logo file found - will be bundled.
) else (
    echo [WARN] Group_Logo.png not found - EXE will show placeholder.
)

pyinstaller ^
    --onefile ^
    --noconsole ^
    --name "JSW_FlashXpert" ^
    --icon NONE ^
    %LOGO_ARG% ^
    --hidden-import PCANBasic ^
    --hidden-import can ^
    --hidden-import can.interfaces.pcan ^
    --hidden-import can.interfaces.vector ^
    --hidden-import can.interfaces.kvaser ^
    --hidden-import isotp ^
    --hidden-import intelhex ^
    --hidden-import tkinter ^
    --hidden-import tkinter.ttk ^
    --hidden-import tkinter.filedialog ^
    --hidden-import tkinter.messagebox ^
    --hidden-import threading ^
    --hidden-import queue ^
    --hidden-import zlib ^
    --hidden-import struct ^
    --hidden-import ctypes ^
    --collect-all can ^
    jsw_gui.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build FAILED. Check the output above for errors.
    pause
    exit /b 1
)

echo.
echo [4/4] Done!
echo.
echo ============================================================
echo   EXE created:  dist\JSW_FlashXpert.exe
echo.
echo   IMPORTANT - The EXE needs these on the target machine:
echo     - PEAK PCAN driver installed  (for Peak hardware)
echo     - PCANBasic.dll  in PATH or same folder as EXE
echo       (copy from: C:\Program Files\PEAK-System\PCAN-Basic API\)
echo ============================================================
echo.

:: Copy PCANBasic.dll if found
set PCAN_DLL=C:\Program Files\PEAK-System\PCAN-Basic API\Win32\PCANBasic.dll
if exist "%PCAN_DLL%" (
    echo [INFO] Copying PCANBasic.dll to dist folder...
    copy "%PCAN_DLL%" dist\ >nul
    echo [OK] PCANBasic.dll copied.
) else (
    echo [WARN] PCANBasic.dll not found at default path.
    echo        Copy it manually to the dist folder if needed.
)

echo.
echo Press any key to open the dist folder...
pause >nul
explorer dist
