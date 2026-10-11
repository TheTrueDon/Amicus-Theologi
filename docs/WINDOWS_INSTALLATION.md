# Windows-Installation (Version 1.0.7)

## Für Anwenderinnen und Anwender – einmal installieren, danach nur noch klicken

Die komfortable Installation erfolgt mit **`Amicus-Theologi-Setup-1.0.7.exe`**. Das ist eine **separat gebaute Windows-Datei**. Das veröffentlichte Quellcode-ZIP ist **nicht bereits diese Setup-Datei**. Ein Windows-Setup wird auf Windows oder über den beiliegenden GitHub-Actions-Build erzeugt.

1. Setup-EXE von einer vertrauenswürdigen Projektveröffentlichung herunterladen.
2. Doppelklicken, die Installation im Assistenten bestätigen und optional „Desktopverknüpfung erstellen“ aktivieren.
3. Danach **Amicus Theologi** im Windows-Startmenü auswählen – oder die Desktopverknüpfung doppelklicken.
4. Das kleine Steuerfenster zeigt an, dass Amicus läuft. Die Oberfläche öffnet sich im Browser. Mit „Im Browser öffnen“ kann man sie jederzeit erneut aufrufen; mit „Beenden“ wird der lokale Dienst gestoppt.
5. Zur Deinstallation: Windows **Einstellungen → Apps → Installierte Apps** → Amicus Theologi → Deinstallieren.

**Python muss nicht installiert werden.** Die Setup-Ausgabe verwendet PyInstaller, der Python und die benötigten Bibliotheken mitsamt der Anwendung bündelt. Daher gibt es auch keinen Python-Downloader im Installationsassistenten: Er wäre unnötig, benötigt Netzwerkzugriff und würde Python systemweit installieren, obwohl Amicus es nur intern benötigt.

**Internet** benötigt die Nutzerin *nur* zum erstmaligen Download des Setup-Pakets und später für gewünschte Textmodule. Einmal installiert, läuft die Anwendung lokal ohne Internet. **Updates erhalten bestehende Nutzerdaten.** Bei der Deinstallation werden Datenbank, installierte Module und interne Sicherungen im Standarddatenordner `%LOCALAPPDATA%\AmicusTheologi\` gelöscht. Vorher extern sichern!

### SmartScreen und digitale Signatur

Selbst erstellte oder über GitHub Actions gebaute EXE-Dateien sind zunächst **nicht digital signiert**. Windows SmartScreen kann deshalb eine Warnung anzeigen. Bitte EXE-Dateien nur aus einer vertrauenswürdigen, vom Projekt selbst veröffentlichten Quelle verwenden. Eine vertrauenswürdige, signierte Veröffentlichung erfordert künftig ein Code-Signing-Zertifikat und eine abgesicherte Release-Pipeline.

## Für die Projektverwaltung – so wird das Setup gebaut

### Variante A: GitHub Actions (ohne eigenen Windows-Entwicklungsrechner)

1. Das komplette Projekt einschließlich `.github/workflows/windows-installer.yml` in das Repository hochladen.
2. Repository → **Actions** → **Windows installation package** → **Run workflow**.
3. Auf den erfolgreichen Durchlauf warten. Er startet zuerst die Unit-Tests, baut unter Windows eine eigenständige Anwendung, führt eine Prüfung der eingebetteten EXE durch und erzeugt mit Inno Setup einen üblichen Windows-Installer.
4. Unter **Artifacts** die Datei `Amicus-Theologi-1.0.7-Windows-Installer` herunterladen.
5. Darin liegen `Amicus-Theologi-Setup-1.0.7.exe` sowie ein portables Windows-Archiv. Die Setup-EXE in der GitHub-Release-Veröffentlichung bereitstellen.

### Variante B: Eigener Windows-PC (Entwickler)

Benötigt: Python 3.12, Inno Setup 6, Internet für die Build-Abhängigkeiten. In einer PowerShell im Projektordner ausführen:

```powershell
./windows/build_windows.ps1
```

Das Skript installiert die Python-Buildpakete in der aktuellen Python-Umgebung, baut mit PyInstaller die Anwendung, prüft die eingefrorene EXE und erstellt anschließend `dist_installer/Amicus-Theologi-Setup-1.0.7.exe`. Für produktive Release-Builds besser eine eigens angelegte virtuelle Build-Umgebung verwenden.

### Verifikation

Der Workflow startet die gebündelte EXE mit `--self-test` auf einem isolierten temporären Datenordner und prüft eine lokale HTTP-Antwort sowie das Handbuch. Ein vollständiger manueller Test des grafischen Installationsassistenten auf einem realen Windows-Computer bleibt zusätzlich erforderlich (Installation, Verknüpfungen, Erststart, Deinstallation, Update von 1.0, Datenerhalt).

Das Paket bietet noch keinen Mehrbenutzer-Serverbetrieb. Eine installierte Windows-Anwendung läuft ausschließlich lokal auf `127.0.0.1`.


## Daten bei Deinstallation

Der Windows-Deinstallationsassistent entfernt den Standarddatenordner des aktuellen Benutzers, einschließlich Module, Studienprojekte und interner Sicherungen. Extern gespeicherte Sicherungen bleiben erhalten. Daten aus abweichend konfigurierten Speicherorten müssen separat gelöscht werden.
