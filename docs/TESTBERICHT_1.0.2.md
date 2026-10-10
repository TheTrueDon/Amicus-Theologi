# Amicus Theologi 1.0.2 – Testbericht

## Funktionsprüfung
- 60 automatisierte Python-Tests bestanden, einschließlich neuer API- und Import-Regressionstests.
- Frontend-Syntax: `node --check frontend/app.js` und `node --check frontend/wordtools.js`.
- Browserkomponenten in Chromium über eine isolierte, nachgestellte Datenquelle geprüft: Hover-Vorschau, lesbarer Lexikontext und Lemma-Dialog; keine JavaScript-Laufzeitfehler.
- Ein Testlexikon enthielt absichtlich nicht vertrauenswürdige HTML-artige Markierung mit Script-Tag: Die Anzeige führte das Script nicht aus und zeigte lesbaren Text.

## Grenzen
- Der vollständige lokale App-Zugriff des Browsers ist in dieser Testumgebung netzwerkseitig gesperrt (`ERR_BLOCKED_BY_ADMINISTRATOR`), deshalb kein integrierter Live-End-to-End-Browsertest. Die API wurde separat getestet.
- Die Darstellung ist auf gängige Formatierungs-Tags ausgelegt, nicht auf eine verlustfreie Edition sämtlicher STEPBible-Sondermarkierungen. Originaldaten bleiben über den aufklappbaren Abschnitt zugänglich.
- Nicht jeder imported Morphologie-Code kann bereits in deutsche Kategorien übersetzt werden. Unbekannte Codes bleiben als Originalcodes erkennbar.
- Die tatsächlichen aktuellen Großarchive von STEPBible konnten in dieser Sitzung nicht neu heruntergeladen und end-to-end geprüft werden.
- Eine Windows-Installer-EXE muss wie bisher über den GitHub-Actions-Workflow erstellt und unter Windows erprobt werden.

## Migration
Keine zusätzlichen Datenbanktabellen und keine Datenmigration. Ein normales Update behält Module, Lexika, Projekte, Markierungen und Einstellungen bei.
