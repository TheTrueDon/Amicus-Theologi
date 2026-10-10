# Prüfbericht – Amicus Theologi 1.0.1

Stand: 10.10.2026

## Automatisiert geprüft (Linux)

- **55 Unit-/API-Tests bestanden** (mit vorhandenen Tests aus 1.0).
- Benutzerhandbuch: lokale HTTP-Bereitstellung der HTML-, JS- und CSS-Datei, Suchfunktionscode vorhanden, anklickbare Kapitelanker, versionsfreie Hauptanwendung.
- Desktop-Launcher: `python windows/launcher.py --self-test` startet eine lokale FastAPI-Anwendung, prüft die API und das Handbuch, beendet den Dienst und verwendet einen isolierten Datenordner.
- JS-Syntaxprüfung für `frontend/app.js`, `frontend/workflow.js`, `frontend/release1.js` und `ANLEITUNG.js`.
- Paketprüfung auf erforderliche Assets, Dokumentation, Skripte und Ausschluss von Testdatenbanken.
- Keine neuen Datenbanktabellen und keine Migration zur Version 1.0.1.

## Erforderliche Windows-Prüfung vor breiter Veröffentlichung

- Windows-Build über GitHub Actions (PyInstaller) erfolgreich; `.exe --self-test` erfolgreich.
- Inno Setup 6 erzeugt die tatsächliche Windows-Setup-EXE.
- Setup-Assistent startet auf einem Windows-10/11-Rechner, legt Startmenü-/Desktopverknüpfungen an, Symbol wird korrekt angezeigt.
- Ersteinrichtung mit lokal installiertem Beispielkorpus.
- Updates von Version 1.0.0 auf 1.0.1 erhalten persönliche Notizen und installierte Module.
- Deinstallation lässt Benutzerdaten bewusst zurück.
- Start/Beenden über Steuerfenster und Handbuch offline.
- Keine unaufgeforderten Internetzugriffe außer ausdrücklich gestarteten Moduldownloads.

Das Windows-Binary kann unter Linux nicht zuverlässig erzeugt oder GUI-getestet werden. Der Installer-Quellcode und CI-Workflow sind fertig, **die tatsächliche Setup-EXE muss durch einen Windows-Build erzeugt und dort getestet werden**. Das GitHub-Artefakt ist zunächst nicht digital signiert; vor einer öffentlichen Veröffentlichung sind Signatur und Tests auf einem sauberen Windows-Gerät empfehlenswert.
