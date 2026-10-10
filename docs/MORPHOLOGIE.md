# Wortannotation (v0.4)

1. `modules/examples/johannes_1_1_grc.tsv` als Textmodul importieren (Modul-ID `grc-joh-demo`, Sprache `grc`, Lizenz `Public Domain – antiker griechischer Bibeltext`, Quelle `Griechischer Johannes-Prolog, Demo-Transkription`).
2. Im Modulfenster unter **Wortannotation importieren** das Modul auswählen und `johannes_1_1_grc_morph.tsv` hochladen.
3. `Joh 1,1` öffnen und auf eines der griechischen Wörter klicken. Lemma-Konkordanz rechts abrufen.
4. Analog Genesis 1,1: Modul-ID `he-gen-demo`, Sprache `he`, dann `genesis_1_1_he_morph.tsv` importieren.

## Annotationsschema

UTF-8-CSV oder TSV mit Spalten `book, chapter, verse, position, surface, lemma, morph` und optional `strong`. Wortposition beginnt je Vers mit 1; kein Feld darf leer sein außer `strong`. `morph` ist in v0.4 ein zitierfähiger **Beschreibungstext**, noch kein normalisierter morphologischer Code. Das Importprogramm prüft, ob die gesamte Wortfolge (ohne Leerzeichen und Satzzeichen) der zugehörigen Textfassung entspricht. Interpunktion wird derzeit beim Anzeigen annotierter Verse nicht wiedergegeben; die Textquelle bleibt unverändert in der Datenbank.

### Wissenschaftliche Grenzen

Die mitgelieferten Annotationen wurden exemplarisch manuell erfasst. Sie stellen **keinen überprüften vollständigen morphologischen Referenzkorpus** dar. Morphologie wird nicht automatisch berechnet; lediglich explizit importierte Wörter erhalten eine Analyse. Varianten in Akzenten oder hebräischen Vokalzeichen dürfen beim Abgleich nicht stillschweigend ausgeglichen werden. Strong-Nummern bleiben leer, sofern keine verifizierte Zuordnung vorliegt.

Neue Annotationen überschreiben nur die Wortdaten für die in der Datei genannten Verse. Bei einem Fehler bleibt die bisherige Annotation unverändert. Beim Löschen eines Textmoduls werden seine Annotationen dank Fremdschlüssel-Kaskade entfernt.
