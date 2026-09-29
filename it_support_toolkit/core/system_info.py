"""System information retrieval - fast, resilient, no hanging."""
import os
import sys
import platform
import subprocess
import socket
from typing import Dict, Any
from datetime import datetime, timedelta


def _run_ps(script: str, timeout: int = 8) -> str:
    """Run PowerShell command with timeout."""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True, text=True, timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return result.stdout.strip()
    except Exception:
        return ""


class SystemInfo:
    """Fast and resilient Windows system information collector."""

    @staticmethod
    def get_computer_name() -> str:
        return platform.node()

    @staticmethod
    def get_current_user() -> str:
        return os.environ.get("USERNAME", "Unknown")

    @staticmethod
    def get_windows_edition() -> str:
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
            try:
                return winreg.QueryValueEx(key, "ProductName")[0]
            finally:
                winreg.CloseKey(key)
        except Exception:
            return platform.version()

    @staticmethod
    def get_windows_build() -> str:
        return platform.version()

    @staticmethod
    def get_system_uptime() -> str:
        try:
            import ctypes
            ticks = ctypes.windll.kernel32.GetTickCount64()
            td = timedelta(milliseconds=ticks)
            parts = []
            if td.days > 0:
                parts.append(f"{td.days}d")
            if td.seconds // 3600 > 0:
                parts.append(f"{td.seconds//3600}h")
            parts.append(f"{(td.seconds//60)%60}m")
            return " ".join(parts)
        except Exception:
            return "Unknown"

    @staticmethod
    def get_cpu_usage() -> float:
        try:
            import psutil
            return psutil.cpu_percent(interval=0.2)
        except Exception:
            return 0.0

    @staticmethod
    def get_ram_usage() -> Dict[str, Any]:
        try:
            import psutil
            mem = psutil.virtual_memory()
            return {
                "used_gb": round(mem.used / (1024**3), 2),
                "total_gb": round(mem.total / (1024**3), 2),
                "percent": mem.percent,
                "available_gb": round(mem.available / (1024**3), 2),
            }
        except Exception:
            return {"used_gb": 0, "total_gb": 0, "percent": 0, "available_gb": 0}

    @staticmethod
    def get_disk_usage() -> Dict[str, Any]:
        try:
            import psutil
            d = psutil.disk_usage("/")
            return {
                "used_gb": round(d.used / (1024**3), 2),
                "total_gb": round(d.total / (1024**3), 2),
                "percent": d.percent,
                "free_gb": round(d.free / (1024**3), 2),
            }
        except Exception:
            return {"used_gb": 0, "total_gb": 0, "percent": 0, "free_gb": 0}

    @staticmethod
    def get_local_ip() -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(2)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    @staticmethod
    def get_public_ip() -> str:
        out = _run_ps(
            "(Invoke-WebRequest -Uri 'https://api.ipify.org' -UseBasicParsing -TimeoutSec 5).Content",
            timeout=8
        )
        return out if out else "-"

    @staticmethod
    def get_antivirus() -> str:
        out = _run_ps("Get-MpComputerStatus | Select-Object -ExpandProperty AntivirusEnabled")
        return "Enabled" if "True" in out else ("Disabled" if "False" in out else "Unknown")

    @staticmethod
    def get_firewall() -> str:
        out = _run_ps("(Get-NetFirewallProfile -Name Domain).Enabled")
        return "Enabled" if "True" in out else ("Disabled" if "False" in out else "Unknown")

    @staticmethod
    def get_windows_update() -> str:
        out = _run_ps("(New-Object -ComObject Microsoft.Update.AutoUpdate).Settings.NotificationLevel")
        level_map = {"0": "Not Configured", "1": "Never Check", "2": "Notify Before Download",
                     "3": "Auto Download", "4": "Auto Install"}
        return level_map.get(out, "Auto") if out else "Unknown"

    @staticmethod
    def get_activation() -> str:
        out = _run_ps(
            "(Get-CimInstance -ClassName SoftwareLicensingProduct -Filter 'PartialProductKey is not null').LicenseStatus"
        )
        if "1" in out:
            return "Activated"
        elif "0" in out or "2" in out or "3" in out:
            return "Not Activated"
        return "Unknown"

    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """Get ALL system info safely. Each call is wrapped in try/except."""
        FUNCTIONS = [
            ("computer_name", cls.get_computer_name),
            ("current_user", cls.get_current_user),
            ("windows_edition", cls.get_windows_edition),
            ("windows_build", cls.get_windows_build),
            ("system_uptime", cls.get_system_uptime),
            ("cpu_usage", cls.get_cpu_usage),
            ("ram", cls.get_ram_usage),
            ("disk", cls.get_disk_usage),
            ("local_ip", cls.get_local_ip),
            ("public_ip", cls.get_public_ip),
            ("antivirus", cls.get_antivirus),
            ("firewall", cls.get_firewall),
            ("windows_update", cls.get_windows_update),
            ("activation", cls.get_activation),
        ]
        data = {}
        for key, func in FUNCTIONS:
            try:
                data[key] = func()
            except Exception:
                data[key] = "-"
        return data
