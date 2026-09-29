"""Settings page with live theme switching and configuration."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QCheckBox, QSpinBox, QFormLayout, QComboBox,
    QMessageBox, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from utils.config import get_settings, save_settings
from utils.permissions import is_admin, FEATURES_REQUIRING_ADMIN


class SettingsPage(QWidget):
    """Settings page that emits theme_changed signal for live theme switching."""

    theme_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._loading = True
        self.setup_ui()
        self.load_settings()
        self._loading = False
        # Connect after load to avoid triggering on initial load
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)

    def setup_ui(self):
        # Scroll area so settings fits on all screen sizes
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(20, 12, 20, 16)
        layout.setSpacing(10)

        title = QLabel("Settings")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # Theme
        theme_group = QGroupBox("Appearance")
        theme_layout = QFormLayout(theme_group)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setToolTip("Changes apply immediately")
        theme_layout.addRow("Theme:", self.theme_combo)

        # Preview note
        preview_note = QLabel("✨ Theme changes apply instantly — no restart needed")
        preview_note.setStyleSheet("font-size: 10px; color: #89b4fa; padding: 2px 0;")
        theme_layout.addRow("", preview_note)
        layout.addWidget(theme_group)

        # General
        general_group = QGroupBox("General")
        general_layout = QFormLayout(general_group)
        self.log_count = QSpinBox()
        self.log_count.setRange(10, 500)
        self.log_count.setValue(50)
        general_layout.addRow("Default Log Count:", self.log_count)

        self.log_type = QComboBox()
        self.log_type.addItems(["System", "Application", "Security"])
        general_layout.addRow("Default Log Type:", self.log_type)

        self.monitor_interval = QSpinBox()
        self.monitor_interval.setRange(1, 60)
        self.monitor_interval.setValue(2)
        self.monitor_interval.setSuffix(" sec")
        general_layout.addRow("Monitor Interval:", self.monitor_interval)

        self.clean_simulation = QCheckBox("Simulation mode for cleaner")
        self.clean_simulation.setChecked(True)
        general_layout.addRow("", self.clean_simulation)

        layout.addWidget(general_group)

        # Admin info
        admin_group = QGroupBox("Administrator Privileges")
        admin_layout = QVBoxLayout(admin_group)
        status = "Running as ADMIN" if is_admin() else "Running with LIMITED privileges"
        status_label = QLabel(f"Status: {status}")
        status_label.setObjectName("adminBadge")
        admin_layout.addWidget(status_label)

        features_label = QLabel("Features requiring admin rights:")
        admin_layout.addWidget(features_label)
        for feature in FEATURES_REQUIRING_ADMIN:
            lbl = QLabel(f"  - {feature}")
            lbl.setStyleSheet("font-size: 11px; color: #9ca0b0;")
            admin_layout.addWidget(lbl)

        layout.addWidget(admin_group)

        # Save — now also applies theme
        btn_save = QPushButton("Save Settings")
        btn_save.clicked.connect(self.save_settings)
        layout.addWidget(btn_save)

        # About
        about_group = QGroupBox("About")
        about_layout = QVBoxLayout(about_group)
        about_layout.addWidget(QLabel("IT Support Toolkit v2.0"))
        about_layout.addWidget(QLabel("Enterprise-grade Windows diagnostics platform"))
        about_layout.addWidget(QLabel("Python 3 + PyQt6 + psutil + pywin32"))
        layout.addWidget(about_group)
        layout.addStretch()

        scroll.setWidget(inner)

    def _on_theme_changed(self, theme_name: str):
        """Apply theme immediately when combo changes."""
        if self._loading:
            return
        theme = theme_name.lower()
        self.theme_changed.emit(theme)

    def load_settings(self):
        settings = get_settings()
        self.theme_combo.setCurrentText(settings.get("theme", "Dark").capitalize())
        self.log_count.setValue(settings.get("default_log_count", 50))
        self.log_type.setCurrentText(settings.get("log_type", "System"))
        self.monitor_interval.setValue(settings.get("monitor_interval", 2))
        self.clean_simulation.setChecked(settings.get("clean_simulation", True))

    def save_settings(self):
        settings = {
            "theme": self.theme_combo.currentText().lower(),
            "default_log_count": self.log_count.value(),
            "log_type": self.log_type.currentText(),
            "monitor_interval": self.monitor_interval.value(),
            "clean_simulation": self.clean_simulation.isChecked(),
        }
        if save_settings(settings):
            QMessageBox.information(self, "Settings Saved",
                "Settings have been saved successfully.")
        else:
            QMessageBox.critical(self, "Error", "Failed to save settings")
