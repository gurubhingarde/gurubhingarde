@echo off
REM Clean-room build for a lightweight JSW_FlashXpert.exe.
REM Run this from a plain "Windows" terminal (not an Anaconda prompt),
REM inside this folder, with a system Python 3.10+ installed.

setlocal

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist .venv rmdir /s /q .venv

py -3 -m venv .venv
call .venv\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r requirements.txt

pyinstaller --clean --noconfirm jsw_flashxpert.spec

echo.
echo Build finished. Exe is at dist\JSW_FlashXpert.exe
dir dist\JSW_FlashXpert.exe

endlocal
