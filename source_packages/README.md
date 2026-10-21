# Amicus-Quellenpakete

Die `.amicus-source`-Dateien sind portable Offlinepakete. Im Quellenstudiumsfenster
unter **Katalog → Amicus-Quellenpaket installieren** auswählen und installieren.
Originaltext, Wortdaten, Übersetzungen und Herkunft werden dabei gemeinsam
importiert. Vollständige Werkübersetzungen erscheinen beim ersten Abschnitt als
eigene Gesamtübersetzung; abschnittsweise Übersetzungen stehen direkt am
jeweiligen Abschnitt.

## Derzeit enthaltene Titel

Alle zehn Pakete enthalten für **jedes Worttoken** ein nichtleeres Lemma und
einen Morphologie-/Wortartcode: insgesamt 720.984 Token in 26.566 Abschnitten.
Das heißt nicht, dass jeder Code Kasus, Numerus, Tempus oder weitere
Einzelmerkmale enthält. Die Spalte „Merkmalsdetails“ zählt Codes mit
grammatischen Merkmalen (`FEATS`/AGDT-Positionen); bloße UD-Wortarten wie
`NOUN` zählen ausdrücklich nicht als volle Morphologie.

| Datei | Text / Edition | Lemma + Code | Merkmalsdetails | Analysebasis |
| --- | --- | ---: | ---: | --- |
| `amicus-latin-augustinus-confessiones.amicus-source` | Augustinus, *Confessiones* (CIRCSE) | 78.563 / 78.563 | 53.742 / 78.563 | CIRCSE/LiLa plus automatische LatinCy UDPipe- und spaCy-Ergänzungen |
| `amicus-latein-augustinus-de-civitate-dei.amicus-source` | Augustinus, *De civitate Dei* (CIRCSE) | 275.860 / 275.860 | 193.732 / 275.860 | CIRCSE/LiLa plus automatische LatinCy UDPipe- und spaCy-Ergänzungen |
| `amicus-latein-augustinus-de-trinitate.amicus-source` | Augustinus, *De Trinitate* (CIRCSE) | 116.048 / 116.048 | 78.020 / 116.048 | CIRCSE/LiLa plus automatische LatinCy UDPipe- und spaCy-Ergänzungen |
| `amicus-griechisch-origenes-de-oratione.amicus-source` | Origenes, *De oratione* (PTA) | 27.937 / 27.937 | 27.829 / 27.937 | Automatische OGA/PTA-Analyse; spaCy-Modell für Restlücken |
| `amicus-griechisch-athanasius-de-incarnatione.amicus-source` | Athanasius, *De incarnatione Verbi* (PTA) | 18.754 / 18.754 | 18.634 / 18.754 | Automatische OGA/PTA-Analyse; spaCy-Modell für Restlücken |
| `amicus-griechisch-chrysostomus-colossenses.amicus-source` | Johannes Chrysostomus, *In epistulam ad Colossenses* (PTA) | 40.797 / 40.797 | 28.864 / 40.797 | PTA-Analyse und automatische griechische Modellanalyse |
| `amicus-griechisch-philo-de-opificio-mundi.amicus-source` | Philon, *De opificio mundi* (Perseus/First1KGreek) | 13.347 / 13.347 | 13.343 / 13.347 | Automatische Open Greek Corpus OGA-Analyse |
| `amicus-griechisch-josephus-bellum-judaicum.amicus-source` | Josephus, *Bellum Judaicum* (Perseus) | 125.211 / 125.211 | 125.120 / 125.211 | Automatische Open Greek Corpus OGA-Analyse; Modell für Restlücken |
| `amicus-griechisch-severian.amicus-source` | Severian, *De fide et lege naturae* (PTA) | 3.838 / 3.838 | 3.818 / 3.838 | Automatische OGA/PTA-Analyse; Modell für Restlücken |
| `amicus-hebraeisch-genesis-oshb.amicus-source` | Genesis (WLC/OSHB) | 20.629 / 20.629 | 19.024 / 20.629 mit mehreren Eigenschaften | Editionsgebundene OSHB-Lemmata und Morphologiecodes |

