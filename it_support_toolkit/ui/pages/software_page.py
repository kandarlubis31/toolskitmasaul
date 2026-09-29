"""Software inventory page with auto-scan, search and export."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QMessageBox, QProgressBar, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from utils.background_tasks import TaskWorker
from core.software_inventory import SoftwareInventory
from core.reporting import ReportGenerator


class SoftwarePage(QWidget):
    def __init__(self):
        super().__init__()
        self.software_list = []
        self._scanned = False
        self._loading = False
        self.setup_ui()

    def setup_ui(self):
        # Scroll area for responsive table scrolling
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

        title = QLabel("Software Inventory")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or publisher...")
        self.search_input.textChanged.connect(self.filter_software)
        search_layout.addWidget(self.search_input)

        self.btn_scan = QPushButton("🔄  Scan Installed Software")
        self.btn_scan.clicked.connect(self.scan_software)
        search_layout.addWidget(self.btn_scan)
        layout.addLayout(search_layout)

        # Status bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)

        # Software table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Name", "Version", "Publisher", "Install Date"])
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

        # Bottom bar
        export_layout = QHBoxLayout()
        self.count_label = QLabel("Click 'Scan' or wait for auto-scan...")
        self.count_label.setObjectName("statusText")
        export_layout.addWidget(self.count_label)
        export_layout.addStretch()

        btn_csv = QPushButton("📥  Export CSV")
        btn_csv.clicked.connect(lambda: self.export("csv"))
        export_layout.addWidget(btn_csv)

        btn_html = QPushButton("🌐  Export HTML")
        btn_html.clicked.connect(lambda: self.export("html"))
        export_layout.addWidget(btn_html)
        layout.addLayout(export_layout)

        scroll.setWidget(inner)

    def showEvent(self, event):
        """Auto-scan on first view."""
        super().showEvent(event)
        if not self._scanned and not self._loading:
            self.scan_software()

    def scan_software(self):
        if self._loading:
            return
        self._loading = True
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.btn_scan.setText("⏳  Scanning...")
        self.btn_scan.setEnabled(False)
        self.count_label.setText("Reading installed software from registry...")

        w = TaskWorker(target=SoftwareInventory.get_installed_software)
        w.result.connect(self._on_scanned)
        w.error.connect(lambda e: self._on_scan_error(e))
        w.start()

    def _on_scanned(self, software):
        self._loading = False
        self._scanned = True
        self.progress.setVisible(False)
        self.btn_scan.setText("🔄  Rescan")
        self.btn_scan.setEnabled(True)
        self.software_list = software
        self.count_label.setText(
            f"📦  {len(software)} applications installed")
        self.populate_table(software)

    def _on_scan_error(self, err):
        self._loading = False
        self.progress.setVisible(False)
        self.btn_scan.setText("🔄  Retry Scan")
        self.btn_scan.setEnabled(True)
        self.count_label.setText(f"⚠️  Error: {err[:60]}")
        QMessageBox.warning(self, "Scan Error", str(err))

    def populate_table(self, data):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        for app in data:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(app.get("name", "")))
            self.table.setItem(r, 1, QTableWidgetItem(app.get("version", "")))
            self.table.setItem(r, 2, QTableWidgetItem(app.get("publisher", "")))
            self.table.setItem(r, 3, QTableWidgetItem(
                app.get("install_date", "")))
        self.table.setSortingEnabled(True)

    def filter_software(self, query: str = None):
        if query is None:
            query = self.search_input.text()
        if not query or not self.software_list:
            self.populate_table(self.software_list)
            self.count_label.setText(
                f"📦  {len(self.software_list)} applications installed")
            return
        filtered = SoftwareInventory.search_software(
            query, self.software_list)
        self.populate_table(filtered)
        self.count_label.setText(
            f"🔍  {len(filtered)} of {len(self.software_list)} — '{query}'")

    def export(self, fmt: str):
        if not self.software_list:
            QMessageBox.information(self, "No Data",
                                    "Scan software first or wait for auto-scan.")
            return
        data = {"software": self.software_list, "type": "software_inventory"}
        gen = ReportGenerator()
        path = gen.generate_report(data, fmt)
        QMessageBox.information(
            self, "Export Complete", f"Report saved to:\n{path}")
