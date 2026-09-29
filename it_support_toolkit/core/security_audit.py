"""Security audit module - checks Windows security settings and generates score."""

import sys
import subprocess
from typing import Dict, Any, List
from .system_info import SystemInfo


class SecurityAudit:
    """Windows security audit and scoring."""

    @staticmethod
    def run_audit() -> Dict[str, Any]:
        """Run full security audit and return score + recommendations."""
        checks = []
        score = 100

        # 1. Windows Defender
        av = SystemInfo.get_antivirus()
        av_pass = "Enabled" in av
        score -= 0 if av_pass else 30
        checks.append({
            "name": "Antivirus (Defender)",
            "status": "PASS" if av_pass else "FAIL",
            "value": av,
            "points_lost": 0 if av_pass else 30,
            "recommendation": "Enable Windows Defender" if not av_pass else "",
        })

        # 2. Firewall
        fw = SystemInfo.get_firewall()
        fw_pass = "Enabled" in fw
        score -= 0 if fw_pass else 20
        checks.append({
            "name": "Firewall",
            "status": "PASS" if fw_pass else "FAIL",
            "value": fw,
            "points_lost": 0 if fw_pass else 20,
            "recommendation": "Enable Windows Firewall" if not fw_pass else "",
        })

        # 3. Windows Update
        wu = SystemInfo.get_windows_update()
        wu_pass = "Unknown" not in wu and "Auto" in wu
        score -= 0 if wu_pass else 15
        checks.append({
            "name": "Windows Update",
            "status": "PASS" if wu_pass else "WARN",
            "value": wu,
            "points_lost": 0 if wu_pass else 15,
            "recommendation": "Configure Windows Update to Automatic" if not wu_pass else "",
        })

        # 4. BitLocker
        bl_status = SecurityAudit._check_bitlocker()
        bl_pass = bl_status in ("On", "Enabled")
        score -= 0 if bl_pass else 10
        checks.append({
            "name": "BitLocker",
            "status": "PASS" if bl_pass else "INFO",
            "value": bl_status,
            "points_lost": 0 if bl_pass else 10,
            "recommendation": "Enable BitLocker encryption for better security" if not bl_pass else "",
        })

        # 5. RDP Status
        rdp = SecurityAudit._check_rdp()
        rdp_pass = rdp == "Disabled"
        score -= 0 if rdp_pass else 5
        checks.append({
            "name": "RDP Status",
            "status": "PASS" if rdp_pass else "WARN",
            "value": rdp,
            "points_lost": 0 if rdp_pass else 5,
            "recommendation": "Disable RDP if not needed" if not rdp_pass else "",
        })

        # 6. SMBv1
        smb = SecurityAudit._check_smbv1()
        smb_pass = "Disabled" in smb or "Not Found" in smb
        score -= 0 if smb_pass else 10
        checks.append({
            "name": "SMBv1 Protocol",
            "status": "PASS" if smb_pass else "FAIL",
            "value": smb,
            "points_lost": 0 if smb_pass else 10,
            "recommendation": "Disable SMBv1 (it's vulnerable)" if not smb_pass else "",
        })

        # 7. Guest Account
        guest = SecurityAudit._check_guest_account()
        guest_pass = "Disabled" in guest
        score -= 0 if guest_pass else 5
        checks.append({
            "name": "Guest Account",
            "status": "PASS" if guest_pass else "FAIL",
            "value": guest,
            "points_lost": 0 if guest_pass else 5,
            "recommendation": "Disable the Guest account" if not guest_pass else "",
        })

        # 8. UAC
        uac = SecurityAudit._check_uac()
        uac_pass = uac > 0
        score -= 0 if uac_pass else 5
        checks.append({
            "name": "UAC",
            "status": "PASS" if uac_pass else "WARN",
            "value": f"Level {uac}" if uac_pass else "Disabled",
            "points_lost": 0 if uac_pass else 5,
            "recommendation": "Enable User Account Control" if not uac_pass else "",
        })

        score = max(0, min(100, score))
        grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 60 else "D" if score >= 40 else "F"

        return {
            "score": score,
            "grade": grade,
            "checks": checks,
            "summary": {
                "total_passed": sum(1 for c in checks if c["status"] == "PASS"),
                "total_warnings": sum(1 for c in checks if c["status"] == "WARN"),
                "total_failed": sum(1 for c in checks if c["status"] == "FAIL"),
            },
        }

    @staticmethod
    def _check_bitlocker() -> str:
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "(Get-BitLockerVolume -MountPoint $env:SystemDrive 2>$null).ProtectionStatus"],
                capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            status = result.stdout.strip()
            return "On" if status == "1" else ("Off" if status == "0" else "Not Available")
        except Exception:
            return "Unknown"

    @staticmethod
    def _check_rdp() -> str:
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"SYSTEM\CurrentControlSet\Control\Terminal Server")
            try:
                val = winreg.QueryValueEx(key, "fDenyTSConnections")[0]
                return "Disabled" if val == 1 else "Enabled"
            finally:
                winreg.CloseKey(key)
        except Exception:
            return "Unknown"

    @staticmethod
    def _check_smbv1() -> str:
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-SmbServerConfiguration | Select-Object -ExpandProperty EnableSMB1Protocol"],
                capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return "Disabled" if "False" in result.stdout else "Enabled"
        except Exception:
            return "Unknown"

    @staticmethod
    def _check_guest_account() -> str:
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "(Get-LocalUser -Name 'Guest' 2>$null).Enabled"],
                capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return "Enabled" if "True" in result.stdout else "Disabled"
        except Exception:
            return "Unknown"

    @staticmethod
    def _check_uac() -> int:
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System")
            try:
                return winreg.QueryValueEx(key, "EnableLUA")[0]
            finally:
                winreg.CloseKey(key)
        except Exception:
            return 0
