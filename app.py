#!/usr/bin/env python3
"""
romcat - a tiny self-hosted ROM catalog that launches games in your real,
native emulators (not in-browser emulation). Runs on the same machine as
your emulators; browser is just the remote control.
"""
import os
import sys
import re
import io
import ujson as json  # <-- This tells Python to use the ultra-fast parser everywhere
import shlex
import subprocess
import yaml
import requests
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory
from PIL import Image

__version__ = "0.1.2"

if getattr(sys, "frozen", False):
    BUNDLE_DIR = Path(sys._MEIPASS)
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BUNDLE_DIR = Path(__file__).resolve().parent
    BASE_DIR = BUNDLE_DIR

CONFIG_PATH = BASE_DIR / "config.yaml"
CONFIG_EXAMPLE_PATH = BUNDLE_DIR / "config.example.yaml"
COVERS_DIR = BASE_DIR / "covers" if getattr(sys, "frozen", False) else BASE_DIR / "static" / "covers"
FAVORITES_PATH = BASE_DIR / "favorites.json"
HIDDEN_PATH = BASE_DIR / "hidden.json"
LIBRARY_CACHE_PATH = BASE_DIR / "library.json"
SETTINGS_PATH = BASE_DIR / "settings.json"
COVERS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_SETTINGS = {
    "title": "ROMcat",
    "icon": "/static/favicon.png",
    "theme": {
        "bg_body": "#14161a",
        "bg_header": "#1c1f26",
        "bg_tabs": "#181b21",
        "bg_card": "#22262e",
        "accent_color": "#3a7bd5",
        "tab_active_text": "#ffffff",
        "favorite_color": "#ff00ff",
        "favorite_star_color": "#ffd700",
        "text_primary": "#e8e8e8",
        "text_muted": "#9aa4b2",
        "border_color": "#2a2e37"
    },
    "visibility": {
        "show_search": True,
        "show_counts": True,
        "show_all_tab": True,
        "show_favorites_tab": True,
        "show_hidden_tab": False,
        "show_card_hide_buttons": False,
        "show_tab_icons": False
    }
}

app = Flask(
    __name__,
    template_folder=str(BUNDLE_DIR / "templates"),
    static_folder=str(BUNDLE_DIR / "static")
)

# Global memory cache for library metadata
_library_cache = None


def get_contrast_color(hex_color: str) -> str:
    if not hex_color:
        return "#ffffff"
    clean = hex_color.lstrip("#")
    if len(clean) == 3:
        clean = "".join(c + c for c in clean)
    if len(clean) != 6:
        return "#ffffff"
    try:
        r, g, b = int(clean[0:2], 16), int(clean[2:4], 16), int(clean[4:6], 16)
        yiq = (r * 299 + g * 587 + b * 114) / 1000
        return "#000000" if yiq >= 140 else "#ffffff"
    except Exception:
        return "#ffffff"


def load_settings() -> dict:
    if not SETTINGS_PATH.exists():
        settings = {
            "title": DEFAULT_SETTINGS["title"],
            "icon": DEFAULT_SETTINGS["icon"],
            "theme": dict(DEFAULT_SETTINGS["theme"]),
            "visibility": dict(DEFAULT_SETTINGS["visibility"]),
        }
        settings["theme"]["accent_contrast"] = get_contrast_color(settings["theme"].get("accent_color", "#88c0d0"))
        return settings
    try:
        data = json.loads(SETTINGS_PATH.read_text())
        settings = {
            "title": DEFAULT_SETTINGS["title"],
            "icon": DEFAULT_SETTINGS["icon"],
            "theme": dict(DEFAULT_SETTINGS["theme"]),
            "visibility": dict(DEFAULT_SETTINGS["visibility"]),
        }
        if isinstance(data, dict):
            if "title" in data and data["title"]:
                settings["title"] = str(data["title"])
            if "icon" in data and data["icon"]:
                settings["icon"] = str(data["icon"])
            if "theme" in data and isinstance(data["theme"], dict):
                settings["theme"].update(data["theme"])
            if "visibility" in data and isinstance(data["visibility"], dict):
                settings["visibility"].update(data["visibility"])
        settings["theme"]["accent_contrast"] = get_contrast_color(settings["theme"].get("accent_color", "#88c0d0"))
        return settings
    except Exception:
        settings = {
            "title": DEFAULT_SETTINGS["title"],
            "icon": DEFAULT_SETTINGS["icon"],
            "theme": dict(DEFAULT_SETTINGS["theme"]),
            "visibility": dict(DEFAULT_SETTINGS["visibility"]),
        }
        settings["theme"]["accent_contrast"] = get_contrast_color(settings["theme"].get("accent_color", "#88c0d0"))
        return settings


