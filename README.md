# Amicus Theologi 📖

**Freie, offlinefähige Studienumgebung für wissenschaftliche Bibelarbeit – Entwicklungsstand 1.3.2.**

> **Optionaler Testzweig Quellenstudium (noch kein Release):** Auf Basis
> des Entwicklungsstands 1.3.2 öffnet sich ein separates Fenster für außerbiblische
> Primärtexte in Latein, Altgriechisch und Hebräisch. Enthalten sind
> manuelle Quellen-, Annotationen- und Lexikonimporte, ein viergeteilter
> Ein-Klick-Katalog (u. a. Augustinus, Clemens, PTA, Sefaria, LSJ,
> Georges und UD-Treebanks), zusätzlich die annotierten *Confessiones*
> (CIRCSE) und die automatisch analysierte Severian-Ausgabe (PTA),
> Wort-Tooltips, Textnavigation, Suche, Statistiken und Notizen.
> Für reine Texteditionen sind nur Vergleichskorpus-Vorschläge möglich,
> keine als gesichert ausgegebenen Wortanalysen.
> **Anleitung:** [docs/QUELLENSTUDIUM.md](docs/QUELLENSTUDIUM.md).

Amicus Theologi bietet eine dreigeteilte Oberfläche aus **Suche · Bibeltext · Analyse**, griechisch/hebräische Wortinformationen, importierbare Bibelausgaben und Lexika, exegetische Studienprojekte, eine begrenzte Synopse und textkritische Vergleiche. Bei den vorkompilierten Windows-/Ubuntu-Installern ist **keine zusätzliche Python-Installation** erforderlich; Internet wird nur zum Herunterladen neuer wissenschaftlicher Datenmodule benötigt. Beim Start aus dem Quellcode-ZIP müssen Python-Abhängigkeiten zunächst installiert werden.

**Dokumentation:** [Vollständiges Benutzerhandbuch](ANLEITUNG.html) ·
[Schnellstart](docs/SCHNELLSTART.md) ·
[Quellenstudium](docs/QUELLENSTUDIUM.md) ·
[Änderungsprotokoll](docs/CHANGELOG.md).

Der Entwicklungszweig `feature/quellenstudium` ergänzt einen eigenen Arbeitsbereich
für außerbiblische lateinische, altgriechische und hebräische Texte. Im Erststart-
Dialog lassen sich mit einem Klick die mitgelieferten Quellenpakete und sämtliche
installierbaren Einträge aus Bibel-, Textmodul- und Quellenkatalog einrichten.
Die Fortschrittsanzeige nennt Quelle und Status; einzelne Fehler halten den Lauf
nicht auf. Eine lokale Installation funktioniert danach offline. Externe
Nachschlageportale bleiben Links. Der Quellenkatalog unterstützt außerdem
Importpakete (`.amicus-source`), Übersetzungen pro Werk, optionale positionsgenaue
Wortdaten, Suche, Lexika, Statistiken sowie Notizen pro Quellenstelle.

> **Wissenschaftliche Einordnung:** 1.0 ist die erste zusammengeführte, getestete *Anwendungsbasis*, kein nachgewiesener vollständiger Ersatz für BibleWorks und keine vollständige kritische Textedition. Einige Quellformate (insbesondere STEPBible TAHOT und SWORD) sind noch experimentell. Angaben zu Morphologie und Wortbedeutung stammen aus den installierten Datensätzen; unbekannte Codes werden nicht geraten.


## Neu in 1.2.0: Suchabfragen speichern

Morphologische Suchabfragen lassen sich benennen und lokal sichern. Kriterien, Textmodul, Buchfilter, Abstand, Reihenfolge und Erstellungszeitpunkt werden gespeichert. Du kannst eine gespeicherte Abfrage laden, erneut ausführen oder löschen. Beim ersten Start wird dafür eine neue Tabelle angelegt; bestehende Daten bleiben erhalten.

## Neu in 1.3.0: Grafischer Abfrageeditor

Die morphologische Suche kann bis zu fünf Wortbedingungen mit UND oder ODER verknüpfen. Bei UND lassen sich Bedingungsreihenfolge und maximaler Abstand zwischen benachbarten Bedingungen festlegen. Gespeicherte Suchen aus 1.2.0 bleiben lesbar; neue Abfragen werden als strukturierte Kriterien gesichert. Für 1.3.0 ist keine weitere Datenbankmigration erforderlich.

## Neu in 1.3.1: Positionsbedingungen

