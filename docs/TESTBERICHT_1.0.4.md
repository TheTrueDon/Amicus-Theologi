# Amicus Theologi 1.0.4 – Testbericht

- 68 automatische Python-Tests bestanden.
- Chromium-Prüfung der tatsächlichen Eingabefarben und Eingabe für Dunkel/Hell bestanden.
- Dunkles Design: Text rgb(228,233,236), Hintergrund rgb(32,45,56), Kontrast 11,49:1.
- Helles Design: Text rgb(37,55,68), Hintergrund rgb(244,247,248), Kontrast 11,42:1.
- Notizeneingabe und CSS-Regeln sind unverändert mit der bisherigen API verbunden.
- Datenbankschema unverändert, keine Migration.
- Windows-Installer wird wie bisher über GitHub Actions erstellt; Quell-ZIP ist keine Setup-EXE.
