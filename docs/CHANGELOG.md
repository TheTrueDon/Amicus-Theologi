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
