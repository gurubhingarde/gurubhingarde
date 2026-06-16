@echo off
title JSW Pump Monitor - Build EXE
color 1F
echo.
echo ============================================================
echo   JSW Pump Monitor - PyInstaller Build Script
echo ============================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found.
    pause & exit /b 1
)

pip install --upgrade pyinstaller python-can intelhex >nul 2>&1
echo [OK] Packages ready.

if exist build_monitor   rmdir /s /q build_monitor
if exist dist_monitor    rmdir /s /q dist_monitor

pyinstaller ^
    --onefile ^
    --noconsole ^
    --name "JSW_PumpMonitor" ^
    --distpath dist_monitor ^
    --workpath build_monitor ^
    --hidden-import PCANBasic ^
    --hidden-import can ^
    --hidden-import can.interfaces.pcan ^
    --hidden-import can.interfaces.vector ^
    --hidden-import can.interfaces.kvaser ^
    --hidden-import tkinter ^
    --hidden-import tkinter.ttk ^
    --hidden-import struct ^
    --collect-all can ^
    pump_monitor_gui.py

if errorlevel 1 (
    echo [ERROR] Build FAILED.
    pause & exit /b 1
)

set PCAN_DLL=C:\Program Files\PEAK-System\PCAN-Basic API\Win32\PCANBasic.dll
if exist "%PCAN_DLL%" (
    copy "%PCAN_DLL%" dist_monitor\ >nul
    echo [OK] PCANBasic.dll copied.
)

echo.
echo [DONE]  dist_monitor\JSW_PumpMonitor.exe
echo.
pause
explorer dist_monitor
