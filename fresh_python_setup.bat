@echo off
echo ================================
echo CLEAN PYTHON ENVIRONMENT SETUP
echo ================================

echo Uninstalling all old Python versions...
wmic product where "name like '%%Python%%'" call uninstall /nointeractive

echo Deleting leftover Python folders...
rmdir /s /q "%LocalAppData%\Programs\Python"
rmdir /s /q "C:\Python27"
rmdir /s /q "C:\Python39"
rmdir /s /q "C:\Python310"
rmdir /s /q "C:\Python311"

echo Downloading Python 3.11.8 installer...
curl -o python-installer.exe https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe

echo Installing Python 3.11.8...
start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

echo Installing required libraries...
pip install aiogram==3.3.0 MetaTrader5 pillow pytesseract

echo =====================
echo Python setup complete!
echo You can now run: python bot.py
pause
