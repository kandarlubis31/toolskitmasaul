"""Remote desktop and administration tools."""

import os
import sys
import subprocess
from typing import Dict, Any


class RemoteTools:
    """Remote machine management tools."""

    @staticmethod
    def launch_rdp(ip: str) -> Dict[str, Any]:
        """Launch Remote Desktop Connection to target IP."""
        if sys.platform != "win32":
            return {"success": False, "error": "Windows only"}
        try:
            subprocess.Popen(["mstsc.exe", "/v:" + ip],
                           creationflags=subprocess.CREATE_NO_WINDOW)
            return {"success": True, "message": f"RDP launched for {ip}"}
        except FileNotFoundError:
            return {"success": False, "error": "mstsc.exe not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def ping(host: str) -> Dict[str, Any]:
        """Quick ping test."""
        try:
            result = subprocess.run(
                ["ping", "-n", "1", "-w", "2000", host],
                capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return {"success": result.returncode == 0, "output": result.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def shutdown_pc(ip: str) -> Dict[str, Any]:
        """Shutdown a remote PC."""
        try:
            cmd = ["shutdown", "/s", "/t", "10", "/m", f"\\\\{ip}",
                   "/c", "Shutdown initiated by IT Toolkit"]
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
            return {"success": result.returncode == 0,
                    "error": result.stderr if result.returncode != 0 else None,
                    "message": f"Shutdown command sent to {ip}" if result.returncode == 0 else None}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def restart_pc(ip: str) -> Dict[str, Any]:
        """Restart a remote PC."""
        try:
            cmd = ["shutdown", "/r", "/t", "10", "/m", f"\\\\{ip}",
                   "/c", "Restart initiated by IT Toolkit"]
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
            return {"success": result.returncode == 0,
                    "error": result.stderr if result.returncode != 0 else None,
                    "message": f"Restart command sent to {ip}" if result.returncode == 0 else None}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def lock_pc(ip: str) -> Dict[str, Any]:
        """Lock a remote PC."""
        if sys.platform != "win32":
            return {"success": False, "error": "Windows only"}
        try:
            cmd = ["psexec", f"\\\\{ip}", "-s", "rundll32.exe",
                   "user32.dll,LockWorkStation"]
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
            if "could not start" in result.stderr.lower() or result.returncode != 0:
                # Fallback: try wmic
                subprocess.run(["wmic", "/node:" + ip, "process", "call", "create",
                               "rundll32.exe user32.dll,LockWorkStation"],
                              capture_output=True, timeout=30,
                              creationflags=subprocess.CREATE_NO_WINDOW)
            return {"success": True, "message": f"Lock command sent to {ip}"}
        except FileNotFoundError:
            return {"success": False, "error": "psexec.exe not found. Use remote shutdown or restart instead."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def run_remote_cmd(ip: str, cmd: str) -> Dict[str, Any]:
        """Run command on remote PC via psexec."""
        try:
            result = subprocess.run(
                ["psexec", f"\\\\{ip}", "-s", "-h", "-accepteula",
                 "cmd", "/c", cmd],
                capture_output=True, text=True, timeout=60,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return {"success": result.returncode == 0,
                    "stdout": result.stdout, "stderr": result.stderr,
                    "error": result.stderr if result.returncode != 0 and not result.stderr else None}
        except FileNotFoundError:
            # Try WMIC fallback
            try:
                result = subprocess.run(
                    ["wmic", "/node:" + ip, "process", "call", "create", cmd],
                    capture_output=True, text=True, timeout=60,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                ok = "ReturnValue = 0" in result.stdout
                return {"success": ok, "stdout": result.stdout, "stderr": result.stderr}
            except Exception as e2:
                return {"success": False, "error": f"psexec not found and WMIC failed: {e2}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
