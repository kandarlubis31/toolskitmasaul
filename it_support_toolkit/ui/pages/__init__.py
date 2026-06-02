"""UI Pages package."""
from .dashboard import DashboardPage
from .hardware_page import HardwarePage
from .software_page import SoftwarePage
from .network_page import NetworkPage
from .remote_page import RemotePage
from .repair_page import RepairPage
from .cleaner_page import CleanerPage
from .security_page import SecurityPage
from .logs_page import LogsPage
from .settings_page import SettingsPage

__all__ = [
    "DashboardPage",
    "HardwarePage",
    "SoftwarePage",
    "NetworkPage",
    "RemotePage",
    "RepairPage",
    "CleanerPage",
    "SecurityPage",
    "LogsPage",
    "SettingsPage",
]
