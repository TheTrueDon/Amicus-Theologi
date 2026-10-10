@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Erster Start: Python-Umgebung wird eingerichtet ...
    py -3 -m venv .venv || goto :error
)
".venv\Scripts\python.exe" -c "import fastapi,uvicorn,multipart,pysword" >nul 2>nul
if errorlevel 1 (
    echo Installiere benoetigte Pakete. Beim ersten Start ist Internet notwendig ...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :error
)
".venv\Scripts\python.exe" -c "import sys,sqlite3;assert sys.version_info >= (3,10);db=sqlite3.connect(':memory:');db.execute('CREATE VIRTUAL TABLE test_fts USING fts5(text)')" || goto :error
".venv\Scripts\python.exe" start.py
if errorlevel 1 goto :error
exit /b 0
:error
echo.
echo Amicus Theologi konnte nicht gestartet werden.
echo Erforderlich: Python 3.10+ mit SQLite FTS5. Weitere Hinweise: README.md
pause
exit /b 1
