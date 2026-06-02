#!/usr/bin/env python3
"""
IT Support Toolkit v2.0 - Enterprise-Grade Windows Diagnostics Platform

A comprehensive IT administration and diagnostics tool featuring:
  - Dashboard with health monitoring
  - Hardware inventory (CPU, RAM, Storage, GPU, Motherboard)
  - Software inventory with search and export
  - Network diagnostics (ping, traceroute, DNS, port scan, network reset)
  - One-click repair tools (SFC, DISM, CHKDSK, cache cleanup)
  - System cleaner with space estimation
  - Security audit with scoring (AV, firewall, BitLocker, RDP, SMB)
  - Event log analyzer with categorization
  - Report generation (HTML, CSV, JSON)

Run:  python main.py
Build: pyinstaller build.spec --clean
"""

import os
import sys
import platform


def main():
    """Launch the IT Support Toolkit."""
    if platform.system() != "Windows":
        print("[ERROR] IT Support Toolkit requires Windows.")
        sys.exit(1)

    # Add project root to path
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    try:
        from ui.app import run_app
        run_app()
    except ImportError as e:
        print(f"[ERROR] Failed to import modules: {e}")
        print("\nInstall dependencies with:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
