# Version 1.0.0 – Qualität und Veröffentlichung

## Release-Ziel

Eine aus der bisherigen Roadmap integrierte, lokal installierbare Anwendung mit überprüfbarer Datenhaltbarkeit und für Nichttechniker verständlichem Einstieg. **Keine vollständige BibleWorks-Kompatibilität** und keine Aussage, dass alle wissenschaftlichen Upstream-Korpora bereits vollständig geprüft wurden.

## Sicherheitskonzept der Sicherungen

Die lokale Datenbank wird zunächst über `sqlite3.Connection.backup()` in einen unabhängigen konsistenten Snapshot kopiert, dann zusammen mit einem SHA256/Versions-Manifest als ZIP ausgegeben. Für die Rücksicherung werden genau `manifest.json` und `database.sqlite3` akzeptiert. Dateigrößen, Prüfsumme, SQLite-Integrität, Foreign-Key-Konsistenz und erforderliche Amicus-Tabellen werden überprüft.

Eine hochgeladene geprüfte Datenbank wird als `restore-pending.sqlite3` hinterlegt, **ohne die laufende Datenbank zu überschreiben**. Während dieses Zustands beantwortet der Server keine normalen Schreibabfragen mehr. Über „Vorgemerkte Wiederherstellung abbrechen“ lässt sich der Vorgang vor dem Neustart zurücknehmen. Beim folgenden Neustart erstellt er eine automatische Vor-Wiederherstellungs-Sicherung und aktiviert dann atomar das zurückgesicherte SQLite-Abbild.

Am Ende des ersten Starts mit 1.0 auf einem älteren Datenbestand wird ein Release-Marker gesetzt. Davor wird einmalig eine automatische Vollsicherung erstellt. `BIBLEWOERKS_DATA_DIR` und der historische Datenpfad bleiben aus Gründen der Datenkompatibilität bestehen. Die 1.0-Erweiterung braucht **keine neue Datenbanktabelle**.

## Tests

Die Test-Suite beinhaltet Kern-APIs, Bibeltexte, Suche, Morphologie, Wörterbücher, wissenschaftliche Importadapter an Testarchiven, Projekte, Varianten sowie neue Sicherungs-/Wiederherstellungs- und Sicherheitsfälle. Browserbasierte visuelle Tests sind für die externe Abnahme vorgesehen.

## Grenzen

- Python-Startskripte, **kein** signierter Windows-EXE- oder macOS-Build.
- Automatisch installierte Onlinekorpora sind nicht durch eine vollständige unabhängige Originaldatenprüfung abgesichert.
- Die Backup-ZIP enthält die lokale SQLite-Datenbank; Browser-localStorage-Verlauf ist nicht enthalten.
- Nur lokaler Einzelplatzbetrieb; kein sicherer öffentlicher Serverbetrieb.
- Keine vollständigen urheberrechtlich geschützten wissenschaftlichen Referenzeditionen im Lieferumfang.
