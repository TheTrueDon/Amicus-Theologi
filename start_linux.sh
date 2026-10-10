#!/usr/bin/env bash
# Amicus Theologi – lokal starten (Ubuntu/Linux)
set -euo pipefail
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null; then
  echo 'Python 3 fehlt. Bitte zuerst Python 3.10 oder neuer installieren.' >&2
  exit 1
fi
if ! python3 -c 'import sys; assert sys.version_info >= (3,10)' 2>/dev/null; then
  echo 'Amicus Theologi benötigt Python 3.10 oder neuer.' >&2
  exit 1
fi
if [[ ! -x .venv/bin/python ]]; then
  echo 'Erster Start: richte die lokale Programmumgebung ein …'
  if ! python3 -m venv .venv; then
    echo 'Konnte die Umgebung nicht erstellen. Unter Ubuntu hilft meistens: sudo apt install python3-venv' >&2
    exit 1
  fi
fi
if ! .venv/bin/python -c 'import fastapi,uvicorn,multipart' >/dev/null 2>&1; then
  echo 'Installiere benötigte Programmbausteine (nur beim ersten Start; Internet erforderlich) …'
  if ! .venv/bin/python -m pip install -r requirements.txt; then
    echo 'Installation fehlgeschlagen. Prüfe die Internetverbindung und starte erneut.' >&2
    exit 1
  fi
fi
.venv/bin/python - <<'PY'
import sqlite3
con=sqlite3.connect(':memory:')
try:
    con.execute('CREATE VIRTUAL TABLE test_fts USING fts5(text)')
except sqlite3.OperationalError:
    raise SystemExit('SQLite FTS5 fehlt. Bitte eine Python-Version mit SQLite FTS5 verwenden.')
finally:
    con.close()
PY
.venv/bin/python start.py
