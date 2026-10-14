# ROMcat: Retro & Modern Emulator Web Catalog

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-Web%20Framework-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SteamGridDB](https://img.shields.io/badge/SteamGridDB-API%20Cover%20Art-171a21)](https://www.steamgriddb.com)
[![YAML](https://img.shields.io/badge/Config-YAML-CB171E?logo=yaml&logoColor=white)](https://yaml.org)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-blue)](https://python.org)

## About

**ROMcat** is a fast, lightweight catalog and launcher for your retro and modern ROM collection that runs directly in your web browser. It can be run in two primary ways:

- **Always-Ready Web Service**: Run ROMcat as a persistent background service (or local web server) accessible in your web browser (`http://localhost:8420`) ready to launch games instantly whenever your system boots.
- **Standalone Desktop Application**: Download the pre-packaged app to run ROMcat as a dedicated, self-contained desktop window with native desktop integration (Wayland, X11, and Windows)—no Python setup or terminal commands required.

ROMcat provides an interactive dashboard with automated cover art scraping, system filtering, instant search, favorites tracking, one-click game launching into your local desktop emulators (Flatpak, AppImage, or native binaries), and customizable themes.

---

## Demo

![ROMcat Demo](screenshots/demo.gif?raw=true&v=1)

---

## Screenshots

### Main Dashboard
![ROM Catalog Dashboard](screenshots/catalog.png?raw=true&v=5)

### Play Time Statistics
![ROMcat Play Statistics](screenshots/statistics.png?raw=true&v=2)

### Theme Presets (Loop)
![ROMcat Themes Animated Preview](screenshots/themes_preview.gif?raw=true&v=3)

### Settings & Customization

<table>
  <tr>
    <th width="50%">Appearance Tab</th>
    <th width="50%">Favicon &amp; Console Icon Tab</th>
  </tr>
  <tr>
    <td><a href="screenshots/settings_appearance.png"><img src="screenshots/settings_appearance.png?raw=true&v=7" alt="Settings Appearance Tab"></a></td>
    <td><a href="screenshots/settings_favicon_console_icon.png"><img src="screenshots/settings_favicon_console_icon.png?raw=true&v=8" alt="Settings Favicon and Console Icon Tab"></a></td>
  </tr>
  <tr>
    <th width="50%">UI Tab</th>
    <th width="50%">Consoles &amp; Emulators Tab</th>
  </tr>
  <tr>
    <td><a href="screenshots/settings_ui.png"><img src="screenshots/settings_ui.png?raw=true&v=7" alt="Settings UI Tab"></a></td>
    <td><a href="screenshots/settings_consoles.png"><img src="screenshots/settings_consoles.png?raw=true&v=8" alt="Settings Consoles & Emulators Tab"></a></td>
  </tr>
  <tr>
    <th width="50%">Interactive Command Guide</th>
    <th width="50%"></th>
  </tr>
  <tr>
    <td><a href="screenshots/settings_consoles_help.png"><img src="screenshots/settings_consoles_help.png?raw=true&v=7" alt="Settings Command Guide"></a></td>
    <td></td>
  </tr>
</table>

---

## Features

- **Direct Native Emulator Launching**: Games launch in your real desktop emulators (Flatpak, native binaries, AppImages, or RetroArch cores) on your system. No slow or inaccurate in-browser emulation.
- **Two Flexible Modes**: Use the standalone desktop app with dedicated window management or run as an always-on background web service.
- **Play Time Statistics Dashboard**: Dedicated statistics page (`/stats`) tracking total play time, session counts, distinct games played, and top consoles. Includes interactive console breakdown charts, play leaderboards, recent activity feeds, per-game reset controls, interactive detailed game statistics modal with 7-Day, 14-Day, 30-Day, and 1-Year timeframe controls, effortless magnetic hover tracking, and responsive category filtering.
- **Dynamic Sorting & Filtering**: Sort your game catalog by Name (A-Z with favorites prioritized), Most Played (by cumulative play time), Most Played (by total play sessions), or Recently Played.
- **Background Session Tracking**: Automatically monitors active emulator processes and systemd scopes in the background to log play sessions (with minimum time threshold) without manual logging.
- **System Tabs & Live Counters**: Instant switching between systems (e.g. NES, SNES, N64, GameCube, Wii U, Switch, Favorites, All, Hidden).
- **Fast Search & Filtering**: Real-time title search across thousands of ROMs with automatic title normalization (stripping tags like `[!]`, `(USA)`, `(Rev 1)`, `.nkit`).
- **Automated Cover Art Scraping & Interactive Picker**: One-click cover fetching from SteamGridDB with per-console targeting, overwrite controls, multi-pass fallback title matching, and authentic portrait box-art filtering (600x900). Includes an interactive modal on game cards to search, browse, and select between alternative box arts with live previews.
- **Manual Cover Art Override**: Drop custom cover art directly into the web UI or filesystem for unmatched or homebrew titles.
- **Favorites & Visibility Management**: Toggle game favorites with custom glowing highlights, or hide unwanted duplicates/updates from the main catalog.
- **Zero Heavy Databases**: Library state is indexed dynamically from your real directory structure, with cached metadata and settings stored in lightweight JSON files.
- **Built-in Settings & Theme Customization**: Click the gear icon in the header to customize the catalog title, select from 6 built-in theme presets, or configure custom colors with live previews.

---

## Ways to Run ROMcat

### Option 1: Automated Installer (Recommended for Linux)

Run the included automated installer to set up ROMcat with a single command. The installer automatically installs Python dependencies, registers the desktop menu launcher and application icon, creates the `romcat` CLI command in `~/.local/bin`, and enables the background systemd user service (`romcat.service`):

1. Clone the repository and run the installer:
   ```bash
   git clone https://github.com/PlasmaDrifter/Emulator-Web-Catelog.git ~/romcat
   cd ~/romcat
   ./install.sh
   ```
2. Open your browser and navigate to:
   ```text
   http://localhost:8420
   ```
   *(Bookmark this address in your browser to access your game catalog instantly anytime, or launch it from your desktop applications menu under **Games**).*

#### CLI Commands

After installation, you can control ROMcat directly from your terminal:

```bash
romcat          # Ensure server is running and open in default browser
romcat start    # Start background service
romcat stop     # Stop background service
romcat restart  # Restart background service
romcat status   # View current service status
romcat logs     # View live service journal logs
```

#### Uninstallation

To uninstall ROMcat and remove its desktop entry, icons, and systemd service:

```bash
./uninstall.sh

# Or uninstall and purge local settings/covers:
./uninstall.sh --purge
```

---

### Option 2: Standalone Windows App (Recommended for Windows)

The standalone Windows application provides a self-contained portable executable with dedicated desktop windowing. No Python installation, terminal commands, or background services are required:

1. Download the Windows release bundle (**`ROMCat-v*-windows-x64.zip`** or standalone **`ROMCat.exe`**) from the [Releases page](https://github.com/PlasmaDrifter/Emulator-Web-Catelog/releases).
2. If using the ZIP, extract it to your preferred folder (for example `C:\ROMcat` or `D:\ROMcat`). If using `ROMCat.exe`, place it in your chosen folder.
3. Double-click **`ROMCat.exe`** to launch ROMcat.
   *(Optional: Right-click `ROMCat.exe` &rarr; **Send to** &rarr; **Desktop (create shortcut)** for quick access).*
4. Open **Settings** (gear icon in the top header) &rarr; **Consoles & Emulators** to configure your ROM folder paths (e.g. `D:\ROMs\NES`) and emulator commands (e.g. `"C:\Emulators\snes9x\snes9x.exe" {rom}`).

*(Your `config.yaml`, custom settings in `settings.json`, and downloaded covers in `static/covers/` are saved directly in the application directory and persist across restarts).*

---

### Option 3: Standalone Linux Desktop App (Portable Binary)

For Linux users who prefer a portable, self-contained desktop window without setting up a background systemd service:

1. Download the latest Linux release bundle (**`ROMCat-v*-linux-x86_64.tar.gz`**, **`ROMCat-v*-linux-x86_64.zip`**, or the standalone Linux executable **`ROMCat`**) from the [Releases page](https://github.com/PlasmaDrifter/Emulator-Web-Catelog/releases).
   *(Note: The standalone Linux binary is named `ROMCat` without a `.exe` extension. If downloading it directly, ensure executable permission with `chmod +x ROMCat`).*
2. If using an archive, extract it:
   ```bash
   tar -xzf ROMCat-*-linux-x86_64.tar.gz
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

### Option 4: Manual Python Web Server (Development / Command Line)

If you prefer starting the local web server manually via the command line (cross-platform for Linux, Windows, or macOS):

**On Linux / macOS**:
```bash
git clone https://github.com/PlasmaDrifter/Emulator-Web-Catelog.git romcat
cd romcat
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

**On Windows (PowerShell / Command Prompt)**:
```powershell
git clone https://github.com/PlasmaDrifter/Emulator-Web-Catelog.git romcat
cd romcat
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open your browser at `http://localhost:8420`.

---

## Updating ROMcat

Updating ROMcat preserves all your existing configuration, scanned games, downloaded covers (`static/covers/`), favorites, and theme settings.

### Option A: One-Click In-App Updater (Recommended)

ROMcat includes an integrated, zero-terminal self-updater for both Git installations and direct archive installations:

1. When a new release is detected, an update notification banner appears inside the Settings dialog (and a red badge appears on the Settings gear icon if enabled).
2. Click **Update Now** on the notification banner.
3. ROMcat downloads and extracts the release directly in place, updates internal files while strictly preserving your `config.yaml`, `settings.json`, downloaded covers (`static/covers/`), and custom theme presets, and automatically restarts the background service or desktop app.
4. Your browser will automatically reconnect and reload the updated dashboard as soon as the service finishes restarting.

*(You can also dismiss the banner until the next release or toggle update notifications under **Settings &rarr; UI &rarr; Check for New Releases**).*

### Option B: Updating with Git (Terminal)

Because this repository is public, `git pull` does **not** require a GitHub account, token, or login:

```bash
cd ~/romcat
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
systemctl --user restart romcat.service
```

### Option C: Updating Manually Without Git (ZIP Archive)

If you installed from an archive without Git, you can also update manually via terminal or by clicking **Code &rarr; Download ZIP** on GitHub:

```bash
cd ~
curl -LO https://github.com/PlasmaDrifter/Emulator-Web-Catelog/archive/refs/heads/main.zip
unzip -q main.zip
# Copy updated application files into your existing folder (overwriting app files, preserving configs & covers)
cp -r Emulator-Web-Catelog-main/* ~/romcat/
rm -rf main.zip Emulator-Web-Catelog-main

cd ~/romcat
source venv/bin/activate
pip install -r requirements.txt
systemctl --user restart romcat.service
```
*(Your custom `config.yaml`, downloaded covers in `static/covers/`, favorites, and theme settings are preserved).*

### Updating the Standalone Desktop Application

#### On Windows:
1. Download the latest Windows release bundle (**`ROMCat-v*-windows-x64.zip`** or **`ROMCat.exe`**) from the [Releases page](https://github.com/PlasmaDrifter/Emulator-Web-Catelog/releases).
2. Replace `ROMCat.exe` inside your ROMcat folder with the newly downloaded version.
   *(Your `config.yaml`, `static/covers/`, and `settings.json` are preserved).*

#### On Linux:
1. Download the latest Linux release bundle (**`ROMCat-v*-linux-x86_64.tar.gz`**, **`ROMCat-v*-linux-x86_64.zip`**, or the standalone Linux executable **`ROMCat`**) from the [Releases page](https://github.com/PlasmaDrifter/Emulator-Web-Catelog/releases).
2. If updating with an archive, extract and replace the executable:
   ```bash
   tar -xzf ROMCat-*-linux-x86_64.tar.gz
   cp Standalone.app/ROMCat ~/path/to/your/Standalone.app/ROMCat
   ```
   If updating directly with the standalone `ROMCat` binary:
   ```bash
   chmod +x ROMCat
   cp ROMCat ~/path/to/your/Standalone.app/ROMCat
   ```
   *(Your `config.yaml`, `static/covers/`, and custom settings are untouched).*

3. **Building from Source (Local Compilation)**:
   If you compile the standalone binary locally on your system:
   ```bash
   cd ~/romcat
   git pull origin main
   source venv/bin/activate
   pip install -r requirements.txt
   pyinstaller ROMCat.spec --noconfirm
   cp dist/ROMCat Standalone.app/ROMCat
   ```

---

## Settings and Customization

ROMcat includes a tabbed Settings interface directly in the web UI (accessible via the gear icon in the top header).

### 1. Appearance Tab
- **General Settings**:
  - **Catalog Title**
- **Theme Presets**
- **Custom Color Pickers**

### 2. Favicon and Console Icon Tab
- **Favicon & Header Icon**
- **Show Console Tab Icons Toggle**
- **Customize Console Tab Icons**
- **Folder & Icon Management**

### 3. UI Tab
- **Library Actions**:
  - **Fetch Cover Art**
  - **Rescan Library**
- **Hidden Games & Edit Mode**:
  - **Show Card Hide Buttons (Edit Mode)**
  - **Show "Hidden" Tab in Navigation**
  - **View Hidden ROMs Button**
- **UI Visibility Controls**:
  - **Show Search Bar**
  - **Show ROM Count Badges**
  - **Show "Favorites" Tab**
  - **Show GitHub Link in Header**
  - **Check for New Updates**

### 4. Consoles & Emulators Tab
- **Console Category Reordering**:
  - **Move Up (▲) / Move Down (▼) Buttons**
  - **Drag-and-Drop Handles (`⋮⋮`)**
  - **Dynamic Persistence**
- **Visual Console Form Cards**:
  - **Display Name**
  - **System Identifier**
  - **ROM Folder Path(s)**
  - **Allowed Extensions**
  - **Emulator Command**
- **SteamGridDB API Key Field**
- **+ Add Console**
- **Advanced Raw YAML Editor (Collapsible)**
- **Instant Save & Rescan**

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

#### 2. Standalone Binaries & AppImages (e.g. `~/Applications/`)

For standalone executables or AppImages kept in your user directories (such as `~/Applications/`, `~/AppImages/`, or `~/.local/bin/`), point directly to the full path of the executable.

> [!TIP]
> **Zero Environment Setup Required**: ROMcat automatically discovers your active desktop environment (`WAYLAND_DISPLAY`, `DISPLAY`, `XAUTHORITY`, `DBUS_SESSION_BUS_ADDRESS`) and automatically launches emulator binaries inside an independent user session scope (`systemd-run --user --scope`). You do **not** need to manually prefix commands with `env DISPLAY=...`.

```yaml
Switch:
  name: "Switch"
  folder: "/path/to/roms/Switch/"
  extensions: [".nsp", ".xci"]
  command: "/home/user/Applications/Eden -g {rom}"
```

Common standalone and AppImage examples:

| System | Emulator / Binary | Example Command in `config.yaml` |
|---|---|---|
| **Nintendo Switch** | Eden (AppImage / Binary) | `/home/user/Applications/Eden -g {rom}` |
| **PlayStation 3** | RPCS3 (AppImage) | `/home/user/Applications/RPCS3.AppImage {rom}` |
| **Nintendo Switch** | Ryujinx | `/home/user/Applications/Ryujinx/Ryujinx {rom}` |
| **PlayStation 2** | PCSX2 (AppImage) | `/home/user/Applications/pcsx2.AppImage {rom}` |
| **Nintendo 3DS** | Citra / Lime3DS | `/home/user/Applications/lime3ds {rom}` |

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

You can add new consoles either directly through the **web interface** (recommended) or manually inside `config.yaml`.

#### Method 1: In the Web UI (Recommended)

1. Click the **Settings** gear icon in the top header.
2. Switch to the **Consoles & Emulators** tab.
3. Click **+ Add Console** at the top right of the section.
4. Fill in the console details:
   - **Display Name**: e.g., `Game Boy Advance` (an internal identifier will be auto-generated).
   - **ROM Folder Path**: e.g., `/home/user/ROMs/GBA/` or `$HOME/ROMs/GBA/`.
   - **Allowed Extensions**: e.g., `.gba, .zip`.
   - **Emulator Launch Command**: e.g., `flatpak run io.mgba.mGBA {rom}` or `$HOME/Applications/mgba {rom}`.
5. Click **Save** at the bottom right. ROMcat validates the settings, saves `config.yaml`, and automatically rescans your library.

#### Method 2: Manually in `config.yaml`

1. Open `config.yaml` in your text editor.
2. Add a new block under `systems:`:

```yaml
  gba:
    name: "Game Boy Advance"
    folder: "$HOME/ROMs/GBA/"
    extensions: [".gba", ".zip"]
    command: "flatpak run io.mgba.mGBA {rom}"
```

3. Save `config.yaml`.
4. Go to **Settings &rarr; UI** and click **Rescan** (or restart the app). The new console tab will appear automatically with game counts.

---

## How Cover Art Scraping Works

1. **Automatic Scraping with SteamGridDB**:
   - Register for a free API key at [SteamGridDB API Preferences](https://www.steamgriddb.com/profile/preferences/api).
   - Paste your key into Settings $\rightarrow$ Consoles tab (or directly into `config.yaml` under `steamgriddb.api_key`).
   - Go to Settings $\rightarrow$ UI tab: choose **All Consoles** or a specific console from the dropdown, optionally check **Overwrite existing**, and click **Fetch Covers**.
   - **Smart Multi-Pass Title Matching**: The engine automatically executes multiple fallback passes:
     - Strips dump/region tags (e.g. `[!]`, `(USA)`, `(Rev 1)`, `.nkit`).
     - Strips multi-disc markers (e.g. `(Disc 1)`).
     - Resolves subtitle variants (e.g. searching both `The Legend of Zelda - Ocarina of Time` and `Ocarina of Time`).
     - Normalizes Roman numerals (`II` $\leftrightarrow$ `2`).
   - **Curated Box-Art Filtering**: Scraper queries authentic high-resolution vertical portrait covers (`600x900`, `342x482`, `660x930`) and filters out joke/meme art (`humor=false`) and adult content (`nsfw=false`).
   - Fetched artwork is compressed, saved to `static/covers/`, and dynamically matched to your catalog.

2. **Interactive In-Card Cover Picker**:
   - For titles where you'd like to pick an alternate artwork style or region variant, click **Find cover** on the game card.
   - An interactive modal displays authentic portrait box art choices from SteamGridDB with live image previews, author credits, and resolution badges.
   - Type any custom keyword into the live search input, or click any box art thumbnail to apply it instantly with zero page reload.

3. **Manual Cover Art Overrides**:
   - Alternatively, drop any custom image directly into `static/covers/` using the naming formula:
     `static/covers/<system>_<rom_stem>.jpg`
     *(Spaces and punctuation in the ROM filename become underscores)*.
   - Click **Rescan** in Settings $\rightarrow$ UI tab to immediately recognize the new files.

---

## Repository File Tree

```text
Emulator-Web-Catelog/
├── README.md                # Full documentation, configuration guides, and theme options
├── install.sh               # Automated installer (systemd service, desktop launcher, CLI)
├── uninstall.sh             # Clean uninstaller with optional --purge support
├── romcat.sh                # Portable CLI and browser launcher script
├── config.example.yaml      # Clean configuration template (systems, paths, commands, SteamGridDB)
├── app.py                   # Flask server, library scanner, SteamGridDB client, and launcher
├── requirements.txt         # Python dependencies (flask, pyyaml, requests, pillow, ujson)
├── .gitignore               # Ignore cache, logs, virtual environments, covers, and local user data
├── screenshots/
│   ├── catalog.jpg          # Application dashboard screenshot (Default theme with glowing borders)
│   ├── statistics.png       # Play statistics and insights dashboard screenshot
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
    ├── index.html           # Main dashboard template with search, tabs, settings, and launching modal
    └── stats.html           # Play statistics and insights dashboard template
```

---

## License

This project is open-source software licensed under the [MIT License](LICENSE).

Created and maintained by [PlasmaDrifter](https://github.com/PlasmaDrifter).

---

## Community & Discussions

Got questions, setup ideas, or feedback?

* Join our subreddit at [**r/PlasmaDrifterProjects**](https://reddit.com/r/PlasmaDrifterProjects) to discuss updates, get support, and share configurations.
* Contact directly via email at [**plasmadrifter121@gmail.com**](mailto:plasmadrifter121@gmail.com).