def save_settings(settings: dict):
    SETTINGS_PATH.write_text(json.dumps(settings, indent=2))


def load_favorites() -> set:
    if not FAVORITES_PATH.exists():
        return set()
    try:
        return set(json.loads(FAVORITES_PATH.read_text()))
    except Exception:
        return set()


def save_favorites(favorites: set):
    FAVORITES_PATH.write_text(json.dumps(sorted(favorites), indent=2))


def load_hidden() -> set:
    if not HIDDEN_PATH.exists():
        return set()
    try:
        return set(json.loads(HIDDEN_PATH.read_text()))
    except Exception:
        return set()


def save_hidden(hidden: set):
    HIDDEN_PATH.write_text(json.dumps(sorted(hidden), indent=2))


def resilient_yaml_load(raw_text: str):
    """Safely parse YAML with fallback handling for unescaped Windows backslashes."""
    if not raw_text:
        return {}
    try:
        return yaml.safe_load(raw_text) or {}
    except Exception:
        # Handle unescaped backslashes in Windows paths (e.g. "C:\Users\...")
        try:
            fixed = re.sub(
                r'"([A-Za-z]:\\[^"]+)"',
                lambda m: repr(m.group(1).replace("\\\\", "\\")),
                raw_text
            )
            return yaml.safe_load(fixed) or {}
        except Exception:
            try:
                fixed = raw_text.replace("\\", "/")
                return yaml.safe_load(fixed) or {}
            except Exception:
                return {}


def load_config():
    if not CONFIG_PATH.exists():
        if CONFIG_EXAMPLE_PATH.exists():
            import shutil
            shutil.copy(CONFIG_EXAMPLE_PATH, CONFIG_PATH)
        else:
            return {"systems": {}, "steamgriddb": {"api_key": ""}}
    try:
        raw_text = CONFIG_PATH.read_text(encoding="utf-8")
        parsed = resilient_yaml_load(raw_text)
        if isinstance(parsed, dict) and "systems" in parsed:
            return parsed
        return {"systems": {}, "steamgriddb": {"api_key": ""}}
    except Exception as e:
        print(f"Error loading config.yaml: {e}", file=sys.stderr)
        return {"systems": {}, "steamgriddb": {"api_key": ""}}


def clean_title(filename: str) -> str:
    """Strip extension and common ROM tags like (USA), (Rev 1), [!] etc.,
    and normalize underscores/dashes into spaces for better search matches."""
    name = Path(filename).stem
    if name.lower().endswith(".nkit"):
        name = name[:-5]
    name = re.sub(r"\([^)]*\)", "", name)
    name = re.sub(r"\[[^\]]*\]", "", name)
    name = name.replace("_", " ").replace("-", " ")
    name = re.sub(r"\s+", " ", name).strip()
    return name


def get_sort_title(title: str) -> str:
    """Helper to get a lowercase title string ignoring any leading 'The ' for sorting."""
    t = title.strip().lower()
    if t.startswith("the "):
        return t[4:]
    return t


def safe_key(system: str, filename: str) -> str:
    """Filesystem-safe cache key for a rom's cover image."""
    stem = Path(filename).stem
    key = f"{system}_{stem}"
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", key)


