#!/usr/bin/env bash
# Optionale Menü-Verknüpfung – ohne Administratorrechte
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd)"
mkdir -p "$HOME/.local/share/applications"
# Use a generated wrapper because .desktop Exec quoting for paths with spaces varies.
WRAPPER="$ROOT/amicus-theologi-launcher.sh"
cat > "$WRAPPER" <<EOF
#!/usr/bin/env bash
exec /bin/bash "${ROOT}/start_linux.sh"
EOF
chmod +x "$WRAPPER"
DESKTOP="$HOME/.local/share/applications/amicus-theologi.desktop"
cat > "$DESKTOP" <<EOF
[Desktop Entry]
Name=Amicus Theologi
Comment=Offline-Werkzeug für wissenschaftliche Bibelarbeit
Exec=${WRAPPER}
Icon=accessories-dictionary
Terminal=true
Type=Application
Categories=Education;Science;
StartupNotify=false
EOF
chmod +x "$DESKTOP"
echo "Menüeintrag angelegt: $DESKTOP"
echo 'Amicus Theologi ist nun im Anwendungsmenü auffindbar.'
