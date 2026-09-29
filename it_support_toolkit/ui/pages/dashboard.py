"""Dashboard — real-time system monitoring with loading feedback."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QProgressBar, QGroupBox, QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
try:
    import psutil
except ImportError:
    psutil = None

from utils.background_tasks import TaskWorker
from core.system_info import SystemInfo


class StatBox(QFrame):
    def __init__(self, label: str, value: str = "-"):
        super().__init__()
        self.setObjectName("statBox")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(2)
        self.val = QLabel(value)
        self.val.setObjectName("statValue")
        lbl = QLabel(label)
        lbl.setObjectName("statLabel")
        layout.addWidget(self.val)
        layout.addWidget(lbl)

    def set_val(self, v):
        self.val.setText(str(v))


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self._loading = False
        self._live_timer = None
        self._system_data = {}
        self.setup_ui()

    def setup_ui(self):
        # Scroll area for dashboard
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(8)

        # Title row with status indicator
        header = QHBoxLayout()
        title = QLabel("Dashboard")
        title.setObjectName("pageTitle")
        header.addWidget(title)
        header.addStretch()
        self.status_dot = QLabel("⚫")
        self.status_dot.setObjectName("statusDot")
        self.status_text = QLabel("Initializing...")
        self.status_text.setObjectName("statusText")
        header.addWidget(self.status_dot)
        header.addWidget(self.status_text)
        layout.addLayout(header)

        # Health cards row
        cards = QHBoxLayout()
        self.health = {}
        for name in ("System", "Security", "Storage", "Network"):
            c = QFrame()
            c.setObjectName("healthCard")
            cl = QVBoxLayout(c)
            cl.setSpacing(2)
            cl.setContentsMargins(10, 8, 10, 8)
            v = QLabel("...")
            v.setObjectName("cardValue")
            s = QLabel("LOADING")
            s.setObjectName("cardStatus")
            cl.addWidget(v)
            cl.addWidget(QLabel(name))
            cl.addWidget(s)
            self.health[name] = (v, s)
            cards.addWidget(c)
        layout.addLayout(cards)

        # System info grid
        g = QGroupBox("System Information")
        grid = QGridLayout(g)
        grid.setSpacing(2)
        grid.setContentsMargins(10, 14, 10, 8)
        self.info = {}
        items = [
            "Computer Name", "User", "Windows", "Build",
            "Uptime", "Local IP", "Public IP", "Antivirus",
            "Firewall", "Activation"
        ]
        keys = [
            "computer_name", "current_user", "windows_edition", "windows_build",
            "system_uptime", "local_ip", "public_ip", "antivirus",
            "firewall", "activation"
        ]
        for i, (lbl, key) in enumerate(zip(items, keys)):
            r, c = divmod(i, 2)
            sb = StatBox(lbl)
            grid.addWidget(sb, r, c)
            self.info[key] = sb
        layout.addWidget(g)

        # Real-time resource bars
        rg = QGroupBox("Live Resources  🔄")
        rl = QVBoxLayout(rg)
        rl.setContentsMargins(10, 14, 10, 8)
        rl.setSpacing(4)
        for name in ("CPU:", "RAM:", "Disk:"):
            h = QHBoxLayout()
            lbl_name = QLabel(f"  {name[:-1]}  ")
            lbl_name.setFixedWidth(50)
            h.addWidget(lbl_name)
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setTextVisible(False)
            val = QLabel("0%")
            val.setFixedWidth(120)
            val.setObjectName("resourceValue")
            h.addWidget(bar)
            h.addWidget(val)
            rl.addLayout(h)
            clean = name.rstrip(":").strip().lower()
            setattr(self, f"{clean}_bar", bar)
            setattr(self, f"{clean}_lbl", val)
        layout.addWidget(rg)
        layout.addStretch()

        scroll.setWidget(inner)

    # ── refresh (first load) ──────────────────────────────

    def refresh(self):
        if self._loading:
            return
        self._loading = True
        self._show_loading()
        # First fetch ALL data, then cache static for subsequent calls
        w = TaskWorker(target=SystemInfo.get_all)
        w.result.connect(self._on_first_load)
        w.error.connect(lambda e: self._on_load_error(e))
        w.start()

    def _show_loading(self):
        self.status_dot.setText("🟡")
        self.status_text.setText("Fetching system data...")
        for key in ("System", "Security", "Storage", "Network"):
            self.health[key][1].setText("LOADING")

    def _on_first_load(self, d):
        self._system_data = d
        self._update_static(d)  # one-time: info grid + AV/firewall/IP etc
        self._update_resources(d)  # first paint of bars
        self._show_ready()
        self._loading = False
        self._start_live_polling()

    def _on_load_error(self, err):
        self.status_dot.setText("🔴")
        self.status_text.setText(f"Error: {err[:40]}")
        self._loading = False

    # ── real-time polling (CPU/RAM/Disk only) ──────────────

    def _start_live_polling(self):
        if self._live_timer is not None:
            return
        # Prime non-blocking CPU measurement
        if psutil:
            try:
                psutil.cpu_percent(interval=0.1)
            except Exception:
                pass
        self._live_timer = QTimer(self)
        self._live_timer.timeout.connect(self._poll_resources)
        self._live_timer.start(3000)

    def hideEvent(self, event):
        """Stop live polling when page is hidden."""
        if self._live_timer:
            self._live_timer.stop()
        super().hideEvent(event)

    def showEvent(self, event):
        """Resume live polling when page becomes visible."""
        if self._live_timer and not self._live_timer.isActive():
            self._live_timer.start()
        super().showEvent(event)

    def _poll_resources(self):
        """Fast non-blocking resource poll."""
        try:
            # Non-blocking CPU (uses last measurement)
            if psutil:
                try:
                    cpu = psutil.cpu_percent(interval=0)
                except Exception:
                    cpu = self._system_data.get("cpu_usage", 0)
            else:
                cpu = self._system_data.get("cpu_usage", 0)

            ram = SystemInfo.get_ram_usage()
            disk = SystemInfo.get_disk_usage()

            self.cpu_bar.setValue(int(cpu))
            self.cpu_lbl.setText(f"{cpu:.0f}%")
            self.cpu_bar.setStyleSheet(self._bar_color(cpu, 70, 90))

            rp = ram.get("percent", 0)
            self.ram_bar.setValue(int(rp))
            self.ram_lbl.setText(
                f"{ram.get('used_gb', 0):.1f}/{ram.get('total_gb', 0):.1f} GB ({rp:.0f}%)")
            self.ram_bar.setStyleSheet(self._bar_color(rp, 70, 90))

            dp = disk.get("percent", 0)
            self.disk_bar.setValue(int(dp))
            self.disk_lbl.setText(
                f"{disk.get('used_gb', 0):.0f}/{disk.get('total_gb', 0):.0f} GB")
            self.disk_bar.setStyleSheet(self._bar_color(dp, 80, 95))

            self.health["System"][0].setText(f"CPU: {cpu:.0f}%")
            self.health["System"][1].setText(
                "OK" if cpu < 70 else ("HIGH" if cpu < 90 else "CRITICAL"))
            self.health["Storage"][0].setText(f"Disk: {dp:.0f}%")
            self.health["Storage"][1].setText(
                "OK" if dp < 80 else ("FULL" if dp < 95 else "CRITICAL"))

            self._system_data["cpu_usage"] = cpu
            self._system_data["ram"] = ram
            self._system_data["disk"] = disk

        except Exception:
            pass

    @staticmethod
    def _bar_color(val: float, warn: int, crit: int) -> str:
        if val < warn:
            c = "#2ecc71"
        elif val < crit:
            c = "#f39c12"
        else:
            c = "#e74c3c"
        return (f"QProgressBar::chunk {{ background: {c}; border-radius: 2px; }}"
                f"QProgressBar {{ background: #181825; border: 1px solid #313244; "
                f"border-radius: 3px; height: 14px; }}")

    # ── state helpers ─────────────────────────────────────

    def _show_ready(self):
        self.status_dot.setText("🟢")
        self.status_text.setText("Live monitoring active")

    # ── one-time static data update ───────────────────────

    def _update_static(self, d):
        """Static info that never changes — called ONCE."""
        if not d:
            return
        for key, sb in self.info.items():
            val = d.get(key, "-")
            if isinstance(val, dict):
                val = f"{val.get('used_gb', 0)}/{val.get('total_gb', 0)} GB"
            sb.set_val(val)
        av = d.get("antivirus", "-")
        self.health["Security"][0].setText(f"AV: {av}")
        self.health["Security"][1].setText(
            "OK" if "Enabled" in av else "CHECK")
        ip = d.get("local_ip", "-")
        self.health["Network"][0].setText(f"IP: {ip}")
        self.health["Network"][1].setText(
            "OK" if ip != "127.0.0.1" else "NONE")

    # ── resource bars initial paint ───────────────────────

    def _update_resources(self, d):
        """Initial paint of resource bars from first load data."""
        if not d:
            return
        cpu = d.get("cpu_usage", 0)
        self.cpu_bar.setValue(int(cpu))
        self.cpu_lbl.setText(f"{cpu:.0f}%")
        ram = d.get("ram", {})
        rp = ram.get("percent", 0)
        self.ram_bar.setValue(int(rp))
        self.ram_lbl.setText(
            f"{ram.get('used_gb', 0)}/{ram.get('total_gb', 0)} GB ({rp:.0f}%)")
        disk = d.get("disk", {})
        dp = disk.get("percent", 0)
        self.disk_bar.setValue(int(dp))
        self.disk_lbl.setText(
            f"{disk.get('used_gb', 0)}/{disk.get('total_gb', 0)} GB")
        self.health["System"][0].setText(f"CPU: {cpu:.0f}%")
        self.health["System"][1].setText(
            "OK" if cpu < 70 else "HIGH")
        self.health["Storage"][0].setText(f"Disk: {dp:.0f}%")
        self.health["Storage"][1].setText(
            "OK" if dp < 80 else "FULL")
