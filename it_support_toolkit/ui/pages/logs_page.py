"""Event log analyzer page with summaries and time filters."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QMessageBox, QGroupBox, QGridLayout, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush
from utils.background_tasks import TaskWorker
from core.eventlog import EventLogAnalyzer


class StatCard(QFrame):
    def __init__(self, title: str, value: str, color: str, parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        v = QLabel(value)
        v.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color};")
        t = QLabel(title)
        t.setStyleSheet("font-size: 11px; color: #707080;")
        layout.addWidget(v)
        layout.addWidget(t)


class LogsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.all_logs = []
        self.setup_ui()

    def setup_ui(self):
        # Scroll area for responsive log viewing
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

        title = QLabel("Event Log Analyzer")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # Summary cards
        summary_layout = QHBoxLayout()
        self.crit_card = StatCard("Critical", "0", "#e74c3c")
        self.err_card = StatCard("Errors", "0", "#e67e22")
        self.warn_card = StatCard("Warnings", "0", "#f39c12")
        self.info_card = StatCard("Info", "0", "#3498db")
        for c in (self.crit_card, self.err_card, self.warn_card, self.info_card):
            summary_layout.addWidget(c)
        layout.addLayout(summary_layout)

        # Controls
        controls = QHBoxLayout()

        controls.addWidget(QLabel("Log Type:"))
        self.log_type = QComboBox()
        self.log_type.addItems(["System", "Application", "Security", "Setup"])
        controls.addWidget(self.log_type)

        controls.addWidget(QLabel("Time Filter:"))
        self.time_filter = QComboBox()
        self.time_filter.addItems(["Last 24 Hours", "Last 7 Days", "Last 30 Days"])
        controls.addWidget(self.time_filter)

        controls.addWidget(QLabel("Level:"))
        self.level_filter = QComboBox()
        self.level_filter.addItems(["All", "ERROR", "WARNING", "INFO"])
        self.level_filter.currentTextChanged.connect(self.apply_filters)
        controls.addWidget(self.level_filter)

        btn_load = QPushButton("Load Logs")
        btn_load.clicked.connect(self.load_logs)
        controls.addWidget(btn_load)

        layout.addLayout(controls)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Time", "Level", "Category", "Source", "Message"])
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        scroll.setWidget(inner)

    def load_logs(self):
        log_type = self.log_type.currentText()
        hours_map = {"Last 24 Hours": 24, "Last 7 Days": 168, "Last 30 Days": 720}
        hours = hours_map.get(self.time_filter.currentText(), 24)

        worker = TaskWorker(
            target=EventLogAnalyzer.get_log_summary,
            args=(log_type, hours)
        )
        worker.result.connect(self._on_loaded)
        worker.start()

    def _on_loaded(self, summary):
        if not summary:
            return

        # Update stat cards - find the value label (first QLabel child)
        cards = [
            (self.crit_card, "critical", "#e74c3c"),
            (self.err_card, "error", "#e67e22"),
            (self.warn_card, "warning", "#f39c12"),
            (self.info_card, "info", "#3498db"),
        ]
        for card, key, color in cards:
            labels = card.findChildren(QLabel)
            if labels:
                labels[0].setText(str(summary.get(key, 0)))
                labels[0].setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color};")

        self.all_logs = summary.get("logs", [])
        self.apply_filters()

    def apply_filters(self):
        level = self.level_filter.currentText()
        filtered = self.all_logs
        if level != "All":
            filtered = [l for l in filtered if l.get("level") == level]

        self.table.setRowCount(0)
        for log in filtered:
            r = self.table.rowCount()
            self.table.insertRow(r)

            level = log.get("level", "")
            color_map = {
                "ERROR": "#e74c3c", "WARNING": "#f39c12",
                "INFO": "#2ecc71", "CRITICAL": "#e74c3c",
                "AUDIT_FAILURE": "#e74c3c", "AUDIT_SUCCESS": "#3498db"
            }
            color = QBrush(QColor(color_map.get(level, "#ffffff")))

            self.table.setItem(r, 0, QTableWidgetItem(log.get("time", "")))
            lvl_item = QTableWidgetItem(level)
            lvl_item.setForeground(color)
            self.table.setItem(r, 1, lvl_item)
            self.table.setItem(r, 2, QTableWidgetItem(log.get("category", "General")))
            self.table.setItem(r, 3, QTableWidgetItem(log.get("source", "")))
            msg = log.get("message", "")
            self.table.setItem(r, 4, QTableWidgetItem(msg[:120] + "..." if len(msg) > 120 else msg))