Jede Wortbedingung kann auf den Versanfang (Tokenposition 1) oder einen inklusiven Tokenpositionsbereich eingeschränkt werden. Tokenpositionen beginnen in jedem Vers bei 1. Die Vorgaben wirken mit UND und ODER; Suchabfragen aus 1.3.0 funktionieren weiter. Es ist keine zusätzliche Datenbankmigration nötig.

## Entwicklungsstand 1.3.2: Quellen mit einem Klick einrichten

Beim ersten Start und nach einem Werksreset kann der Willkommensdialog alle
mitgelieferten Quellenpakete und alle installierbaren Onlineeinträge aus den
Bibel-, Textmodul- und Quellenkatalogen nacheinander installieren. Bereits
vorhandene Module werden übersprungen. Die Anzeige nennt die aktuell bearbeitete
Quelle, den Gesamtfortschritt und einzelne Fehler; ein Fehler hält die übrigen
Installationen nicht auf. Externe Forschungshilfen bleiben Links, da sie keine
lokal installierbaren Datenmodule sind. Onlineinstallationen benötigen eine
Internetverbindung. Die Anwendung verwendet dafür keine zusätzliche
Datenbanktabelle.

## Aus 1.1.2: Wortformensuche nach Bibelbuch filtern

In der Wortformenübersicht kannst du auf eine Form klicken, um sie im ausgewählten Modul exakt zu suchen. Ein Klick auf ein Buch in der Häufigkeitsverteilung schränkt dieselbe Suche auf dieses Buch ein.

## Aus 1.1.1: Wortdaten gezielt prüfen

Im Textmodul-Dialog kann für griechische und hebräische Ausgaben eine Prüfung gestartet werden. Sie vergleicht die gespeicherten Wortoberflächen mit dem Vers, kontrolliert die lückenlose Reihenfolge der Tokenpositionen und meldet fehlende Lemma-/Morphologiefelder. Das Ergebnis ist eine interne Datenkonsistenzprüfung, kein Nachweis für Vollständigkeit, Lizenz oder wissenschaftliche Richtigkeit. Es werden keine Daten verändert.

## Aus 1.1.0: Wortformen und Datenabdeckung

Die Wortanalyse zeigt jetzt für ein Lemma alle im gewählten Modul tatsächlich belegten Schreibweisen, deren Häufigkeiten und Verteilung nach biblischen Büchern. Eine Form kann direkt als exakte Wortsuche geöffnet werden. Die Datenbankdiagnose weist zusätzlich aus, in wie vielen Versen Wortannotationen vorhanden sind. Diese Abdeckung ist kein Vollständigkeits- oder Qualitätsnachweis. Keine Migration erforderlich.

## Aus 1.0.9: Amicus-Datenverzeichnis und vollständige Deinstallation

Beim ersten Start werden bisherige lokale Daten sicher in den neuen Amicus-Datenordner verschoben. Ein Update erhält die Daten; eine vollständige Deinstallation löscht Datenbank, Module, Notizen und interne Backups. Vor der Deinstallation externe Sicherung erstellen. Bei vorhandenen Daten in beiden Verzeichnissen wird nichts überschrieben.

## Aus 1.0.8: Grafischer Ubuntu-Installer

- **Ubuntu 24.04 (x86_64) und neuere kompatible Systeme:** Installer mit GitHub Actions unter **Ubuntu installation package** bauen.
- Doppelklick auf das `.deb`: grafische Installation über Ubuntu App Center, anschließend Start mit eigenem Icon im Anwendungsmenü.
- **Python ist bereits im fertig gebauten Ubuntu-Paket enthalten.** Kein Terminal oder separates Python für Anwender nötig.
- Optionales Desktop-Icon, normale Deinstallation über die Softwareverwaltung und unveränderte persönliche Daten.
- Anleitung: [`docs/UBUNTU_INSTALLATION.md`](docs/UBUNTU_INSTALLATION.md). Das Quellcode-ZIP ist **nicht** das fertige DEB.

## Aus Version 1.0.7: Hebräische Wortanalyse repariert

