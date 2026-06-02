"""Permission checking and privilege management utilities."""

import sys
import ctypes
import os


def is_admin() -> bool:
    """Check if the current process has administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def require_admin(message: str = None) -> bool:
    """Check admin and warn if not running as admin."""
    if not is_admin():
        print(f"[WARNING] {message or 'This operation requires administrator privileges.'}")
        return False
    return True


def run_as_admin(script: str = None) -> bool:
    """Re-launch the current script with administrator privileges."""
    if is_admin():
        return True
    try:
        script = script or sys.argv[0]
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{script}"', None, 1
        )
        return True
    except Exception:
        return False


FEATURES_REQUIRING_ADMIN = [
    "Service management (start/stop/restart)",
    "Event log reading (Security log)",
    "DNS cache flush",
    "SFC / DISM scans",
    "Winsock / TCP/IP reset",
    "Windows Update cache cleanup",
    "System Temp (C:\\Windows\\Temp) cleanup",
    "Remote command execution",
]
