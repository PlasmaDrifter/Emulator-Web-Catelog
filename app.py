#!/usr/bin/env python3
"""
romcat - a tiny self-hosted ROM catalog that launches games in your real,
native emulators (not in-browser emulation). Runs on the same machine as
your emulators; browser is just the remote control.
"""
import os
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

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.yaml"
COVERS_DIR = BASE_DIR / "static" / "covers"
FAVORITES_PATH = BASE_DIR / "favorites.json"
HIDDEN_PATH = BASE_DIR / "hidden.json"
LIBRARY_CACHE_PATH = BASE_DIR / "library.json"
COVERS_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)

# Global memory cache for library metadata
_library_cache = None


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


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


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

    # Cache existing cover filenames in memory for fast lookup
    existing_covers = {p.name for p in COVERS_DIR.iterdir() if p.is_file()}

    for sys_id, sys_cfg in config["systems"].items():
        folders_cfg = sys_cfg["folder"]
        folders = [folders_cfg] if isinstance(folders_cfg, str) else folders_cfg
        exts = [e.lower() if e.startswith('.') else f".{e.lower()}" for e in sys_cfg["extensions"]]
        games = []
        seen_paths = set()

        for folder_str in folders:
            folder = Path(folder_str).expanduser()
            if not folder.is_dir():
                continue

            # Scan matching target extensions explicitly (skips unneeded disk files)
            for ext in exts:
                for entry in folder.rglob(f"*{ext}"):
                    if not entry.is_file():
                        continue
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
                    except ValueError:
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
            "name": sys_cfg["name"],
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
    return render_template("index.html", library=library)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.jpg",
        mimetype="image/jpeg"
    )


@app.route("/api/rescan")
def api_rescan():
    library_data = scan_library()
    save_library_cache(library_data)
    return jsonify(library_data)


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

    rom_path = Path(path)
    try:
        resolved = rom_path.resolve()
    except Exception:
        return jsonify({"ok": False, "error": "bad path"}), 400

    folders_cfg = sys_cfg["folder"]
    folders = [folders_cfg] if isinstance(folders_cfg, str) else folders_cfg
    allowed = False
    for folder_str in folders:
        try:
            configured_folder = Path(folder_str).expanduser().resolve()
            if configured_folder in resolved.parents or resolved == configured_folder:
                allowed = True
                break
        except Exception:
            continue

    if not allowed:
        return jsonify({"ok": False, "error": "path outside configured folder"}), 400
    if not resolved.is_file():
        return jsonify({"ok": False, "error": "file not found"}), 404

    cmd_template = sys_cfg["command"]
    cmd = cmd_template.format(rom=shlex.quote(str(resolved)))
    env = os.environ.copy()
    if "DISPLAY" not in env:
        env["DISPLAY"] = ":0"
    if "WAYLAND_DISPLAY" not in env:
        env["WAYLAND_DISPLAY"] = "wayland-0"
    if "XDG_RUNTIME_DIR" not in env:
        env["XDG_RUNTIME_DIR"] = f"/run/user/{os.getuid()}"

    try:
        subprocess.Popen(
            shlex.split(cmd),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
            start_new_session=True,
        )
    except FileNotFoundError as e:
        return jsonify({"ok": False, "error": f"emulator not found: {e}"}), 500

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


@app.route('/static/covers/<path:filename>')
def serve_covers(filename):
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
