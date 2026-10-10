# Version 0.6.3 – Ein-Klick-Installation und Werksreset

## Verwendung
1. Textmodule → Modulkatalog öffnen.
2. STEPBible TBESG (Griechisch), TBESH (Hebräisch), TFLSJ (griechisch) oder ein annotiertes Bibelkorpus auswählen.
3. „Installieren“ klicken. Amicus lädt das Originalarchiv und importiert nur den gewählten Datenbestand. Bei Formatabweichungen zeigt es eine Fehlermeldung an, statt Einträge zu erfinden.
4. Auf ein Wort im annotierten Bibeltext klicken und den Lexikoneintrag rechts ansehen.

**Bei griechischen/ hebräischen Textkorpora sind Wortannotationen im selben Installationsschritt enthalten.** Für eigene CSV-/TSV-Texte benötigt man weiterhin passende Wortannotation mit identischer Wortfolge; Fremdannotationen dürfen nicht blind angehängt werden.

## Werksreset
Einstellungen → „Alle Daten löschen und zurücksetzen“ → erste Bestätigung → `WERKSRESET` eingeben.
Löscht alle Textmodule, Wortannotationen, Lexika und Einstellungen. Legt danach die Standardeinstellungen erneut an. Der Reset verändert keine Programmdateien. Vorher ggf. eine Datenbanksicherung anlegen.

## Datenbankmigration
Keine Schemaänderung. Ein Werksreset löscht Daten ausdrücklich auf Wunsch, nicht beim regulären Update. Bestehende Daten aus Version 0.6.2 bleiben bei normalem Start erhalten.

## Hinweis zur Datenqualität
STEPBible-Originaldateien werden online vom Anbieter geladen und unter CC BY 4.0 angeboten. Metadaten zu Quelle und Lizenz bleiben erhalten. Der Parser für Lexika wurde anhand von konstruierten Tabellen geprüft; das exakte aktuelle Originalformat von TBESG, TBESH und TFLSJ konnte in der Entwicklungsumgebung nicht vollständig heruntergeladen und Ende-zu-Ende geprüft werden. Falls die Datenstruktur verändert ist, kann der Import abgelehnt werden. Nicht als vollständig wissenschaftlich verifizierte Datenübernahme ansehen.

Originalquelle: https://github.com/STEPBible/STEPBible-Data
