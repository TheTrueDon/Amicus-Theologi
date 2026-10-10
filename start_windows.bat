@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" ( py -3 -m venv .venv || goto :error )
".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :error
".venv\Scripts\python.exe" start.py
pause
exit /b 0
:error
echo Fehler: Python 3.10 oder neuer erforderlich.
pause