def compress_and_save_image(img_bytes, out_path) -> bool:
    """Resizes and compresses images to a standard grid size to maximize loading performance."""
    try:
        img = Image.open(io.BytesIO(img_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img = img.resize((300, 400), Image.Resampling.LANCZOS)
        img.save(out_path, "JPEG", quality=80, optimize=True)
        return True
    except Exception as e:
        print(f"Compression error: {e}")
        return False


def scan_library():
    """Walk configured folders and build the game list, grouped by system."""
    config = load_config()
    favorites = load_favorites()
    hidden = load_hidden()
    library = {}

    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    existing_covers = {p.name for p in COVERS_DIR.iterdir() if p.is_file()}

    for sys_id, sys_cfg in config.get("systems", {}).items():
        if not isinstance(sys_cfg, dict):
            continue
        folders_cfg = sys_cfg.get("folder", [])
        folders = [folders_cfg] if isinstance(folders_cfg, str) else folders_cfg
        raw_exts = sys_cfg.get("extensions", [])
        exts_set = {e.lower() if e.startswith('.') else f".{e.lower()}" for e in raw_exts}
        games = []
        seen_paths = set()

        for folder_str in folders:
            cleaned_str = str(folder_str).strip().strip('"').strip("'")
            if not cleaned_str:
                continue
            folder = Path(cleaned_str).expanduser()
            if not folder.is_dir():
                continue

            # Case-insensitive filesystem walk
            for root, dirs, files in os.walk(folder):
                for file in files:
                    ext = Path(file).suffix.lower()
                    if ext not in exts_set:
                        continue
                    entry = Path(root) / file
                    try:
                        resolved_path = str(entry.resolve())
                    except Exception:
                        resolved_path = str(entry)
                    if resolved_path in seen_paths:
                        continue
                    seen_paths.add(resolved_path)

                    try:
                        relative = entry.relative_to(folder)
                        parts = relative.parts
                        is_wiiu = sys_id.lower() == "wiiu"
                        stem_lower = entry.stem.lower()
                        if stem_lower.endswith(".nkit"):
                            stem_lower = stem_lower[:-5]
                        is_generic_name = stem_lower in ("game", "boot", "main")
                        display_name = parts[0] if len(parts) > 1 and (is_wiiu or is_generic_name) else entry.name
                    except Exception:
                        display_name = entry.name

                    key = safe_key(sys_id, display_name)

                    cover_path = None
                    for ext_type in (".jpg", ".jpeg", ".png"):
                        if f"{key}{ext_type}" in existing_covers:
                            cover_path = f"/static/covers/{key}{ext_type}"
                            break

                    fav_key = f"{sys_id}:{display_name}"
                    games.append({
                        "title": clean_title(display_name),
                        "filename": display_name,
                        "path": str(entry),
                        "cover": cover_path,
                        "key": key,
                        "favorite": fav_key in favorites,
                        "hidden": fav_key in hidden,
                    })
        games.sort(key=lambda g: (not g["favorite"], get_sort_title(g["title"])))
        library[sys_id] = {
            "name": sys_cfg.get("name", sys_id),
            "games": games,
        }
    return library


def load_cached_library():
    """Load the pre-scanned library from disk if it exists."""
    global _library_cache
    if _library_cache is not None:
        return _library_cache

    if LIBRARY_CACHE_PATH.exists():
        try:
            _library_cache = json.loads(LIBRARY_CACHE_PATH.read_text())
            return _library_cache
        except Exception as e:
            print(f"Error reading library cache file: {e}")

    # Automated fall-back on first-ever run if JSON doesn't exist
    return save_library_cache(scan_library())


def save_library_cache(library_data):
    """Save the library metadata to disk to avoid future scans."""
    global _library_cache
    _library_cache = library_data
    try:
        LIBRARY_CACHE_PATH.write_text(json.dumps(library_data, indent=2))
    except Exception as e:
        print(f"Error writing library cache file: {e}")
    return _library_cache


@app.route("/")
def index():
    library = load_cached_library()
    settings = load_settings()
    return render_template("index.html", library=library, settings=settings, version=__version__)


@app.route("/api/settings", methods=["GET", "POST"])
def api_settings():
    if request.method == "POST":
        data = request.get_json(force=True)
        if not isinstance(data, dict):
            return jsonify({"ok": False, "error": "invalid payload"}), 400
        settings = load_settings()
        if "title" in data and data["title"] is not None:
            settings["title"] = str(data["title"]).strip() or DEFAULT_SETTINGS["title"]
        if "icon" in data and data["icon"] is not None:
            settings["icon"] = str(data["icon"]).strip() or DEFAULT_SETTINGS["icon"]
        if "theme" in data and isinstance(data["theme"], dict):
            settings["theme"].update(data["theme"])
        if "visibility" in data and isinstance(data["visibility"], dict):
            settings["visibility"].update(data["visibility"])
        save_settings(settings)
        return jsonify({"ok": True, "settings": settings})
    return jsonify(load_settings())


@app.route("/api/upload_icon", methods=["POST"])
def api_upload_icon():
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "No file uploaded"}), 400
    file = request.files["file"]
    if not file or not file.filename:
        return jsonify({"ok": False, "error": "Empty filename"}), 400
    ext = Path(file.filename).suffix.lower()
    if ext not in [".png", ".svg", ".ico", ".jpg", ".jpeg", ".webp"]:
        return jsonify({"ok": False, "error": "Invalid image format"}), 400

    icons_dir = BASE_DIR / "static" / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)
    clean_stem = re.sub(r"[^a-zA-Z0-9_-]", "_", Path(file.filename).stem)
    filename = f"custom_{clean_stem}{ext}"
    target_path = icons_dir / filename
    file.save(str(target_path))

    icon_url = f"/static/icons/{filename}"
    settings = load_settings()
    settings["icon"] = icon_url
    save_settings(settings)
    return jsonify({"ok": True, "icon": icon_url})


