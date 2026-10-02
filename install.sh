#!/bin/bash
# Install PyTrainer: background user service + app launcher entry.
set -euo pipefail
APP_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
PORT="${PYTRAINER_PORT:-8765}"

mkdir -p ~/.config/systemd/user ~/.local/share/applications ~/.local/share/icons/hicolor/256x256/apps ~/.local/bin

cat > ~/.config/systemd/user/pytrainer.service <<UNIT
[Unit]
Description=PyTrainer local Python practice server

[Service]
ExecStart=/usr/bin/python3 $APP_DIR/server.py --port $PORT
Restart=on-failure
RestartSec=2

[Install]
WantedBy=default.target
UNIT

if command -v rsvg-convert >/dev/null; then
  rsvg-convert -w 256 -h 256 "$APP_DIR/static/icon.svg" -o ~/.local/share/icons/hicolor/256x256/apps/pytrainer.png
  ICON=pytrainer
else
  ICON="$APP_DIR/static/icon.svg"
fi

cat > ~/.local/share/applications/PyTrainer.desktop <<DESK
[Desktop Entry]
Version=1.0
Name=PyTrainer
Comment=Test your Python for AI engineering
Exec=$APP_DIR/bin/pytrainer
Terminal=false
Type=Application
Icon=$ICON
Categories=Development;Education;
StartupNotify=true
DESK

ln -sf "$APP_DIR/bin/pytrainer" ~/.local/bin/pytrainer

systemctl --user daemon-reload
systemctl --user enable --now pytrainer.service
update-desktop-database ~/.local/share/applications 2>/dev/null || true
gtk-update-icon-cache ~/.local/share/icons/hicolor 2>/dev/null || true

echo "PyTrainer installed."
echo "  App launcher:  search for 'PyTrainer' (Super + Space)"
echo "  Terminal:      pytrainer"
echo "  URL:           http://127.0.0.1:$PORT"