Die linke Abdeckungsangabe bezeichnet nur die technische Abdeckung: In diesen
Paketen hat jedes der 720.984 Worttoken ein nichtleeres Lemma und einen
Morphologie-/Wortartcode; keines ist als unbekannt (`X`) markiert. Die
Detailzahl zählt Tokens mit ausformulierten Merkmalen oder positionsgebundenen
Tags. Ein POS-only-Code ist also kein leeres Feld: er bedeutet, dass die Quelle
keine weiteren Merkmale liefert oder das Modell keine belastbare Ergänzung
ergab. Bei Latein erfüllen diese Pakete den Anspruch vollständig
ausdifferenzierter Flexionsmerkmale derzeit **nicht**; das gilt auch für einen
Teil der griechischen Eigennamen und Numeralia. **Die griechischen OGA-Daten
sind automatisch erzeugt** (morphosyntaktische Analysen des COMBO-Parsers,
trainiert auf Treebank-Daten); auch die Ergänzungen für Latein und Griechisch
sind Modellanalysen und nicht redaktionell vollgeprüft. Sie können
Fehlzuordnungen enthalten und bleiben ein experimenteller Arbeitsstand, kein
Ersatz für eine fachliche Prüfung. Die Herkunft der lateinischen Analyse ist
auf Paketebene als gemischt ausgewiesen, nicht für jedes einzelne Token. Die
hebräische Morphologie übernimmt editionsgebundene OSHB-Codes. Lemmata und
Morphologiecodes sind keine vollständigen Wörterbuchdefinitionen; die
Wörterbuchsuche der Anwendung kann weiterhin für einzelne Lemmata keinen
deutschen oder englischen Bedeutungsartikel liefern.

## Herkunft und Rechte

- Augustinus: CIRCSE/LiLa, `AugustiniConfessiones` (Commit `02fc680`),
  `AugustiniDeCiuitateDei` und `AugustiniDeTrinitate`; CIRCSE nennt für die
  Datensätze CC BY-SA 4.0. Die deutsche *Confessiones*-Übersetzung stammt aus
  der BKV-Ausgabe von 1914, die *Gottesstaat*-Übersetzung von 1911–1916. BKV
  erklärt, die digitalisierten alten Texte seien frei verwendbar.
- Severian: Patristic Text Archive; die Edition nennt CC BY-SA 4.0 und markiert
  die Analyse als automatisch.
- Origenes, Athanasius und Chrysostomus: Patristic Text Archive, Quellstand
  Commit `524eb97`; Lizenz und Analysedeckung stehen editionsgenau im Manifest.
  Die automatischen PTA-Wortanalysen sind nicht redaktionell geprüft. Die
  deutschen Texte stammen aus den verlinkten BKV-Ausgaben.
- Philon: griechischer Text und englische Übersetzung aus Perseus/First1KGreek
  unter CC BY-SA 4.0; Analyse ergänzt mit Open Greek Corpus OGA.
- Josephus: griechischer Text aus der Perseus Digital Library; die Whiston-
  Übersetzung des *Bellum Judaicum* stammt aus der historischen Ausgabe von
  1895 und ist gemeinfrei. Analysen aus Open Greek Corpus OGA und Modellergänzung.
- Genesis: Open Scriptures Hebrew Bible; WLC-Text Public Domain, Morphologie
  CC BY 4.0. Lutherbibel 1912 Public Domain, vollständiges Genesis-Buch.
- Die eigenen kurzen Arbeitsübertragungen sind CC BY 4.0.

Die genauen Ausgaben, Rechte, Quellenstände, Abdeckungsangaben und SHA-256-
Prüfsummen stehen auch in den jeweiligen Manifesten. Die Dateien enthalten
keinen ausführbaren Code.

## Format und Erzeugung

ASPK v1 ist ein ZIP-Archiv mit Manifest, Abschnitten, optionaler positionsgenauer
Wortanalyse und Übersetzungen. `@work` speichert eine vollständige
Gesamtübersetzung unabhängig von der Abschnittsgranularität des Originaltexts.
Die Installation prüft Prüfsummen, Referenzen und Wortpositionen. Ein bereits
installiertes Paket aktualisiert Wortanalysen und Übersetzungen nur, wenn alle
Stellen und Originaltexte exakt übereinstimmen; persönliche Abschnittsnotizen
bleiben erhalten. Bei verändertem Textstand wird das Update abgewiesen.

Die Confessiones-, Severian- und Genesis-Pakete werden mit
`tools/build_starter_source_packages.py` aus den in dieser Datei genannten
Quellständen erzeugt. Für die vollständige Genesis-Übersetzung wird außerdem
die Luther-1912-OSIS-Datei verwendet. Die zusätzlichen Augustinus-Pakete baut
`tools/build_augustine_packages.py` aus den passenden CIRCSE-CoNLL-U-Dateien.
Die griechischen PTA-Pakete baut `tools/build_pta_packages.py` aus PTA-TEI und
den jeweils angegebenen vollständigen BKV-Übersetzungen.
Das Philon-Paket baut `tools/build_philo_package.py` aus Perseus/First1KGreek-TEI
und der historischen BKV-Übersetzung.
Das Josephus-Paket baut `tools/build_josephus_package.py` aus den griechischen
und englischen Perseus-TEI-Dateien.
Die Skripte laden keine Quelldateien selbst herunter und führen keine
Archivdateien aus.
