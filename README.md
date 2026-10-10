# Amicus Theologi 0.4.1

**Neue Funktionen:** griechische/hebräische Wortannotation und Lemma-Konkordanz. Anleitung: [docs/MORPHOLOGIE.md](docs/MORPHOLOGIE.md).

# Amicus Theologi 0.4.1

**Offlinefähige Bibel-Studienumgebung** mit parallelen Textmodulen und indizierter Volltextsuche.

## Update von 0.2.1
1. Anwendung beenden; Datenbank sichern (siehe unten).
2. ZIP in einen neuen Ordner entpacken und normal starten.
3. Die ursprüngliche lokale Datenbank wird weiterbenutzt und beim Start automatisch um einen FTS5-Index sowie Trigger ergänzt. **Dies ist eine Datenbankschemaänderung.** Bestehende Verse/Module/Einstellungen bleiben erhalten.
4. Vor dem Update die Datei `amicus_theologi.sqlite3` aus dem Datenordner kopieren. Der Datenordner lässt sich über `/api/info` prüfen; standardmäßig unter Linux `~/.local/share/biblewoerks`, unter Windows `%LOCALAPPDATA%\Biblewoerks`. Die alten Ordnernamen bleiben aus Gründen der Abwärtskompatibilität vorerst bestehen.

## Suchbeispiele (nach Import der mitgelieferten Demomodule)
- `Anfang` – alle Verse mit diesem Wort
- `=im Anfang` – genaue Wortfolge
- `+Anfang Wort` – beide Wörter im Vers
- `?Anfang Wort` – mindestens eines der Wörter
- `Anfang*` – Wortanfang
- Buchfilter `Joh` und Modulauswahl zur Eingrenzung
- Klick auf einen Treffer öffnet das Kapitel und markiert den Vers.

**Hinweis:** Diese Befehle sind eine erste Amicus-Syntax, noch keine direkte BibleWorks-Suchsprachenkompatibilität. FTS5 sucht nach Wörtern, nicht nach beliebigen Zeichenfolgen. Für Morphologie sind annotierte Quellen nötig (Roadmap 0.4).

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

## Aktualisierung und bisherige Einstellungen

Das Programm behält den vorhandenen Datenordner aus 0.1/0.2 bei, um installierte Module und Einstellungen zu erhalten. Die Datenbankdatei heißt `amicus_theologi.sqlite3` (die vorherige README erwähnte hier irrtümlich `biblewoerks.sqlite3`).

- Linux: `${XDG_DATA_HOME:-~/.local/share}/biblewoerks/amicus_theologi.sqlite3`
- Windows: `%LOCALAPPDATA%\Biblewoerks\amicus_theologi.sqlite3`
- Eigenes Verzeichnis: über `AMICUS_THEOLOGI_DATA_DIR` (oder den älteren Alias `BIBLEWOERKS_DATA_DIR`).

**Datenbankänderung mit 0.4.1:** Die SQLite-Datenbank erhält einen Volltextindex (`verse_fts`) und drei Trigger. Bereits vorhandene Daten werden beim ersten Start in den Suchindex aufgenommen. Bitte vorher sichern. Ein Zurückwechseln auf 0.2 wird nach der Migration nicht als regulärer Downgrade unterstützt.

## Projektstruktur und Rechte

- `backend/` FastAPI, SQLite und Suchlogik
- `frontend/` HTML/CSS/JavaScript
- `modules/examples/` Mini-Demos (jeweils nur fünf Verse)
- `docs/` Architektur, Roadmap, Änderungen
- `tests/` automatische Tests

Vor einer öffentlichen Veröffentlichung ist die endgültige Open-Source-Lizenz festzulegen. Die Textrechte sind pro Modul zu prüfen.
