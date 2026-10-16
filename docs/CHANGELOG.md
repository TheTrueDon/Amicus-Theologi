## 1.1.1 – Prüfung importierter Wortdaten

- Griechische und hebräische Module können gezielt auf passende Wortfolge zum gespeicherten Vers, lückenlose Tokenpositionen und vorhandene Lemma-/Morphologiefelder geprüft werden.
- Auffällige Bibelstellen werden mit begrenzter Fundstellenliste und Gesamtzahl ausgegeben; Module ohne Annotationen werden nicht als geprüft bestanden gemeldet.
- Ergebnis ist eine interne Konsistenzprüfung. Sie belegt weder Vollständigkeit des Korpus noch Lizenz oder wissenschaftliche Richtigkeit.
- Rein lesend; keine Schemaänderung oder Datenmigration.

## 1.1.0 – Wortformen und Datenabdeckung

- Wortanalyse bietet für griechische und hebräische Lemmata eine paginierte Formenübersicht mit belegten Schreibweisen, Häufigkeiten, grammatischer Analyse und Verteilung nach biblischen Büchern.
- Anklicken einer Form startet eine exakte Oberflächensuche.
- Datenbankdiagnose zeigt pro Textmodul Verse mit Wortannotationen und deren Anteil an den vorhandenen Versen.
- Die Diagnose erklärt ausdrücklich, dass Abdeckung weder Vollständigkeit des Textes noch Richtigkeit der Annotationen nachweist.
- Auswertungen beruhen ausschließlich auf tatsächlich importierten Daten. Keine Schemaänderung oder Datenmigration.

## 1.0.9 – Amicus-Datenverzeichnis und vollständige Deinstallation

- Bisherige Daten werden auf den neuen Standard-Datenpfad migriert, ohne Tabellenänderungen.
- Windows- und Ubuntu-Deinstaller löschen alle lokalen Anwendungsdaten im Standardordner.
- Upgrades behalten Daten, externe Sicherungen bleiben unangetastet.
- Daten in benutzerdefinierten Pfaden müssen separat gelöscht werden.

## 1.0.8 – Ubuntu-Installation und Menüintegration (11.10.2026)
- Neuer GitHub-Actions-Workflow `Ubuntu installation package` erstellt ein normales `.deb` für Ubuntu 24.04 x86_64.
- PyInstaller bündelt Python und Bibliotheken; keine manuelle Python-Installation bei der fertigen Ubuntu-Ausgabe.
- Eigene Programmsymbole, Startmenü-Einträge, optionaler Desktop-Shortcut und Deinstallation via Ubuntu-Paketverwaltung.
- Der bestehende Datenordner und die SQLite-Datenbank bleiben unverändert.
- Der erste Ubuntu-Build muss auf GitHub Actions bzw. Ubuntu 24.04 getestet werden; Quellcodepaket enthält keinen vorgebauten Linux-Binary.

## 1.0.7 – Hebräische Wortvorschau repariert (11.10.2026)

- Grundform aus hebräischen Lexikoneinträgen per Strong-Zuordnung anzeigen, statt Strong- oder Präfixcodes als Lemma auszugeben.
- Quellbasierte Kurzglosse statt grammatischer Kategorien im Tooltip; falls keine überprüfbare Glosse gefunden wird, deutlicher Leerwert.
- Open-Scriptures-Morphologie einschließlich zusammengesetzter Codes verständlich auflösen.
- Rechte Analysespalte zeigt für hebräische Einträge ebenfalls die ermittelte Grundform an.
- Bestehende Module und Annotationen bleiben unverändert. Keine Schemaänderung.
- Vier neue Regressionstests mit OSHB-artigen Hebräischcodes.

## 1.0.6 – Verse unmittelbar zwischen Bibelausgaben vergleichen (11.10.2026)

- **Versweise Parallelansicht als Standard:** gleiche Versnummern aus allen aktivierten Bibelausgaben stehen direkt untereinander; bisherige Ansicht nach Ausgabe bleibt umschaltbar.
- Ausgabenreihenfolge aus dem Auswahlmenü übernehmen; Ansichtsmodus dauerhaft in den bestehenden Einstellungen speichern.
- Klick auf Versüberschrift/Verszeile aktiviert Bibelstelle und Studiennotizen; Wortanalyse, Hover, Markierungen und RTL-Hebräisch beibehalten.
- Einzelne fehlende Verse markieren; Ausgaben ohne Text für das gesamte Kapitel getrennt auflisten; keine textkritischen Aussagen aus Datenlücken ableiten.
- Integriertes und eigenständiges Offline-Handbuch auf denselben Dokumentationsstand gebracht.
- Keine Änderung des Datenbankschemas oder installierter Textinhalte.

