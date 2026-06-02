"""Enhanced Event Log analyzer with summaries and time filters."""

import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List


class EventLogAnalyzer:
    """Windows Event Log analyzer with categorization and filtering."""

    COMMON_LOGS = ["System", "Application", "Security", "Setup"]

    @classmethod
    def get_log_summary(cls, log_type: str = "System", hours_back: int = 24) -> Dict[str, Any]:
        """Get categorized summary of event logs."""
        logs = cls.get_logs(log_type, count=500, hours_back=hours_back)
        summary = {"critical": 0, "error": 0, "warning": 0, "info": 0, "total": 0, "logs": []}

        for log in logs:
            level = log.get("level", "")
            if level == "ERROR":
                summary["error"] += 1
            elif level == "WARNING":
                summary["warning"] += 1
            elif level == "INFO":
                summary["info"] += 1
            else:
                summary["critical"] += 1
            summary["total"] += 1

        summary["logs"] = logs[:100]  # Cap display at 100
        return summary

    @staticmethod
    def get_logs(log_type: str = "System", count: int = 100, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Read Windows Event Log entries."""
        if sys.platform != "win32":
            return [{"error": "Windows only"}]

        try:
            import win32evtlog
        except ImportError:
            return [{"error": "pywin32 not installed"}]

        logs = []
        try:
            handle = win32evtlog.OpenEventLog(None, log_type)
        except Exception as e:
            return [{"error": f"Cannot open event log '{log_type}': {e}"}]

        try:
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            cutoff = datetime.now() - timedelta(hours=hours_back)
            events_read = 0

            while events_read < count:
                events = win32evtlog.ReadEventLog(handle, flags, 0)
                if not events:
                    break

                for event in events:
                    try:
                        et = event.TimeGenerated.Format()
                        try:
                            edt = datetime.strptime(et, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            try:
                                edt = datetime.strptime(et, "%a %b %d %H:%M:%S %Y")
                            except ValueError:
                                edt = datetime.now()

                        if edt < cutoff:
                            continue

                        evt_type = event.EventType
                        level_map = {
                            win32evtlog.EVENTLOG_ERROR_TYPE: "ERROR",
                            win32evtlog.EVENTLOG_WARNING_TYPE: "WARNING",
                            win32evtlog.EVENTLOG_INFORMATION_TYPE: "INFO",
                            win32evtlog.EVENTLOG_AUDIT_SUCCESS: "AUDIT_SUCCESS",
                            win32evtlog.EVENTLOG_AUDIT_FAILURE: "AUDIT_FAILURE",
                        }
                        level = level_map.get(evt_type, "OTHER")

                        logs.append({
                            "time": et,
                            "level": level,
                            "source": event.SourceName,
                            "event_id": event.EventID,
                            "category": cls._categorize_event(event.SourceName, event.EventID),
                            "message": str(event.StringInserts) if event.StringInserts else "(No details)",
                        })
                        events_read += 1
                        if events_read >= count:
                            break
                    except Exception:
                        continue
        except Exception as e:
            return [{"error": f"Read failed: {e}"}]
        finally:
            try:
                win32evtlog.CloseEventLog(handle)
            except Exception:
                pass

        return logs

    @staticmethod
    def _categorize_event(source: str, event_id: int) -> str:
        """Categorize event by source and ID."""
        source_lower = source.lower()
        if "disk" in source_lower or "stor" in source_lower:
            return "Disk"
        if "driver" in source_lower or "ntfs" in source_lower:
            return "Driver"
        if "network" in source_lower or "tcp" in source_lower or "dns" in source_lower:
            return "Network"
        if "kernel" in source_lower or "processor" in source_lower:
            return "Kernel"
        if "service" in source_lower or "svchost" in source_lower:
            return "Service"
        if "security" in source_lower or "security" in source_lower:
            return "Security"
        if "update" in source_lower or "wuau" in source_lower:
            return "Update"
        if event_id in (41, 1001, 6008):
            return "Kernel"
        if event_id in (7, 9, 11, 51, 153):
            return "Disk"
        return "General"

    @staticmethod
    def filter_by_time(logs: List[Dict], hours: int) -> List[Dict]:
        """Filter logs by hours back from now."""
        cutoff = datetime.now() - timedelta(hours=hours)
        filtered = []
        for log in logs:
            try:
                log_time = datetime.strptime(log["time"], "%Y-%m-%d %H:%M:%S")
                if log_time >= cutoff:
                    filtered.append(log)
            except (ValueError, KeyError):
                filtered.append(log)
        return filtered
