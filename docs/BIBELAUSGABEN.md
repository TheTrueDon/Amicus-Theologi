# Bibelausgaben auswählen und installieren (Amicus Theologi 1.0.5)

## So einfach geht es

1. In der oberen Leiste **Bibelausgaben** anklicken.
2. Die gewünschte historische Übersetzung auswählen, z. B. **Elberfelder 1905**.
3. **Installieren** anklicken. Amicus lädt das SWORD-Raw-ZIP von CrossWire und liest das Textmodul ein.
4. Danach erscheint die Ausgabe im Bereich **Bibeltext**. Bei Bedarf **Ausgaben auswählen** anklicken.
5. Mehrere Ausgaben anhaken; bei Bedarf mit ↑ und ↓ die Anzeigereihenfolge verändern.

Im Textfenster können aktive Ausgaben direkt durch Anklicken ihres kleinen Chips (×) ausgeblendet werden. **Ausgaben auswählen** bietet auch „Alle anzeigen“, „Alle abwählen“, „Nur Deutsch“ und „Nur Originalsprachen“.

Die Auswahl und die Anzeigereihenfolge werden in den bestehenden lokalen **Einstellungen** gespeichert; sie verändern **keine** Bibeltextdaten und sind unabhängig vom Suchfilter links. Installierte Ausgaben können weiterhin im Modulmanager entfernt werden.

## Curatierte CrossWire-Bibelausgaben

| Kennung | Text | Repository |
|---|---|---|
| GerElb1905 | Elberfelder 1905 | reguläre CrossWire-Module |
| GerElb1871 | Elberfelder 1871 | reguläre CrossWire-Module |
| GerMenge | Menge-Bibel 1939 | reguläre CrossWire-Module |
| GerTextbibel | Textbibel 1906 | reguläre CrossWire-Module |
| GerLut1912 | Lutherbibel 1912 | CrossWire-Beta-Module |

Diese fünf Ausgaben sind in den offiziellen CrossWire-Metadaten als **Public Domain** gekennzeichnet. Das gilt nicht automatisch für moderne Elberfelder-, Luther- oder andere Bibelübersetzungen. **Rechte, Edition und Eignung jeder Ausgabe vor einer wissenschaftlichen Publikation prüfen.** Das Programm selbst enthält die Texte nicht.

Originalquellen:

- https://www.crosswire.org/sword/modules/ModDisp.jsp?modType=Bibles
- https://www.crosswire.org/sword/modules/ModInfo.jsp?modName=GerElb1905
- https://www.crosswire.org/sword/modules/ModInfo.jsp?modName=GerMenge
- https://www.crosswire.org/ftpmirror/pub/sword/packages/rawzip/
- https://www.crosswire.org/ftpmirror/pub/sword/betapackages/rawzip/

## Technische Grenzen

- Zum erstmaligen Herunterladen ist Internet erforderlich. Danach bleiben die importierten Texte lokal verfügbar.
- CrossWire liefert teils weitere Formate und komplexe Verszählungen. Der SWORD-Adapter verwendet PySword 0.2.8; nicht alle moduleigenen Zusätze, Versifikationen oder Kommentare werden übernommen.
- Die fünf aktuellen Original-ZIP-Pakete konnten in dieser Entwicklungsumgebung nicht vollständig geladen und Ende-zu-Ende gegen PySword geprüft werden. Deshalb muss die Ein-Klick-Installation der einzelnen Ausgaben im Windows-Build praktisch getestet werden.
- Installationen werden atomar gespeichert: Bei einem fehlgeschlagenen Import werden keine Teiltexte angelegt. Bereits vorhandene Module und Notizen bleiben erhalten.
- Ein importierter SWORD-Text ist nicht automatisch mit interaktiver griechischer/hebräischer Morphologie versehen. Dafür sind separate wissenschaftliche Annotationen nötig.
- Das Windows-Setup enthält PySword im Anwendungsbundle. Bei Start über den Quellcode installieren die Startskripte es aus `requirements.txt`.

## Update und Datenbank

**Keine Änderung des Datenbankschemas.** Die zwei neuen Einstellungen `display_module_ids` und `display_module_order` werden automatisch in der vorhandenen `settings`-Tabelle verwaltet. Vorhandene Textmodule und persönliche Projekte bleiben unverändert.
