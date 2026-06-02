# IT Support Toolkit v2.0

Enterprise-grade Windows diagnostics, monitoring, and repair platform.

## Features

| Page | Description |
|------|-------------|
| 🏠 **Dashboard** | System overview with health cards, resource usage, and key metrics |
| 🖥 **Hardware** | CPU, RAM, Storage, GPU, Motherboard inventory |
| 📦 **Software** | Installed apps with search, filter, and CSV/HTML export |
| 🌐 **Network** | Ping, traceroute, DNS lookup, port scanner, network reset |
| 🔧 **Repair Tools** | One-click SFC scan, DISM, CHKDSK, cache cleanup, and more |
| 🧹 **Cleaner** | Safe/advanced cleanup with space estimation and history |
| 🛡 **Security Audit** | Score-based security analysis (0-100) with recommendations |
| 📋 **Event Logs** | Event viewer with categorization and time filters |
| ⚙ **Settings** | Theme, preferences, and admin status |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run from source
python main.py

# Build EXE
pyinstaller build.spec --clean
```

## Architecture

```
it_support_toolkit/
├── main.py                 # Entry point
├── core/                   # Data & logic layer
│   ├── system_info.py      # Windows edition, build, uptime, IPs, AV
│   ├── hardware_info.py    # CPU, RAM, Storage, GPU, Motherboard
│   ├── software_inventory.py
│   ├── network_tools.py    # Ping, traceroute, DNS, port scan
│   ├── eventlog.py         # Event log analyzer
│   ├── repair_tools.py     # SFC, DISM, CHKDSK, cleanup
│   ├── cleaner.py          # Space estimation, safe/advanced modes
│   ├── security_audit.py   # Score-based security analysis
│   └── reporting.py        # HTML/CSV/JSON report generation
├── ui/
│   ├── app.py              # Main window with sidebar navigation
│   ├── styles.qss          # Enterprise dark theme
│   └── pages/              # One file per page
│       ├── dashboard.py
│       ├── hardware_page.py
│       ├── software_page.py
│       ├── network_page.py
│       ├── repair_page.py
│       ├── cleaner_page.py
│       ├── security_page.py
│       ├── logs_page.py
│       └── settings_page.py
├── utils/
│   ├── config.py           # JSON-based settings
│   ├── logger.py           # Internal logging
│   ├── permissions.py      # Admin check utilities
│   └── background_tasks.py # QThread worker pool
├── assets/
│   └── icon.ico            # Application icon
└── build.spec              # PyInstaller configuration
```

## Requirements

- **OS:** Windows 10 / Windows 11 / Windows Server 2016+
- **Python:** 3.8+
- **Admin rights:** Recommended for full functionality

## Build Output

`dist/ITSupportToolkit.exe` (~40 MB standalone executable)
