# Architektur 0.1

`start.py` startet Uvicorn auf einer zufälligen lokalen Loopback-Portnummer. `backend/main.py` stellt die API bereit und liefert das statische Frontend. `backend/database.py` initialisiert eine langlebige SQLite-Datenbank im Benutzerverzeichnis. Das Frontend nutzt `fetch()`.

Datenmodell: `modules` (Editionen und Lizenzmetadaten), `verses` (kanonische Referenz **vorläufig**, Buchkürzel), `tokens` (Wortpositionen und morphologische Annotationen), `verse_mapping` (abweichende Verszählung, noch ohne Algorithmus) und `settings`.

**Wichtig:** Die Tabellen sind ein bewusst kleiner Anfang und **noch kein endgültiges Bibelstellenmodell**. Vor 0.2 werden standardisierte Buch-IDs, deuterokanonische Bücher, versfreie Überschriften sowie Unterschiede der Verszählung detailliert spezifiziert.

API: `GET /api/status`, `GET /api/settings`, `PATCH /api/settings`, `GET /api/modules`, `GET /api/verses?book=Joh&chapter=1&verse=1`.

Spätere modulare Adapter: OSIS/SWORD. Keine Fremdsoftware oder Texteditionen im Lieferumfang.
