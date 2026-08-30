# ROM Cat: Retro & Modern Emulator Web Catalog

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-Web%20Framework-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SteamGridDB](https://img.shields.io/badge/SteamGridDB-API%20Cover%20Art-171a21)](https://www.steamgriddb.com)
[![YAML](https://img.shields.io/badge/Config-YAML-CB171E?logo=yaml&logoColor=white)](https://yaml.org)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-blue)](https://python.org)

## About

**ROM Cat** is a fast, lightweight catalog and launcher for your retro and modern ROM collection. It can be run in two primary ways:

- **Standalone Desktop Application**: Download the pre-packaged app to run ROM Cat as a dedicated, self-contained desktop window with native desktop integration (Wayland and X11 app icon and launcher support)—no Python setup or terminal commands required.
- **Always-Ready Web Service**: Run ROM Cat as a persistent background service (or local web server) accessible in your web browser (`http://localhost:8420`) ready to launch games instantly whenever your system boots.

ROM Cat provides an interactive dashboard with automated cover art scraping, system filtering, instant search, favorites tracking, one-click game launching into your local desktop emulators (Flatpak, AppImage, or native binaries), and customizable themes.

---

## Screenshots

### Main Dashboard
![ROM Catalog Dashboard](screenshots/catalog.png?raw=true&v=3)

### Theme Presets (Loop)
![ROM Cat Themes Animated Preview](screenshots/themes_preview.gif?raw=true&v=2)

### Settings: Appearance Tab
![Settings Appearance Tab](screenshots/settings_appearance.png?raw=true&v=3)

### Settings: UI Tab
![Settings UI Tab](screenshots/settings_ui.png?raw=true&v=3)

### Settings: Consoles & Emulators Tab
![Settings Consoles & Emulators Tab](screenshots/settings_consoles.png?raw=true&v=3)

### Settings: Interactive Command Guide
![Settings Command Guide](screenshots/settings_consoles_help.png?raw=true&v=3)

---

## Features

- **Direct Native Emulator Launching**: Games launch in your real desktop emulators (Flatpak, native binaries, AppImages, or RetroArch cores) on your system. No slow or inaccurate in-browser emulation.
- **Two Flexible Modes**: Use the standalone desktop app with dedicated window management or run as an always-on background web service.
- **System Tabs & Live Counters**: Instant switching between systems (e.g. NES, SNES, N64, GameCube, Wii U, Switch, Favorites, All, Hidden).
- **Fast Search & Filtering**: Real-time title search across thousands of ROMs with automatic title normalization (stripping tags like `[!]`, `(USA)`, `(Rev 1)`, `.nkit`).
- **Automated Cover Art Scraping**: One-click cover fetching from SteamGridDB with automatic image optimization and local caching in `static/covers/`.
- **Manual Cover Art Override**: Drop custom cover art directly into the web UI or filesystem for unmatched or homebrew titles.
- **Favorites & Visibility Management**: Toggle game favorites with custom glowing highlights, or hide unwanted duplicates/updates from the main catalog.
- **Zero Heavy Databases**: Library state is indexed dynamically from your real directory structure, with cached metadata and settings stored in lightweight JSON files.
- **Built-in Settings & Theme Customization**: Click the gear icon in the header to customize the catalog title, select from 6 built-in theme presets, or configure custom colors with live previews.
- **Automatic High-Contrast Text**: Active tab text dynamically detects background color luminance to ensure legibility on both bright and dark themes.
- **UI Visibility Controls**: Toggle visibility of the search bar, cover scraping buttons, rescan button, numeric ROM counts, and tabs.

---

## Ways to Run ROM Cat

### Option 1: Standalone Desktop App (Recommended for Desktop Users)

The packaged standalone desktop app provides a self-contained executable with native desktop windowing and launcher integration. No Python installation is required.

1. Download the latest Linux release bundle (`ROMCat-v0.1.0-linux-x86_64.tar.gz` or `.zip`) from the [Releases page](https://github.com/PlasmaDrifter/Emulator-Web-Catelog/releases).
2. Extract the archive:
   ```bash
   tar -xzf ROMCat-v0.1.0-linux-x86_64.tar.gz
   cd Standalone.app
   ```
3. Run the application directly:
   ```bash
   ./ROMCat
   ```
4. *(Optional)* Install the Desktop Launcher and Icon into your desktop environment:
   ```bash
   mkdir -p ~/.local/share/applications ~/.local/share/icons/hicolor/256x256/apps
   cp icon.png ~/.local/share/icons/hicolor/256x256/apps/romcat.png
   sed -i "s|Exec=.*|Exec=\"$(pwd)/ROMCat\"|" ROMCat.desktop
   cp ROMCat.desktop ~/.local/share/applications/
   update-desktop-database ~/.local/share/applications/
   ```

---

### Option 2: Always-On Background Service (Systemd)

To keep ROM Cat running automatically in the background so your catalog is always loaded, ready, and accessible at `http://localhost:8420` whenever your computer starts:

1. Clone the repository and install dependencies:
   ```bash
   git clone https://github.com/PlasmaDrifter/Emulator-Web-Catelog.git ~/romcat
   cd ~/romcat
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Create a systemd user service file at `~/.config/systemd/user/romcat.service`:
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
3. Enable and start the background service:
   ```bash
   systemctl --user daemon-reload
   systemctl --user enable --now romcat.service
   ```
4. Open your browser and navigate to:
   ```text
   http://localhost:8420
   ```
   *(Or access from any device on your local network using `http://<your-ip>:8420`).*

To check service status or view logs:
```bash
systemctl --user status romcat.service
journalctl --user -u romcat.service -f
```

---

### Option 3: Manual Python Web Server (Development / Command Line)

If you prefer starting the web server manually via the command line:

1. Clone and install dependencies:
   ```bash
   git clone https://github.com/PlasmaDrifter/Emulator-Web-Catelog.git romcat
   cd romcat
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python3 app.py
   ```
3. Open your browser at `http://localhost:8420`.

---

## Settings and Customization

ROM Cat includes a tabbed Settings interface directly in the web UI (accessible via the gear icon in the top header).

### 1. Appearance Tab
- **General Settings**:
  - **Catalog Title**: Update the dashboard title and browser tab title on the fly.
  - **Webpage & Tab Icon**: Select from 35+ retro and modern console icons (Nintendo, PlayStation, Xbox, Sega, Atari, Commodore, Retro) or upload a custom image.
- **Theme Presets**: Switch instantly between 6 presets: Default Dark, Pure OLED, Catppuccin, Cyberpunk, Nord Frost, and Emerald.
- **Custom Color Pickers**: Fine-tune every color element individually with real-time live preview (backgrounds, accents, glowing borders, active tab text, favorite star).

### 2. UI Tab
- **Library Actions**:
  - **Fetch Cover Art**: One-click automated cover scraping from SteamGridDB with live status feedback.
  - **Rescan Library**: Scan storage paths for newly added, moved, or deleted ROM files.
- **Hidden Games & Edit Mode**:
  - **Show Card Hide Buttons (Edit Mode)**: Displays eye buttons on individual game cards to hide duplicates, DLCs, and unwanted ROMs.
  - **Show "Hidden" Tab in Navigation**: Adds a "Hidden" tab to the top navigation bar.
  - **View Hidden ROMs Button**: Jump straight to hidden ROMs with a single click.
- **UI Visibility Controls**:
  - **Show Search Bar**: Toggle real-time search input in the header.
  - **Show ROM Count Badges**: Display numeric game counts on system tabs (e.g. `(42)`).
  - **Show "Favorites" Tab**: Toggle favorites tab on the navigation bar.

### 3. Consoles & Emulators Tab
- **Visual Console Form Cards**: Add, configure, and remove consoles through clean input fields without manually formatting YAML:
  - **Display Name**: User-facing name shown in tabs and headers.
  - **System Identifier**: Lowercase key used internally (e.g. `nes`, `switch`).
  - **ROM Folder Path(s)**: Host directory path (or multiple lines for multi-folder scanning).
  - **Allowed Extensions**: Comma-separated list (e.g. `.iso, .rvz, .zip`).
  - **Emulator Command**: Full command line template with `{rom}` token.
- **SteamGridDB API Key Field**: Direct input with show/hide password toggle.
- **+ Add Console**: Instantly append a new console configuration card.
- **Advanced Raw YAML Editor (Collapsible)**: Optional raw editor with two-way sync for advanced users.
- **Instant Save & Rescan**: Automatically compiles the form into `config.yaml`, validates structure, and rescans your library immediately.

Settings and theme configurations are stored on disk in `settings.json` and persist across browser sessions.

---

## How to Edit Emulators and Systems

All emulator execution commands, system definitions, ROM paths, and allowed file extensions can be configured directly in the web UI under the **Consoles & Emulators** tab, or edited manually inside `config.yaml`.

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

#### 4. Windows Executables (.exe)

On Windows, point directly to your emulator `.exe` and ROM folders:

```yaml
gamecube:
  name: "GameCube"
  folder: "D:/ROMs/GameCube"
  extensions: [".iso", ".rvz", ".gcz"]
  command: '"C:\\Emulators\\Dolphin\\Dolphin.exe" -b -e {rom}'

snes:
  name: "SNES"
  folder: "D:/ROMs/SNES"
  extensions: [".sfc", ".smc", ".zip"]
  command: '"C:\\RetroArch-Win64\\retroarch.exe" -L "cores\\snes9x_libretro.dll" {rom}'
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
├── config.example.yaml      # Clean configuration template (systems, paths, commands, SteamGridDB)
├── app.py                   # Flask server, library scanner, SteamGridDB client, and launcher
├── requirements.txt         # Python dependencies (flask, pyyaml, requests, pillow, ujson)
├── .gitignore               # Ignore cache, logs, virtual environments, covers, and local user data
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

## License

Created and maintained by [PlasmaDrifter](https://github.com/PlasmaDrifter). Distributed for personal and self-hosted use.

