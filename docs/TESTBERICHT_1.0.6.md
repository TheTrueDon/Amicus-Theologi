# Testbericht – Amicus Theologi 1.0.6

- **77 Python-Unittests bestanden** (`python -m unittest discover -s tests -q`), darunter drei neue Tests für neue/alte Einstellungen, Persistenz, unveränderte Module und Handbuch/Installer-Konsistenz.
- **JavaScript-Syntax erfolgreich** für die Browser- und Hilfeskripte (`node --check`).
- **HTTP-Starttest via FastAPI TestClient:** Programm, Hilfe und Status über die vorgesehenen Endpunkte erreichbar.
- **Chromium-Browsertest erfolgreich** mit nachgestellter API-Antwort und fünf Textmodulen: versweise Gruppierung nach Bibelstelle, korrekte Reihenfolge, Kennzeichnung fehlender Verse, ausgeblendete Ausgabe ohne Kapitelinhalt (Septuaginta in Johannes), Hover-Tooltip, Wortauswahl/Analyse, Aktivieren eines Verses, Wechsel zur alten Ausgabenansicht, Speicherung des Modus, Spracheinstellungen, keine JavaScript-Fehler.
- **Umgebungsgrenze:** Direkter Chromium-Aufruf einer lokalen HTTP-Adresse wurde durch die Sandbox blockiert. Deshalb erfolgte der Browsertest mit identischem Frontend und isolierten Testantworten, nicht mit einer echten Browser-Server-Verbindung. Windows-Installer und vollständige Originaldatenkorpora wurden in diesem Durchlauf nicht unter Windows neu getestet.
- **Datenbank:** keine Schemamigration; `text_layout` wird in der bestehenden Einstellungstabelle gesichert. Texte und persönliche Daten werden nicht überschrieben.
