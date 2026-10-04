#!/bin/bash
# Install PyTrainer: background user service + app launcher entry (Linux: systemd, macOS: launchd).
set -euo pipefail
SELF="$0"
while [ -L "$SELF" ]; do
  LINK="$(readlink "$SELF")"
  case "$LINK" in /*) SELF="$LINK" ;; *) SELF="$(dirname "$SELF")/$LINK" ;; esac
done
APP_DIR="$(cd "$(dirname "$SELF")" && pwd)"
PORT="${PYTRAINER_PORT:-8765}"
PYTHON="$(command -v python3 || true)"

if [ -z "$PYTHON" ] || ! "$PYTHON" -c 'import sys; sys.exit(sys.version_info < (3, 11))'; then
  echo "PyTrainer needs Python 3.11 or newer as python3." >&2
  exit 1
fi

mkdir -p ~/.local/bin
ln -sf "$APP_DIR/bin/pytrainer" ~/.local/bin/pytrainer

if [ "$(uname)" = "Darwin" ]; then
  DATA_DIR="$HOME/Library/Application Support/PyTrainer"
  PLIST=~/Library/LaunchAgents/com.pytrainer.server.plist
  mkdir -p ~/Library/LaunchAgents "$DATA_DIR"
  cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.pytrainer.server</string>
  <key>ProgramArguments</key>
  <array><string>$PYTHON</string><string>$APP_DIR/server.py</string><string>--port</string><string>$PORT</string></array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><dict><key>SuccessfulExit</key><false/></dict>
  <key>StandardOutPath</key><string>$DATA_DIR/server.log</string>
  <key>StandardErrorPath</key><string>$DATA_DIR/server.log</string>
</dict>
</plist>
PLIST
  launchctl bootout "gui/$(id -u)/com.pytrainer.server" 2>/dev/null || true
  launchctl bootstrap "gui/$(id -u)" "$PLIST"

  echo "PyTrainer installed."
  echo "  Terminal:      pytrainer   (make sure ~/.local/bin is on your PATH)"
  echo "  URL:           http://127.0.0.1:$PORT"
  exit 0
fi

mkdir -p ~/.config/systemd/user ~/.local/share/applications ~/.local/share/icons/hicolor/256x256/apps

cat > ~/.config/systemd/user/pytrainer.service <<UNIT
[Unit]
Description=PyTrainer local Python practice server

[Service]
ExecStart=$PYTHON $APP_DIR/server.py --port $PORT
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

systemctl --user daemon-reload
systemctl --user enable --now pytrainer.service
update-desktop-database ~/.local/share/applications 2>/dev/null || true
gtk-update-icon-cache ~/.local/share/icons/hicolor 2>/dev/null || true

if ! command -v bwrap >/dev/null; then
  echo "Tip: install bubblewrap (bwrap) so exercise code runs with no network and a read-only filesystem."
fi

echo "PyTrainer installed."
echo "  App launcher:  search for 'PyTrainer' (Super + Space)"
echo "  Terminal:      pytrainer"
echo "  URL:           http://127.0.0.1:$PORT"