- **Hebräische Grundformen:** Numerische OSHB-Lemmata (z. B. `c/m/6529`) werden im Tooltip nicht mehr als angebliche Grundformen angezeigt. Amicus löst die hebräische Grundform aus einem installierten Lexikon über den zugehörigen Strong-Schlüssel auf.
- **Bedeutung:** Grammatische Kennzeichnungen wie „Prefix“ werden nicht mehr als Übersetzungen ausgegeben. Es werden quellgestützte deutsche oder englische Kurzglossen angezeigt, wenn verfügbar.
- **Morphologie:** Einfache und zusammengesetzte OSHB-Codes, etwa `HVqp3ms` oder `HC/R/Ncfsa`, werden in lesbare deutsche Angaben zerlegt. Unbekannte Codes bleiben weiterhin unverändert abrufbar.
- **Update:** Keine Datenbankmigration und keine Neuinstallation bestehender Korpora notwendig. Für hebräische Grundformen und Übersetzungen wird ein installiertes Lexikon wie **TBESH** benötigt.

## Loslegen – ohne Informatikkenntnisse

**Ubuntu-Installer:** über GitHub Actions **Ubuntu installation package** das fertige `.deb` erstellen, herunterladen und per Doppelklick im Ubuntu App Center installieren. Danach Amicus über das Anwendungsmenü starten. Keine separate Python-Installation erforderlich. [Schritt-für-Schritt-Anleitung](docs/UBUNTU_INSTALLATION.md).

**Windows-Installer:** über GitHub Actions **Windows installation package** die Setup-EXE erstellen, per Doppelklick installieren und über Startmenü/Desktop starten. Python ist enthalten.

