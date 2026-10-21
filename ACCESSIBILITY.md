# Erklärung zur Barrierefreiheit

**Stand: 21. Oktober 2026**

## Geltungsbereich

Diese Erklärung bezieht sich auf die lokal laufende Amicus-Theologi-Anwendung einschließlich des separaten Fensters **Quellenstudium** sowie auf die mit dem Projekt ausgelieferte Dokumentation. Die GitHub-Plattform und externe Nachschlageangebote liegen außerhalb des Einflussbereichs dieses Projekts und haben eigene Barrierefreiheitserklärungen.

## Stand der Barrierefreiheit

Amicus Theologi wird fortlaufend entwickelt. Es liegt derzeit kein unabhängiges Barrierefreiheitsaudit vor; das Projekt beansprucht deshalb keine vollständige Konformität mit WCAG oder einer anderen Norm.

Im aktuellen Frontend werden für viele Bedienelemente native HTML-Elemente, Beschriftungen und zugängliche Namen verwendet. Status- und Fehlermeldungen nutzen an mehreren Stellen ARIA-Live-Regionen. Für Teile der Oberfläche gibt es sichtbare Tastaturfokus-Markierungen. Einige häufige Aktionen besitzen Tastenkürzel, die im Benutzerhandbuch aufgeführt sind. Das sind vorhandene Maßnahmen, aber kein Nachweis, dass alle Abläufe mit jeder Kombination aus Tastatur, Browser und Hilfstechnologie funktionieren.

## Bekannte Grenzen

- Die Anwendung wurde noch nicht systematisch ausschließlich mit Tastatur und mit verbreiteten Screenreadern getestet. Beschriftungen und dynamische Rückmeldungen können daher uneinheitlich sein.
- Die Spaltenbreiten lassen sich über Ziehgriffe verändern. Die Bedienbarkeit dieser Ziehgriffe ohne Maus ist nicht verlässlich geprüft; **Layout zurücksetzen** stellt die Standardaufteilung wieder her.
- Komplexe Tabellen und Analysen sowie griechische und hebräische Schrift mit diakritischen Zeichen oder Schreibrichtung von rechts nach links können je nach Browser und Hilfstechnologie schwerer zu erfassen sein.
- Ein Hell-Dunkel-Thema ist verfügbar. Kontrast, Vergrößerung und Darstellung wurden jedoch nicht in allen Ansichten und Kombinationen vollständig geprüft.

## Rückmeldung und Unterstützung

Wenn du auf ein Barrierefreiheitsproblem stößt, melde es bitte über [einen Verbesserungsvorschlag im Issue-Tracker](https://github.com/TheTrueDon/Amicus-Theologi/issues/new?template=feature_request.yml). Wähle als Kontext **Barrierefreiheit** und beschreibe möglichst:

- die betroffene Ansicht und die Schritte zum Auftreten des Problems;
- Betriebssystem, Browser und verwendete Hilfstechnologie;
- was du erwartet hast und was tatsächlich passiert ist;
- falls vorhanden, einen möglichen Workaround.

Bitte veröffentliche keine privaten Studiennotizen, personenbezogenen Daten oder urheberrechtlich geschützten Volltexte. Wenn du wegen des Problems kein Issue erstellen kannst, bitte über einen in [GitHub-Profil des Projektverantwortlichen](https://github.com/TheTrueDon) angegebenen Kontaktweg um Unterstützung.

## Weiterentwicklung

Rückmeldungen zur Barrierefreiheit helfen dabei, Probleme zu priorisieren und künftige Tests zu verbessern. Änderungen an der Oberfläche sollen nach Möglichkeit mit Tastaturbedienung, verständlichen Beschriftungen und assistiven Technologien geprüft werden.
