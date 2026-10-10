# Mitwirken bei Amicus Theologi

Wir möchten eine wissenschaftlich zuverlässige, kostenlose und langfristig wartbare Alternative für die bibelwissenschaftliche Arbeit entwickeln.

**Beiträge sind willkommen:** besonders reproduzierbare Fehlerberichte, reproduzierbare Morphologie- und Verszählungsfälle, Lizenznachweise für offene Textkorpora, Tests mit unterschiedlichen Betriebssystemen und Hinweise aus realen exegetischen Arbeitsabläufen.

Vor einem Pull Request: `python -m unittest discover -s tests -v` ausführen. Neue Importadapter sollen **stabile Referenzen, Datenausgabe und Metadaten** sorgfältig prüfen, unerkannte Formate ausdrücklich ablehnen und keine unannotierten Aussagen als belegte Morphologie präsentieren. Autor:innen müssen die Rechte der beigefügten Daten dokumentieren; keine geschützten Lexika oder Texte direkt ins Repository aufnehmen.

**Versionsverwaltung:** Branch pro Funktion oder Bugfix; Änderungen der Datenbankstruktur müssen im Changelog ausdrücklich genannt und migriert werden. Datenbankmigrationen müssen den Bestand respektieren und nach Möglichkeit nur additiv sein.

Projektquellcode: GPL-3.0-only. Dateninhalte behalten die jeweilige eigene Lizenz.
