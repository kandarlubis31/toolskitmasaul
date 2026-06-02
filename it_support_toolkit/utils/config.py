import json
import os
import sys
from typing import Any, Dict, List, Optional

# In PyInstaller, use APPDATA for writable config; in dev, use local config dir
if getattr(sys, 'frozen', False):
    CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")),
                              "ITSupportToolkit", "config")
else:
    CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "config")
DEVICES_FILE = os.path.join(CONFIG_DIR, "devices.json")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "theme": "dark",
    "default_log_count": 50,
    "log_type": "System",
    "ping_timeout": 3000,
    "monitor_interval": 2,
    "clean_simulation": True,
}


def _ensure_config_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)


def _load_json(path: str, default: Any) -> Any:
    _ensure_config_dir()
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, PermissionError, OSError):
        return default


def _save_json(path: str, data: Any) -> bool:
    _ensure_config_dir()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except (PermissionError, OSError):
        return False


def get_devices() -> List[Dict[str, str]]:
    """Return list of devices: [{name, ip, os}...]"""
    return _load_json(DEVICES_FILE, [])


def save_devices(devices: List[Dict[str, str]]) -> bool:
    return _save_json(DEVICES_FILE, devices)


def add_device(name: str, ip: str, os_type: str = "Windows") -> bool:
    devices = get_devices()
    # Avoid duplicates by IP
    devices = [d for d in devices if d.get("ip") != ip]
    devices.append({"name": name, "ip": ip, "os": os_type})
    return save_devices(devices)


def remove_device(ip: str) -> bool:
    devices = get_devices()
    devices = [d for d in devices if d.get("ip") != ip]
    return save_devices(devices)


def get_settings() -> Dict[str, Any]:
    settings = _load_json(SETTINGS_FILE, {})
    merged = DEFAULT_SETTINGS.copy()
    merged.update(settings)
    return merged


def save_settings(settings: Dict[str, Any]) -> bool:
    return _save_json(SETTINGS_FILE, settings)


def update_setting(key: str, value: Any) -> bool:
    settings = get_settings()
    settings[key] = value
    return save_settings(settings)
