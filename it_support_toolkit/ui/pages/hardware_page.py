"""Hardware inventory page."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QGridLayout,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt
from utils.background_tasks import TaskWorker
from core.hardware_info import HardwareInfo


class SpecRow(QFrame):
    def __init__(self, label: str, value: str, parent=None):
        super().__init__(parent)
        self.setObjectName("specRow")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        lbl = QLabel(label)
        lbl.setObjectName("specLabel")
        val = QLabel(value)
        val.setObjectName("specValue")
        layout.addWidget(lbl)
        layout.addStretch()
        layout.addWidget(val)


class HardwarePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        # Scroll area for responsive resizing
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

        title = QLabel("Hardware Inventory")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # CPU
        cpu_group = QGroupBox("Processor")
        cpu_layout = QVBoxLayout(cpu_group)
        self.cpu_name = QLabel("Loading...")
        self.cpu_name.setObjectName("hardwareValue")
        cpu_layout.addWidget(self.cpu_name)
        cpu_specs = QHBoxLayout()
        self.cpu_cores = QLabel("Cores: -")
        self.cpu_threads = QLabel("Threads: -")
        self.cpu_usage = QLabel("Usage: -")
        for w in (self.cpu_cores, self.cpu_threads, self.cpu_usage):
            w.setObjectName("hardwareSpec")
        cpu_specs.addWidget(self.cpu_cores)
        cpu_specs.addWidget(self.cpu_threads)
        cpu_specs.addWidget(self.cpu_usage)
        cpu_specs.addStretch()
        cpu_layout.addLayout(cpu_specs)
        layout.addWidget(cpu_group)

        # RAM
        ram_group = QGroupBox("Memory")
        ram_layout = QVBoxLayout(ram_group)
        self.ram_total = QLabel("Total: -")
        self.ram_used = QLabel("Used: -")
        self.ram_speed = QLabel("Speed: -")
        self.ram_slots = QLabel("Slots Used: -")
        for w in (self.ram_total, self.ram_used, self.ram_speed, self.ram_slots):
            w.setObjectName("hardwareValue")
        for w in (self.ram_total, self.ram_used, self.ram_speed, self.ram_slots):
            ram_layout.addWidget(w)
        layout.addWidget(ram_group)

        # Storage
        storage_group = QGroupBox("Storage")
        storage_layout = QVBoxLayout(storage_group)
        self.storage_table = QTableWidget()
        self.storage_table.setColumnCount(6)
        self.storage_table.setHorizontalHeaderLabels(["Drive", "Type", "Model", "Total", "Free", "Usage"])
        self.storage_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.storage_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.storage_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        storage_layout.addWidget(self.storage_table)
        layout.addWidget(storage_group)

        # GPU
        gpu_group = QGroupBox("Graphics")
        gpu_layout = QVBoxLayout(gpu_group)
        self.gpu_table = QTableWidget()
        self.gpu_table.setColumnCount(2)
        self.gpu_table.setHorizontalHeaderLabels(["GPU Name", "VRAM"])
        self.gpu_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.gpu_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.gpu_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        gpu_layout.addWidget(self.gpu_table)
        layout.addWidget(gpu_group)

        # Motherboard
        mb_group = QGroupBox("Motherboard")
        mb_layout = QVBoxLayout(mb_group)
        self.mb_manu = QLabel("Manufacturer: -")
        self.mb_model = QLabel("Model: -")
        for w in (self.mb_manu, self.mb_model):
            w.setObjectName("hardwareValue")
        mb_layout.addWidget(self.mb_manu)
        mb_layout.addWidget(self.mb_model)
        layout.addWidget(mb_group)

        # Refresh
        btn = QPushButton("Refresh Hardware Info")
        btn.clicked.connect(self.refresh)
        layout.addWidget(btn)
        layout.addStretch()

        scroll.setWidget(inner)

    def refresh(self):
        self.worker = TaskWorker(target=HardwareInfo.get_all)
        self.worker.result.connect(self._update)
        self.worker.start()

    def _update(self, data):
        if not data:
            return

        cpu = data.get("cpu", {})
        self.cpu_name.setText(f"Name: {cpu.get('name', 'N/A')}")
        self.cpu_cores.setText(f"Cores: {cpu.get('cores', '-')}")
        self.cpu_threads.setText(f"Threads: {cpu.get('threads', '-')}")
        self.cpu_usage.setText(f"Usage: {cpu.get('usage', 0)}%")

        ram = data.get("ram", {})
        self.ram_total.setText(f"Total: {ram.get('total_gb', 0)} GB")
        self.ram_used.setText(f"Used: {ram.get('used_gb', 0)} GB")
        self.ram_speed.setText(f"Speed: {ram.get('speed_mhz', '-')} MHz")
        self.ram_slots.setText(f"Slots Used: {ram.get('slots_used', '-')}")

        storage = data.get("storage", [])
        self.storage_table.setRowCount(0)
        for d in storage:
            r = self.storage_table.rowCount()
            self.storage_table.insertRow(r)
            self.storage_table.setItem(r, 0, QTableWidgetItem(d.get("drive", "")))
            self.storage_table.setItem(r, 1, QTableWidgetItem(d.get("media_type", "HDD")))
            self.storage_table.setItem(r, 2, QTableWidgetItem(d.get("model", "")))
            self.storage_table.setItem(r, 3, QTableWidgetItem(f"{d.get('total_gb', 0)} GB"))
            self.storage_table.setItem(r, 4, QTableWidgetItem(f"{d.get('free_gb', 0)} GB"))
            self.storage_table.setItem(r, 5, QTableWidgetItem(f"{d.get('percent', 0)}%"))

        gpu = data.get("gpu", [])
        self.gpu_table.setRowCount(0)
        for g in gpu:
            r = self.gpu_table.rowCount()
            self.gpu_table.insertRow(r)
            self.gpu_table.setItem(r, 0, QTableWidgetItem(g.get("Name", "")))
            vram = g.get("VRAM_GB", 0)
            self.gpu_table.setItem(r, 1, QTableWidgetItem(f"{vram} GB" if vram else "N/A"))

        mb = data.get("motherboard", {})
        self.mb_manu.setText(f"Manufacturer: {mb.get('manufacturer', 'N/A')}")
        self.mb_model.setText(f"Model: {mb.get('model', 'N/A')}")
