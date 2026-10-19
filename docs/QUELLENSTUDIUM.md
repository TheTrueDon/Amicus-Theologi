# Amicus Quellenstudium – Funktions- und Testanleitung

**Entwicklungsstand:** lokaler Testzweig auf Basis von Amicus Theologi 1.3.1.
Diese Erweiterung ist noch nicht in einer regulären Version veröffentlicht.

## Funktionsumfang

Über die Schaltfläche **Quellenstudium ↗** im Kopfbereich öffnet sich ein
eigener Arbeitsbereich. Die bisherige Bibeloberfläche bleibt unverändert.

- Eigene Bibliothek für außerbiblische Primärtexte in **Latein, Altgriechisch und Hebräisch**.
- Navigation über frei strukturierte Quellenreferenzen statt fester Bibelverse.
- Volltextsuche, exakte Phrasen, UND/ODER, Präfixsuche und Quellenfilter.
- Wortform-, Lemma- und Morphologie-Code-Suche (bei vorhandener Annotation).
- Integrierter Import wissenschaftlicher UD-CoNLL-U-Treebanks im Ein-Klick-Katalog.
- Klickbare Wörter und wieder sichtbare Tooltips beim Überfahren oder Fokussieren
  (auf Touchgeräten per Antippen), Lexikonabfragen, Formen, Häufigkeiten, Fundstellen.
- Vergleich mit gleich geschriebenen Formen in bereits installierten annotierten
  Korpora; **mögliche Analysen** werden ausdrücklich als solche gekennzeichnet.
- Notizen und eigene Übersetzungen pro Quellenstelle.
- Importassistent für Texte, Wortannotationen und Lexika sowie Ein-Klick-Katalog.

**Grenze:** Ein bloßer Textimport erzeugt Wortpositionen, aber **keine**
wissenschaftlichen Lemmata oder Grammatik. Sprachwissenschaftliche Analysen
stehen nur nach Import geeigneter Annotationen zur Verfügung. Aus anderen
Korpora belegte Wörter werden als **nicht kontextgeprüfte Vorschläge** getrennt
angezeigt. Weder Lexikonbedeutungen noch grammatische Merkmale werden durch KI erfunden.

## Erste Schritte

1. Amicus wie gewohnt starten und oben **Quellenstudium ↗** anklicken.
2. Im zweiten Fenster **Katalog** öffnen.
3. Eine lateinische, griechische oder hebräische Quelle auswählen und installieren.
4. Über **Werk** und **Stelle** zu einem Abschnitt navigieren.
5. Wörter anklicken, nach Formen suchen, Statistiken öffnen oder Notizen speichern.
6. Über den **Importassistenten** eigene Text-, Annotationen- und Lexikondateien ergänzen.

### Der Ein-Klick-Katalog: vier Arbeitsbereiche

| Kategorie | Installierbare Beispiele | Datenquelle |
| --- | --- | --- |
| **1. Primärquellen** | Cicero, Platon, Augustinus: Confessiones, Clemens von Rom: 1. Korintherbrief, Severian von Gabala | Perseus, Open Greek and Latin/CSEL, First1KGreek, Patristic Text Archive |
| **1. Primärquellen** | Pirkei Avot 1 und 2, Mischna Berakhot 1, Maimonides: Mischne Tora, Grundlagen 1 | Sefaria v3 API |
| **2. Lexika** | Lewis & Short; Liddell–Scott–Jones; Karl Ernst Georges (Latein–Deutsch); vorhandene STEPBible-Lexika | Perseus, PTA-Lexikondaten, STEPBible |
| **3. Sprachwissenschaftliche Daten** | Augustinus, komplette annotierte *Confessiones* (4.051 Abschnitte, CIRCSE, manuell nachgeprüft); Severian von Gabala, 11/13 Abschnitte mit automatisch analysierten griechischen Wörtern | CIRCSE / LiLa; Patristic Text Archive |
| **3. Sprachwissenschaftliche Daten** | Annotierte Proben aus Index Thomisticus (Thomas von Aquin) und Perseus Ancient Greek | Universal Dependencies, CoNLL-U |
| **4. Hilfsmittel** | Corpus Corporum, Morphologie-Merkmalsverzeichnis von Universal Dependencies | Externe wissenschaftliche Portale |

Hilfsmittel im vierten Bereich werden über einen deutlich beschrifteten
**Online öffnen**-Knopf gestartet; sie sind keine herunterladbaren Module.
**Corpus Corporum** erlaubt nur je nach Werk und dessen Rechten einen Export.
Die Version installiert keine komplette fremde Forschungsdatenbank.

Die Wortannotationen der Treebanks werden beim Installieren dem eigenen
Quellentext zugeordnet. Wenn die Wortgrenzen in Originaltext und Annotation
nicht übereinstimmen, bleibt die Stelle lesbar, wird aber **nicht falsch
annotiert**. Im geprüften Index-Thomisticus-Testkorpus waren 1.997 Abschnitte
vollständig zuordenbar, 104 nicht; im griechischen Perseus-UD-Testkorpus
waren 1.137 Abschnitte zuordenbar.

**Das war im bisherigen Teststand unvollständig:** Bei Cicero, Platon,
CSEL-Augustinus, den unanalysierten PTA-Texten und Sefaria-Quellen wird nur der
Text installiert. Das ist kein Importfehler eines vorhandenen Morphologiepakets:
Diese ausgewählten Quelldateien enthalten selbst keine vollständige,
positionsbezogene Wortanalyse. Die beiden neuen Ein-Klick-Editionen bringen
solche Daten mit. Bereits installierte unannotierte Werke werden **nicht**
heimlich mit einer anderen Textedition überschrieben: Sie bleiben für Editionen-
vergleiche erhalten; die annotierten Ausgaben erscheinen separat im Werkauswahlmenü.

