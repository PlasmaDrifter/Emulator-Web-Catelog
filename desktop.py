#!/usr/bin/env python3
"""
ROMcat Desktop Launcher (Standalone Desktop App)
Launches the Flask backend server in a background thread
and presents the interface in a native desktop window via pywebview.
"""
import os
import sys
import time
import socket
import shutil
import threading
from pathlib import Path
import webview
from app import app, load_settings, BUNDLE_DIR


def find_free_port(default_port=8420):
    """Attempt default port 8420; fallback to an ephemeral port if occupied."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', default_port))
            return default_port
        except OSError:
            pass
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def run_server(port):
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)


def setup_desktop_integration(title, icon_path):
    """Register application name, prgname and icons for Wayland and X11."""
    if sys.platform == 'win32' or os.name == 'nt':
        return
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk, GLib

        GLib.set_prgname("romcat")
        GLib.set_application_name(title)

        if icon_path.exists():
            Gtk.Window.set_default_icon_from_file(str(icon_path))
    except Exception as e:
        print(f"GTK icon setup note: {e}", file=sys.stderr)

    # Register user desktop entry & icon so Wayland compositor / dock displays icon
    try:
        home = Path.home()
        icon_dir = home / ".local" / "share" / "icons" / "hicolor" / "256x256" / "apps"
        icon_dir.mkdir(parents=True, exist_ok=True)
        dest_icon = icon_dir / "romcat.png"
        if icon_path.exists():
            shutil.copy2(icon_path, dest_icon)

        apps_dir = home / ".local" / "share" / "applications"
        apps_dir.mkdir(parents=True, exist_ok=True)
        desktop_file = apps_dir / "romcat.desktop"
        exec_path = str(Path(sys.executable if getattr(sys, "frozen", False) else sys.argv[0]).resolve())
        desktop_content = f"""[Desktop Entry]
Name={title}
Comment=Modern Retro ROM Library & Game Launcher
Exec="{exec_path}"
Icon=romcat
Terminal=false
Type=Application
Categories=Game;Emulator;
StartupWMClass=romcat
"""
        desktop_file.write_text(desktop_content)
    except Exception as e:
        print(f"Desktop entry registration note: {e}", file=sys.stderr)


def main():
    port = find_free_port(8420)
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()

    time.sleep(0.35)

    settings = load_settings()
    title = settings.get("title", "ROMcat")
    icon_path = BUNDLE_DIR / "static" / "favicon.png"

    setup_desktop_integration(title, icon_path)

    window = webview.create_window(
        title=title,
        url=f'http://127.0.0.1:{port}',
        width=1440,
        height=900,
        min_size=(960, 600),
        background_color='#14161a'
    )
    webview.start()


if __name__ == '__main__':
    main()
