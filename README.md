# pyAlienFX

A Python 3 application to control the AlienFX LED lighting on Alienware computers.

## Supported Computers

- Alienware M11x R1/R2/R3
- Alienware M14x R1
- Alienware M15x (Area51 and AllPowerful variants)
- Alienware M17x R3
- Alienware M18x R2

## Requirements

- Python 3.6+
- [PyUSB](https://github.com/pyusb/pyusb) (`pyusb >= 1.0.0`)
- [PyGObject](https://pygobject.readthedocs.io/) (`PyGObject >= 3.36.0`) with GTK 3
- [pycairo](https://pycairo.readthedocs.io/) (`pycairo >= 1.16.0`)
- libusb (system package: `libusb-1.0-0` on Debian/Ubuntu)
- AppIndicator3 (system package: `gir1.2-appindicator3-0.1` on Debian/Ubuntu)

### Install dependencies on Ubuntu/Debian

```bash
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
    gir1.2-appindicator3-0.1 libusb-1.0-0
pip3 install -r requirements.txt
```

## Installation

```bash
sudo python3 install.py
```

## Running

Launch the GUI directly (requires root for USB access):

```bash
sudo python3 pyAlienFX.py
```

Or start the background daemon and indicator:

```bash
sudo python3 pyAlienFX_daemon.py &
python3 pyAlienFX_Indicator.py &
```

## Architecture

- **`pyAlienFX.py`** — GTK 3 GUI configuration editor
- **`pyAlienFX_daemon.py`** — TCP daemon (port 25436) that holds the USB driver and accepts commands
- **`pyAlienFX_Indicator.py`** — System tray AppIndicator3 applet
- **`AlienFX/AlienFXEngine.py`** — USB driver and command builder
- **`AlienFX/AlienFXComputers.py`** — Per-model hardware definitions
- **`AlienFX/AlienFXConfiguration.py`** — Profile load/save

## License

GNU General Public License v3 — see [COPYING](COPYING) for details.