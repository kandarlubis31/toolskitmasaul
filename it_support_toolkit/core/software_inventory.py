"""Software inventory module - installed applications listing."""

import sys
import subprocess
from typing import Dict, Any, List


class SoftwareInventory:
    """Installed software inventory collector."""

    @staticmethod
    def get_installed_software() -> List[Dict[str, Any]]:
        """Get list of installed applications with name, version, publisher, install date."""
        apps = []

        # Method 1: Registry (HKLM Uninstall keys)
        try:
            import winreg

            def _from_key(key_path):
                results = []
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                    try:
                        i = 0
                        while True:
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                subkey = winreg.OpenKey(key, subkey_name)
                                try:
                                    try:
                                        name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                    except OSError:
                                        i += 1
                                        continue

                                    version = ""
                                    try:
                                        version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                                    except OSError:
                                        pass

                                    publisher = ""
                                    try:
                                        publisher = winreg.QueryValueEx(subkey, "Publisher")[0]
                                    except OSError:
                                        pass

                                    install_date = ""
                                    try:
                                        install_date = winreg.QueryValueEx(subkey, "InstallDate")[0]
                                        if install_date and len(install_date) == 8:
                                            install_date = f"{install_date[:4]}-{install_date[4:6]}-{install_date[6:]}"
                                    except OSError:
                                        pass

                                    results.append({
                                        "name": name,
                                        "version": version,
                                        "publisher": publisher,
                                        "install_date": install_date,
                                    })
                                finally:
                                    winreg.CloseKey(subkey)
                                i += 1
                            except OSError:
                                break
                    finally:
                        winreg.CloseKey(key)
                except Exception:
                    pass
                return results

            apps.extend(_from_key(r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"))
            apps.extend(_from_key(r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"))

        except ImportError:
            pass

        # Method 2: PowerShell fallback for more complete list
        if not apps:
            try:
                result = subprocess.run(
                    ["powershell", "-Command",
                     "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | "
                     "Where-Object { $_.DisplayName } | "
                     "Select-Object DisplayName, DisplayVersion, Publisher, InstallDate | ConvertTo-Json"],
                    capture_output=True, text=True, timeout=30,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if result.stdout.strip():
                    import json
                    data = json.loads(result.stdout)
                    if not isinstance(data, list):
                        data = [data]
                    for item in data:
                        apps.append({
                            "name": item.get("DisplayName", ""),
                            "version": item.get("DisplayVersion", ""),
                            "publisher": item.get("Publisher", ""),
                            "install_date": str(item.get("InstallDate", "")),
                        })
            except Exception:
                pass

        # Deduplicate by name
        seen = set()
        unique_apps = []
        for app in apps:
            name = app["name"]
            if name not in seen:
                seen.add(name)
                unique_apps.append(app)

        return sorted(unique_apps, key=lambda x: x["name"].lower())

    @staticmethod
    def search_software(query: str, apps: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search installed software by name."""
        if apps is None:
            apps = SoftwareInventory.get_installed_software()
        if not query:
            return apps
        q = query.lower()
        return [a for a in apps if q in a["name"].lower() or q in a.get("publisher", "").lower()]
