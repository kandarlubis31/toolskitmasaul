"""Hardware inventory module - CPU, RAM, Storage, GPU, Motherboard."""

import sys
import subprocess
from typing import Dict, Any, List


class HardwareInfo:
    """Comprehensive hardware information collector."""

    @staticmethod
    def get_cpu_info() -> Dict[str, Any]:
        info = {"name": "Unknown", "cores": 0, "threads": 0, "usage": 0}
        try:
            import psutil
            info["usage"] = psutil.cpu_percent(interval=0.3)
            info["cores"] = psutil.cpu_count(logical=False)
            info["threads"] = psutil.cpu_count(logical=True)
        except ImportError:
            pass

        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            try:
                info["name"] = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
            finally:
                winreg.CloseKey(key)
        except Exception:
            pass

        return info

    @staticmethod
    def get_ram_info() -> Dict[str, Any]:
        info = {"total_gb": 0, "used_gb": 0, "available_gb": 0, "percent": 0, "speed_mhz": 0, "slots_used": 0, "form_factor": ""}
        try:
            import psutil
            mem = psutil.virtual_memory()
            info["total_gb"] = round(mem.total / (1024**3), 2)
            info["used_gb"] = round(mem.used / (1024**3), 2)
            info["available_gb"] = round(mem.available / (1024**3), 2)
            info["percent"] = mem.percent
        except ImportError:
            pass

        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-CimInstance Win32_PhysicalMemory | "
                 "Measure-Object -Property Speed -Average | Select-Object -ExpandProperty Average"],
                capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.stdout.strip():
                info["speed_mhz"] = int(float(result.stdout.strip()))

            result2 = subprocess.run(
                ["powershell", "-Command",
                 "(Get-CimInstance Win32_PhysicalMemory).Count"],
                capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result2.stdout.strip():
                info["slots_used"] = int(result2.stdout.strip())
        except Exception:
            pass

        return info

    @staticmethod
    def get_storage_info() -> List[Dict[str, Any]]:
        disks = []
        try:
            import psutil
            for part in psutil.disk_partitions():
                if part.fstype and part.fstype != "FAT":
                    try:
                        usage = psutil.disk_usage(part.mountpoint)
                        disks.append({
                            "drive": part.device,
                            "mount": part.mountpoint,
                            "fstype": part.fstype,
                            "total_gb": round(usage.total / (1024**3), 2),
                            "used_gb": round(usage.used / (1024**3), 2),
                            "free_gb": round(usage.free / (1024**3), 2),
                            "percent": usage.percent,
                        })
                    except (PermissionError, OSError):
                        continue
        except ImportError:
            pass

        # Get physical disk info (SSD/HDD) via PowerShell
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-PhysicalDisk | Select-Object FriendlyName, MediaType, Size, @{N='SizeGB';E={[math]::Round($_.Size/1GB,2)}} | ConvertTo-Json"],
                capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.stdout.strip():
                import json
                phys_disks = json.loads(result.stdout)
                if not isinstance(phys_disks, list):
                    phys_disks = [phys_disks]
                for i, d in enumerate(phys_disks):
                    if i < len(disks):
                        disks[i]["model"] = d.get("FriendlyName", "Unknown")
                        disks[i]["media_type"] = d.get("MediaType", "HDD")
        except Exception:
            for d in disks:
                d.setdefault("model", "Unknown")
                d.setdefault("media_type", "HDD")

        return disks

    @staticmethod
    def get_gpu_info() -> List[Dict[str, Any]]:
        gpus = []
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-CimInstance Win32_VideoController | "
                 "Select-Object Name, @{N='VRAM_GB';E={[math]::Round($_.AdapterRAM/1GB,2)}} | ConvertTo-Json"],
                capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.stdout.strip():
                import json
                data = json.loads(result.stdout)
                if not isinstance(data, list):
                    data = [data]
                gpus = data
        except Exception:
            pass
        return gpus

    @staticmethod
    def get_motherboard_info() -> Dict[str, str]:
        info = {"manufacturer": "Unknown", "model": "Unknown"}
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-CimInstance Win32_BaseBoard | Select-Object Manufacturer, Product | ConvertTo-Json"],
                capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.stdout.strip():
                import json
                data = json.loads(result.stdout)
                if data:
                    info["manufacturer"] = data.get("Manufacturer", "Unknown")
                    info["model"] = data.get("Product", "Unknown")
        except Exception:
            pass
        return info

    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        return {
            "cpu": cls.get_cpu_info(),
            "ram": cls.get_ram_info(),
            "storage": cls.get_storage_info(),
            "gpu": cls.get_gpu_info(),
            "motherboard": cls.get_motherboard_info(),
        }
