"""Repair tools page with one-click actions."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QGroupBox, QMessageBox, QGridLayout, QProgressBar
)
from PyQt6.QtCore import Qt
from utils.background_tasks import TaskWorker
from core.repair_tools import RepairTools
from utils.permissions import is_admin


class RepairPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Repair Tools")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        info = QLabel(
            "One-click repair and maintenance operations. "
            "Admin rights are required for most actions."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        # Admin badge
        self.admin_badge = QLabel("Running as ADMIN" if is_admin() else "Limited privileges - some tools need admin")
        self.admin_badge.setObjectName("adminBadge")
        layout.addWidget(self.admin_badge)

        # Progress
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Action buttons grid
        actions_group = QGroupBox("Repair Actions")
        grid = QGridLayout(actions_group)
        grid.setSpacing(8)

        self.action_buttons = {}
        actions = RepairTools.get_actions()
        for i, action in enumerate(actions):
            row, col = divmod(i, 3)
            aid = action["id"]
            btn = QPushButton(action["name"])
            btn.setToolTip(action["description"])
            if action["admin"]:
                btn.setToolTip(btn.toolTip() + " [Admin Required]")
            btn.clicked.connect(lambda checked, a=aid: self.run_repair(a))
            btn.setMinimumHeight(48)
            grid.addWidget(btn, row, col)
            self.action_buttons[aid] = btn

        layout.addWidget(actions_group)

        # Output
        out_group = QGroupBox("Operation Log")
        out_layout = QVBoxLayout(out_group)
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setObjectName("outputArea")
        self.output.setMaximumHeight(200)
        out_layout.addWidget(self.output)
        layout.addWidget(out_group)

    def run_repair(self, action_id: str):
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.output.clear()
        self.output.append(f"Starting: {action_id}...")

        self.worker = TaskWorker(
            target=RepairTools.execute,
            args=(action_id,),
            kwargs={"progress_callback": lambda msg: self.output.append(f"> {msg}")}
        )
        self.worker.result.connect(self._on_complete)
        self.worker.error.connect(lambda e: self._on_error(e))
        self.worker.start()

    def _on_complete(self, result):
        self.progress.setVisible(False)
        if result.get("success"):
            self.output.append(f"\n[OK] {result.get('message', 'Completed successfully')}")
        else:
            self.output.append(f"\n[FAIL] {result.get('error', 'Operation failed')}")

    def _on_error(self, error):
        self.progress.setVisible(False)
        self.output.append(f"\n[ERROR] {error}")
