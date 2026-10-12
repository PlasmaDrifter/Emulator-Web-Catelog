#!/usr/bin/env bash
# ROMcat Automated Installer
# Installs application icon, desktop launcher, CLI command, and systemd user service.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
ICON_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/256x256/apps"
ICON_ROOT_DIR="${HOME}/.local/share/icons"
SYSTEMD_USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"

echo "Installing ROMcat..."

# 1. Check Python 3 (>= 3.10)
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 is not installed. Please install Python 3 (>= 3.10) first." >&2
    exit 1
fi

PY_MAJOR="$(python3 -c 'import sys; print(sys.version_info.major)')"
PY_MINOR="$(python3 -c 'import sys; print(sys.version_info.minor)')"

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    echo "Error: Python 3.10 or newer is required. Found Python ${PY_MAJOR}.${PY_MINOR}." >&2
    exit 1
fi

# 2. Check and install Python dependencies
check_and_install_dependencies() {
    local missing=()
    for mod in flask yaml requests PIL ujson; do
        if ! python3 -c "import ${mod}" >/dev/null 2>&1; then
            missing+=("${mod}")
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        echo "Missing Python dependencies detected: ${missing[*]}"
        echo "Attempting to install dependencies from requirements.txt..."
        if [ -f "${REPO_DIR}/requirements.txt" ]; then
            local pip_args=()
            if python3 -m pip install --help 2>&1 | grep -q -- '--break-system-packages'; then
                pip_args+=(--break-system-packages)
            fi
            python3 -m pip install --user "${pip_args[@]}" -r "${REPO_DIR}/requirements.txt" || true
        fi

        local still_missing=()
        for mod in flask yaml requests PIL ujson; do
            if ! python3 -c "import ${mod}" >/dev/null 2>&1; then
                still_missing+=("${mod}")
            fi
        done

        if [ ${#still_missing[@]} -gt 0 ]; then
            echo ""
            echo "Notice: Some dependencies could not be automatically installed: ${still_missing[*]}"
            echo "You can install them via your distribution package manager or pip:"
            echo "  Fedora / Nobara: sudo dnf install python3-flask python3-pyyaml python3-requests python3-pillow python3-ujson"
            echo "  Ubuntu / Debian: sudo apt install python3-flask python3-yaml python3-requests python3-pil python3-ujson"
            echo "  Arch Linux:      sudo pacman -S python-flask python-pyyaml python-requests python-pillow python-ujson"
            echo "  Pip:             pip install -r requirements.txt"
            echo ""
        fi
    fi
}

check_and_install_dependencies

# 3. Create required target directories
mkdir -p "${BIN_DIR}" "${DESKTOP_DIR}" "${ICON_DIR}" "${ICON_ROOT_DIR}" "${SYSTEMD_USER_DIR}"

# 4. Initialize config.yaml if missing
if [ ! -f "${REPO_DIR}/config.yaml" ] && [ -f "${REPO_DIR}/config.example.yaml" ]; then
    cp -f "${REPO_DIR}/config.example.yaml" "${REPO_DIR}/config.yaml"
    echo "Created initial configuration at ${REPO_DIR}/config.yaml"
fi

# 5. Make launcher script executable and symlink to ~/.local/bin
chmod +x "${REPO_DIR}/romcat.sh"
ln -sf "${REPO_DIR}/romcat.sh" "${BIN_DIR}/romcat"
echo "Created CLI command link: ${BIN_DIR}/romcat"

# 6. Install application icon
if [ -f "${REPO_DIR}/static/favicon.png" ]; then
    cp -f "${REPO_DIR}/static/favicon.png" "${ICON_DIR}/romcat.png"
    cp -f "${REPO_DIR}/static/favicon.png" "${ICON_ROOT_DIR}/romcat.png"
    echo "Installed application icon to ${ICON_DIR}/romcat.png"
elif [ -f "${REPO_DIR}/Standalone.app/icon.png" ]; then
    cp -f "${REPO_DIR}/Standalone.app/icon.png" "${ICON_DIR}/romcat.png"
    cp -f "${REPO_DIR}/Standalone.app/icon.png" "${ICON_ROOT_DIR}/romcat.png"
    echo "Installed application icon to ${ICON_DIR}/romcat.png"
fi

# 7. Generate and install desktop menu entry
cat > "${DESKTOP_DIR}/romcat.desktop" <<DESKTOPEOF
[Desktop Entry]
Type=Application
Name=ROMcat
GenericName=ROM Library & Game Launcher
Comment=Retro and modern emulator web catalog and launcher
Exec=${REPO_DIR}/romcat.sh launch
Icon=romcat
Terminal=false
Categories=Game;Emulator;
StartupWMClass=romcat
Keywords=rom;roms;emulator;retro;nes;snes;n64;gamecube;switch;games;
StartupNotify=true
DESKTOPEOF
chmod 644 "${DESKTOP_DIR}/romcat.desktop"
echo "Installed desktop launcher: ${DESKTOP_DIR}/romcat.desktop"

# 8. Detect Python interpreter for systemd service
PYTHON_BIN="$(which python3)"
if [ -f "${REPO_DIR}/venv/bin/python3" ]; then
    PYTHON_BIN="${REPO_DIR}/venv/bin/python3"
fi

# 9. Generate and install systemd user service
cat > "${SYSTEMD_USER_DIR}/romcat.service" <<SERVICEOF
[Unit]
Description=ROMcat Emulator Web Catalog
After=network.target

[Service]
Type=simple
WorkingDirectory=${REPO_DIR}
ExecStart=${PYTHON_BIN} ${REPO_DIR}/app.py
Restart=on-failure
RestartSec=3

[Install]
WantedBy=default.target
SERVICEOF
chmod 644 "${SYSTEMD_USER_DIR}/romcat.service"
echo "Installed systemd user service: ${SYSTEMD_USER_DIR}/romcat.service"

# 10. Reload systemd and enable/start service
if command -v systemctl >/dev/null 2>&1; then
    systemctl --user daemon-reload
    systemctl --user enable --now romcat.service
    echo "ROMcat background service enabled and started."
fi

# 11. Refresh desktop and icon databases
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "${DESKTOP_DIR}" >/dev/null 2>&1 || true
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -q -t "${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor" >/dev/null 2>&1 || true
fi

echo ""
echo "Installation complete."
echo "Access ROMcat at:   http://localhost:8420"
echo "Run via terminal:   romcat"
echo "Menu launcher:      ROMcat in Applications -> Games"
