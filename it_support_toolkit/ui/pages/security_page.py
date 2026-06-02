"""Security audit page with scoring and recommendations."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QFrame, QProgressBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush
from utils.background_tasks import TaskWorker
from core.security_audit import SecurityAudit


class SecurityPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Security Audit")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # Score display
        score_group = QGroupBox("Security Score")
        score_layout = QHBoxLayout(score_group)

        self.score_label = QLabel("--")
        self.score_label.setObjectName("securityScore")
        score_layout.addWidget(self.score_label)

        self.grade_label = QLabel("--")
        self.grade_label.setObjectName("securityGrade")
        score_layout.addWidget(self.grade_label)

        self.score_bar = QProgressBar()
        self.score_bar.setRange(0, 100)
        score_layout.addWidget(self.score_bar)

        layout.addWidget(score_group)

        # Checks table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Security Check", "Status", "Value", "Recommendation"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Summary
        summary_group = QGroupBox("Summary")
        summary_layout = QHBoxLayout(summary_group)
        self.passed_label = QLabel("Passed: -")
        self.warn_label = QLabel("Warnings: -")
        self.failed_label = QLabel("Failed: -")
        for w in (self.passed_label, self.warn_label, self.failed_label):
            w.setObjectName("summaryLabel")
        summary_layout.addWidget(self.passed_label)
        summary_layout.addWidget(self.warn_label)
        summary_layout.addWidget(self.failed_label)
        summary_layout.addStretch()
        layout.addWidget(summary_group)

        # Button
        btn = QPushButton("Run Security Audit")
        btn.clicked.connect(self.run_audit)
        layout.addWidget(btn)

    def run_audit(self):
        self.score_label.setText("Scanning...")
        worker = TaskWorker(target=SecurityAudit.run_audit)
        worker.result.connect(self._on_result)
        worker.start()

    def _on_result(self, result):
        score = result.get("score", 0)
        grade = result.get("grade", "F")

        self.score_label.setText(f"{score}/100")
        self.grade_label.setText(f"Grade: {grade}")

        self.score_bar.setValue(score)
        color = "#2ecc71" if score >= 80 else "#f39c12" if score >= 60 else "#e74c3c"
        self.score_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; }}")

        self.table.setRowCount(0)
        for check in result.get("checks", []):
            r = self.table.rowCount()
            self.table.insertRow(r)

            status = check.get("status", "")
            status_color = QBrush(QColor("#2ecc71") if status == "PASS" else
                                 QColor("#f39c12") if status == "WARN" else
                                 QColor("#e74c3c"))

            self.table.setItem(r, 0, QTableWidgetItem(check.get("name", "")))
            status_item = QTableWidgetItem(status)
            status_item.setForeground(status_color)
            self.table.setItem(r, 1, status_item)
            self.table.setItem(r, 2, QTableWidgetItem(check.get("value", "")))
            self.table.setItem(r, 3, QTableWidgetItem(check.get("recommendation", "")))

        summary = result.get("summary", {})
        self.passed_label.setText(f"Passed: {summary.get('total_passed', 0)}")
        self.warn_label.setText(f"Warnings: {summary.get('total_warnings', 0)}")
        self.failed_label.setText(f"Failed: {summary.get('total_failed', 0)}")
