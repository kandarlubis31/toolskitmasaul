"""Remote Desktop and machine administration page."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QGroupBox, QFormLayout, QMessageBox,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from utils.background_tasks import TaskWorker
from core.remote_tools import RemoteTools


class RemotePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # Scroll area for remote tools
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

        title = QLabel("Remote Control")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # Target IP
        ip_group = QGroupBox("Target Machine")
        ip_layout = QHBoxLayout(ip_group)
        ip_layout.addWidget(QLabel("IP Address:"))
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("e.g. 192.168.1.100")
        ip_layout.addWidget(self.ip_input)
        layout.addWidget(ip_group)

        # Quick actions
        quick_group = QGroupBox("Quick Actions")
        quick_layout = QHBoxLayout(quick_group)

        btn_ping = QPushButton("Ping")
        btn_ping.clicked.connect(lambda: self.run_action("ping"))
        quick_layout.addWidget(btn_ping)

        btn_rdp = QPushButton("RDP")
        btn_rdp.clicked.connect(lambda: self.run_action("rdp"))
        quick_layout.addWidget(btn_rdp)

        btn_restart = QPushButton("Restart")
        btn_restart.clicked.connect(lambda: self.run_action("restart"))
        quick_layout.addWidget(btn_restart)

        btn_shutdown = QPushButton("Shutdown")
        btn_shutdown.clicked.connect(lambda: self.run_action("shutdown"))
        quick_layout.addWidget(btn_shutdown)

        btn_lock = QPushButton("Lock")
        btn_lock.clicked.connect(lambda: self.run_action("lock"))
        quick_layout.addWidget(btn_lock)

        layout.addWidget(quick_group)

        # Remote command
        cmd_group = QGroupBox("Remote Command (requires psexec)")
        cmd_layout = QVBoxLayout(cmd_group)
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("e.g. ipconfig /all, systeminfo, whoami")
        cmd_layout.addWidget(self.cmd_input)
        btn_cmd = QPushButton("Run Command")
        btn_cmd.clicked.connect(lambda: self.run_action("cmd"))
        cmd_layout.addWidget(btn_cmd)
        layout.addWidget(cmd_group)

        # Output
        out_group = QGroupBox("Output")
        out_layout = QVBoxLayout(out_group)
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setMaximumHeight(300)
        self.output.setObjectName("outputArea")
        out_layout.addWidget(self.output)
        layout.addWidget(out_group)

        scroll.setWidget(inner)

    def get_ip(self):
        ip = self.ip_input.text().strip()
        if not ip:
            QMessageBox.warning(self, "Input Error", "Enter an IP address")
            return None
        return ip

    def run_action(self, action):
        ip = self.get_ip()
        if not ip:
            return

        self.output.clear()
        self.output.append(f"Running {action} on {ip}...\n")

        kwargs = {"ip": ip}
        if action == "cmd":
            cmd = self.cmd_input.text().strip()
            if not cmd:
                QMessageBox.warning(self, "Error", "Enter a command")
                return
            kwargs["cmd"] = cmd
            worker = TaskWorker(target=RemoteTools.run_remote_cmd, args=(ip, cmd))
        elif action == "ping":
            worker = TaskWorker(target=RemoteTools.ping, args=(ip,))
        elif action == "rdp":
            worker = TaskWorker(target=RemoteTools.launch_rdp, args=(ip,))
        elif action == "restart":
            worker = TaskWorker(target=RemoteTools.restart_pc, args=(ip,))
        elif action == "shutdown":
            worker = TaskWorker(target=RemoteTools.shutdown_pc, args=(ip,))
        elif action == "lock":
            worker = TaskWorker(target=RemoteTools.lock_pc, args=(ip,))
        else:
            return

        worker.result.connect(self.show_result)
        worker.error.connect(lambda e: self.output.append(f"[ERROR] {e}"))
        worker.start()

    def show_result(self, result):
        if isinstance(result, dict):
            if result.get("success"):
                msg = result.get("message", result.get("stdout", "Done"))
                self.output.append(f"[OK] {msg}")
            else:
                self.output.append(f"[FAIL] {result.get('error', 'Unknown error')}")
            stdout = result.get("stdout", "")
            if stdout:
                self.output.append(stdout)
            latency = result.get("latency_ms", 0)
            if latency:
                self.output.append(f"Latency: {latency} ms")
        else:
            self.output.append(str(result))
