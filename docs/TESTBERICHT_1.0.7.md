# Testbericht: Amicus Theologi 1.0.7

## Durchgeführt

- 81 automatische Unit-/API-/Regressionstests: erfolgreich (vorher 77, neu 4).
- Python-Syntax: erfolgreich (compileall).
- JavaScript-Syntax (`frontend/app.js`, `frontend/wordtools.js`, `frontend/editions.js`): erfolgreich.
- Isolierter Chromium-Test der hebräischen Wortvorschau: erfolgreich. Die Wortform `בָּרָא` zeigt hebräische Grundform `ברא`, die englische Bedeutung „create, make“ und verständliche Angaben „Verb · Qal · Perfekt“.
- Archivstruktur des Quellcode-ZIPs: erfolgreich geprüft.

## Grenzen

Ein Ende-zu-Ende-Test über den lokalen HTTP-Server im Chromium-Browser war in dieser Umgebung blockiert (`ERR_BLOCKED_BY_ADMINISTRATOR`). Die tatsächlichen vollständigen aktuellen STEPBible-Originalarchive und die spätere Windows-Setup-EXE wurden hier nicht erneut getestet.

## Datenbank

Keine Datenbankmigration. Testinstanzen wurden mit separaten, temporären Datenbanken betrieben.