@app.route("/favicon.ico")
def favicon():
    settings = load_settings()
    icon_path = settings.get("icon", "/static/favicon.png")
    if icon_path.startswith("/static/"):
        rel_path = icon_path[len("/static/"):]
        return send_from_directory(os.path.join(app.root_path, "static"), rel_path)
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.png"
    )


@app.route("/api/rescan", methods=["GET", "POST"])
def api_rescan():
    global _library_cache
    _library_cache = None
    library_data = scan_library()
    save_library_cache(library_data)
    resp = {"ok": True, "library": library_data}
    resp.update(library_data)
    return jsonify(resp)


@app.route("/api/favorite", methods=["POST"])
def api_favorite():
    data = request.get_json(force=True)
    system = data.get("system")
    filename = data.get("filename")
    if not system or not filename:
        return jsonify({"ok": False, "error": "missing system or filename"}), 400

    fav_key = f"{system}:{filename}"
    favorites = load_favorites()
    if fav_key in favorites:
        favorites.discard(fav_key)
        is_fav = False
    else:
        favorites.add(fav_key)
        is_fav = True
    save_favorites(favorites)

    # In-memory inline state updates prevent dropping cache
    library = load_cached_library()
    if system in library:
        for game in library[system]["games"]:
            if game["filename"] == filename:
                game["favorite"] = is_fav
                break
        library[system]["games"].sort(key=lambda g: (not g["favorite"], get_sort_title(g["title"])))
        save_library_cache(library)

    return jsonify({"ok": True, "favorite": is_fav})


@app.route("/api/hide", methods=["POST"])
def api_hide():
    data = request.get_json(force=True)
    system = data.get("system")
    filename = data.get("filename")
    if not system or not filename:
        return jsonify({"ok": False, "error": "missing system or filename"}), 400

    hide_key = f"{system}:{filename}"
    hidden = load_hidden()
    if hide_key in hidden:
        hidden.discard(hide_key)
        is_hidden = False
    else:
        hidden.add(hide_key)
        is_hidden = True
    save_hidden(hidden)

    # In-memory inline state updates prevent dropping cache
    library = load_cached_library()
    if system in library:
        for game in library[system]["games"]:
            if game["filename"] == filename:
                game["hidden"] = is_hidden
                break
        save_library_cache(library)

    return jsonify({"ok": True, "hidden": is_hidden})


