# Entwicklungsroadmap – Amicus Theologi

- [x] 0.1 – Grundgerüst, dreigeteilte Oberfläche, Konfiguration
- [x] 0.2 – Textmodule, Navigation, parallele Texte
- [x] 0.3 – FTS5-Volltextsuche, Filter, erste Befehle
- [x] 0.4 – Wortannotationen Griechisch/Hebräisch, Lemma-Konkordanz
- [x] 0.5 – Lexika, Strong-Verknüpfung, Wortstudien-Grundlage
- [x] 0.6 – Erweiterte Suche mit Wortabstand (Grundfunktionen)
- [x] 0.6.1–0.6.3 – Datenquellenkatalog und erste Adapter (teils experimentell)
- [x] 0.7 – Studienprojekte, Notizen, Markierungen, JSON-Export, verständliche Morphologie
- [x] 0.8 – Ausgabenvergleich, neun synoptische Parallelperikopen, eigene dokumentierte Lesarten
- [x] 0.9 – Schnellbedienung, Befehlssuche, Verlauf, Tastenkürzel
- [x] 1.0 – Erste konsolidierte lokale Veröffentlichung, Datenbankprüfung, Vollbackup, geprüfte Wiederherstellung, Erststart-Hilfe, Skriptinstaller, Qualitätsprüfungen
- [x] 1.1.0 – Erste Formenübersicht und Diagnose der Versabdeckung importierter Wortannotationen
- [x] 1.1.1 – Interne Konsistenzprüfung gespeicherter griechischer/hebräischer Wortannotationen
- [x] 1.1.2 – Exakte Wortformsuche aus Häufigkeitsverteilung nach Buch eingrenzen
- [x] 1.2.0 – Morphologische Suchabfragen lokal benennen, speichern, wieder öffnen und ausführen
- [x] 1.3.0 – Grafischer Abfrageeditor mit bis zu fünf Wortbedingungen, UND/ODER, Reihenfolge und Abstand
- [x] 1.3.1 – Positionsbedingungen je Wort: Versanfang oder begrenzter Tokenpositionsbereich

## Noch offen innerhalb 1.3

- Suchbereiche um Sprache/Korpus, Kapitel und benutzerdefinierte Referenzbereiche erweitern.
- Gespeicherte Muster bearbeiten und duplizieren; Kriterien vor dem Ausführen lesbar zusammenfassen.
- Eine dokumentierte Amicus-Kurzsyntax für häufige Abfragen ausarbeiten. BibleWorks-Kompatibilität nur für einzeln getestete Fälle zusagen.

## Weitere notwendige Arbeit nach 1.0

Die 1.1.1-Prüfung vergleicht lokale Tokenfolgen mit den jeweils gespeicherten Versen und kontrolliert Positionen sowie ausgefüllte Lemma-/Morphologiefelder. Sie validiert keine Originalarchive und ersetzt weder Quellenprüfung noch eine wissenschaftliche Vollständigkeitskontrolle. Die umfassende Reproduzierbarkeitstests für vollständige OSHB-, STEPBible- und SWORD-Archive bleiben offen.

- Unabhängige Validierung **vollständiger** aktueller STEPBible-, OSHB- und CrossWire-Originalarchive; reproduzierbare Datensatzstatistik und Referenzfälle.
- Korrekte vollständige Morphologie-Decodierung anhand editionsspezifischer Grammatiken (TEGMC/TEHMC etc.), differenzierte hebräische Präfix- und Suffixanalyse.
- Erweiterung auf deuterokanonische Schriften sowie verlässliches Mapping abweichender Verszählungen.
- SWORD-Binärformate und automatische Moduleinrichtung für tatsächliche Fremdformate zuverlässig absichern.
- Wissenschaftlicher Textapparat, vollständige Synopse und eigene Quellen-/Textzeugenmodelle.
- Import eigener Studienprojekte aus JSON, bessere Forschungs-Zitation und PDF/Word-Export.
- Native Windows-/Linux-Installer mit signierten Binärdateien, Barrierefreiheitstests, Benutzertests mit theologischer Fachpraxis.
- Regelmäßige Dependency- und Sicherheitsupdates, externe Code- und Datenprüfung.

Eine 1.0-Version ist hier ein **Meilenstein für das integrierte Einzelplatzprogramm**, nicht die Behauptung vollständiger Parität mit früheren Referenzanwendung.
