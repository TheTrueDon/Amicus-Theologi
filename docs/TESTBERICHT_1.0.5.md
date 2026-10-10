# Testbericht – Amicus Theologi 1.0.5

- **74 Python-Unittests** bestanden (`python -m unittest discover -s tests -q`), darunter sechs neue Tests für den CrossWire-Katalog, transaktionalen Import, Dubletten, alte Einstellungen und unverändertes Schema.
- **JavaScript-Syntax** bestanden (`node --check frontend/app.js`, `node --check frontend/editions.js`).
- **API-Starttest**: lokale Uvicorn-App antwortet mit Version 1.0.5.
- **Chromium-Komponententest** mit isolierten Testdaten und nachgestellten API-Antworten: Oberfläche lädt fehlerfrei, drei Textausgaben auswählbar, „Nur Deutsch“ → zwei Ausgaben, „Nur Originalsprachen“ → eine Ausgabe, Bibliothekskatalog öffnet.
- **Nicht abgeschlossen**: automatisierter Live-Ende-zu-Ende-Import der fünf aktuellen CrossWire-ZIP-Pakete, vollständiger Windows-Installer-Lauf und grafischer Test auf einem realen Windows-Desktop. Das Testsystem kann die externen Archive nicht beziehen.
- **Datenbankmigration:** keine Tabellen- oder Indexänderung; zwei Einstellungen werden durch den vorhandenen Settings-Mechanismus ergänzt.
