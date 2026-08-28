# ROM Cat: Retro & Modern Emulator Web Catalog

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-Web%20Framework-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SteamGridDB](https://img.shields.io/badge/SteamGridDB-API%20Cover%20Art-171a21)](https://www.steamgriddb.com)
[![YAML](https://img.shields.io/badge/Config-YAML-CB171E?logo=yaml&logoColor=white)](https://yaml.org)
[![Linux](https://img.shields.io/badge/Platform-Linux%20%2F%20Wayland%20%2F%20X11-FCC624?logo=linux&logoColor=black)](https://kernel.org)

A fast, lightweight, self-hosted web catalog and remote launcher for your retro and modern ROM collection. It runs locally alongside your installed emulators (Flatpak, AppImage, or native binaries), providing an interactive web dashboard with cover art, system filtering, instant search, favorites tracking, one-click game launching, and customizable themes.

---

## Screenshots

### Main Dashboard (Favorites & Custom Glowing Borders)
![ROM Catalog Dashboard](screenshots/catalog.jpg?raw=true&v=2)

### Settings & Customization Modal
![Settings Modal](screenshots/settings.png?raw=true&v=2)

### Nord Frost Theme
![Nord Theme](screenshots/theme.jpg?raw=true&v=2)

---

## Features

- **Direct Native Emulator Launching**: Games launch in your real desktop emulators (Flatpak, native binaries, or RetroArch cores) on the host machine. No slow or inaccurate in-browser emulation.
- **System Tabs & Live Counters**: Instant switching between systems (e.g. NES, SNES, N64, Gamecube, Wii U, Switch, Favorites, All, Hidden).
- **Fast Search & Filtering**: Real-time title search across thousands of ROMs with automatic title normalization (stripping tags like `[!]`, `(USA)`, `(Rev 1)`, `.nkit`).
- **Automated Cover Art Scraping**: One-click cover fetching from SteamGridDB with automatic image optimization and local caching in `static/covers/`.
- **Manual Cover Art Override**: Drop custom cover art directly into the web UI or filesystem for unmatched or homebrew titles.
- **Favorites & Visibility Management**: Toggle game favorites with custom glowing highlights, or hide unwanted duplicates/updates from the main catalog.
- **Zero Heavy Databases**: Library state is indexed dynamically from your real directory structure, with cached metadata and settings stored in lightweight JSON files.
- **Built-in Settings & Theme Customization**: Click the gear icon in the header to customize the catalog title, select from 6 built-in theme presets, or configure custom colors with live previews.
- **Automatic High-Contrast Text**: Active tab text dynamically detects background color luminance to ensure legibility on both bright and dark themes.
- **UI Visibility Controls**: Toggle visibility of the search bar, cover scraping buttons, rescan button, numeric ROM counts, and tabs.

---

## Quickstart & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/PlasmaDrifter/Emulator-Web-Catelog.git romcat
cd romcat
```

### 2. Create Python Virtual Environment & Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Required Python packages:
- `flask`
- `pyyaml`
- `requests`
- `pillow`
- `ujson`

### 3. Configure Systems & SteamGridDB Key

Edit `config.yaml` to point to your ROM directories and configure emulator commands (see detailed instructions below).

### 4. Run the Application

```bash
python3 app.py
```

Open your browser and navigate to:
```text
http://localhost:8420
```
Or use your machine's local IP / Tailscale IP (e.g. `http://<server-ip>:8420`).

---

## Settings and Customization

ROM Cat includes a Settings interface directly in the web UI (accessible via the gear icon in the top header).

### 1. General Settings
- **Catalog Title**: Update the dashboard title and browser tab title on the fly.
- **Webpage & Tab Icon**: Select from 35+ retro and modern console icons to customize your browser tab favicon and header brand icon:
  - **Nintendo**: NES, SNES, Nintendo 64, GameCube, Wii, Wii U, Switch, Game Boy, GBA, DS, 3DS.
  - **PlayStation**: PlayStation 1, PS2, PS3, PS4, PS5, PSP, PS Vita.
  - **Xbox**: Xbox (Original), Xbox 360, Xbox One, Xbox Series X/S.
  - **Sega**: Master System, Genesis / Mega Drive, Sega CD, 32X, Saturn, Dreamcast, Game Gear.
  - **Atari**: Atari 2600, 5200, 7800, Lynx, Jaguar.
  - **Commodore**: Commodore 64, Amiga, VIC-20.
  - **Retro & Other**: Retro Gamepad, Arcade Cabinet, Neo Geo, Default Favicon.
  - **Custom URL & File Upload**: Paste any image URL or upload any custom PNG/SVG/ICO/JPG directly.

### 2. Theme Presets
- **Default Dark**: Slate dark background with blue accents and magenta favorite glow.
- **Pure OLED**: Pitch black (`#000000`) background with cyan accents and gold favorite highlights.
- **Catppuccin**: Soft purple pastel theme with lavender accents and peach borders.
- **Cyberpunk**: Dark neon theme with bright yellow accents and hot pink glow.
- **Nord Frost**: Arctic blue and slate gray palette with soft amber highlights.
- **Emerald**: Forest dark green background with emerald accents and sky blue highlights.

### 3. Custom Color Pickers
Every color element can be fine-tuned individually with real-time live preview:
- Body Background
- Header Bar
- Tabs Bar
- Card Background
- Primary Accent (Tabs & Focus rings)
- Selected Tab Text Color (with automatic luminance contrast detection)
- Favorite Star & Glowing Border
- Primary Text
- Muted Text & Details

### 4. UI Visibility Toggles
Customize which elements appear on your dashboard:
- Show / Hide Search Bar
- Show / Hide "Fetch Cover Art" Button
- Show / Hide "Rescan Library" Button
- Show / Hide ROM Count Badges (e.g. `(42)`)
- Show / Hide "Favorites" Tab
- Show / Hide "Hidden" Tab & Hide Controls

Settings are stored on disk in `settings.json` and persist across all devices connected to your network.

---

## How to Edit Emulators and Systems

All emulator execution commands, system definitions, ROM paths, and allowed file extensions are configured inside `config.yaml`.

### Configuration Structure

Each system entry in `config.yaml` is structured under the `systems:` block:

```yaml
systems:
  <system_identifier>:
    name: "Display Name"
    folder: "/path/to/rom/directory/"
    extensions: [".ext1", ".ext2"]
    command: "<command_template> {rom}"
```

### Understanding Parameters

- **`system_identifier`**: Lowercase or camelCase key used internally (e.g. `nes`, `snes`, `n64`, `gamecube`, `wiiu`, `switch`).
- **`name`**: The user-facing name shown in the top navigation tab and header.
- **`folder`**: Path to the ROM directory on your host filesystem. Can be a single directory path or a YAML list of multiple paths:
  ```yaml
  folder:
    - "/path/to/primary/roms/WiiU/"
    - "/path/to/secondary/storage/WiiU/"
  ```
- **`extensions`**: List of file extensions to include in the scan.
- **`command`**: The exact shell command used to start the emulator.
  - `{rom}` is automatically replaced by `app.py` with the full, shell-quoted path to the selected ROM file.
  - Environment variables such as `DISPLAY=:0` and `WAYLAND_DISPLAY=wayland-0` can be prepended if needed.

---

### Emulator Command Examples

#### 1. Flatpak Emulators

If your emulators are installed via Flatpak, use `flatpak run <Application-ID> {rom}`:

| System | Emulator | Command in `config.yaml` |
|---|---|---|
| **NES** | Nestopia | `flatpak run ca._0ldsk00l.Nestopia {rom}` |
| **SNES** | Snes9x | `flatpak run com.snes9x.Snes9x {rom}` |
| **SNES** | BSNES | `flatpak run dev.bsnes.bsnes {rom}` |
| **SNES** | ZSNES | `flatpak run io.github.xyproto.zsnes {rom}` |
| **N64** | Gopher64 | `flatpak run io.github.gopher64.gopher64 {rom}` |
| **N64** | Mupen64Plus | `flatpak run io.github.mupen64plus.mupen64plus-gui {rom}` |
| **GameCube / Wii** | Dolphin | `flatpak run org.DolphinEmu.dolphin-emu {rom}` |
| **Wii U** | Cemu | `flatpak run info.cemu.Cemu -g {rom}` |
| **PlayStation 1** | DuckStation | `flatpak run org.duckstation.DuckStation {rom}` |
| **PlayStation 2** | PCSX2 | `flatpak run net.pcsx2.PCSX2 {rom}` |
| **GBA** | mGBA | `flatpak run io.mgba.mGBA {rom}` |
| **PSP** | PPSSPP | `flatpak run org.ppsspp.PPSSPP {rom}` |

#### 2. Native Binaries & AppImages

For standalone binaries or AppImages located in your system or applications directory:

```yaml
Switch:
  name: "Switch"
  folder: "/path/to/roms/Switch/"
  extensions: [".nsp", ".xci"]
  command: "env DISPLAY=:0 WAYLAND_DISPLAY=wayland-0 /path/to/emulator/binary -g {rom}"
```

#### 3. RetroArch with Libretro Cores

To launch via RetroArch cores directly:

```yaml
snes:
  name: "SNES"
  folder: "/path/to/roms/SNES/"
  extensions: [".sfc", ".smc"]
  command: "retroarch -L /usr/lib/libretro/snes9x_libretro.so {rom}"
```

---

### Adding a New Console / System

To add a new console (for example, Game Boy Advance):

1. Open `config.yaml`.
2. Add a new block under `systems:`:

```yaml
  gba:
    name: "Game Boy Advance"
    folder: "/path/to/roms/GBA/"
    extensions: [".gba", ".zip"]
    command: "flatpak run io.mgba.mGBA {rom}"
```

3. Save `config.yaml`.
4. Click **Rescan library** in the top navigation bar or restart `app.py`. The new tab will appear automatically with game counts.

---

## How Cover Art Scraping Works

1. **Automatic Scraping with SteamGridDB**:
   - Register for a free API key at [SteamGridDB API Preferences](https://www.steamgriddb.com/profile/preferences/api).
   - Paste your key into `config.yaml` under `steamgriddb.api_key`.
   - Click **Fetch cover art** in the header.
   - The application automatically strips revision and dump tags (e.g. `(USA)`, `[!]`, `.nkit`), searches SteamGridDB, resizes the image to 300x400 JPG, and saves it to `static/covers/`.
   - Re-running only downloads covers for games that are still missing art.

2. **Manual Cover Art Overrides**:
   - For obscure or homebrew titles, type a custom search term into the cover card's **Find cover** input and click search.
   - Alternatively, drop any image into `static/covers/` using the following naming convention:
     `static/covers/<system>_<rom_stem>.jpg`
     *(Spaces and punctuation in the ROM filename become underscores)*.

---

## Repository File Tree

```text
Emulator-Web-Catelog/
├── README.md                # Full documentation, configuration guides, and theme options
├── config.yaml              # System definitions, ROM folder paths, and emulator commands
├── app.py                   # Flask server, library scanner, SteamGridDB client, and launcher
├── requirements.txt         # Python dependencies (flask, pyyaml, requests, pillow, ujson)
├── settings.json            # User customizable title, theme colors, and UI visibility options
├── favorites.json           # Saved user favorites list
├── hidden.json              # List of hidden ROM keys (updates, duplicates, DLCs)
├── library.json             # Cached library metadata for instant page load performance
├── .gitignore               # Ignore cache, logs, virtual environments, and scraped covers
├── screenshots/
│   ├── catalog.jpg          # Application dashboard screenshot (Default theme with glowing borders)
│   ├── settings.png         # Settings and customization modal screenshot
│   └── theme.jpg            # Application dashboard screenshot (Catppuccin theme)
├── static/
│   ├── favicon.png          # Web browser favicon
│   ├── covers/              # Local cache directory for game boxart
│   │   └── .gitkeep
│   ├── icons/               # System SVG icons (Nintendo, PlayStation, Xbox, Sega, Atari, Commodore)
│   └── css/
│       └── style.css        # CSS styles, theme variables, grid layout, and glow animations
└── templates/
    └── index.html           # Main dashboard template with search, tabs, settings, and launching modal
```

---

## Running as a Background Systemd Service

To keep the web catalog running automatically in the background on boot:

1. Create a user service definition at `~/.config/systemd/user/romcat.service`:

```ini
[Unit]
Description=ROM Cat Emulator Web Catalog
After=network.target

[Service]
Type=simple
WorkingDirectory=%h/romcat
ExecStart=%h/romcat/venv/bin/python3 %h/romcat/app.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

*(Note: `%h` is a standard systemd specifier that automatically expands to the user's home directory. Adjust `%h/romcat` if your clone is located in another folder).*

2. Enable and start the user service:

```bash
systemctl --user daemon-reload
systemctl --user enable --now romcat.service
```

3. Check service status:

```bash
systemctl --user status romcat.service
```

---

## License

Created and maintained by [PlasmaDrifter](https://github.com/PlasmaDrifter). Distributed for personal and self-hosted use.

