# Windows-Build: UTF-8-Kodierung (Version 1.0.7)

Der GitHub-Actions-Test konnte unter Windows mit einem `UnicodeDecodeError` (cp1252) scheitern, wenn eine Testdatei HTML/JS ohne explizite Kodierung las.

Behebung: Tests lesen Textdateien explizit mit `encoding="utf-8"`. Der Windows-Workflow setzt außerdem `PYTHONUTF8=1` und `PYTHONIOENCODING=utf-8`.

Dadurch ändert sich weder das Datenbankschema noch die Anwendungsversion. Die Änderungen betreffen nur Build/Test. Der vollständige Build der Windows-EXE muss weiterhin in GitHub Actions geprüft werden.
