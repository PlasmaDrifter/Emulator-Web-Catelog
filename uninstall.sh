#!/usr/bin/env bash
# ROMcat Uninstaller
# Stops and removes systemd user service, desktop menu launcher, application icon, and CLI command.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
ICON_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/256x256/apps"
ICON_ROOT_DIR="${HOME}/.local/share/icons"
SYSTEMD_USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"

echo "Uninstalling ROMcat..."

# 1. Stop and disable systemd user service
if command -v systemctl >/dev/null 2>&1; then
    if systemctl --user is-active --quiet romcat.service 2>/dev/null; then
        echo "Stopping systemd service..."
        systemctl --user stop romcat.service || true
    fi

    if systemctl --user is-enabled --quiet romcat.service 2>/dev/null; then
        echo "Disabling systemd service..."
        systemctl --user disable romcat.service || true
    fi
fi

# 2. Stop any standalone background instances
pkill -f "${REPO_DIR}/app.py" 2>/dev/null || true

# 3. Remove installed files
rm -f "${SYSTEMD_USER_DIR}/romcat.service"
rm -f "${DESKTOP_DIR}/romcat.desktop"
rm -f "${ICON_DIR}/romcat.png"
rm -f "${ICON_ROOT_DIR}/romcat.png"
rm -f "${BIN_DIR}/romcat"

if command -v systemctl >/dev/null 2>&1; then
    systemctl --user daemon-reload || true
fi

# 4. Optional purge of configuration and cached covers
if [ "${1:-}" = "--purge" ]; then
    echo "Purging local configuration and cached covers..."
    rm -f "${REPO_DIR}/settings.json"
    rm -rf "${REPO_DIR}/static/covers"/*
else
    echo "Configuration (config.yaml, settings.json) and downloaded covers (static/covers/) have been preserved."
    echo "To delete them, run: ./uninstall.sh --purge"
fi

# 5. Refresh desktop and icon databases
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "${DESKTOP_DIR}" >/dev/null 2>&1 || true
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -q -t "${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor" >/dev/null 2>&1 || true
fi

echo ""
echo "ROMcat has been uninstalled."
