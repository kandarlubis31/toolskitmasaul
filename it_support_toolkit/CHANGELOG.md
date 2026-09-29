# Changelog

All notable changes to IT Support Toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [2.0.0] - 2024

### Added
- Collapsible sidebar with smooth animation
- System tray minimize-to-tray support
- Professional splash screen with progress bar
- Light theme (`Catppuccin Latte`) alongside dark theme
- Real-time dashboard with live CPU/RAM/Disk monitoring
- Hardware inventory: CPU, RAM, Storage (SSD/HDD), GPU, Motherboard
- Software inventory with search, filter, and CSV/HTML export
- Network tools: ping, traceroute, DNS lookup, port scanner
- Network reset utilities: flush DNS, reset Winsock, reset TCP/IP
- One-click repair tools: SFC, DISM, CHKDSK, cache cleanup, and more
- System cleaner with space estimation, safe/advanced modes, and history
- Security audit with 0-100 scoring, grade, and recommendations
- Event Log analyzer with categorization and time filters
- Remote machine management (RDP, restart, shutdown, lock, remote commands)
- Report generation (HTML, CSV, JSON)
- Background task worker (threading-based, no QThread segfaults)
- pywin32 integration for deep Windows diagnostics

### Changed
- Migrated from QThread to Python threading for stability in admin mode
- Redesigned UI with Catppuccin Mocha dark theme
- Improved error resilience — all core methods wrapped in try/except
- Responsive layout with scroll areas on all pages

### Fixed
- Administrator mode crash caused by QThread C++ segfaults
- Event log datetime parsing for multiple Windows locale formats

## [1.0.0] - 2023

### Added
- Initial release with basic system info, network ping, and cleaner
- PyQt6 GUI with dark theme
- Basic PyInstaller build support
