# Wissenschaftliche Daten (0.6.1)

Unter **Textmodule → Wissenschaftliche Bibliothek** sind drei Quellen auswählbar.

## A: STEPBible (CC BY 4.0)
Quelle: https://github.com/STEPBible/STEPBible-Data

- TAGNT: Aus dem amalgamierten griechischen Datensatz wird **nur die mit SBL markierte Wortauswahl** verwendet. Das Ergebnis ist keine buchstabengetreue digitale SBLGNT-Edition: Schreibweise und Zeichensetzung können abweichen. Die Morphologie-Codes werden unverändert gespeichert. Weitere Varianten gehören zu späteren textkritischen Werkzeugen.
- TAHOT: experimenteller Parser für die komplexen tabulatorgetrennten hebräischen Dateien. Das Format ist nicht für jede Version geprüft; ein fehlgeschlagener Import verändert bestehende Module nicht. Für einen belastbaren hebräischen Gesamtkorpus vorerst B bevorzugen.
- Per Schaltfläche wird das offizielle GitHub-Quellarchiv heruntergeladen; alternativ ein zuvor geladenes Repository-ZIP auswählen.
- Lizenz: STEPBible Data CC BY 4.0, Quellenangabe im Modul gespeichert. Es ist keine pauschale Lizenzfreigabe für andere eingebettete Drittwerke.

## B: Open Scriptures Hebrew Bible
Quelle: https://github.com/openscriptures/morphhb

- Das Repository-ZIP enthält im Unterverzeichnis `wlc/` OSIS-XML-Dateien mit Text, Lemmata, Morphologie und Strong-Referenzen.
- XML-Wörter werden für die Anzeige zu Versen zusammengeführt und mit den Original-Codes als Token gespeichert. Ein Import ist **keine vollständige Reproduktion der editorischen Textgestaltung**; Textvarianten/Verszuordnungen müssen später gesondert behandelt werden.
- Textgrundlage WLC gemeinfrei, Morphologie/Annotation CC BY 4.0. Attribution: Open Scriptures Hebrew Bible Project.

## C: CrossWire / SWORD
Quelle: https://www.crosswire.org/sword/modules/ModDisp.jsp

- Ein **Raw-ZIP eines Bibelmoduls** von CrossWire kann im Assistenten ausgewählt werden.
- Erfordert zusätzlich `pysword` (`python -m pip install pysword` in der verwendeten virtuellen Umgebung). Nicht alle SWORD-Module sind kompatibel; Wörterbücher und Kommentare werden noch nicht über diesen Adapter eingelesen.
- Die SWORD-Modul-Lizenz kann verschieden sein und muss **vor dem Download/der Verwendung** auf der Quellseite geprüft werden. Der Import kennzeichnet sie deshalb als „separat prüfen“.
- Der Python-Adapter liest ausgewählte Bibelverse aus dem gelieferten Paket aus; SWORD-Morphologie und Sonderverszählungen werden derzeit nicht importiert.

## Wichtige Grenzen

- Download setzt einmalig Internet voraus, die spätere Textarbeit bleibt offline.
- Es werden keine fremden Programme und keine Skripte aus ZIP-Dateien ausgeführt.
- Originaldateien werden nicht in den Git-Quellcode eingecheckt.
- Echte Drittanbieter-Repositorien konnten in der isolierten Buildumgebung nicht live heruntergeladen werden; Importschnittstellen wurden mit konstruierten Testarchiven geprüft. Insbesondere STEP-TAHOT und einige SWORD-Modultypen sind deshalb noch **experimentell**.
- Während eines großen Imports offen lassen; das lokale Backend verarbeitet die Daten synchron.
- Bereits vorhandene Module werden weder gelöscht noch überschrieben.
- Keine Änderungen am bestehenden Datenbankschema erforderlich: Tabellen `modules`, `verses`, `tokens` werden wiederverwendet.
