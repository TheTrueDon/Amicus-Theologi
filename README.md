# Amicus Theologi 0.2.1

Eine freie, offlinefähige Studienumgebung für wissenschaftliche Bibelarbeit. **Frühe Entwicklungsfassung:** die wissenschaftliche Suche (0.3), Morphologie (0.4) und komplette Textbibliothek sind noch nicht enthalten.

## Start

- **Windows:** `start_windows.bat` doppelklicken.
- **Ubuntu/Linux:** Terminal im Verzeichnis öffnen, `bash start_linux.sh` ausführen.
- **Alternative:** `python -m venv .venv`, virtuelle Umgebung aktivieren, `pip install -r requirements.txt`, dann `python start.py`.
- Python **3.10+** erforderlich. Beim ersten Start Internet für Python-Pakete; die eigentliche Anwendung funktioniert danach offline.
- Das Programm lauscht ausschließlich auf `127.0.0.1` und öffnet einen Browser. Mit Strg+C beenden.

## Was neu ist

1. Echte Kapitelanzeige aus installierten Textmodulen (kein Fake-Vorschautext).
2. Bibelstellennavigation mit `Joh 1,1`, `Gen 1`, Buchauswahl sowie Pfeilen zwischen vorhandenen Kapiteln.
3. Parallelanzeige mehrerer Ausgaben samt synchroner Versmarkierung.
4. Modulmanager zum Hinzufügen und Entfernen von UTF-8-CSV/TSV-Bibelausgaben mit Metadaten (Lizenz, Herkunft, Edition).
5. Dauerhafte Übernahme der alten 0.1-Einstellungen und Texte aus derselben Datenbank.
6. Sämtliche sichtbaren Namen wurden zu **Amicus Theologi** geändert.

## So probierst du zwei Texte parallel aus

Klicke **Textmodule**, wähle die Demo-TSV-Datei aus und prüfe die automatisch eingetragenen Angaben. Importiere zunächst `modules/examples/johannes_demo_de.tsv`, ID `joh-demo-de`, Titel `Luther 1912 – Johannes 1,1–5 (Demonstration)`, Sprache `de`, Lizenz `Public Domain (historischer Text; Provenienz selbst prüfen)`, Quelle `Kurzer Demonstrationsauszug nach Luther 1912`.

Importiere anschließend `modules/examples/johannes_demo_la.tsv`, ID `joh-demo-la`, Titel `Vulgata – Johannes 1,1–5 (Demonstration)`, Sprache `la`, Lizenz `Public Domain (historischer Text; Provenienz selbst prüfen)`, Quelle `Kurzer Demonstrationsauszug aus lateinischer Vulgata`.

Rufe `Joh 1,1` auf. Klicke Vers 3: beide Ausgaben markieren Vers 3.

**Wichtig:** Die zwei mitgelieferten Dateien enthalten jeweils nur **fünf Verse**, keine vollständige Edition. Sie dienen zur Erprobung des Imports und sind keine wissenschaftlich kollationierten Referenztexte. Für echte Forschungsarbeit bitte überprüfte Volltexteditionen mit Editions- und Lizenznachweis importieren.

## Texte importieren

- Datei muss UTF-8 sein, CSV oder TSV mit Kopfzeile `book,chapter,verse,text`.
- Beispiel: `Joh,1,1,"Im Anfang ..."`.
- Bibelbuchnamen und Kurzformen werden vereinheitlicht (z. B. `1 Mose` → `Gen`). Unterstützt sind derzeit die 66 üblichen Buchkennungen; deuterokanonische Erweiterungen stehen auf der Roadmap.
- Alle Zeilen werden vor dem Schreiben validiert und als ein Modul gespeichert. Doppelte Referenzen, unbekannte Bücher und unvollständige Zeilen werden zurückgewiesen.
- Maximal 12 MB und 200.000 Verse pro Modul.
- **Keine automatische Rechteprüfung:** die importierende Person verantwortet die Zulässigkeit der Texte.
- Import ist lokal und benötigt keinen Internetzugriff.

## Aktualisierung von 0.1

1. Backup empfohlen: die Datendatei `biblewoerks.sqlite3` im bisherigen 0.1-Datenordner sichern.
2. 0.1 beenden, 0.2 in einen **neuen** Programmordner entpacken, starten.
3. Die App nutzt absichtlich weiterhin den alten 0.1-Datenpfad, damit die Einstellungen übernommen werden:
   - Linux: `${XDG_DATA_HOME:-~/.local/share}/biblewoerks/biblewoerks.sqlite3`
   - Windows: `%LOCALAPPDATA%\Biblewoerks\biblewoerks.sqlite3`
   - Benutzerdefiniert: `AMICUS_THEOLOGI_DATA_DIR` oder weiterhin `BIBLEWOERKS_DATA_DIR`.
4. **Keine notwendige Änderung des vorhandenen Datenbankschemas!** Das vorhandene `modules`/`verses`-Schema aus 0.1 wird erstmals produktiv verwendet.
5. Die alten Datenverzeichnisse und der alte Datenbank-Dateiname bleiben aus Gründen der Updatekompatibilität vorerst erhalten. Im Programmnamen ist der alte Name vollständig entfernt.

## Projekt

- `backend/` FastAPI und SQLite-Datenhaltung
- `frontend/` HTML, CSS und Vanilla JavaScript
- `modules/examples/` kleine Beispieldateien zum manuellen Import
- `docs/` Roadmap und Architektur
- `tests/` automatisierte Backendtests

Das Projekt ist noch nicht unter einer endgültigen Open-Source-Lizenz veröffentlicht. Vor dem öffentlichen Verteilen oder Einbinden fremder Inhalte bitte eine Lizenz wählen und die Textrechte prüfen.

## Fehlerbehebung in 0.2.1

Die Modulauswahl erkennt die beiden mitgelieferten Johannes-Demodateien und füllt ID, Titel, Sprache, Lizenzhinweis und Herkunft im Importformular automatisch aus. Bei anderen CSV-/TSV-Dateien werden nur die Modul-ID und der Titel vorgeschlagen; Lizenz und Herkunft müssen weiterhin bewusst ergänzt werden. Du kannst sämtliche Angaben manuell ändern. Die Datenbankstruktur bleibt gegenüber 0.2.0 unverändert.
