# Amicus Theologi – Ubuntu-Installationspaket

## Installation für Anwenderinnen und Anwender

Du benötigst **Ubuntu 24.04 oder neuer (64-Bit-x86_64)**. Das von GitHub Actions erzeugte `.deb` enthält die Python-Laufzeit und die verwendeten Python-Bibliotheken. Du musst Python nicht selbst installieren.

1. Das GitHub-Repository öffnen → **Actions** → **Ubuntu installation package**.
2. **Run workflow** starten; nach erfolgreichem Build unten unter **Artifacts** das Paket **Amicus-Theologi-Ubuntu-Installer** herunterladen.
3. Das Artifact-ZIP entpacken; die Datei `Amicus-Theologi-1.3.0-Ubuntu-24.04-amd64.deb` per Doppelklick öffnen.
4. Im **Ubuntu App Center** auf **Installieren** klicken und das Systempasswort bestätigen. Wenn die Datei nicht automatisch mit dem App Center geöffnet wird: Rechtsklick → **Öffnen mit** → **App Center**.
5. Das Programm über **Aktivitäten / Anwendungen → Amicus Theologi** starten. Beim ersten Start erscheint ein kleines Steuerfenster, das den lokalen Browser öffnet.
6. Optional im Anwendungsmenü **Amicus Theologi – Desktopverknüpfung** öffnen und die Nachfrage bestätigen; je nach GNOME-Einstellungen muss das neue Desktop-Icon als vertrauenswürdig markiert werden. Über einen Rechtsklick auf das App-Symbol kann es außerdem ans Dock angeheftet werden.

**Für die spätere Nutzung ist keine Internetverbindung erforderlich**, sobald alle gewünschten Textmodule installiert sind. Internet wird nur für das Nachladen neuer Bibeltexte/Lexika benötigt. **Die Benutzerin muss nicht im Terminal arbeiten.**

### Update und Deinstallation

Ein neues `.deb` installiert das Programm über die vorhandene Ausgabe. Bereits importierte Bibeltexte, Lexika und Studienprojekte verbleiben im Benutzerordner (`~/.local/share/amicus-theologi/`). Vor größeren Updates trotzdem die integrierte Datensicherung nutzen.

Über Ubuntu App Center beziehungsweise die System-Softwareverwaltung lässt sich Amicus wieder entfernen. Die persönlichen Daten bleiben aus Sicherheitsgründen erhalten. Ein vollständiger Datenreset kann innerhalb von Amicus mit der Werksreset-Funktion ausgeführt werden.

### Das ist anders als unter Windows

Ubuntu zeigt keinen identischen Inno-Setup-Assistenten. Die grafische Installation und die Passwortabfrage übernimmt das Ubuntu App Center, der übliche Weg für DEB-Pakete. Das Ergebnis – installiertes Programm mit Icon, Anwendungsmenü und Deinstallation – ist vergleichbar.

## Erstellung für Entwickler

Der Workflow `.github/workflows/ubuntu-installer.yml` führt auf `ubuntu-24.04` Folgendes durch:

1. Python-3.12-venv mit Projektabhängigkeiten und PyInstaller einrichten.
2. Unittests und JavaScript-Syntax überprüfen.
3. Mit `linux/build_ubuntu_deb.sh` einen gefrorenen Linux-PyInstaller-Ordner erzeugen.
4. Das Binary ohne grafische Sitzung über `--self-test` prüfen; zusätzlich die Tk-GUI unter Xvfb über `--gui-self-test` starten.
5. Das Binärprogramm nach `/opt/amicus-theologi/`, das Icon nach `/usr/share/icons/` und die `.desktop`-Dateien nach `/usr/share/applications/` packen.
6. Das `.deb` erstellen, Metadaten und Paketinhalt prüfen und als GitHub-Artifact hochladen.

**Lokal auf Ubuntu 24.04:** Python-Virtualenv mit `requirements-dev.txt` und `pyinstaller>=6.15,<7` erstellen, anschließend `AMICUS_BUILD_PYTHON=.venv/bin/python bash linux/build_ubuntu_deb.sh` ausführen. Die Ubuntu-Buildumgebung benötigt zusätzlich tkinter, Xvfb und dpkg. Das Paket erscheint unter `dist_installer/`.

### Architektur und Kompatibilität

Der offizielle Build wird auf Ubuntu 24.04/amd64 erstellt (glibc 2.39). Ubuntu 22.04 und ARM64 sind **nicht** dadurch abgedeckt. Die App verwendet Tkinter für den lokalen Starter und den Browser für die Hauptoberfläche. Das Paket ist nicht digital signiert und wird nicht automatisch über ein eigenes APT-Repository aktualisiert.

### Datenbank und Sicherheit

Version 1.2.0 legte beim Start additiv die Tabelle `saved_searches` an. Version 1.3.0 benötigt keine weitere Datenbankmigration; vorhandene Verse, Annotationen, gespeicherte Suchen und Studien bleiben erhalten. Das `.deb` enthält keine Nutzerdaten und keine urheberrechtlich geschützten Bibelwerke. Es installiert nichts automatisch aus dem Internet. Bei der Deinstallation löscht ein postrm-Skript lokale Anwendungsdaten; bei Updates nicht.


## Vollständige Deinstallation

Beim Entfernen des Debian-Pakets löscht der postrm-Hook die lokalen Amicus-Daten aus Standardverzeichnissen der Benutzer. Persönliche Notizen, Bibelmodule und interne Backups gehen verloren. Deshalb vorher extern sichern! Bei einem Upgrade bleiben die Daten erhalten. Ein benutzerdefinierter Pfad aus AMICUS_THEOLOGI_DATA_DIR ist nicht automatisch ermittelbar und muss separat gelöscht werden.