**Windows:** [Python 3.10 oder neuer](https://www.python.org/downloads/) installieren (bei der Installation „Add Python to PATH“ aktivieren), ZIP entpacken, `start_windows.bat` doppelklicken. Beim ersten Mal lädt das Programm die benötigten Komponenten. Danach öffnet sich Amicus Theologi im Browser.

**Ubuntu / Linux:** ZIP entpacken, Terminal im entpackten Ordner öffnen und `bash start_linux.sh` ausführen. Unter Ubuntu müssen ggf. zuerst die Pakete `python3`, `python3-venv` und `python3-pip` installiert werden. Optional: `bash install_linux_desktop.sh` legt einen Menüeintrag an.

**Windows-Desktopverknüpfung (optional):** Die Datei `install_windows_shortcut.ps1` erstellt eine Desktopverknüpfung, wenn du sie über PowerShell ausführst. Die normalen Startskripte reichen ansonsten aus.

Im Browser erscheint beim ersten Start die **dreiteilige Einführung**. „Alle verfügbaren Quellen installieren“ richtet die installierbaren Bibelausgaben, Quellenkataloge und mitgelieferten Offlinepakete ein; die Fortschrittsanzeige nennt den aktuellen Titel und einzelne Fehler. Für Onlinequellen ist Internet erforderlich. „Mini-Beispiele installieren“ bleibt als kleine Offline-Alternative zum Ausprobieren verfügbar.

📗 Eine verständliche Schritt-für-Schritt-Anleitung: [docs/SCHNELLSTART.md](docs/SCHNELLSTART.md). Auch die Datei `ANLEITUNG.html` lässt sich direkt im Browser öffnen; für die Suche werden `ANLEITUNG.js` und `ANLEITUNG.css` aus demselben Ordner geladen.

## Neu in 1.0.6: Versweiser Bibelvergleich

Im mittleren Textfenster werden Bibelausgaben standardmäßig **nach Versnummer** gruppiert: zuerst Vers 1 aus allen ausgewählten Ausgaben, dann Vers 2 usw. So sind Satzstruktur und Übersetzung schnell vergleichbar. Mit **Darstellung → Nach Ausgabe anzeigen** lässt sich die bisherige kapitelweise Sortierung wiederherstellen. Die Einstellung bleibt gespeichert. Wenn einzelne Ausgaben einen Vers nicht enthalten, wird dies ausdrücklich ausgewiesen; ein solcher Datenmangel ist **kein** textkritischer Nachweis. Für die Septuaginta gibt es z. B. im Johannesevangelium kein Kapitel, da sie das griechische Alte Testament umfasst.

**Keine Datenbankschemaänderung.** Die zusätzliche Einstellung `text_layout` wird in der bestehenden `settings`-Tabelle gespeichert; Texte und Projekte bleiben unverändert.

## Neu in 1.0.5: Bibelübersetzungen mit einem Klick

Über **Bibelausgaben** können historische deutsche Textausgaben aus dem offiziellen CrossWire-Katalog heruntergeladen werden, beispielsweise die **Elberfelder 1905** oder **Menge 1939**. Über **Ausgaben auswählen** direkt oberhalb des Bibeltextes lassen sich einzelne oder mehrere Übersetzungen ein- und ausblenden und die Reihenfolge festlegen. Die Auswahl wird lokal gespeichert und gilt nicht für den unabhängigen Suchfilter. Technische Angaben und Grenzen stehen in [docs/BIBELAUSGABEN.md](docs/BIBELAUSGABEN.md).

Der Windows-Build bündelt die zusätzliche SWORD-Lesebibliothek **PySword**. **Datenbankschema unverändert.** Für die Original-SWORD-Dateien steht noch ein Live-Integrationstest aus.

## Neu in 1.0.4: Echte Lexikonübersetzungen und sortierbare Konkordanz

STEPBible-Transliterationen werden in der Wortvorschau nicht mehr als Bedeutungen ausgegeben. Die Anwendung sucht echte Kurzglossen in bereits installierten Lexika, nach Möglichkeit auf Deutsch, sonst Englisch. Ein Lexikoneintrag ohne zuverlässig extrahierbare Bedeutung wird als fehlend gekennzeichnet. Bereits installierte Lexikonmodule müssen dafür **nicht** erneut geladen werden. Im Dialog „Alle Vorkommen dieses Lemmas“ kann die komplette Liste nach kanonischer Bibelstelle oder Wortform, aufsteigend/absteigend sortiert werden; Seitenwechsel respektieren die Sortierung.

**Keine Datenbankänderung:** Die Analyse der Lexikoneinträge erfolgt beim Anzeigen; die Originaldaten bleiben erhalten.

## Seit 1.0.2: Wortvorschau, lesbare Lexika, Lemma-Konkordanz

Beim Darüberfahren über ein annotiertes Wort erscheint eine Vorschau mit Grundform, vorhandener Kurzglosse und grammatischen Angaben. Die Wortanalyse zeigt STEPBible-Lexika formatiert an; unter „Originaldaten anzeigen“ bleibt die Quelle unverändert einsehbar. „Alle Vorkommen dieses Lemmas“ öffnet eine eigene, seitenweise durchsuchbare Konkordanz.

## Bereits ab 1.0.1: Ausführliche Suche im Handbuch und Windows-Setup

- **`ANLEITUNG.html`**: großes, offline nutzbares Benutzerhandbuch mit JavaScript-Volltextsuche, kopierbaren Suchbeispielen, FAQ, Grammatik, Lexika, Textkritik und Datensicherung. Im Programm öffnet **F1** oder **Handbuch** die Anleitung.
- **Windows-Setup als Build**: Inno Setup erstellt einen normalen Installationsassistenten mit Startmenü-Verknüpfung, optionalem Desktop-Icon und Deinstallation. Die Python-Laufzeit wird durch PyInstaller eingebettet – Anwender müssen Python nicht installieren.
- **Wichtig:** Ein ausführbares Windows-Setup ist **nicht bereits im plattformneutralen Quellcode-ZIP**. Der beigefügte GitHub-Actions-Workflow erstellt es automatisiert auf Windows (Details: [docs/WINDOWS_INSTALLATION.md](docs/WINDOWS_INSTALLATION.md)).
- **Keine neue Datenbanktabelle / Migration.** Bestehende Bibliotheks- und Nutzerdaten bleiben erhalten.

## Was funktioniert?

| Bereich | Stand |
| --- | --- |
| Mehrere Texte / Navigation | lokal installierte Ausgaben, kapitelweise synchron |
| Volltextsuche | SQLite FTS5, Filter und einfache Suchsyntax |
| Wortanalyse | importierte griechische/hebräische Annotationen, Lemma-Konkordanz, übersetzte Standard-Codes |
| Wortformen | belegte Formen, Häufigkeit und Buchverteilung je Lemma; exakte Suche aus der Formenliste |
| Morphologische Suche | bis zu fünf Wortbedingungen, UND/ODER, Abstand / Reihenfolge, Tokenpositionsbereiche, Stringfilter in Morph-Codes |
| Gespeicherte Suchen | strukturierte Kriterien, Modul- und Buchfilter lokal benennen, speichern und erneut ausführen; 1.2-Abfragen bleiben erhalten |
| Wörterbücher | TSV/CSV-Import, experimentelle Direktinstallation ausgewählter STEPBible-Lexika |
| Persönliche Studien | Projekte, Notizen, Markierungen, JSON-Export einzelner Projekte |
| Ausgabenvergleich / Synopse | 2–4 Ausgaben, neun beispielhafte Parallelperikopen, importierte dokumentierte Varianten |
| Bedienung | Befehlssuche Strg+K, Referenz-Verlauf, Tastenkürzel |
| Diagnose | Datenbankprüfung und Versabdeckung der Wortannotationen je Modul; kein Vollständigkeitsnachweis |
| Neu in 1.0 | Erststart-Einführung, vollständige Sicherung, geführte Rücksicherung, Gesundheitscheck, Startskripte |

## Vollständige Sicherung und Wiederherstellung

Oben auf **Datensicherung** klicken → **„Vollständige Sicherung herunterladen“**. Das ZIP enthält **alle lokal gespeicherten Texte, Wortdaten, Lexika, Projekte und Einstellungen**. Bewahre eine Kopie außerhalb dieses Computers auf.

Für die Rücksicherung: **Datensicherung → gesichertes ZIP auswählen → Wiederherstellung vorbereiten**. Amicus kontrolliert Dateiformat, Prüfsumme und Datenbankintegrität. **Erst nach vollständigem Beenden und Neustarten** ersetzt es den aktuellen Stand. Vor dem Ersetzen erstellt es automatisch eine zusätzliche Sicherheitskopie.

**Update von 0.9:** Entpacke 1.0 in einen neuen Ordner und starte das Programm. Es verwendet den bestehenden Datenordner weiterhin. Beim ersten Start von 1.0 wird vor einer eventuell notwendigen Migration automatisch eine vollständige Sicherung unter `backups/` erstellt. Eine manuelle Migration ist nicht nötig und **das bestehende Datenbankschema wird für die 1.0-Funktionen nicht erweitert** (lediglich eine Versionseinstellung wird gespeichert).

Der neue Standard-Datenordner heißt:
- Linux: `~/.local/share/amicus-theologi/` (bzw. `$XDG_DATA_HOME/amicus-theologi`)
- Windows: `%LOCALAPPDATA%\AmicusTheologi\`
- Alternative: Umgebungsvariable `AMICUS_THEOLOGI_DATA_DIR`

Bei bisherigen Installationen werden die Daten beim ersten Start automatisch umgezogen. Beachte: Der Browser speichert die Liste zuletzt besuchter Stellen getrennt im jeweiligen Browser-Profil; die ZIP-Sicherung erfasst die lokalen SQLite-Daten, **nicht** den Browser-Verlauf.

## Datenquellen und Grenzen

- **STEPBible:** https://github.com/STEPBible/STEPBible-Data – viele Daten CC BY 4.0, mit Quellenattribution und teils getrennten Bedingungen.
- **Open Scriptures Hebrew Bible:** https://github.com/openscriptures/morphhb – WLC-Text gemeinfrei, Lemma/Morphologie CC BY 4.0.
- **CrossWire/SWORD:** https://www.crosswire.org/sword/ – jedes Modul hat eine eigene Lizenz. Der Import benötigt derzeit ggf. die optionale Bibliothek `pysword` und unterstützt nicht jedes Format.

Amicus lädt **keine unrechtmäßig kopierten kommerziellen Editionen** mit. Die aktuell verfügbaren Quellen und Editionen sind vor wissenschaftlichen Publikationen auf Vollständigkeit, Textstand, Verszählung, Rechte und Annotationen zu prüfen. Weitere Hinweise: [docs/WISSENSCHAFTLICHE_DATEN.md](docs/WISSENSCHAFTLICHE_DATEN.md).

## Entwicklung / Tests

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
node --check frontend/app.js
node --check frontend/workflow.js
node --check frontend/release1.js
node --check ANLEITUNG.js
```

Die API ist auf `127.0.0.1` gebunden, blockiert fremde HTTP-Hosts und Cross-Origin-Schreibzugriffe. Es gibt keine Nutzerkonten, Telemetrie oder KI-Pflicht. **Nicht als öffentlich erreichbaren Webserver betreiben:** Für einen Mehrbenutzerbetrieb bräuchte die Anwendung gesonderte Authentifizierung und Rechteverwaltung.

[Architektur](docs/ARCHITEKTUR.md) · [Roadmap](docs/ROADMAP.md) · [Changelog](docs/CHANGELOG.md) · [Hinweise für Mitwirkende](CONTRIBUTING.md) · [Sicherheit](SECURITY.md)

## Lizenz

Amicus-Theologi-Quellcode: **GNU GPL-3.0-only** (siehe [LICENSE](LICENSE)). **Datenmodule besitzen eigene Lizenzbedingungen**; das GPL-Label auf dem Code erteilt keine Rechte an fremden Bibeltexten. Bei einer Veröffentlichung des Repositories sollten Projektverantwortliche Copyright- und Lizenzangaben nochmals prüfen.
