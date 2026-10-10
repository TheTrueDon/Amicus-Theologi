# Amicus Theologi – Schritt-für-Schritt-Anleitung

## 1. Das Programm starten

**Windows:** `start_windows.bat` öffnen. **Ubuntu:** Im entpackten Ordner `bash start_linux.sh` eingeben. Beim ersten Start brauchen die Python-Abhängigkeiten Internet; später ist die Software offline nutzbar. Beim Beenden das Terminal schließen oder Strg+C drücken.

## 2. Das erste Mal

Beim ersten Start führt Amicus durch drei Schritte:

1. **Mini-Beispiele installieren.** Johannes 1,1 (Griechisch), Genesis 1,1 (Hebräisch) sowie kleine deutsche/lateinische Ausschnitte und Demo-Lexika erscheinen sofort. Zum Ausprobieren benötigt man kein Konto und keinen Download.
2. **Originalsprachen erkunden.** Oben im Feld „Bibelstelle“ `Joh 1,1` eingeben. Ein griechisches Wort anklicken: rechts erscheinen Grundform, grammatische Merkmale und – sofern installiert – Lexikoneinträge. Unbekannte Codes werden nicht erfunden.
3. **Eigene Arbeit sichern.** Oben „Studienprojekte“ → neues Projekt → Notiz schreiben. Über „Datensicherung“ die vollständige ZIP-Sicherung auf einem anderen Datenträger aufbewahren.

## 3. Echte Bibelausgaben installieren

Oben **Textmodule → Modulkatalog** öffnen und das gewünschte Modul installieren. Bei einer Erstinstallation ist hierfür Internet notwendig. Der Import großer wissenschaftlicher Quellen kann eine Weile dauern. Bei einer Fehlermeldung bleiben bereits installierte Module erhalten. Einige Quellen sind experimentell und sollten vor der wissenschaftlichen Verwendung geprüft werden.

## 4. Suchen

Im linken Fenster Wort oder Wortfolge eingeben. `=im Anfang` sucht die genaue Wortfolge; `?Gott Wort` mindestens einen Begriff; `Anfang*` einen Wortanfang. Bei **„Erweiterte Suche“** kannst du zwei Lemmata und Wortabstände angeben. **Achtung:** Diese Suche funktioniert nur mit vorhandenen Wortannotationen; ein leerer Treffer ist nicht immer eine sprachwissenschaftliche Aussage.

## 5. Notizen / Markierungen

Über „Studienprojekte“ ein Projekt anlegen. Eine Bibelstelle auswählen und rechts eine Notiz eingeben oder den Vers farbig markieren. Die Daten sind lokal und projektabhängig. Einzelne Studienprojekte können als JSON exportiert werden, ein JSON-Rückimport ist derzeit nicht integriert. Benutze für die vollständige Rücksicherung die ZIP-Funktion.

## 6. Vollständige Sicherung und Datenprüfung

Über **Datensicherung** → „Vollständige Sicherung herunterladen“. Die Datei enthält **alle Daten in SQLite**, einschließlich Studienprojekten und installierten Modulen. Für den Rechnerwechsel: Neues Programm starten → Datensicherung → ZIP auswählen → Sicherheitsbestätigungen durchführen → Programm **vollständig beenden** → wieder starten. Danach sind die gesicherten Daten wieder da. Solange die Rücksicherung nur vorbereitet ist, kannst du sie im gleichen Dialog noch **abbrechen**.

Der Knopf **Datenbank prüfen** zeigt die Anzahl installierter Texte, annotierter Wörter, Lexika, Notizen und das Ergebnis der SQLite-Konsistenzprüfung. Bei Problemen keine weiteren Importe vornehmen und zuerst eine Sicherung erstellen.

## 7. Werksreset

Unter Einstellungen → „Alle Daten löschen und zurücksetzen“ entfernt Amicus **alle installierten Texte, Projekte und Einstellungen**. Er fragt zweimal nach. Vorher selbst eine ZIP-Sicherung herunterladen, wenn etwas erhalten bleiben soll.

## 8. Versionsupdate

Programm schließen → neue Version in **neuen Ordner** entpacken → starten. Die lokale Datenbank liegt **nicht im Programmordner** und wird wiedergefunden. Die erste 1.0-Ausführung erstellt eine Update-Sicherung. Falls eine Rücksicherung vorbereitet wurde, unbedingt vor weiteren Schritten neu starten.

## 9. Häufige Fragen

**Ich sehe keine Bibeltexte.** Es ist noch kein Modul installiert. Im ersten Dialog Demo installieren oder Modulkatalog öffnen.

**Ein Wort lässt sich nicht anklicken.** Das betreffende Modul hat an dieser Stelle keine Wortannotation; diese muss passend zum Text installiert sein.

**Was heißt `V-IAI-3S` / `G1510`?** Ein Morphologie-Code beschreibt Grammatik; `G1510` ist eine Strong-Kennung für ein Lexikonlemma. Unterstützte Codes werden ausgeschrieben; die Rohdaten sind weiterhin einsehbar.

**Funktioniert der Computer ohne Internet?** Ja, nachdem Python-Pakete und gewünschte Datenmodule installiert wurden.

**Kann ich Texte für eine Veröffentlichung zitieren?** Dafür die Edition, Lizenz und den wissenschaftlichen Textstand jedes Moduls separat prüfen.
