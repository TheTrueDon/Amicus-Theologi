# Architektur 0.2

FastAPI (Python) liefert eine lokale API unter `127.0.0.1` und stellt die statischen HTML/CSS/JS-Dateien bereit. SQLite hält Benutzerkonfiguration, Module, Verse sowie vorläufig die schon in 0.1 angelegten Tabellen für Token/Referenzmappings. Keine Online-Dienste, Loginserver oder KI.

## API

- `GET /api/status` Version und Modulanzahl
- `GET/PATCH /api/settings` lokale Konfiguration
- `GET /api/books` 66 kanonische Bücher
- `GET /api/reference?q=Joh%201,1` Referenz parsen
- `GET /api/chapter?book=Joh&chapter=1` parallele Kapitelansicht
- `GET /api/verses?book=Joh&chapter=1&verse=1` einzelner Vers
- `GET /api/modules` Modulübersicht
- `POST /api/modules/import` multipart-Datei und Metadaten
- `DELETE /api/modules/{module_id}` explizite Entfernung

## Sicherheit und Grenzen

Importprüfungen: Größe 12 MB, maximal 200.000 Verse, UTF-8, Spalten und Referenzen validiert, keine direkten SQL-Strings aus Texteingaben, eindeutige Modul-IDs. Die App ist ein lokales Einzelplatzwerkzeug, **nicht zur Veröffentlichung im Internet bestimmt**: keine Authentifizierung und keine CSRF-Abwehr für Schreibendpunkte. Nur an 127.0.0.1 binden.

Ab Version 0.3 tokenbasierte Indizes und Volltextzugriff auf importierte Module. Versifikationsmappings und OSIS/SWORD sind noch nicht implementiert.


## Suchindex 0.3
`verse_fts` ist eine FTS5-External-Content-Tabelle auf `verses.rowid` mit `unicode61`-Tokenizer. Drei Trigger halten INSERT, UPDATE und DELETE synchron. `fts_schema_version` ist eine interne Migrationsmarke in `settings`. Der Abfragetext wird in `backend/search.py` in eine eingeschränkte, parametrisierte FTS5-Abfrage übersetzt. Ohne Morphologie-Annotationen ist nur Textsuche möglich.
