"""One-click system repair and maintenance tools."""

import os
import sys
import subprocess
from typing import Dict, Any, List, Callable


class RepairAction:
    """Represents a single repair action that can be executed."""
    def __init__(self, name: str, description: str, admin_required: bool = True):
        self.name = name
        self.description = description
        self.admin_required = admin_required


class RepairTools:
    """Collection of one-click system repair tools."""

    @staticmethod
    def get_actions() -> List[Dict[str, Any]]:
        """Return list of available repair actions."""
        return [
            {"id": "restart_explorer", "name": "Restart Explorer", "description": "Restart Windows Explorer shell", "admin": False},
            {"id": "clear_win_temp", "name": "Clear Windows Temp", "description": "Delete C:\\Windows\\Temp contents", "admin": True},
            {"id": "clear_user_temp", "name": "Clear User Temp", "description": "Delete %TEMP% contents", "admin": False},
            {"id": "clear_update_cache", "name": "Clear Windows Update Cache", "description": "Delete SoftwareDistribution folder", "admin": True},
            {"id": "rebuild_icon_cache", "name": "Rebuild Icon Cache", "description": "Delete and rebuild icon cache database", "admin": False},
            {"id": "rebuild_thumb_cache", "name": "Rebuild Thumbnail Cache", "description": "Clear thumbnail cache", "admin": False},
            {"id": "reset_network", "name": "Reset Network Stack", "description": "Reset Winsock and TCP/IP stack", "admin": True},
            {"id": "sfc_scan", "name": "SFC Scan", "description": "Run System File Checker (SFC /scannow)", "admin": True},
            {"id": "dism_scan", "name": "DISM Scan Health", "description": "Check Windows image health (DISM)", "admin": True},
            {"id": "dism_restore", "name": "DISM Restore Health", "description": "Restore Windows image health", "admin": True},
            {"id": "chkdsk", "name": "Schedule CHKDSK", "description": "Schedule disk check on next reboot", "admin": True},
            {"id": "cleanmgr", "name": "Disk Cleanup", "description": "Launch Disk Cleanup utility", "admin": False},
        ]

    @staticmethod
    def execute(action_id: str, progress_callback: Callable = None) -> Dict[str, Any]:
        """Execute a repair action by ID."""
        if progress_callback:
            progress_callback("Starting...")

        actions = {
            "restart_explorer": RepairTools._restart_explorer,
            "clear_win_temp": RepairTools._clear_win_temp,
            "clear_user_temp": RepairTools._clear_user_temp,
            "clear_update_cache": RepairTools._clear_update_cache,
            "rebuild_icon_cache": RepairTools._rebuild_icon_cache,
            "rebuild_thumb_cache": RepairTools._rebuild_thumb_cache,
            "reset_network": RepairTools._reset_network,
            "sfc_scan": RepairTools._sfc_scan,
            "dism_scan": RepairTools._dism_scan,
            "dism_restore": RepairTools._dism_restore,
            "chkdsk": RepairTools._chkdsk,
            "cleanmgr": RepairTools._cleanmgr,
        }

        func = actions.get(action_id)
        if func is None:
            return {"success": False, "error": f"Unknown action: {action_id}"}

        try:
            return func(progress_callback)
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def _run_cmd(cmd: list, timeout: int = 120) -> Dict[str, Any]:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    timeout=timeout, creationflags=subprocess.CREATE_NO_WINDOW)
            return {"success": result.returncode == 0, "output": result.stdout + result.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def _restart_explorer(pb=None) -> Dict[str, Any]:
        if pb: pb("Restarting Windows Explorer...")
        subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], capture_output=True,
                       creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.Popen(["explorer.exe"], creationflags=subprocess.CREATE_NO_WINDOW)
        return {"success": True, "message": "Explorer restarted"}

    @staticmethod
    def _clear_win_temp(pb=None) -> Dict[str, Any]:
        if pb: pb("Clearing Windows Temp...")
        temp = r"C:\Windows\Temp"
        return RepairTools._clear_folder(temp, pb)

    @staticmethod
    def _clear_user_temp(pb=None) -> Dict[str, Any]:
        if pb: pb("Clearing User Temp...")
        temp = os.environ.get("TEMP", "")
        return RepairTools._clear_folder(temp, pb) if temp else {"success": False, "error": "No TEMP path"}

    @staticmethod
    def _clear_folder(folder: str, pb=None) -> Dict[str, Any]:
        import shutil
        deleted = 0
        errors = 0
        for root, dirs, files in os.walk(folder):
            for f in files:
                try:
                    fp = os.path.join(root, f)
                    os.remove(fp)
                    deleted += 1
                except Exception:
                    errors += 1
            for d in dirs:
                try:
                    dp = os.path.join(root, d)
                    shutil.rmtree(dp, ignore_errors=True)
                except Exception:
                    pass
        return {"success": deleted > 0 or errors == 0, "message": f"Cleaned {deleted} files ({errors} errors)"}

    @staticmethod
    def _clear_update_cache(pb=None) -> Dict[str, Any]:
        if pb: pb("Stopping Windows Update service...")
        subprocess.run(["net", "stop", "wuauserv"], capture_output=True, timeout=30,
                       creationflags=subprocess.CREATE_NO_WINDOW)
        cache_path = r"C:\Windows\SoftwareDistribution"
        if pb: pb("Deleting update cache...")
        import shutil
        if os.path.exists(cache_path):
            try:
                shutil.rmtree(cache_path, ignore_errors=True)
            except Exception:
                pass
            # Recreate folder
            os.makedirs(cache_path, exist_ok=True)
        if pb: pb("Restarting Windows Update service...")
        subprocess.run(["net", "start", "wuauserv"], capture_output=True, timeout=30,
                       creationflags=subprocess.CREATE_NO_WINDOW)
        return {"success": True, "message": "Update cache cleared"}

    @staticmethod
    def _rebuild_icon_cache(pb=None) -> Dict[str, Any]:
        if pb: pb("Rebuilding icon cache...")
        icon_cache = os.path.join(os.environ.get("LOCALAPPDATA", ""), "IconCache.db")
        if os.path.exists(icon_cache):
            try:
                os.remove(icon_cache)
            except Exception as e:
                return {"success": False, "error": str(e)}
        subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], capture_output=True,
                       creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.Popen(["explorer.exe"], creationflags=subprocess.CREATE_NO_WINDOW)
        return {"success": True, "message": "Icon cache rebuilt"}

    @staticmethod
    def _rebuild_thumb_cache(pb=None) -> Dict[str, Any]:
        if pb: pb("Clearing thumbnail cache...")
        thumb_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Explorer")
        if os.path.exists(thumb_path):
            import shutil
            try:
                shutil.rmtree(thumb_path, ignore_errors=True)
            except Exception:
                pass
        subprocess.run(["cmd", "/c", "del /f /s /q /a %USERPROFILE%\\AppData\\Local\\Microsoft\\Windows\\Explorer\\thumbcache_*.db"],
                       capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return {"success": True, "message": "Thumbnail cache rebuilt"}

    @staticmethod
    def _reset_network(pb=None) -> Dict[str, Any]:
        if pb: pb("Resetting Winsock...")
        RepairTools._run_cmd(["netsh", "winsock", "reset"])
        if pb: pb("Resetting TCP/IP...")
        RepairTools._run_cmd(["netsh", "int", "ip", "reset"])
        if pb: pb("Flushing DNS...")
        RepairTools._run_cmd(["ipconfig", "/flushdns"])
        return {"success": True, "message": "Network stack reset (reboot recommended)"}

    @staticmethod
    def _sfc_scan(pb=None) -> Dict[str, Any]:
        if pb: pb("Running SFC Scan (this may take a while)...")
        return RepairTools._run_cmd(["sfc", "/scannow"], timeout=600)

    @staticmethod
    def _dism_scan(pb=None) -> Dict[str, Any]:
        if pb: pb("Running DISM CheckHealth...")
        return RepairTools._run_cmd(["dism", "/online", "/cleanup-image", "/checkhealth"], timeout=120)

    @staticmethod
    def _dism_restore(pb=None) -> Dict[str, Any]:
        if pb: pb("Running DISM RestoreHealth (this may take a while)...")
        return RepairTools._run_cmd(["dism", "/online", "/cleanup-image", "/restorehealth"], timeout=600)

    @staticmethod
    def _chkdsk(pb=None) -> Dict[str, Any]:
        if pb: pb("Scheduling CHKDSK on next reboot...")
        return RepairTools._run_cmd(["chkdsk", "C:", "/f", "/r"], timeout=30)

    @staticmethod
    def _cleanmgr(pb=None) -> Dict[str, Any]:
        if pb: pb("Launching Disk Cleanup...")
        subprocess.Popen(["cleanmgr"], creationflags=subprocess.CREATE_NO_WINDOW)
        return {"success": True, "message": "Disk Cleanup launched"}
