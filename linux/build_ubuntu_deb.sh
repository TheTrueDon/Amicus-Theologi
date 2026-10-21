#!/usr/bin/env bash
# Native Ubuntu installer: freezes Python first, then constructs a standard .deb.
# Run on Ubuntu 24.04 x86_64 (locally or via GitHub Actions).
set -Eeuo pipefail
cd "$(dirname "$0")/.."
ROOT="$PWD"

if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]]; then
  echo 'This build targets Ubuntu Linux x86_64 (amd64).' >&2
  exit 1
fi
if ! command -v dpkg-deb >/dev/null; then
  echo 'dpkg-deb missing. Install the dpkg package.' >&2
  exit 1
fi
VERSION="$(tr -d '\r\n' < VERSION)"
if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Unexpected version string: ${VERSION}" >&2
  exit 1
fi
PYTHON="${AMICUS_BUILD_PYTHON:-python3}"
if [[ "${AMICUS_USE_EXISTING_FROZEN:-0}" != '1' ]]; then
  "$PYTHON" -m PyInstaller --noconfirm --clean --onedir \
    --name AmicusTheologi --paths . \
    --add-data 'frontend:frontend' \
    --add-data 'modules/examples:modules/examples' \
    --add-data 'source_packages:source_packages' \
    --add-data 'assets/amicus.png:assets' \
    --add-data 'assets/amicus.ico:assets' \
    --add-data 'ANLEITUNG.html:.' \
    --add-data 'ANLEITUNG.css:.' \
    --add-data 'ANLEITUNG.js:.' \
    --collect-submodules uvicorn \
    --collect-submodules fastapi \
    --collect-submodules pysword \
    --hidden-import tkinter \
    linux/launcher.py
fi
FROZEN="$ROOT/dist/AmicusTheologi/AmicusTheologi"
if [[ ! -x "$FROZEN" ]]; then
  echo "Missing frozen executable: $FROZEN" >&2
  exit 1
fi
if [[ "${AMICUS_SKIP_FROZEN_TEST:-0}" != '1' ]]; then
  echo 'Testing frozen HTTP server and offline manual ...'
  "$FROZEN" --self-test
  if command -v xvfb-run >/dev/null; then
    echo 'Testing native Tk GUI under virtual X display ...'
    xvfb-run -a "$FROZEN" --gui-self-test
  fi
fi

STAGE="$(mktemp -d -t amicus-deb-XXXXXXXX)"
trap 'rm -rf "$STAGE"' EXIT
chmod 0755 "$STAGE" # Do not ship a 0700 package root from mktemp.
DEST="$STAGE/opt/amicus-theologi"
mkdir -p "$DEST" "$STAGE/DEBIAN" \
    "$STAGE/usr/share/applications" \
    "$STAGE/usr/share/icons/hicolor/512x512/apps" \
    "$STAGE/usr/share/doc/amicus-theologi/handbuch" \
    "$STAGE/usr/share/metainfo"
cp -a "$ROOT/dist/AmicusTheologi/." "$DEST/"
install -m 644 assets/amicus.png "$STAGE/usr/share/icons/hicolor/512x512/apps/amicus-theologi.png"
install -m 644 linux/amicus-theologi.desktop "$STAGE/usr/share/applications/amicus-theologi.desktop"
install -m 644 linux/amicus-theologi-shortcut.desktop "$STAGE/usr/share/applications/amicus-theologi-shortcut.desktop"
install -m 644 linux/amicus-theologi.metainfo.xml "$STAGE/usr/share/metainfo/amicus-theologi.metainfo.xml"
install -m 644 LICENSE "$STAGE/usr/share/doc/amicus-theologi/copyright"
for name in ANLEITUNG.html ANLEITUNG.css ANLEITUNG.js; do
  install -m 644 "$name" "$STAGE/usr/share/doc/amicus-theologi/handbuch/$name"
done
cat > "$STAGE/DEBIAN/control" <<EOF
Package: amicus-theologi
Version: $VERSION
Section: education
Priority: optional
Architecture: amd64
Maintainer: Amicus Theologi Community <noreply@github.com>
Depends: libc6 (>= 2.39), libstdc++6, libgcc-s1, libtk8.6, libtcl8.6, libx11-6, libxcb1, libxft2, libxext6, libxrender1, zlib1g
Homepage: https://github.com/TheTrueDon/Amicus-Theologi
Description: Offline-first scientific Bible study and exegesis
 A local scientific environment for original-language Bible study,
 morphology, lexica, concordances, and study notes.
 The Python runtime is bundled. No activation or account is needed.
EOF
# Remove user-owned local data on package removal (not on upgrade).
# A package maintainer script runs as root, so ignore symbolic links and
# never follow a symlinked home/.local/share directory.
cat > "$STAGE/DEBIAN/postrm" <<'POSTRM'
#!/bin/sh
set -eu
case "${1:-}" in
  remove|purge)
    if [ -f /etc/passwd ]; then
      while IFS=: read -r username ignored uid gid gecos home shell; do
        [ -n "$home" ] && [ "$home" != "/" ] || continue
        [ -d "$home" ] && [ ! -L "$home" ] || continue
        [ -d "$home/.local" ] && [ ! -L "$home/.local" ] || continue
        [ -d "$home/.local/share" ] && [ ! -L "$home/.local/share" ] || continue
        data="$home/.local/share/amicus-theologi"
        if [ -d "$data" ] && [ ! -L "$data" ]; then
          rm -rf -- "$data"
        fi
      done < /etc/passwd
    fi
    ;;
  upgrade|failed-upgrade|abort-install|abort-upgrade|disappear)
    ;;
esac
exit 0
POSTRM
chmod 0755 "$STAGE/DEBIAN/postrm"
mkdir -p dist_installer
OUT="$ROOT/dist_installer/Amicus-Theologi-${VERSION}-Ubuntu-24.04-amd64.deb"
dpkg-deb --root-owner-group --build "$STAGE" "$OUT"
dpkg-deb --info "$OUT" | head -30
printf '\nCreated Ubuntu package: %s\n' "$OUT"
