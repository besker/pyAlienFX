# pyAlienFX

> Control the AlienFX LED lighting on your Alienware laptop from Linux — fully open source, Python 3.

---

## Table of Contents

- [Supported Hardware](#supported-hardware)
- [Requirements](#requirements)
- [Installation](#installation)
  - [1. System packages](#1-system-packages)
  - [2. Python dependencies](#2-python-dependencies)
  - [3. USB permissions](#3-usb-permissions)
  - [4. Install pyAlienFX](#4-install-pyalienfx)
- [Running pyAlienFX](#running-pyalienfx)
  - [Option A — GUI only (simplest)](#option-a--gui-only-simplest)
  - [Option B — Daemon + System-tray indicator](#option-b--daemon--system-tray-indicator)
  - [Option C — Auto-start at login](#option-c--auto-start-at-login)
- [Using the GUI](#using-the-gui)
  - [Profiles](#profiles)
  - [Lighting zones](#lighting-zones)
  - [Lighting modes](#lighting-modes)
  - [Colour selection](#colour-selection)
  - [Speed control](#speed-control)
  - [Preview vs Save](#preview-vs-save)
  - [Advanced mode](#advanced-mode)
- [Using the System-tray Indicator](#using-the-system-tray-indicator)
- [Configuration files](#configuration-files)
- [Project structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Supported Hardware

| Model | USB Product ID |
|---|---|
| Alienware M11x R1 | `0x187c:0x0514` |
| Alienware M11x R2 | `0x187c:0x0515` |
| Alienware M11x R2.5 | `0x187c:0x0516` |
| Alienware M11x R3 | `0x187c:0x0522` |
| Alienware M14x R1 | `0x187c:0x0521` |
| Alienware M15x Area51 | `0x187c:0x0511` |
| Alienware M15x AllPowerful | `0x187c:0x0512` |
| Alienware M17x R3 | `0x187c:0x0520` |
| Alienware M18x R2 | `0x187c:0x0518` |

> **Don't see your model?** Check the USB vendor/product IDs with `lsusb | grep 187c` and open an issue — adding support is straightforward.

---

## Requirements

### Operating system

- Linux (tested on Ubuntu 20.04+, Debian 11+)
- Python **3.6** or newer

### System libraries

| Package | Purpose |
|---|---|
| `libusb-1.0-0` | Low-level USB access |
| `python3-gi` | Python GTK3 / GObject bindings |
| `python3-gi-cairo` | Cairo rendering via GObject |
| `gir1.2-gtk-3.0` | GTK 3 typelib |
| `gir1.2-appindicator3-0.1` | System-tray indicator support |

### Python packages (via pip)

| Package | Version | Purpose |
|---|---|---|
| `pyusb` | ≥ 1.0.0 | USB communication |
| `PyGObject` | ≥ 3.36.0 | GTK3 Python bindings |
| `pycairo` | ≥ 1.16.0 | Cairo drawing |

---

## Installation

### 1. System packages

On **Ubuntu / Debian**:

```bash
sudo apt-get update
sudo apt-get install \
    python3 python3-pip \
    libusb-1.0-0 \
    python3-gi python3-gi-cairo \
    gir1.2-gtk-3.0 \
    gir1.2-appindicator3-0.1
```

On **Fedora / RHEL**:

```bash
sudo dnf install \
    python3 python3-pip \
    libusb \
    python3-gobject \
    gtk3 \
    libappindicator-gtk3
```

### 2. Python dependencies

From the project directory:

```bash
pip3 install -r requirements.txt
```

Or install packages individually:

```bash
pip3 install "pyusb>=1.0.0" "PyGObject>=3.36.0" "pycairo>=1.16.0"
```

### 3. USB permissions

The AlienFX controller is a USB HID device. By default, direct USB access requires root. You can either:

**Option A — run with sudo** (quick, no extra setup):

```bash
sudo python3 pyAlienFX.py
```

**Option B — add a udev rule** (recommended, no sudo needed after setup):

Create the file `/etc/udev/rules.d/60-alienfx.rules`:

```bash
sudo tee /etc/udev/rules.d/60-alienfx.rules > /dev/null << 'EOF'
# Alienware AlienFX lighting controller
SUBSYSTEM=="usb", ATTRS{idVendor}=="187c", MODE="0664", GROUP="plugdev"
EOF
```

Then reload udev and re-plug the device (or reboot):

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Add your user to the `plugdev` group if not already a member:

```bash
sudo usermod -aG plugdev $USER
# log out and back in for the group change to take effect
```

### 4. Install pyAlienFX

The installer sets up launcher scripts, a `.desktop` entry, and (optionally) configures the daemon to start at login:

```bash
sudo python3 install.py
```

You will be asked two questions:

1. **Continue with installation?** — press `Y`.
2. **Launch the daemon at startup?** — press `Y` to have the lighting daemon start automatically at login, or `N` to start it manually when needed.

> The installer writes files to `/usr/share/pyAlienFX/`, creates `/usr/bin/pyAlienFX`, and registers a `.desktop` entry so the app appears in your application launcher.

---

## Running pyAlienFX

There are three ways to run the application, depending on how much you want running in the background.

### Option A — GUI only (simplest)

Launches the configuration editor directly. The USB driver is loaded in-process.

```bash
sudo python3 pyAlienFX.py
```

> Requires root (or the udev rule from step 3) because the app talks directly to the USB device.

This is the best option for occasional use or first-time setup.

---

### Option B — Daemon + System-tray indicator

The daemon holds the USB driver and listens on a local TCP socket (`localhost:25436`). The GUI and indicator connect to it instead of accessing USB directly.

**Step 1 — start the daemon** (requires root for USB access):

```bash
sudo python3 pyAlienFX_daemon.py &
```

You should see:

```
Initializing Driver  ...
Computer M11XR3 found ! Loading the parameters ...
Initializing Controller ...
...listening
```

**Step 2 — start the system-tray indicator** (does *not* need root):

```bash
python3 pyAlienFX_Indicator.py &
```

A small icon appears in your system tray. Right-click it for quick controls.

**Step 3 — optionally open the full GUI** from the tray menu → *Configuration Editor*, or directly:

```bash
python3 pyAlienFX.py
```

When a daemon is running, the GUI connects to it automatically — no extra flags needed.

---

### Option C — Auto-start at login

If you answered **Y** to the daemon question during installation, the launcher script (`pyAlienFX_Launcher.sh`) is already registered for auto-start.

To add it manually to your session, open your desktop environment's **Startup Applications** manager and add:

```
/usr/share/pyAlienFX/pyAlienFX_Launcher.sh
```

Or run the launcher script directly at any time:

```bash
/usr/share/pyAlienFX/pyAlienFX_Launcher.sh
```

This starts the daemon (as root via `gksudo`) and the indicator in one step.

---

## Using the GUI

When the GUI window opens you will see three main panels:

```
┌─────────────────────────────────────────────────────────┐
│  Menu bar  (File / Edit / Help)                          │
├──────────────┬──────────────────────────┬───────────────┤
│              │                          │               │
│  Colour      │   Zone configurator      │  Tempo        │
│  palette     │   (scrollable)           │  (speed)      │
│              │                          │               │
├──────────────┴──────────────────────────┴───────────────┤
│  Profile selector    [Preview]  [Save]  [Show Advanced] │
└─────────────────────────────────────────────────────────┘
```

### Profiles

A **profile** is a named set of lighting settings saved to a `.cfg` file inside the `Profiles/` directory.

| Action | How |
|---|---|
| Create a new profile | **File → New** — enter a name in the dialog |
| Open an existing profile | **File → Open** — browse to any `.cfg` file |
| Switch between profiles | Use the drop-down at the bottom of the window |
| Save current profile | Click **Save** or **File → Save** |
| Save to a new file | **File → Save As** |

The last-used profile is remembered across sessions and loaded automatically on startup.

---

### Lighting zones

Each Alienware model exposes a different set of independently controllable zones. Common zones include:

- **Keyboard** (or Left / Right / Center sections on larger models)
- **Alienware Logo**
- **Alienware Head**
- **Speaker grilles** (Left / Right)
- **Touchpad**
- **Media bar**
- **Power button** *(special — controls sleep/charge colours)*

Each zone is shown as a coloured block in the configurator. Click a block to select that zone and start editing it.

---

### Lighting modes

Every zone (except the power button) supports three modes:

| Mode | Icon | Description |
|---|---|---|
| **Fixed** | Solid dot | Zone glows a single static colour |
| **Blink** | Pulsing dot | Zone pulses on/off at the current speed |
| **Morph** | Two-tone dot | Zone smoothly transitions between two colours |

Click the small mode icon next to a zone block to switch modes. The icon row shows which modes the zone supports (greyed icons mean unsupported).

---

### Colour selection

1. **Click a zone block** to select it. Left-half = colour 1 (start), right-half = colour 2 (end, used for Morph).
2. **Click a colour** in the palette on the left to apply it to the selected slot.
3. For a custom colour, click the **Color Selector** button at the bottom of the palette to open a full colour picker dialog.

> **Tip:** Right-clicking a zone block also selects its current colour into the active slot, making it easy to copy a colour from one zone to another.

---

### Speed control

The **Tempo** slider on the right side controls the animation speed for Blink and Morph effects.

- Drag **up** → slower
- Drag **down** → faster

The speed applies globally to all zones in the current profile.

---

### Preview vs Save

| Button | What it does |
|---|---|
| **Preview** | Sends the current configuration to the LEDs immediately, *without* writing to the device's non-volatile memory. Lights revert on reboot. |
| **Save** | Writes the configuration to the device's flash memory across all power blocks (AC power, battery, charging, sleep, critical battery). Lighting persists after reboot. |

Always **Preview** first to verify the look, then **Save** when you're happy.

---

### Advanced mode

Click **Show Advanced** to reveal the full multi-step configurator table.

In advanced mode each zone can have **multiple animation steps** (a loop). For example, a keyboard zone could morph red→blue, then blue→green, then green→red in sequence.

- **Add** — appends a new step to the zone's animation loop
- **✕ (remove button)** — deletes that step from the loop
- Steps play back in order, then repeat

Click **Hide Advanced** to return to the simplified single-step view.

---

## Using the System-tray Indicator

Right-click the tray icon for the quick-action menu:

| Menu item | Action |
|---|---|
| **Configuration Editor** | Opens the full GUI window |
| **Lights On** | Restores the last saved profile if lights were turned off |
| **Lights Off** | Turns all LEDs off immediately |
| **Change All Lights** | Sub-menu with preset colours — applies that colour to every zone at once |
| **Quit** | Stops the indicator (daemon keeps running) |

The icon changes appearance when the daemon is connected (attention state) vs. when it is operating normally (active state).

---

## Configuration files

Profiles are plain text files with a `.cfg` extension stored in the `Profiles/` subdirectory next to `pyAlienFX.py`.

Example file (`Profiles/Blue.cfg`):

```
name=Blue
computer=M11XR3
speed=65280
area=RK
type=fixed
color=0000FF
color2=0000FF
area=LS
type=fixed
color=0000FF
color2=0000FF
...
```

| Field | Description |
|---|---|
| `name` | Human-readable profile name shown in the drop-down |
| `computer` | Model key (must match an entry in `AlienFXComputers.py`) |
| `speed` | Animation speed as a 16-bit integer (e.g. `65280` = `0xFF00`) |
| `area` | Zone ID (e.g. `RK` = Right Keyboard, `AL` = Alienware Logo) |
| `type` | Lighting mode: `fixed`, `blink`, or `morph` |
| `color` | Primary colour as 6-digit hex RGB (e.g. `FF0000` = red) |
| `color2` | Secondary colour for `morph` mode; same as `color` otherwise |

You can edit `.cfg` files by hand — just restart the GUI or switch away and back to reload.

The special file `Profiles/last` contains only the filename of the most recently used profile and is written automatically.

---

## Project structure

```
pyAlienFX/
│
├── pyAlienFX.py              # GTK 3 GUI — main entry point
├── pyAlienFX_daemon.py       # Background TCP daemon (port 25436)
├── pyAlienFX_Indicator.py    # AppIndicator3 system-tray applet
├── install.py                # Installer script (run as root)
├── usbmonparser.py           # Developer utility: parse usbmon logs
├── requirements.txt          # pip dependencies
│
├── AlienFX/
│   ├── AlienFXEngine.py      # USB driver + packet builder
│   ├── AlienFXComputers.py   # Per-model hardware definitions
│   ├── AlienFXConfiguration.py  # Profile load / save / check
│   ├── AlienFXProperties.py  # Application-wide constants
│   └── AlienFXTexts.py       # UI string constants
│
├── glade/
│   └── AlienFXMain.glade     # GTK Builder UI layout
│
├── images/                   # UI artwork and icons
│   └── *.png / *.jpg
│
└── Profiles/                 # Created at runtime — your .cfg files live here
    └── last                  # Tracks the most recently used profile
```

---

## Troubleshooting

### "No AlienFX USB controller found"

1. Confirm your device is listed: `lsusb | grep 187c`
   - If nothing appears, your kernel may not expose the device — try rebooting.
2. Check you are running with sufficient permissions (root or the udev rule).
3. Verify your model is in the [Supported Hardware](#supported-hardware) table.

---

### "Can't set the configuration" / USB errors

The kernel's HID driver holds the device. pyAlienFX attempts to detach it automatically. If it fails:

```bash
# Find the bus and device numbers
lsusb | grep 187c
# e.g. "Bus 003 Device 004: ID 187c:0522"

# Manually unbind the kernel driver
sudo sh -c 'echo -n "3-1" > /sys/bus/usb/drivers/usbhid/unbind'
```

Replace `3-1` with the correct bus-port path shown by `udevadm info`.

---

### "Connection refused" when starting the GUI

The GUI tried to connect to the daemon but nothing is listening on port 25436. Either:

- Start the daemon first: `sudo python3 pyAlienFX_daemon.py &`
- Or run the GUI standalone (it will use the USB driver directly): `sudo python3 pyAlienFX.py`

---

### Lights revert to default after reboot

You used **Preview** instead of **Save**. Open the GUI, verify your profile looks correct, and click **Save** to write to the device's flash memory.

---

### AppIndicator3 / tray icon not showing

On modern GNOME you need an extension to display AppIndicator tray icons:

```bash
# Ubuntu 22.04+
sudo apt-get install gnome-shell-extension-appindicator
# Then enable it:
gnome-extensions enable ubuntu-appindicators@ubuntu.com
# Log out and back in
```

---

### `ModuleNotFoundError: No module named 'gi'`

PyGObject is not installed, or is installed system-wide but your pip environment can't see it.

```bash
# Ubuntu/Debian — install the system package
sudo apt-get install python3-gi python3-gi-cairo

# Do NOT install PyGObject via pip into a venv on most distros;
# it requires system-compiled C extensions.
```

---

### `ModuleNotFoundError: No module named 'usb'`

PyUSB is not installed:

```bash
pip3 install pyusb
```

---

## License

pyAlienFX is free software released under the **GNU General Public License v3**.
See [COPYING](COPYING) for the full text.