@app.route("/api/launch", methods=["POST"])
def api_launch():
    data = request.get_json(force=True)
    system = data.get("system")
    path = data.get("path")

    config = load_config()
    sys_cfg = config["systems"].get(system)
    if not sys_cfg:
        return jsonify({"ok": False, "error": "unknown system"}), 400

    cleaned_path = str(path).strip().strip('"').strip("'")
    rom_path = Path(cleaned_path)
    try:
        resolved = rom_path.resolve()
    except Exception:
        resolved = rom_path

    folders_cfg = sys_cfg["folder"]
    folders = [folders_cfg] if isinstance(folders_cfg, str) else folders_cfg
    allowed = False
    for folder_str in folders:
        try:
            cleaned_folder = str(folder_str).strip().strip('"').strip("'")
            configured_folder = Path(cleaned_folder).expanduser().resolve()
            if (
                configured_folder in resolved.parents
                or resolved == configured_folder
                or str(resolved).lower().startswith(str(configured_folder).lower())
            ):
                allowed = True
                break
        except Exception:
            continue

    if not allowed:
        return jsonify({"ok": False, "error": "path outside configured folder"}), 400
    if not resolved.is_file():
        return jsonify({"ok": False, "error": "file not found"}), 404

    cmd_template = sys_cfg["command"]
    if os.name == "nt":
        # Windows execution
        cmd = cmd_template.format(rom=f'"{resolved}"')
        try:
            subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            return jsonify({"ok": False, "error": "Emulator launch failed on Windows."}), 500
    else:
        # Linux / Unix execution
        cmd = cmd_template.format(rom=shlex.quote(str(resolved)))
        env = os.environ.copy()
        if "DISPLAY" not in env:
            env["DISPLAY"] = ":0"
        if "WAYLAND_DISPLAY" not in env:
            env["WAYLAND_DISPLAY"] = "wayland-0"
        if "XDG_RUNTIME_DIR" not in env and hasattr(os, "getuid"):
            env["XDG_RUNTIME_DIR"] = f"/run/user/{os.getuid()}"

        try:
            subprocess.Popen(
                shlex.split(cmd),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env,
                start_new_session=True,
            )
        except FileNotFoundError:
            return jsonify({"ok": False, "error": "Emulator executable not found. Please check your command in settings."}), 500
        except Exception:
            return jsonify({"ok": False, "error": "Failed to launch emulator process."}), 500

    return jsonify({"ok": True})


def fetch_one_cover(api_key: str, title: str, key: str) -> bool:
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        search_url = f"https://www.steamgriddb.com/api/v2/search/autocomplete/{requests.utils.quote(title)}"
        r = requests.get(search_url, headers=headers, timeout=10)
        r.raise_for_status()
        results = r.json().get("data", [])
        if not results:
            return False
        game_id = results[0]["id"]

        grids_url = f"https://www.steamgriddb.com/api/v2/grids/game/{game_id}"
        r = requests.get(grids_url, headers=headers, timeout=10)
        r.raise_for_status()
        grids = r.json().get("data", [])
        if not grids:
            return False
        image_url = grids[0]["url"]

        img_resp = requests.get(image_url, timeout=15)
        img_resp.raise_for_status()

        for old_ext in (".jpg", ".jpeg", ".png"):
            old_path = COVERS_DIR / f"{key}{old_ext}"
            if old_path.exists():
                old_path.unlink()

        out_path = COVERS_DIR / f"{key}.jpg"
        return compress_and_save_image(img_resp.content, out_path)
    except Exception:
        return False


@app.route("/api/fetch_cover_single", methods=["POST"])
def api_fetch_cover_single():
    data = request.get_json(force=True)
    system = data.get("system")
    filename = data.get("filename")
    query = (data.get("query") or "").strip()

    config = load_config()
    api_key = config.get("steamgriddb", {}).get("api_key", "")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        return jsonify({"ok": False, "error": "no SteamGridDB API key set in config.yaml"}), 400

    sys_cfg = config["systems"].get(system)
    if not sys_cfg or not filename:
        return jsonify({"ok": False, "error": "unknown system or filename"}), 400

    key = safe_key(system, filename)
    title = query if query else clean_title(filename)
    success = fetch_one_cover(api_key, title, key)

    if not success:
        return jsonify({"ok": False, "error": f"no match found for '{title}'"}), 404

    # Update state variables instantly without triggering heavy scans
    library = load_cached_library()
    if system in library:
        for game in library[system]["games"]:
            if game["filename"] == filename:
                game["cover"] = f"/static/covers/{key}.jpg"
                break
        save_library_cache(library)

    return jsonify({"ok": True, "cover": f"/static/covers/{key}.jpg"})


