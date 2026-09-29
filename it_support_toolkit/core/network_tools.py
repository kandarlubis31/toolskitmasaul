"""Network diagnostics and repair toolkit."""

import sys
import subprocess
import socket
from typing import Dict, Any, List


class NetworkTools:
    """Professional network diagnostics tools."""

    @staticmethod
    def ping(host: str, count: int = 4) -> Dict[str, Any]:
        """Ping a host and return results."""
        try:
            cmd = ["ping", "-n", str(count), host]
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
            output = result.stdout + result.stderr
            if result.returncode != 0:
                return {"success": False, "latency_ms": 0, "output": "Host unreachable"}

            avg_ms = 0
            for line in output.splitlines():
                if "Average" in line or "Moyenne" in line:
                    try:
                        avg_ms = int(line.split("=")[-1].strip().replace("ms", "").strip())
                    except (ValueError, IndexError):
                        pass
                    break
            return {"success": True, "latency_ms": avg_ms, "output": output}
        except Exception as e:
            return {"success": False, "latency_ms": 0, "error": str(e)}

    @staticmethod
    def traceroute(host: str, max_hops: int = 20) -> List[Dict[str, str]]:
        """Run traceroute and return list of hops."""
        hops = []
        try:
            cmd = ["tracert", "-h", str(max_hops), host]
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    timeout=60, creationflags=subprocess.CREATE_NO_WINDOW)
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line or "Tracing" in line or "over" in line:
                    continue
                if line[0].isdigit():
                    parts = line.split()
                    if len(parts) >= 2:
                        hop_num = parts[0]
                        ip = parts[-1].strip("[]")
                        latency = parts[-2] if len(parts) > 2 else "*"
                        hops.append({"hop": hop_num, "ip": ip, "latency": latency})
        except Exception:
            pass
        return hops

    @staticmethod
    def nslookup(host: str) -> Dict[str, Any]:
        """DNS lookup for a host."""
        try:
            result = subprocess.run(
                ["nslookup", host], capture_output=True, text=True,
                timeout=15, creationflags=subprocess.CREATE_NO_WINDOW
            )
            return {"success": result.returncode == 0, "output": result.stdout + result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def port_scan(host: str, ports: List[int], timeout: float = 2.0) -> List[Dict[str, Any]]:
        """Scan a list of ports on a host."""
        results = []
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                sock.close()
                service = {22: "SSH", 80: "HTTP", 443: "HTTPS", 3389: "RDP",
                           21: "FTP", 25: "SMTP", 110: "POP3", 143: "IMAP",
                           53: "DNS", 445: "SMB", 8080: "HTTP-Alt"}.get(port, "")
                results.append({"port": port, "open": result == 0, "service": service})
            except Exception:
                results.append({"port": port, "open": False, "service": ""})
        return results

    @staticmethod
    def flush_dns() -> Dict[str, Any]:
        """Flush DNS cache."""
        try:
            result = subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True,
                                    timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
            return {"success": result.returncode == 0, "output": result.stdout + result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def reset_winsock() -> Dict[str, Any]:
        """Reset Winsock catalog."""
        try:
            result = subprocess.run(["netsh", "winsock", "reset"], capture_output=True, text=True,
                                    timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
            return {"success": result.returncode == 0, "output": result.stdout + result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def reset_tcpip() -> Dict[str, Any]:
        """Reset TCP/IP stack."""
        try:
            result = subprocess.run(["netsh", "int", "ip", "reset"], capture_output=True, text=True,
                                    timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
            return {"success": result.returncode == 0, "output": result.stdout + result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_local_ip() -> str:
        from core.system_info import SystemInfo
        return SystemInfo.get_local_ip()
