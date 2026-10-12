#!/usr/bin/env bash
# ROMcat CLI & Browser Launcher
# Portable launcher script for ROMcat

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${ROMCAT_PORT:-8420}"
URL="http://localhost:${PORT}"
ACTION="${1:-launch}"

is_running() {
    curl -s --connect-timeout 1 "${URL}/api/settings" >/dev/null 2>&1 || curl -s --connect-timeout 1 "${URL}/" >/dev/null 2>&1
}

wait_for_server() {
    local timeout=15
    local count=0
    while ! is_running; do
        sleep 0.5
        count=$((count + 1))
        if [ "$count" -ge $((timeout * 2)) ]; then
            echo "Error: Timed out waiting for ROMcat server to start." >&2
            return 1
        fi
    done
}

ensure_server() {
    if is_running; then
        return 0
    fi

    # Try starting systemd service first if available
    if command -v systemctl >/dev/null 2>&1 && systemctl --user list-unit-files romcat.service >/dev/null 2>&1; then
        echo "Starting ROMcat systemd user service..."
        systemctl --user start romcat.service
        if wait_for_server; then
            return 0
        fi
    fi

    # Otherwise fallback to starting in background directly
    local python_bin="python3"
    if [ -f "${SCRIPT_DIR}/venv/bin/python3" ]; then
        python_bin="${SCRIPT_DIR}/venv/bin/python3"
    fi

    echo "Starting ROMcat server on port ${PORT}..."
    nohup "${python_bin}" "${SCRIPT_DIR}/app.py" >/dev/null 2>&1 &
    wait_for_server
}

open_browser() {
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "${URL}" >/dev/null 2>&1 &
    elif command -v gio >/dev/null 2>&1; then
        gio open "${URL}" >/dev/null 2>&1 &
    else
        echo "Open your browser to: ${URL}"
    fi
}

case "${ACTION}" in
    launch)
        ensure_server
        open_browser
        ;;
    start)
        ensure_server
        echo "ROMcat server is running at ${URL}"
        ;;
    open)
        open_browser
        ;;
    status)
        if command -v systemctl >/dev/null 2>&1 && systemctl --user list-unit-files romcat.service >/dev/null 2>&1; then
            systemctl --user status romcat.service --no-pager || true
        elif is_running; then
            echo "ROMcat is running at ${URL}"
        else
            echo "ROMcat server is not running."
        fi
        ;;
    stop)
        if command -v systemctl >/dev/null 2>&1 && systemctl --user is-active --quiet romcat.service 2>/dev/null; then
            echo "Stopping ROMcat systemd service..."
            systemctl --user stop romcat.service
        fi
        pkill -f "${SCRIPT_DIR}/app.py" 2>/dev/null || true
        echo "ROMcat server stopped."
        ;;
    restart)
        if command -v systemctl >/dev/null 2>&1 && systemctl --user list-unit-files romcat.service >/dev/null 2>&1; then
            echo "Restarting ROMcat systemd service..."
            systemctl --user restart romcat.service
            wait_for_server
        else
            pkill -f "${SCRIPT_DIR}/app.py" 2>/dev/null || true
            sleep 1
            ensure_server
        fi
        echo "ROMcat server restarted at ${URL}"
        ;;
    logs)
        if command -v journalctl >/dev/null 2>&1; then
            journalctl --user -u romcat.service -f
        else
            echo "journalctl not available."
        fi
        ;;
    *)
        echo "Usage: $0 [launch|start|open|status|stop|restart|logs]"
        echo "  launch   Ensure server is running and open browser (default)"
        echo "  start    Start server in background if not running"
        echo "  open     Open ROMcat in browser without starting server"
        echo "  status   Check server status"
        echo "  stop     Stop the background server"
        echo "  restart  Restart the server"
        echo "  logs     View live server logs"
        exit 1
        ;;
esac