## 1.0.5 – Bibelausgabenkatalog und flexible Parallelansicht (11.10.2026)
- Kuratierter CrossWire/SWORD-Katalog: Elberfelder 1905/1871, Menge 1939, Textbibel 1906, Luther 1912 (Beta) mit Quellen- und Lizenzinformationen.
- Ein-Klick-Installationsweg für offizielle Raw-ZIP-Module, feste Downloadziele, Größenbegrenzung, explizite Modul-ID und transaktionale Speicherung.
- PySword 0.2.8 gehört jetzt zu den installierten Python-Abhängigkeiten und wird beim Windows-Build mitgebündelt.
- Oberhalb des Bibeltexts: Ausgaben an- und abwählen, aktive Chips, Mehrfachauswahl, Suche in installierten Ausgaben, Reihenfolge per Pfeilen ändern.
- Schnellfilter „Alle“, „Keine“, „Nur Deutsch“, „Nur Originalsprachen“; Auswahl und Reihenfolge als lokale Einstellungen gespeichert.
- Alle bisherigen Inhalte, Suche, Studiennotizen und Lexika bleiben erhalten. **Keine Datenbankschemamigration.**
- Automatisierte Tests und Chromium-Interaktionstest mit lokalen Testdaten bestanden; Live-ZIP-Import aller fünf Originalarchive steht noch aus.

## 1.0.4 – Lesbarkeit der Studiennotizen (11.10.2026)
- Fehler im rechten Notiz-Eingabefeld behoben: keine dunkle Schrift auf schwarzem Hintergrund mehr.
- Eingabefeld erhält für helles und dunkles Theme jeweils explizit Hintergrund-, Text- und Cursorfarbe aus den vorhandenen Designvariablen.
- Projektformularfelder ebenfalls angepasst; Platzhalter und Fokus-Rahmen verbessert.
- Ausschließlich Frontend-CSS und Versionskennzeichnung geändert; keine Datenbankmigration.

## 1.0.3 – Tooltip-Übersetzungen und Konkordanzsortierung (11.10.2026)
- Fehler bei STEPBible-Lexika korrigiert: Transliteration/Aussprache nicht mehr als Wortbedeutung in Tooltips. Vorhandene Lexikon-Datensätze werden dynamisch richtig ausgewertet; keine Neuinstallation nötig.
- Kurzglossen werden aus markierten Gloss-Feldern bevorzugt. Deutsch, sofern durch die Quelle erkennbar, ansonsten Englisch. Falls keine sichere Bedeutung vorhanden ist, erscheint ein ehrlicher Hinweis.
- Auch in der rechten Lexikonspalte zeigt „Kurzglosse“ nun die aufbereitete Bedeutung; vollständige Lexikon-Einträge und Originaldaten bleiben unverändert.
- Konkordanz: Sortierung der gesamten Treffermenge nach Bibelstelle (kanonische Reihenfolge) oder Wortform sowie auf-/absteigend; korrekt paginiert.
- Keine Änderung des Datenbankschemas. Regressionstests für existierende STEPBible-Importe, neue Quellfelder, Pagination und sichere Eingaben.
- Original-STEPBible-Gesamtarchive weiterhin noch nicht vollständig mit allen Dateivarianten live getestet.

## 1.0.2 – Lexikondarstellung, Lemma-Konkordanz und Wortvorschau (11.10.2026)
- STEPBible-Lexika werden aus den gespeicherten Markup-Daten sicher formatiert; Rohtext bleibt bei Bedarf aufklappbar.
- Lemma-Konkordanz in eigenem Dialog mit Trefferanzahl, 50 Treffern je Seite und Navigation.
- Tooltip bei Hover und Tastaturfokus: Lemma, installierte Lexikonglosse, grammatische Formen (rot hervorgehoben).
- Neue lokale API für Vorschau und paginierte Konkordanz. Keine neuen Datenbanktabellen.
- Quelle, Edition und Originalcodes bleiben sichtbar; fehlende Übersetzungen werden nicht erfunden.

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
- Die genannten Befehle sind Amicus-Funktionen; keine vollständige früheren Referenzanwendung-Befehlskompatibilität.

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
