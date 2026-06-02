"""Enhanced system cleaner with space estimation, categories, and history."""

import os
import sys
import json
import subprocess
from typing import Dict, Any, List
from datetime import datetime


class SystemCleaner:
    """Enhanced system cleaner with safe and advanced modes."""

    def __init__(self):
        self.history_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config", "cleaner_history.json"
        )

    @staticmethod
    def get_categories() -> List[Dict[str, Any]]:
        """Get categorized cleanup targets with size estimation."""
        categories = [
            {
                "name": "Windows Temp",
                "path": r"C:\Windows\Temp",
                "safe": True,
                "items": [],
            },
            {
                "name": "User Temp",
                "path": os.environ.get("TEMP", ""),
                "safe": True,
                "items": [],
            },
            {
                "name": "Browser Cache",
                "paths": [
                    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "User Data", "Default", "Cache"),
                    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Edge", "User Data", "Default", "Cache"),
                ],
                "safe": True,
                "items": [],
            },
            {
                "name": "Prefetch",
                "path": r"C:\Windows\Prefetch",
                "safe": True,
                "items": [],
            },
            {
                "name": "Recycle Bin",
                "path": "recycle_bin",
                "safe": True,
                "items": [],
            },
            {
                "name": "DNS Cache",
                "path": "dns",
                "safe": True,
                "items": [],
            },
            {
                "name": "Windows Update Cache",
                "path": r"C:\Windows\SoftwareDistribution\Download",
                "safe": False,
                "items": [],
            },
            {
                "name": "Thumbnail Cache",
                "path": os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Explorer"),
                "safe": True,
                "items": [],
            },
        ]
        return categories

    @staticmethod
    def estimate_size(path: str) -> int:
        """Calculate directory size in bytes."""
        if not path or not os.path.exists(path):
            return 0
        total = 0
        try:
            for dirpath, _, filenames in os.walk(path):
                for f in filenames:
                    try:
                        fp = os.path.join(dirpath, f)
                        if os.path.isfile(fp):
                            total += os.path.getsize(fp)
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError):
            pass
        return total

    @staticmethod
    def format_size(size_bytes: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    @staticmethod
    def get_all_sizes() -> List[Dict[str, Any]]:
        """Get all cache categories with estimated sizes."""
        results = []
        for cat in SystemCleaner.get_categories():
            size = 0
            if "paths" in cat:
                for p in cat["paths"]:
                    size += SystemCleaner.estimate_size(p)
            elif "path" in cat and cat["path"] and cat["path"] not in ("recycle_bin", "dns"):
                size = SystemCleaner.estimate_size(cat["path"])

            results.append({
                "name": cat["name"],
                "size_bytes": size,
                "size_str": SystemCleaner.format_size(size) if size > 0 else "Unknown",
                "safe": cat.get("safe", True),
            })
        return results

    @staticmethod
    def clean_item(name: str, simulate: bool = True) -> Dict[str, Any]:
        """Clean a specific cache category."""
        if sys.platform != "win32":
            return {"success": False, "error": "Windows only"}

        if simulate:
            return {"success": True, "simulated": True, "message": f"[SIMULATION] Would clean {name}"}

        try:
            action_map = {
                "Windows Temp": lambda: SystemCleaner._clean_path(r"C:\Windows\Temp"),
                "User Temp": lambda: SystemCleaner._clean_path(os.environ.get("TEMP", "")),
                "Prefetch": lambda: SystemCleaner._clean_path(r"C:\Windows\Prefetch"),
                "Thumbnail Cache": lambda: SystemCleaner._clean_path(
                    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Explorer")
                ),
                "Windows Update Cache": lambda: SystemCleaner._clean_path(r"C:\Windows\SoftwareDistribution\Download"),
                "DNS Cache": lambda: SystemCleaner._flush_dns(),
                "Recycle Bin": lambda: SystemCleaner._empty_recycle_bin(),
                "Browser Cache": lambda: SystemCleaner._clean_browser_caches(),
            }

            action = action_map.get(name)
            if action:
                return action()
            return {"success": False, "error": f"Unknown category: {name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def _clean_path(path: str) -> Dict[str, Any]:
        import shutil
        if not os.path.exists(path):
            return {"success": True, "message": f"{path} does not exist, nothing to clean"}
        deleted = 0
        errors = 0
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    deleted += 1
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
                    deleted += 1
            except Exception:
                errors += 1
        return {"success": True, "message": f"Cleaned {deleted} items ({errors} errors)"}

    @staticmethod
    def _flush_dns() -> Dict[str, Any]:
        try:
            subprocess.run(["ipconfig", "/flushdns"], capture_output=True, timeout=15,
                           creationflags=subprocess.CREATE_NO_WINDOW)
            return {"success": True, "message": "DNS cache flushed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def _empty_recycle_bin() -> Dict[str, Any]:
        try:
            import ctypes
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0)
            return {"success": True, "message": "Recycle Bin emptied"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def _clean_browser_caches() -> Dict[str, Any]:
        results = []
        local_appdata = os.environ.get("LOCALAPPDATA", "")
        for path in [
            os.path.join(local_appdata, "Google", "Chrome", "User Data", "Default", "Cache"),
            os.path.join(local_appdata, "Microsoft", "Edge", "User Data", "Default", "Cache"),
        ]:
            if os.path.exists(path):
                r = SystemCleaner._clean_path(path)
                results.append(r)
        return {"success": True, "message": f"Browser caches cleaned ({len(results)} folders)"}

    def get_history(self) -> List[Dict[str, Any]]:
        """Get cleanup history."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def save_cleanup(self, results: List[Dict[str, Any]]):
        """Save cleanup to history."""
        history = self.get_history()
        entry = {
            "timestamp": datetime.now().isoformat(),
            "items_cleaned": [r for r in results if r.get("success")],
            "total_freed": sum(r.get("freed_bytes", 0) for r in results if r.get("success")),
        }
        history.append(entry)
        # Keep last 50 entries
        history = history[-50:]
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, "w") as f:
                json.dump(history, f, indent=2)
        except Exception:
            pass
