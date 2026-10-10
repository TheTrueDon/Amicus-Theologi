## 1.0.1 – Benutzerhandbuch & Windows-Installationsprojekt (10.10.2026)
- Ausführliches, offline lesbares HTML/JavaScript-Handbuch mit Suche und Praxisbeispielen. F1 / Handbuch öffnet die Anleitung.
- Eigenes Anwendungssymbol als ICO/PNG/SVG, auch im Browser.
- Windows-Desktoplauncher mit lokaler Serversteuerung und eigenem Beenden-Knopf.
- PyInstaller-Build mit gebündelter Python-Laufzeit; echter Inno-Setup-Assistent mit Startmenü-, optionalem Desktop-Eintrag und Deinstallation.
- Automatisierter Windows-Build inklusive Self-Test über GitHub Actions. Die fertig kompilierte Windows-EXE entsteht bei diesem Build, nicht hier im Linux-Quellpaket.
- Keine Datenbankmigration; vorhandene Notizen, Wörterbücher und Bibeltexte bleiben unverändert.

## 0.9.0 – Bedienung und Arbeitsabläufe
- Befehlssuche per Strg+K/Cmd+K und Schaltfläche in der Kopfzeile.
- Tastenkürzel für Bibelstellennavigation, Suche, Kapitel, Studienprojekte und Bereichsfokus.
- Verlauf mit Vorwärts-/Zurücknavigation sowie lokal gespeicherte Liste zuletzt besuchter Bibelstellen.
- Hilfe und eigene Kurzreferenz zu den Tastenkombinationen.
- Keine Änderung am Datenbankschema. Die kleine Besuchsliste wird im Browser-localStorage abgelegt.
- Browser-Titel weiterhin nur „Amicus Theologi“.
- Die genannten Befehle sind Amicus-Funktionen; keine vollständige BibleWorks-Befehlskompatibilität.

## 0.6.3
- Klick-Katalog mit STEPBible TBESG, TBESH, TFLSJ, TAGNT, TAHOT und Open Scriptures.
- Transaktionaler Werksreset mit doppelter Bestätigung.
- Browser-Titel ohne Versionsnummer.
- Keine neue Datenbanktabelle; Module und Lexika weiterhin getrennt.
- STEPBible-Lexikontabellen-Import in Praxistests mit aktuellen Originaldateien noch zu validieren.

## 0.6.2
- STEPBible-Archivprüfung auf ausgewähltes TAGNT/TAHOT-Korpus eingegrenzt.
- Sicherheitsgrenzen für ausgewählte Dateien erhalten.
- Regressionstests gegen zu viele fremde Dateien ergänzt.
- Keine Datenbankmigration.

## 0.6.1
- Wissenschaftlicher Importassistent: STEPBible (TAGNT/experimentell TAHOT), Open Scriptures OSHB, CrossWire SWORD (pysword optional).
- Downloads nur auf Nutzeranforderung, ZIP-Upload, Lizenz- und Quellenangaben, Transaktionsimport.
- Keine Datenbankschemamigration.

# Änderungen

## 0.6.0 – Erweiterte morphologische Suche
- Suche nach Lemma, Wortform, Strong und Teiltext im Morphologiefeld.
- Zwei Bedingungen mit maximalem Wortabstand und Reihenfolge innerhalb eines Verses.
- Eigene Suchmaske und API `/api/search/advanced`.
- Keine Datenbankmigration notwendig; alte Daten bleiben erhalten.
- Quellenrecherche und Datenimport-Plan in `docs/DATENQUELLEN.md`.

# Änderungsprotokoll

## 0.5.0 – Lexika und Wörterbücher
- Eigenständige, lokale Lexikonmodule mit Angabe von Herkunft und Lizenz.
- CSV-/TSV-Import mit Prüfungen und atomarer Übernahme.
- Wörterbucheinträge in der Analyseleiste nach Wortklick, verknüpft über Lemma und/oder Strong-ID.
- Griechische und hebräische Mini-Demolexika zur Erprobung.
- Lexika auflisten und entfernen; neue API-Endpunkte unter `/api/lexica` und `/api/lexicon/lookup`.
- Datenbankmigration: zusätzliche Tabellen und Indizes, keine Datenlöschung.

## 0.4.1 – Hebräische Texte
- Hinweis bei fehlenden Wortannotationen und rechts-nach-links-Darstellung.

## 0.4.0 – Morphologie
- Wortannotationsimport für Griechisch und Hebräisch, Lemma-Konkordanz.

## 0.3.0 – Suche
- FTS5-Volltextindex und Suchfilter.

## 0.7.0
- Versnotizen, ausgabenübergreifende Farbmarkierungen und exegetische Studienprojekte mit lokalem JSON-Export.
- Deutsche Erklärungen ausgewählter griechischer und hebräischer Morphologiecodes; Originalcodes weiterhin sichtbar.
- Additive SQLite-Tabellen für Studienobjekte; Werksreset berücksichtigt diese.

## 0.8.0
- Ausgabenvergleich (2–4 installierte Ausgaben, kapitelweise, fehlende Verse markiert)
- Auswahl synoptischer Parallelperikopen (Mt / Mk / Lk)
- Quellengebundener Import dokumentierter Textvarianten (TSV / CSV), Anzeige und Sammlungsverwaltung
- Additive Tabelle `textual_variants`, automatisches Datenbankupdate und Werksresetunterstützung
- Wichtige Unterscheidung zwischen Editionsunterschieden und eigentlichen Handschriftenvarianten

## 1.0.0 – Erste konsolidierte Einzelplatzversion (10.10.2026)

- **Erststart-Assistent** mit einem einzigen Knopf für installierbare Offline-Mini-Beispiele (griechisch/hebräisch/deutsch/lateinisch samt kleinen Morphologie- und Lexikondaten).
- **Komplette ZIP-Datensicherung** via SQLite-Online-Backup einschließlich aller Module, Studienprojekte, Lexika und Einstellungen.
- **Geprüfte Wiederherstellung**: genau zwei ZIP-Dateien, Formatversion, SHA256, SQLite-Integritätscheck, FK-Prüfung, gestaffelte Datenbankübernahme nach Neustart, Sicherheitskopie des bisherigen Standes.
- **Automatische Sicherung** vor dem ersten 1.0-Start mit bestehender Datenbank und persistente Kennzeichnung des Release-Standes.
- **Diagnose-Übersicht** über Texte, Wortannotation, Lexika, eigene Studien und Datenbankzustand.
- Datenbankverbindungen nach jedem Zugriff zuverlässig geschlossen; lokale schreibende APIs gegen Cross-Origin-Aufrufe geschützt und Hosts validiert.
- Optimierte Startskripte installieren Python-Pakete nur bei Bedarf, Linux-Menüintegration optional; ausführliche verständliche Dokumentation und GitHub-CI-Vorbereitung.
- **Keine neue Datenbanktabelle** und keine Änderung bestehender Tabellenspalten in 1.0; lediglich neue Anwendungseinstellungen.
- Grenzen der Bibliotheksimporte und der wissenschaftlichen Textdaten ausdrücklich dokumentiert. Große STEPBible-Textdateien werden jetzt zeilenweise gelesen; defektes UTF-8 wird nicht mehr stillschweigend ersetzt.
