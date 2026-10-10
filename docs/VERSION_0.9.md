# Amicus Theologi 0.9.0 – Tastatur und Arbeitsabläufe

## Bedienung

Der Befehlskatalog wird durch die Schaltfläche „Befehle“ oder Strg+K/Cmd+K geöffnet. Ein Befehl lässt sich durch Namen filtern, mit den Pfeiltasten wählen und mit Enter ausführen. Escape schließt den Dialog. Auch bis zu fünf zuletzt verwendete Referenzen erscheinen in der Befehlsliste.

Im Suchbereich befinden sich bis zu sieben direkt anklickbare „Zuletzt besuchte Stellen“. Alle 16 Referenzen der lokalen Liste werden im Browser gespeichert, der Verlauf der vor- und zurückspringbaren Stellen dagegen nur für den aktuellen Tab. Letzterer startet nach einem Neuladen neu.

## Tastenkürzel

| Kürzel | Aktion |
| --- | --- |
| Strg+K (Cmd+K) | Befehle suchen |
| Alt+R | Bibelstellenfeld auswählen |
| / | Suchbegriff eingeben |
| Alt+S | Erweiterte morphologische Suche |
| Alt+Links/Rechts | Im aktuellen Verlauf zurück/vor |
| Alt+Hoch/Runter | Vorheriges/nächstes Kapitel |
| Alt+1/2/3 | Suchbereich/Textansicht/Analyse fokussieren |
| Strg+Umschalt+P | Studienprojekte |
| F1 | Hilfe |

**Hinweis:** Tastenkombinationen innerhalb von Eingabefeldern werden (mit Ausnahme von expliziten globalen Kombinationen) nicht abgefangen. Ein offener Dialog hat Vorrang. Browser- bzw. Betriebssystemkürzel können lokale Abweichungen verursachen.

## Wissenschaftliche Transparenz

Kein Import oder Wandel wissenschaftlicher Inhalte erfolgt in 0.9. Die neuen Funktionen beschleunigen die Bedienung, ersetzen aber keine vollständige BibleWorks-Befehlssyntax. Eine echte quantitative Nutzungsstudie mit BibleWorks-erfahrenen Theologinnen und Theologen steht aus.

## Datenhaltung / Update

Keine neuen SQLite-Tabellen und keine Migration. Bereits installierte Texte, Annotationen, Lexika, Projekte, Notizen und Varianten werden nicht geändert. Die lokale Referenzliste liegt zusätzlich unter `amicus-workflow-recent-v1` im localStorage des jeweiligen Browsers. Der integrierte Werksreset löscht auch die Referenzliste aus dem localStorage der aktuell verwendeten Browseradresse. Browserdaten anderer Profile oder abweichender lokaler Ports können weiterhin im jeweiligen Browser bestehen.