@app.route("/api/fetch_covers", methods=["POST"])
def api_fetch_covers():
    config = load_config()
    api_key = config.get("steamgriddb", {}).get("api_key", "")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        return jsonify({"ok": False, "error": "no SteamGridDB API key set in config.yaml"}), 400

    headers = {"Authorization": f"Bearer {api_key}"}
    library = load_cached_library()
    fetched, skipped, failed = 0, 0, 0

    for sys_id, sys_data in library.items():
        for game in sys_data["games"]:
            if game["cover"]:
                skipped += 1
                continue
            try:
                search_url = f"https://www.steamgriddb.com/api/v2/search/autocomplete/{requests.utils.quote(game['title'])}"
                r = requests.get(search_url, headers=headers, timeout=10)
                r.raise_for_status()
                results = r.json().get("data", [])
                if not results:
                    failed += 1
                    continue
                game_id = results[0]["id"]

                grids_url = f"https://www.steamgriddb.com/api/v2/grids/game/{game_id}"
                r = requests.get(grids_url, headers=headers, timeout=10)
                r.raise_for_status()
                grids = r.json().get("data", [])
                if not grids:
                    failed += 1
                    continue
                image_url = grids[0]["url"]

                img_resp = requests.get(image_url, timeout=15)
                img_resp.raise_for_status()

                for old_ext in (".jpg", ".jpeg", ".png"):
                    old_path = COVERS_DIR / f"{game['key']}{old_ext}"
                    if old_path.exists():
                        old_path.unlink()

                out_path = COVERS_DIR / f"{game['key']}.jpg"
                if compress_and_save_image(img_resp.content, out_path):
                    game["cover"] = f"/static/covers/{game['key']}.jpg"
                    fetched += 1
                else:
                    failed += 1
            except Exception:
                failed += 1

    save_library_cache(library)
    return jsonify({"ok": True, "fetched": fetched, "skipped": skipped, "failed": failed})


@app.route("/api/config", methods=["GET"])
def api_get_config():
    try:
        raw_yaml = CONFIG_PATH.read_text(encoding="utf-8") if CONFIG_PATH.exists() else ""
        parsed = resilient_yaml_load(raw_yaml) if raw_yaml else {}
        return jsonify({"ok": True, "raw_yaml": raw_yaml, "config": parsed})
    except Exception:
        return jsonify({"ok": False, "error": "Failed to read configuration."}), 500


@app.route("/api/config", methods=["POST"])
def api_save_config():
    global _library_cache
    try:
        data = request.get_json(force=True)
        raw_yaml = data.get("raw_yaml", "")
        if not raw_yaml and "config" in data:
            raw_yaml = yaml.dump(data["config"], sort_keys=False)

        parsed = resilient_yaml_load(raw_yaml)
        if not isinstance(parsed, dict) or "systems" not in parsed:
            return jsonify({"ok": False, "error": "Invalid configuration: 'systems' block is required."}), 400

        systems = parsed.get("systems")
        if not isinstance(systems, dict) or not systems:
            return jsonify({"ok": False, "error": "Configuration must define at least one console under 'systems'."}), 400

        errors = []
        for sys_id, sys_cfg in systems.items():
            if not isinstance(sys_cfg, dict):
                errors.append(f"Console '{sys_id}' configuration must be a mapping.")
                continue
            name = sys_cfg.get("name", sys_id)
            folder = sys_cfg.get("folder")
            if not folder:
                errors.append(f"Console '{name}': ROM folder path is required.")
            command = sys_cfg.get("command", "")
            if not command:
                errors.append(f"Console '{name}': Emulator launch command is required.")
            elif "{rom}" not in command:
                errors.append(f"Console '{name}': Emulator command must include the '{{rom}}' token.")
            exts = sys_cfg.get("extensions")
            if not exts:
                errors.append(f"Console '{name}': At least one allowed file extension is required.")

        if errors:
            return jsonify({"ok": False, "error": "Validation failed", "errors": errors}), 400

        CONFIG_PATH.write_text(raw_yaml, encoding="utf-8")
        _library_cache = None
        library = scan_library()
        save_library_cache(library)
        return jsonify({"ok": True, "config": parsed, "raw_yaml": raw_yaml, "library": library})
    except Exception:
        return jsonify({"ok": False, "error": "Invalid YAML configuration syntax."}), 400


@app.route('/static/covers/<path:filename>')
def serve_covers(filename):
    if (COVERS_DIR / filename).exists():
        return send_from_directory(COVERS_DIR, filename)
    bundled_covers = BUNDLE_DIR / "static" / "covers"
    if (bundled_covers / filename).exists():
        return send_from_directory(bundled_covers, filename)
    return send_from_directory(COVERS_DIR, filename)


@app.after_request
def add_cache_headers(response):
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    else:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8420, debug=False)
