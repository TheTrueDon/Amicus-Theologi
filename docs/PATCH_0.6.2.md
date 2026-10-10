# Amicus Theologi 0.6.2 – STEPBible-Importkorrektur

## Problem
Das GitHub-Archiv `STEPBible-Data` enthält zahlreiche zusätzliche und teils große Dateien. Bis 0.6.1 wurde das *gesamte* Archiv (maximal 2.500 Dateien und 280 MB entpackt) überprüft, obwohl beim ausgewählten TAGNT-/TAHOT-Import nur dessen Textdateien gelesen werden.

## Korrektur
Bei STEPBible werden jetzt nur die zum ausgewählten TAGNT- bzw. TAHOT-Korpus passenden `.txt`-Dateien für die Entpackgrenzen bewertet und eingelesen. Historische Dateien im Verzeichnis `Older Formats` werden ausgeschlossen. Die allgemeine Archiv-Downloadgrenze beträgt weiterhin 145 MB. Für ausgewählte STEPBible-Einträge gelten weiterhin Schutzgrenzen (je Eintrag 130 MB, insgesamt 350 MB, maximal 150 Dateien).

## Datenhaltung
Keine Änderungen an Datenbanktabellen, Spalten oder Einstellungen. Bereits installierte Texte und Lexika bleiben unverändert. Der Import versucht bei einer bereits vorhandenen Modul-ID kein Überschreiben.

## Bedienung
Nach Update `Textmodule → Wissenschaftliche Bibliothek → STEPBible → TAGNT/TAHOT → Installieren` erneut wählen. Bei einer anderen Fehlermeldung bitte deren genauen Wortlaut mitteilen; die tatsächliche Kompatibilität aktueller TAGNT-/TAHOT-Quelldaten muss weiterhin durch Realimporte validiert werden.
