# Amicus Theologi 1.0.7 – Hebräische Grundformen und Morphologie

## Was wurde behoben?

- Im Open-Scriptures- und STEPBible-Hebräisch stehen im Annotationsfeld `lemma` häufig lexikalische Kennungen, z. B. `b/7225`. Sie werden nun **nicht** mehr fälschlich als Grundform ausgegeben.
- Die hebräische Grundform wird anhand der Strong-Nummer aus den installierten Hebräischlexika (vorzugsweise TBESH) ermittelt. Kein Dictionary = kein erfundenes Lemma.
- In den Tooltips gelten nur eindeutige Bedeutungen als Übersetzungen, keine Angaben wie „Prefix“, „noun“ oder reine Morphologie-Codes.
- Bekannte OSHB-Morphologie-Codes, auch zusammengesetzte Token wie `HC/R/Ncfsa`, werden in deutsche Fachbegriffe zerlegt. Originalcode bleibt erhalten.
- Die rechte Analysespalte zeigt das aus einem Lexikon ermittelte Grundwort.

## Installation/Update

ZIP entpacken und wie bisher starten. Unter Windows das Setup über GitHub Actions neu erzeugen. **Datenbankschema unverändert.** Vorhandene Texte, Lexika, Annotationen und Studienprojekte bleiben erhalten; eine Neuinstallation der wissenschaftlichen Daten ist nicht nötig.

## Datenquellen

Die morphologischen Codierungen orientieren sich an der [Open Scriptures Hebräisch-Morphologie](https://hb.openscriptures.org/parsing/HebrewMorphologyCodes.html) und der STEPBible-Dokumentation zu [TAHOT/TEHMC](https://github.com/STEPBible/STEPBible-Data). Der Textbestand wird nicht automatisch korrigiert oder ergänzt.

## Grenzen

- Nicht jeder hebräische Morphologie-Code (insbesondere spezielle Aramäisch- und Varianten-Codes) kann bereits sicher aufgelöst werden. In solchen Fällen wird kein Grammatikbefund behauptet.
- Ohne passendes Lexikon kann die ausgeschriebene hebräische Grundform nicht sicher aus einer numerischen Kennung rekonstruiert werden.
- Wörter mit mehreren Bestandteilen erhalten eine grammatische Beschreibung der Komponenten; eine präzise syntaktische Analyse wird daraus nicht abgeleitet.
