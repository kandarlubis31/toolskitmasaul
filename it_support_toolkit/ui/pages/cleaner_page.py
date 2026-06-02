"""Enhanced cleaner page with space estimation and history."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
    QMessageBox, QGroupBox, QProgressBar, QTextEdit
)
from PyQt6.QtCore import Qt
from utils.background_tasks import TaskWorker
from core.cleaner import SystemCleaner


class CleanerPage(QWidget):
    def __init__(self):
        super().__init__()
        self.cleaner = SystemCleaner()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("System Cleaner")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # Mode toggle
        mode_layout = QHBoxLayout()
        self.safe_mode = QCheckBox("Safe Mode (recommended) - only safe items")
        self.safe_mode.setChecked(True)
        mode_layout.addWidget(self.safe_mode)
        layout.addLayout(mode_layout)

        # Cache table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["", "Category", "Size", "Safe"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 40)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        # Progress
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_scan = QPushButton("Scan Now")
        btn_scan.clicked.connect(self.scan)
        btn_layout.addWidget(btn_scan)

        btn_clean = QPushButton("Clean Selected")
        btn_clean.clicked.connect(self.clean_selected)
        btn_clean.setObjectName("dangerButton")
        btn_layout.addWidget(btn_clean)

        btn_view_history = QPushButton("View History")
        btn_view_history.clicked.connect(self.view_history)
        btn_layout.addWidget(btn_view_history)

        layout.addLayout(btn_layout)

        # Output
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setObjectName("outputArea")
        self.output.setMaximumHeight(150)
        layout.addWidget(self.output)

    def scan(self):
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.output.append("Scanning system...")
        worker = TaskWorker(target=SystemCleaner.get_all_sizes)
        worker.result.connect(self._on_scan)
        worker.start()

    def _on_scan(self, items):
        self.progress.setVisible(False)
        self.table.setRowCount(0)
        for item in items:
            r = self.table.rowCount()
            self.table.insertRow(r)
            chk = QTableWidgetItem()
            chk.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk.setCheckState(Qt.CheckState.Checked if item.get("safe") else Qt.CheckState.Unchecked)
            self.table.setItem(r, 0, chk)
            self.table.setItem(r, 1, QTableWidgetItem(item.get("name", "")))
            self.table.setItem(r, 2, QTableWidgetItem(item.get("size_str", "")))
            self.table.setItem(r, 3, QTableWidgetItem("Yes" if item.get("safe") else "No"))
        self.output.append(f"Found {len(items)} categories to clean")

    def clean_selected(self):
        safe_only = self.safe_mode.isChecked()
        targets = []
        for r in range(self.table.rowCount()):
            chk = self.table.item(r, 0)
            name_item = self.table.item(r, 1)
            safe_item = self.table.item(r, 3)
            if chk and chk.checkState() == Qt.CheckState.Checked:
                is_safe = safe_item and safe_item.text() == "Yes"
                if not safe_only or is_safe:
                    targets.append(name_item.text() if name_item else "")

        if not targets:
            QMessageBox.information(self, "Nothing Selected", "Select items to clean")
            return

        reply = QMessageBox.question(self, "Confirm Clean",
            f"Clean {len(targets)} items?\n\n" + "\n".join(f"- {t}" for t in targets),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.output.append("Cleaning in background...")

        self.worker = TaskWorker(target=self._run_cleanup, args=(targets,))
        self.worker.result.connect(self._on_clean_done)
        self.worker.error.connect(lambda e: self._on_clean_error(e))
        self.worker.start()

    def _run_cleanup(self, targets):
        results = []
        for name in targets:
            r = SystemCleaner.clean_item(name, simulate=False)
            results.append({**r, "name": name})
        self.cleaner.save_cleanup(results)
        return results

    def _on_clean_done(self, results):
        self.progress.setVisible(False)
        for r in results:
            self.output.append(f"  {r.get('name')}: {'OK' if r.get('success') else 'FAIL'} - {r.get('message', r.get('error', ''))}")
        QMessageBox.information(self, "Done", f"Cleaned {sum(1 for r in results if r.get('success'))} items")
        self.scan()

    def _on_clean_error(self, error):
        self.progress.setVisible(False)
        self.output.append(f"[ERROR] {error}")

    def view_history(self):
        history = self.cleaner.get_history()
        if not history:
            QMessageBox.information(self, "History", "No cleanup history yet")
            return
        lines = []
        for entry in history[-10:]:
            ts = entry.get("timestamp", "?")[:19]
            count = len(entry.get("items_cleaned", []))
            lines.append(f"{ts} - {count} items cleaned")
        QMessageBox.information(self, "Cleanup History (last 10)", "\n".join(lines))
