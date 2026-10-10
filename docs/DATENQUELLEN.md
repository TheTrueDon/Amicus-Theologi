# Datenquellen für Amicus Theologi — Recherche 10.10.2026

## Priorität 1: Offene Urtextdaten und wissenschaftliche Annotationen

### Open Scriptures Hebrew Bible (OSHB)
- Repository: https://github.com/openscriptures/morphhb
- Hebräischer Text der Westminster Leningrad Codex (WLC) in OSIS XML, Wort-Lemmata und morphologische Kennzeichnungen.
- Nach Angaben des Projekts bleibt der WLC-Text Public Domain; die OSHB-Lemma- und Morphologiedaten stehen unter **CC BY 4.0** und erfordern Namensnennung.
- Besonderheiten: Präfixe, hebräische Orthografie, Ketiv/Qere und tokenübergreifende Zeichenfolgen müssen beim Import sauber behandelt werden.
- Empfehlung: Zuerst kleinen OSIS-XML-Prototyp erstellen, danach Gesamttextkonverter mit Versmapping und Qualitätstests.

### STEPBible-Data (Tyndale House)
- Repository: https://github.com/STEPBible/STEPBible-Data
- Unter anderem **TAGNT** (griechisches NT, Editionen/Varianten), **TAHOT** (hebräisches AT mit Annotationen), Lexikaldaten wie **TBESH** und **TBESG** (Bestand und Dateilizenzen gezielt verifizieren).
- Das Hauptrepository bezeichnet die eigenen Daten als **CC BY 4.0**; einzelne eingebundene Quelldaten und Versionen gesondert nach den Lizenzdateien prüfen.
- Empfehlung: **Top-Kandidat für eine wissenschaftlich nutzbare offene Datenbasis.** Wichtig sind Parser pro Dateityp, getrennte Editionen und Nachweis der Zuordnung.

## Priorität 2: Weitere Bibeltexte und Lexika

### CrossWire / SWORD
- Module: https://crosswire.org/sword/modules/ModDisp.jsp
- Quellen/Repositories: https://wiki.crosswire.org/Official_and_Affiliated_Module_Repositories
- Bietet vielfältige Bibeltexte, Kommentare und Wörterbücher, z. B. historische Luther-Ausgaben.
- **Wichtig:** Keine pauschale „Open Data“-Lizenz: jedes SWORD-Modul hat eigene Bedingungen, die auch bei Wiederverbreitung außerhalb von CrossWire relevant sind.
- Amicus Theologi unterstützt zurzeit **keinen direkten SWORD-Modulimport**. Ein lizenzbewusster SWORD-Adapter ist gesonderte Entwicklung.

## Datenverwaltung und Rechte

Für jeden später importierten Datensatz Metadaten dokumentieren: Name, Sprache, Edition, Textbasis, URL, Rechteinhaber, Lizenz, Versionsstand/Commit, Abrufdatum, ggf. Attribution. Moderne Bibelausgaben oder Wissenschaftslexika dürfen **nicht** einfach mit dem Open-Source-Programm verteilt werden, wenn die Lizenz es nicht gestattet.

### Konkrete Umsetzungsschritte
1. OSHB- und STEPBible-Datenformate anhand kleiner Auszüge testen; Zuordnung Buch–Kapitel–Vers und Wortposition evaluieren.
2. Lizenzdateien pro Datensatz/Unterordner dokumentieren und Attributionen im Modulmanager sichtbar machen.
3. Parser/Importer für OSIS/STEP-Spezialformate schreiben; nicht durch blindes TSV-Zusammenkleben diakritische Zeichen oder Ketiv/Qere zerstören.
4. Versionierte Module ausgeben und Importprüfungen auf Vollständigkeit, Duplikate, Tokenreihenfolge und Stellenmapping ergänzen.
5. Erneut prüfen, ob Hosting/GitHub-Distribution des jeweiligen Textbestands tatsächlich gestattet ist.

**Nicht in 0.6 enthalten:** Downloadmanager oder fertiger Komplettimport aller OSHB-/STEPBible-Daten. Die gegenwärtige Suche funktioniert mit importierten TSV-Morphologiedaten aus Version 0.4.
