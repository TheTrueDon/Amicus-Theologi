# Amicus Theologi 1.0.6 – Versweiser Bibelvergleich

Die mittlere Bibeltextspalte zeigt nun standardmäßig **Vers 1 in allen ausgewählten Ausgaben**, danach **Vers 2 in allen ausgewählten Ausgaben** usw. „Darstellung“ schaltet zwischen **Versweise vergleichen** und **Nach Ausgabe anzeigen** um. Die Einstellung wird dauerhaft gespeichert. Unter „Ausgaben auswählen“ lassen sich beliebige Ausgaben kombinieren und sortieren.

Die Versdarstellung bleibt in die Wortanalyse, die Hover-Kurzanalysen sowie die Projektmarkierungen und Studiennotizen eingebunden. Einzelne fehlende Verse werden neutral als Datenlücke gekennzeichnet; Ausgaben ohne Text für das ganze Kapitel erscheinen nur in einer aufklappbaren Übersicht. Die Septuaginta enthält kein Johannesevangelium.

**Wissenschaftliche Grenze:** Die Ausrichtung beruht auf identischen Buch-/Kapitel-/Verskennungen. Eine Zuordnung abweichender Editionszählungen (etwa bei den Psalmen in MT und LXX) ist noch nicht implementiert.

**Datenbank:** keine Schemamigration. Der Wert `text_layout` (verse/edition) wird in der bestehenden settings-Tabelle gespeichert. Vorhandene Texte, Lexika und Studienprojekte bleiben erhalten.

**Windows:** Das normale Installer-Build-Skript ist für Version 1.0.6 aktualisiert. Ein Windows-Setup wird weiterhin über GitHub Actions erzeugt und muss dort geprüft werden.
