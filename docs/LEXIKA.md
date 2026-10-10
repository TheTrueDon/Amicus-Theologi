# Lexikonmodule – Amicus Theologi 0.5

Der Wörterbuchimport erfolgt unter **Textmodule → Lexikon / Wörterbuch importieren**.

## TSV-/CSV-Format

UTF-8; erste Zeile mit `lemma,definition` und optional `strong,gloss,reference`. Als Trennzeichen sind Tab oder Komma möglich. Ein Eintrag je Lemma und Strong-Kennung innerhalb eines Lexikons. Definitionen dürfen Zeilenumbrüche enthalten, wenn CSV-konform in Anführungszeichen eingeschlossen.

| Spalte | Inhalt |
|---|---|
| lemma | Wörterbuchgrundform; Schreibweise sollte zu den Morphologiedaten passen |
| definition | Definition oder lexikalische Erläuterung |
| strong | optionale Strong-Kennung, z. B. G3056, H1254 |
| gloss | optionale kurze Bedeutungsangabe |
| reference | optionale bibliografische Eintragsreferenz |

Grenzen: 12 MB, 100.000 Einträge je Import, 8.000 Zeichen pro Definition. Import atomar: Ungültige Zeilen brechen den gesamten Import ab.

## Beispielablauf

1. Das griechische oder hebräische Demotextmodul und danach die passende Wortannotation importieren (siehe MORPHOLOGIE.md).
2. `demo_lexikon_grc.tsv` beziehungsweise `demo_lexikon_he.tsv` aus `modules/examples` als Lexikonmodul importieren. Die Demo-Metadaten werden vorgeschlagen.
3. `Joh 1,1` bzw. `Gen 1,1` öffnen und ein annotiertes Wort anklicken.
4. Rechts erscheinen die aus dem Import übernommenen Definitionen, Lemmata und Quellenangaben.

## Wissenschaftliche Grenzen

Die mitgelieferten Worterklärungen sind **kleine selbst erstellte Demonstrationen**, keine wissenschaftlich geprüften Volllexika. Andere Lexika werden nicht automatisch heruntergeladen; OSIS-/SWORD-Import und ein kuratierter Modulkatalog sind noch nicht implementiert. Die Zuordnung erfolgt über identische Lemmata (Unicode NFC/casefold) oder passende Strong-ID; unterschiedliche Editionskonventionen können deshalb Treffer verhindern oder eine manuelle Überprüfung erfordern. Die Übernahme von Wortartikeln setzt entsprechende Rechte voraus.

## Datenmigration

Beim ersten Start werden ausschließlich die Tabellen `lexicon_modules`, `lexicon_entries` sowie Suchindizes ergänzt. Vorhandene Module, Verse, Tokens und Einstellungen bleiben erhalten. Ein vorheriges Datenbank-Backup wird empfohlen.
