"""Network tools page."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QGroupBox, QSpinBox, QMessageBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from utils.background_tasks import TaskWorker
from core.network_tools import NetworkTools


class NetworkPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Network Toolkit")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        self.tabs = QTabWidget()

        # Ping tab
        ping_w = QWidget()
        ping_l = QVBoxLayout(ping_w)
        h = QHBoxLayout()
        self.ping_host = QLineEdit("google.com")
        h.addWidget(QLabel("Host:"))
        h.addWidget(self.ping_host)
        btn = QPushButton("Ping")
        btn.clicked.connect(lambda: self.run_network("ping"))
        h.addWidget(btn)
        ping_l.addLayout(h)
        self.ping_out = QTextEdit()
        self.ping_out.setReadOnly(True)
        self.ping_out.setObjectName("outputArea")
        ping_l.addWidget(self.ping_out)
        self.tabs.addTab(ping_w, "Ping")

        # Traceroute tab
        tr_w = QWidget()
        tr_l = QVBoxLayout(tr_w)
        h = QHBoxLayout()
        self.tr_host = QLineEdit("google.com")
        h.addWidget(QLabel("Host:"))
        h.addWidget(self.tr_host)
        btn = QPushButton("Traceroute")
        btn.clicked.connect(lambda: self.run_network("traceroute"))
        h.addWidget(btn)
        tr_l.addLayout(h)
        self.tr_out = QTextEdit()
        self.tr_out.setReadOnly(True)
        self.tr_out.setObjectName("outputArea")
        tr_l.addWidget(self.tr_out)
        self.tabs.addTab(tr_w, "Traceroute")

        # DNS Lookup tab
        dns_w = QWidget()
        dns_l = QVBoxLayout(dns_w)
        h = QHBoxLayout()
        self.dns_host = QLineEdit("google.com")
        h.addWidget(QLabel("Host:"))
        h.addWidget(self.dns_host)
        btn = QPushButton("NSLookup")
        btn.clicked.connect(lambda: self.run_network("nslookup"))
        h.addWidget(btn)
        dns_l.addLayout(h)
        self.dns_out = QTextEdit()
        self.dns_out.setReadOnly(True)
        self.dns_out.setObjectName("outputArea")
        dns_l.addWidget(self.dns_out)
        self.tabs.addTab(dns_w, "DNS Lookup")

        # Port Scanner tab
        port_w = QWidget()
        port_l = QVBoxLayout(port_w)
        h = QHBoxLayout()
        self.port_host = QLineEdit("localhost")
        h.addWidget(QLabel("Host:"))
        h.addWidget(self.port_host)
        h.addWidget(QLabel("Ports:"))
        self.port_range = QLineEdit("22,80,443,3389,8080")
        self.port_range.setPlaceholderText("Comma-separated ports")
        h.addWidget(self.port_range)
        btn = QPushButton("Scan Ports")
        btn.clicked.connect(lambda: self.run_network("portscan"))
        h.addWidget(btn)
        port_l.addLayout(h)
        self.port_table = QTableWidget()
        self.port_table.setColumnCount(3)
        self.port_table.setHorizontalHeaderLabels(["Port", "Service", "Status"])
        self.port_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        port_l.addWidget(self.port_table)
        self.tabs.addTab(port_w, "Port Scanner")

        # Network Reset tab
        reset_w = QWidget()
        reset_l = QVBoxLayout(reset_w)
        info = QLabel("One-click network reset operations. Admin rights required.")
        info.setWordWrap(True)
        reset_l.addWidget(info)
        for name, action in [("Flush DNS", "flushdns"), ("Reset Winsock", "resetwinsock"),
                              ("Reset TCP/IP", "resettcpip")]:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, a=action: self.run_network(a))
            reset_l.addWidget(btn)
        reset_l.addStretch()
        self.tabs.addTab(reset_w, "Network Reset")

        # Output for reset operations
        self.reset_out = QTextEdit()
        self.reset_out.setReadOnly(True)
        self.reset_out.setMaximumHeight(100)
        self.reset_out.setObjectName("outputArea")
        self.reset_out.setVisible(False)
        reset_l.addWidget(self.reset_out)

        layout.addWidget(self.tabs)

    def run_network(self, action: str):
        target_map = {
            "ping": (self.ping_host, self.ping_out),
            "traceroute": (self.tr_host, self.tr_out),
            "nslookup": (self.dns_host, self.dns_out),
        }

        if action == "portscan":
            host = self.port_host.text().strip()
            ports_str = self.port_range.text().strip()
            if not host or not ports_str:
                return
            try:
                ports = [int(p.strip()) for p in ports_str.split(",") if p.strip().isdigit()]
            except ValueError:
                QMessageBox.warning(self, "Error", "Invalid port numbers")
                return
            self.worker = TaskWorker(target=NetworkTools.port_scan, args=(host, ports))
            self.worker.result.connect(self._display_ports)
            self.worker.start()
            return

        if action in ("flushdns", "resetwinsock", "resettcpip"):
            self.reset_out.setVisible(True)
            self.reset_out.append(f"Running {action}...")
            func_map = {
                "flushdns": NetworkTools.flush_dns,
                "resetwinsock": NetworkTools.reset_winsock,
                "resettcpip": NetworkTools.reset_tcpip,
            }
            worker = TaskWorker(target=func_map[action])
            worker.result.connect(lambda r: self.reset_out.append(
                f"{'OK' if r.get('success') else 'FAIL'}: {r.get('output', r.get('error', ''))}"
            ))
            worker.start()
            return

        if action in target_map:
            host_input, output = target_map[action]
            host = host_input.text().strip()
            if not host:
                return
            func_map = {
                "ping": lambda: NetworkTools.ping(host),
                "traceroute": lambda: NetworkTools.traceroute(host),
                "nslookup": lambda: NetworkTools.nslookup(host),
            }
            output.clear()
            output.append(f"Running {action} on {host}...\n")
            worker = TaskWorker(target=func_map[action])
            worker.result.connect(lambda r, o=output: self._display_result(r, o, action))
            worker.start()

    def _display_result(self, result, output, action):
        if action == "ping":
            if result.get("success"):
                output.append(f"Ping OK - Latency: {result.get('latency_ms', 0)} ms")
            else:
                output.append(f"Ping FAILED: {result.get('error', 'Unknown')}")
        elif action == "traceroute":
            hops = result if isinstance(result, list) else []
            for h in hops:
                output.append(f" Hop {h.get('hop', '?')}: {h.get('ip', '?')} ({h.get('latency', '?')})")
        elif action == "nslookup":
            output.append(result.get("output", str(result)))

    def _display_ports(self, results):
        self.port_table.setRowCount(0)
        for r in results:
            row = self.port_table.rowCount()
            self.port_table.insertRow(row)
            self.port_table.setItem(row, 0, QTableWidgetItem(str(r.get("port", ""))))
            self.port_table.setItem(row, 1, QTableWidgetItem(r.get("service", "")))
            status = "OPEN" if r.get("open") else "CLOSED"
            item = QTableWidgetItem(status)
            item.setForeground(Qt.GlobalColor.green if r.get("open") else Qt.GlobalColor.red)
            self.port_table.setItem(row, 2, item)
