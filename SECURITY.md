# Sicherheit und Privatsphäre

Amicus Theologi ist für **einen lokalen Einzelplatz** entwickelt. Der Webserver lauscht ausschließlich auf der Loopback-Adresse `127.0.0.1` und erlaubt keine entfernten Hosts. Es gibt keinen Cloud-Sync, kein Tracking, keine Nutzerkonten und keinen Login.

Sicherheitsmaßnahmen: Host-Validierung gegen DNS-Rebinding, Kontrolle von Origin / Fetch-Site bei schreibenden API-Requests, validierte Importe, Transaktionen bei Datenänderungen, geprüfte ZIP-Sicherungen, Sicherungs-Prüfsummen, Integritäts- und Fremdschlüsselprüfung, Wiederherstellung nur nach Neustart.

**Grenzen:** Ein lokaler Prozess mit Rechten derselben Benutzerin kann auf deren lokalen Datenordner zugreifen. Auf gemeinsam genutzten Rechnern sind getrennte Betriebssystemkonten sinnvoll. Die Python-Abhängigkeiten und Online-Importarchive stammen von Dritten und müssen regelmäßig aktualisiert beziehungsweise geprüft werden. Es gibt noch keine digitale Signierung der Programm-ZIPs und keinen verifizierten Offline-Installer für Windows. Der SWORD-Importer ist experimentell.

Nicht auf einem Internetserver, in einem gemeinsam erreichbaren LAN oder in einem Mehrbenutzerbetrieb starten. Solche Szenarien verlangen zusätzliche Authentifizierung, Autorisierung, TLS und Ressourcenlimits.

Bei einem Sicherheitsproblem keine sensiblen Studiennotizen in öffentliche GitHub-Issues kopieren. Fehlerberichte nach Möglichkeit mit einem Demo-Korpus reproduzieren und ohne personenbezogene Daten einreichen.
