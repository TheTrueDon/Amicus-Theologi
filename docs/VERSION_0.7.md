# Amicus Theologi 0.7.0 – Studienprojekte und verständliche Morphologie

## Änderungen
- Projekte mit Titel und Beschreibung anlegen, auswählen, umbenennen und löschen.
- Mehrere versbezogene Notizen anlegen, bearbeiten und löschen; durch Anklicken einer Notiz zur Stelle springen.
- Farbmarkierungen für Verse (gelb, grün, blau, rosa, orange), projektabhängig und ausgabenübergreifend.
- Export eines vollständigen Projekts inklusive Notizen und Markierungen als JSON (kein Reimport in 0.7).
- Griechische Robinson-ähnliche Morphologie-Codes und ausgewählte Open-Scriptures-Hebräisch-Codes werden in verständliche deutsche Begriffe aufgeschlüsselt. Das System interpretiert unbekannte Formate **nicht** automatisch. Originalcode/Strong-Nummer bleiben aufklappbar sichtbar.
- Browser-Tab enthält weiterhin keine Versionsnummer.

## Aktualisierung von 0.6.3
Bestehenden lokalen Datenordner **nicht** löschen. Das Datenbankschema wird beim ersten Start automatisch um drei neue Tabellen erweitert: `study_projects`, `study_notes`, `study_highlights` (sowie ein Index). Vorher Sicherung anlegen. Alte Bibeltextmodule, Lexika, Tokens und Einstellungen bleiben unverändert.

## Bedienung
1. Oben **Studienprojekte** öffnen, Titel eingeben und **Projekt anlegen** wählen.
2. Bibelstelle aufrufen und einen Vers anklicken; rechts erscheint das Notizfeld.
3. Notiz speichern oder eine Markierungsfarbe wählen.
4. Über **Studienprojekte** vorhandene Notizen auswählen oder unter **JSON exportieren** sichern.
5. In griechischen oder hebräischen Texten ein annotiertes Wort anklicken: Eigenschaften werden – soweit für das Codiersystem unterstützt – ausgeschrieben angezeigt.

## Grenzen
- Noch kein Import exportierter Projekt-JSONs und keine automatisierte Synchronisierung; Sicherung deshalb sowohl der lokalen Datenbank als auch optional der Exporte.
- Notizen und Farben beziehen sich auf Buch/Kapitel/Vers innerhalb eines Projekts, nicht auf einzelne Texteditionen oder Textstellenbereiche.
- Schemata der Morphologie unterscheiden sich zwischen Datenanbietern. Die Darstellung ist absichtlich konservativ und deckt noch nicht alle STEPBible-spezifischen Annotationen ab.
- Ein Werksreset löscht **auch** die Projekte samt Notizen und Markierungen.
