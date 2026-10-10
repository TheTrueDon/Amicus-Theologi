# Biblewörks · Version 0.1.0

**Freies, offlinefähiges Bibelwissenschafts-Werkzeug im Aufbau.** Entwicklungsstand: Grundlage und Bedienoberfläche, **keine vollständige Exegesesoftware**.

## Schnellstart

Voraussetzung: Python **3.10 oder neuer** und einmaliger Internetzugang zur Installation der Python-Abhängigkeiten. Danach läuft die Anwendung vollständig lokal.

**Windows:** `start_windows.bat` doppelklicken (Python muss installiert sein; `py`-Launcher empfohlen).

**Linux:** `bash start_linux.sh` (Paket `python3-venv` muss ggf. installiert werden).

**Manuell, Windows/Linux/macOS:**

```bash
python -m venv .venv
# Linux/macOS:
.venv/bin/pip install -r requirements.txt
.venv/bin/python start.py
# Windows:
# .venv\Scripts\python.exe -m pip install -r requirements.txt
# .venv\Scripts\python.exe start.py
```

Ein Browserfenster wird automatisch geöffnet. Falls dies fehlschlägt, die im Terminal angezeigte lokale Adresse öffnen. **Zum Beenden Strg+C im Terminal.**

## Lieferumfang 0.1

- FastAPI-Backend und responsive HTML/CSS/JS-Oberfläche mit drei Bereichen (Suche / Text / Analyse)
- Verschiebbare Trennlinien (auf großen Bildschirmen), Light/Dark Theme, Schriftgröße, Textvorschau-Schalter
- Lokale SQLite-Datenbank mit Platzhaltern für Module, Verse, Token, Versmapping; persistente Einstellungen
- Lokale API zur Konfiguration, Modulauflistung, Nachschlagen gespeicherter Verse
- Explizit gekennzeichnete **illustrierende Vorschautexte**; **keine Bibelmodule mitgeliefert**

## Nicht enthalten

Keine Volltext-Suchmaschine, kein Import-UI, keine vollständigen Texteditionen, keine echte morphologische Analyse, noch kein Desktop-Installer. Die Module- und Vers-API ist eine technische Vorstufe; Installation und Datenbefüllung werden mit 0.2 gebaut. Die Versreferenz wird momentan nur als Arbeitsposition gespeichert; sie lädt noch keine anderen Verse in der Oberfläche.

## Speicherung und Sicherheit

Nutzerdaten: unter Linux `~/.local/share/biblewoerks/biblewoerks.sqlite3`, Windows `%LOCALAPPDATA%\Biblewoerks\biblewoerks.sqlite3`. Alternativ `BIBLEWOERKS_DATA_DIR` definieren. Der Server bindet **nur an 127.0.0.1**, ohne Anmeldung; **niemals öffentlich ins Internet weiterleiten**. Eine Sicherung der SQLite-Datei nur bei beendetem Programm anlegen.

## Entwicklung

Architektur und Roadmap: `docs/`. Tests mit `python -m unittest discover -s tests`. Quellcode: `backend/`, `frontend/`. Modulregeln: `modules/README.md`.

Git-Repository-Name empfohlen: `biblewoerks`; öffentlicher Projektname: **Biblewörks**. Lizenzentscheidung ausstehend: Noch **keine** generelle Open-Source-Lizenz gewährt. Vor öffentlicher Zusammenarbeit eine Lizenz auswählen (z. B. GPL-3.0-or-later).
