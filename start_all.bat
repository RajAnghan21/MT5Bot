@echo off
echo Installing MetaTrader 5...
start "" "exness5setup.exe"
timeout /t 15 > nul
echo Launching MetaTrader 5...
start "" "C:\Program Files\MetaTrader 5\terminal64.exe"
timeout /t 10 > nul
echo Installing Python libraries...
cd /d "%~dp0"
pip install -r requirements.txt
python bot.py
pause
