# Amicus Theologi 1.0.3 – Testbericht

## Funktionsprüfung
- 65 automatisierte Python-Unittests bestanden: Lexikonkompatibilität, bereits installierte alte STEPBible-Tabellen, neue STEPBible-Header, korrekte Übersetzungsauswahl, sortierte/paginierte Lemma-Konkordanz und bisherige Programmfunktionen.
- Python-Module kompiliert; `node --check` für alle Anwendungs- und Hilfe-JavaScript-Dateien erfolgreich.
- HTTP-API für Preview und sortierte Lemma-Abfragen mit isolierten Testdaten erfolgreich geprüft.
- API schützt ungültige Sortierwerte durch strikte Eingabevalidierung.

## Grenzen
- Der vollständige Browser-Interaktionstest in Chromium konnte nicht abgeschlossen werden: sowohl der lokale HTTP-Zugriff als auch `file://` waren in der Testumgebung durch `ERR_BLOCKED_BY_ADMINISTRATOR` gesperrt. Die UI-Logik wurde statisch und über API-Tests geprüft, aber nicht vollständig grafisch verifiziert.
- Die aktuellen STEPBible-Großarchive wurden in dieser Entwicklungsumgebung nicht geladen. Die Rückwärtskompatibilität wurde gegen repräsentative Legacy-Daten getestet. Nicht identifizierbare Quellfelder werden nicht als Übersetzung ausgegeben.
- Das Windows-Setup wird im GitHub-Actions-Workflow auf Windows erzeugt; kein Windows-Installer wurde auf Linux kompiliert oder ausgeführt.

## Datenbank und Update
- Keine zusätzlichen Tabellen oder Schemaänderungen.
- Bereits importierte Lexika bleiben unverändert; korrigierte Kurzglossen werden beim Anzeigen aus gespeicherten Feldern gewonnen.
- Sämtliche bisherigen Nutzerdaten und Datensicherungen bleiben erhalten.
