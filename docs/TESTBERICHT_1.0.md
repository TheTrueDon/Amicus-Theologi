# Testbericht – Amicus Theologi 1.0.0

**Prüfumgebung:** Linux-Container, Python 3.13, FastAPI, SQLite FTS5, Node.js. Datum: 10. Oktober 2026.

## Erfolgreich automatisiert geprüft

- **52 Python-Unittests** (einschließlich FastAPI TestClient-Integrationstests).
- Initiale SQLite-Struktur und Erhaltung bestehender Einstellungen.
- Import von Bibeltexten und Wortannotationen; Lemma-Abfrage und Volltextsuche.
- Import und Suche in Lexika; morphologische Abstands- und Kombinationssuche.
- Anlegen, Aktualisieren, Löschen und Export von Studienprojekten, Notizen, Markierungen.
- Ausgabenvergleich, Synopse und dokumentierte Lesarten.
- Testarchiv-Importer (STEPBible, Open Scriptures) mit kleinen lokal konstruierten Archivdateien.
- Offline-Mini-Beispielinstallation und erneuter Aufruf ohne Datenverdoppelung.
- Komplettbackup mit SHA256 und Wiederherstellung nach Änderung von persönlichen und fachlichen Daten.
- Sicherheitsprüfung manipulierten Backups und ZIP-Archiven mit unzulässigen Einträgen.
- Vorgemerkte Rücksicherung sperrt Änderungsoperationen und ist vor Neustart abbrechbar.
- DNS-Rebinding-Host-Validierung und Origin-Schutz bei schreibenden API-Aufrufen.
- Automatische Update-Sicherung wird nach Release-Marker nicht mehrfach erstellt.
- JavaScript-Syntax aller drei JS-Dateien; Python-Kompilierung; Shell-Syntax.
- HTTP-Smoke-Test mit eigenem Testdatenordner: HTML, drei JS-Dateien, CSS, API, Demo, Wortanalyse, Suche und ZIP-Sicherung.

## Noch nicht unabhängig abgeschlossen

- **Vollständige browserbasierte Grafiktests**: Die vorhandene Chromium-Umgebung blockierte den Aufruf lokaler Seiten durch Administratorrichtlinien. Ein manueller Test unter Ubuntu und Windows bleibt notwendig.
- Komplette Downloads und Importe der **aktuellen großen Originalarchive** von STEPBible, OSHB und CrossWire; die Tests verwenden kontrollierte kleinere Beispiele.
- Native signierte Windows- oder Linux-Binärinstaller; vorhanden sind startfähige Python-Skripte und eine optionale Linux-Menüverknüpfung.
- Prüfung theologischer Vollständigkeit, Variantenqualität und Vergleich mit einer funktionierenden BibleWorks-Installation.
- Lasttests mit mehrjährigen theologischen Forschungsbeständen und mehreren hunderttausend annotierten Wörtern auf schwacher Hardware.

Der Begriff **1.0.0** bezeichnet eine integrierte, testbare erste Anwendungsversion und **keine wissenschaftliche Vollständigkeitszusage**.