Wortanalysen in der PTA-Ausgabe wurden **maschinell erzeugt** und nicht
redaktionell geprüft. Der analysierte Augustinus-Korpus wurde laut CIRCSE
nachträglich **manuell kontrolliert**. Die Leserseite weist auf diese Unterschiede
hin. Für andere Primärquellen werden gegebenenfalls mögliche Lemmata aus
installierten, annotierten Vergleichskorpora angezeigt; diese Formen sind
**keine** sichere Interpretation des angeklickten Wortes im vorliegenden Kontext.

Die großen Wörterbücher können jeweils ungefähr 40 bis 77 MB übertragen.
Bei der Installation bleiben Urheber, Edition, Herkunft und Lizenz sichtbar.
**Wichtig:** Die Index-Thomisticus-Proben stehen unter CC BY-NC-SA 3.0,
die griechischen Perseus-UD-Proben unter CC BY-NC-SA 2.5. Beide dürfen
nicht kommerziell weiterverwendet werden. Bei jeder anderen Edition die konkreten Nutzungsrechte
ebenfalls prüfen. Für Sefaria erfolgt vor dem Import eine explizite
Prüfung der Versionslizenz. Die Kataloginstallation braucht Internet,
danach können die installierten Module offline genutzt werden.

Die digitalen CSEL-Bände sind maschinenkorrigierte historische Editionen.
Für wissenschaftliche Zitate muss die gedruckte Ausgabe beziehungsweise
die entsprechende Edition gegengeprüft werden.

## Textquelle manuell importieren

**UTF-8-CSV oder TSV** mit den Spalten ref und text:

~~~csv
ref,text
I.1,"In principio erat verbum."
I.2,"Et ..."
~~~

Die Referenz kann beispielsweise I.1, I.1.1 oder q.2.a.3 heißen. Sie muss
innerhalb eines Werks eindeutig sein. Die Dateireihenfolge bestimmt die
Navigation. Maximal 25 MB, 100.000 Abschnitte und 20.000 Zeichen je Abschnitt.

**JSON** wird ebenfalls unterstützt:

~~~json
{"sections":[{"ref":"I.1","text":"In principio erat verbum."}]}
~~~

**TEI P5 XML** muss einen Textkörper (body) und gegliederte Absätze/Zeilen
enthalten. Die Gliederung aus div-Elementen wird als Referenz übernommen.
Komplexe editorische Apparate können bei dieser Überführung Informationen
verlieren; Referenzen und Absatzgrenzen anschließend kontrollieren.

## Morphologische Wortdaten importieren

Zuerst den Text installieren, danach über **Importassistent → Wortannotationen**
eine UTF-8-TSV-/CSV-Datei mit ref, position, surface, lemma, morph
und optional strong importieren:

~~~tsv
ref	position	surface	lemma	morph	strong
I.1	1	In	in	Adp
I.1	2	principio	principium	Case=Abl|Number=Sing
I.1	3	erat	sum	VerbForm=Fin|Tense=Imp
~~~

Wortpositionen beginnen bei 1. Die Datei muss alle Wörter eines annotierten
Abschnitts in derselben Reihenfolge enthalten. Ein fehlerhafter Import wird
vollständig zurückgerollt; bestehende Annotationen bleiben erhalten.
Morphologie darf leer sein, wenn sie nicht geprüft wurde.

## Wörterbuch importieren

UTF-8-CSV/-TSV, Pflichtspalten lemma und definition,
optional gloss, strong und reference:

~~~csv
lemma,definition,gloss,reference
amicus,"Beispieleintrag für ein eigenes Lexikon","Freund","eigene Quelle"
~~~

Lateinische Makronzeichen werden beim Nachschlagen ignoriert; die originale
Stichwortschreibweise bleibt gespeichert. Die Lexikonsprache muss zur Quelle
passen. Auch bei nicht annotierten Wörtern wird nach einem exakt passenden
Stichwort gesucht; das ist noch keine morphologische Bestimmung.

## Datenbank, Sicherung und Updates

**Neue additive SQLite-Tabellen:** source_modules, source_sections,
source_tokens, source_notes und source_fts einschließlich Indizes und Triggern.
Ein zusätzlicher Oberflächenform-Index für die bisherigen Bibel-Token unterstützt
die Vergleichssuche; bestehende Daten werden nicht verändert.
Bestehende Bibeltexttabellen, Einstellungen und Studienprojekte bleiben erhalten.

Die Vollsicherung enthält die zusätzlichen Quellenstudium-Daten, weil
Amicus den gesamten SQLite-Datenbestand sichert. Vor dem Test mit produktiven
Daten dennoch eine externe Sicherung erstellen. Ein Werksreset oder eine
vollständige Deinstallation mit Datenlöschung entfernt auch diese Quellen.

Die Versionsdatei bleibt auf dem Basisstand 1.3.1. Es erfolgt ausdrücklich
**kein Commit auf GitHub**, bis der Nutzer den Teststand freigegeben hat.

## Tests für Entwickler

~~~bash
python3 -m unittest discover -s tests -v
node --check frontend/sources.js
~~~

Netzwerktests laufen nur explizit aktiviert:

~~~bash
AMICUS_TEST_SOURCE_NETWORK=1 python3 -m unittest tests.test_sources_online -v
AMICUS_TEST_SOURCE_NETWORK=1 AMICUS_TEST_LARGE_LEXICON=1 python3 -m unittest tests.test_sources_online -v
~~~
