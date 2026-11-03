# IT Support Toolkit

A Windows-only desktop application for day-to-day IT support work: system
diagnostics, hardware and software inventory, network troubleshooting, one-click
repairs, security auditing, and report export. Built with PyQt6 and packaged as a
single executable with PyInstaller.

This repository contains one project, in [`it_support_toolkit/`](it_support_toolkit/).

## Features

- **Dashboard** — health monitoring at a glance
- **Hardware inventory** — CPU, RAM, storage, GPU, motherboard
- **Software inventory** — searchable list with export
- **Network diagnostics** — ping, traceroute, DNS lookup, port scan, network reset
- **Repair tools** — SFC, DISM, CHKDSK, cache cleanup
- **System cleaner** — scans and estimates reclaimable space before deleting
- **Security audit** — scored checks for antivirus, firewall, BitLocker, RDP, SMB
- **Event log analyser** — categorised Windows event logs
- **Reporting** — HTML, CSV, and JSON output

## Requirements

- Windows 10 or 11
- Python 3.9+
- Administrator rights for the repair, cleaner, and audit features

```bash
cd it_support_toolkit
pip install -r requirements.txt
```

Dependencies: `pyqt6`, `psutil`, `pywin32`, and `pyinstaller` for packaging.

## Run

```bash
cd it_support_toolkit
python main.py
```

The entry point refuses to start on non-Windows platforms.

## Build a standalone executable

```bash
cd it_support_toolkit
build.bat
```

Or call PyInstaller directly with the shipped spec:

```bash
pyinstaller build.spec --clean
```

`build_manifest.xml` holds the UAC manifest, and `embed_manifest.bat` embeds it
into the produced binary so the app can request elevation when needed.

## Layout

```
it_support_toolkit/
  main.py               entry point, platform guard
  ui/                   PyQt6 windows, pages, and two QSS themes
  core/                 diagnostics modules:
                          system_info, hardware_info, software_inventory,
                          network_tools, remote_tools, repair_tools,
                          cleaner, security_audit, eventlog, reporting
  utils/                shared helpers
  config/               application configuration
  assets/               icons
  build.spec            PyInstaller spec
  build.bat             build wrapper
  CHANGELOG.md          version history
  CONTRIBUTING.md       how to contribute
  CODE_OF_CONDUCT.md
```

## Status

Version 2.0.0. See [CHANGELOG.md](it_support_toolkit/CHANGELOG.md) for what changed
since 1.x.

## License

MIT — see [LICENSE](it_support_toolkit/LICENSE).
