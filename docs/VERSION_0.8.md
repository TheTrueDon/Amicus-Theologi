# Amicus Theologi 0.8.0 – Textkritik und Synopsen

## Benutzung

Über **Textkritik & Synopse** in der Kopfzeile die Ansicht öffnen:

1. **Ausgabenvergleich:** zwei bis vier installierte Bibeltextmodule wählen, aktuelles Kapitel vergleichen. Fehlende Verse erscheinen als „—“. Das sind Unterschiede in verfügbaren Ausgaben, **keine automatisch bestimmten textkritischen Varianten**. Verschiedene Verszählungen werden in dieser ersten Fassung nicht automatisch abgeglichen.
2. **Evangelien-Synopse:** eine installierte Ausgabe und eine der neun ausgewählten Parallelperikopen wählen. Mt, Mk und Lk stehen in drei Spalten. Die Zuordnungen sind thematische Perikopen, keine wissenschaftlich exakte Satz- oder Versausrichtung. Es werden ausschließlich Verse angezeigt, die in der gewählten Ausgabe vorhanden sind.
3. **Dokumentierte Lesarten:** zu der aktuell aufgerufenen Stelle importierte Lesarten einsehen. Eigene Quellen als UTF-8 CSV oder TSV importieren: `book,chapter,verse,reading,witness,source,license` und optional `notes`. Leere Quellen-/Zeugenangaben werden zurückgewiesen. Keine automatische Erkennung echter Handschriftenvarianten.

## Datenbasis und wissenschaftliche Grenzen

- Kein textkritischer Apparat ist mitgeliefert; für einen solchen braucht es eine rechtmäßig nutzbare, editorisch gepflegte Datensammlung, inklusive benannter Textzeugen, Editionen und Apparateinträge.
- Es werden **keine erfundenen Lesarten oder Textzeugen** ausgeliefert.
- Es wird keine Aussage über die Priorität oder Ursprünglichkeit einer Lesart getroffen.
- Synoptische Referenzen wurden als einfache, ausgewählte Arbeitsbeispiele manuell angelegt. Vollständige synoptische Zuordnung und Versmapping stehen noch aus.
- Exegetische Notizen werden weiterhin in Version 0.7 verwaltet.

## Datenbank und Updates

Neue Tabelle `textual_variants`, Index `idx_variants_ref`. Die Tabellen werden beim Start automatisch angelegt. Bestehende Module, Wortannotationen, Wörterbücher und Studienprojekte bleiben erhalten. Backup der bestehenden `amicus_theologi.sqlite3` empfohlen. Der Werksreset leert auch Textvariantensammlungen.

## Weitere technische Hinweise

Der Vergleich arbeitet nur mit bereits importierten Ausgaben; er benötigt keine Internetverbindung. Die Importfunktion begrenzt Dateien auf 5 MB und 15.000 Lesarten und validiert notwendige Metadaten. Die Oberflächenansicht wird als Textknoten gerendert, um HTML aus importierten Quellen nicht auszuführen.
