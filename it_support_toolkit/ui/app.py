"""Main application window with modern sidebar navigation."""

import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QStatusBar, QScrollArea,
    QLabel, QFrame, QPushButton, QSplashScreen
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QColor, QFont

from ui.pages import (
    DashboardPage, HardwarePage, SoftwarePage, NetworkPage,
    RemotePage, RepairPage, CleanerPage, SecurityPage, LogsPage, SettingsPage
)
from utils.permissions import is_admin


def _create_splash():
    """Create a safe splash screen using only built-in Qt APIs."""
    try:
        pix = QPixmap(500, 260)
        pix.fill(QColor("#1e1e2e"))
        splash = QSplashScreen(pix)
        splash.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.SplashScreen
            | Qt.WindowType.FramelessWindowHint
        )
        splash.setFont(QFont("Segoe UI", 11))
        splash.showMessage(
            "\n\n\nIT Support Toolkit\nv2.0 Enterprise\n\nLoading...",
            Qt.AlignmentFlag.AlignCenter,
            QColor("#cdd6f4")
        )
        return splash
    except Exception:
        return None


class SidebarButton(QPushButton):
    """A sidebar navigation button."""

    def __init__(self, text: str, icon: str = "", parent=None):
        super().__init__(parent)
        self.setText(f"  {icon}  {text}")
        self.setMinimumHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setCheckable(True)


class MainWindow(QMainWindow):
    """Main application window with sidebar navigation."""

    PAGE_CLASSES = {
        "dashboard": DashboardPage,
        "hardware": HardwarePage,
        "software": SoftwarePage,
        "network": NetworkPage,
        "remote": RemotePage,
        "repair": RepairPage,
        "cleaner": CleanerPage,
        "security": SecurityPage,
        "logs": LogsPage,
        "settings": SettingsPage,
    }

    def __init__(self, splash=None):
        super().__init__()
        self._splash = splash
        self.setWindowTitle("IT Support Toolkit")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        self.setObjectName("mainWindow")
        self.load_stylesheet()
        self.setup_ui()

    def load_stylesheet(self):
        """Load the QSS stylesheet."""
        style_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "ui", "styles.qss"
        )
        if os.path.exists(style_path):
            try:
                with open(style_path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
            except Exception:
                pass

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # App title in sidebar
        title_frame = QFrame()
        title_frame.setObjectName("sidebarTitle")
        title_layout = QVBoxLayout(title_frame)
        app_title = QLabel("IT Support Toolkit")
        app_title.setObjectName("sidebarAppTitle")
        version = QLabel("v2.0 Enterprise")
        version.setObjectName("sidebarVersion")
        title_layout.addWidget(app_title)
        title_layout.addWidget(version)
        sidebar_layout.addWidget(title_frame)

        # Navigation buttons
        self.nav_buttons = []
        nav_items = [
            ("dashboard", "🏠", "Dashboard"),
            ("hardware", "🖥", "Hardware"),
            ("software", "📦", "Software"),
            ("network", "🌐", "Network"),
            ("remote", "🖥", "Remote"),
            ("repair", "🔧", "Repair Tools"),
            ("cleaner", "🧹", "Cleaner"),
            ("security", "🛡", "Security Audit"),
            ("logs", "📋", "Event Logs"),
            ("settings", "⚙", "Settings"),
        ]

        self.nav_group = QFrame()
        self.nav_group.setObjectName("navGroup")
        nav_group_layout = QVBoxLayout(self.nav_group)
        nav_group_layout.setContentsMargins(4, 8, 4, 8)
        nav_group_layout.setSpacing(2)

        self.nav_map = {}
        for page_id, icon, text in nav_items:
            btn = SidebarButton(text, icon)
            btn.clicked.connect(lambda checked, pid=page_id: self.navigate_to(pid))
            nav_group_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            self.nav_map[page_id] = btn

        nav_group_layout.addStretch()
        sidebar_layout.addWidget(self.nav_group)

        # Admin badge
        admin_badge = QLabel("🛡️ Admin" if is_admin() else "⚠️ Limited")
        admin_badge.setObjectName("adminBadge" if is_admin() else "limitedBadge")
        admin_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        admin_badge.setFixedHeight(36)
        sidebar_layout.addWidget(admin_badge)

        main_layout.addWidget(sidebar)

        # Content area
        content = QFrame()
        content.setObjectName("contentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self.stack.setObjectName("pageStack")

        # Lazy-load pages: only create dashboard initially
        self.pages = {}
        self._create_page("dashboard")

        # Wrap in scroll area so tall pages can scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.stack)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content_layout.addWidget(scroll)
        main_layout.addWidget(content)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        self.admin_status = QLabel("Administrator" if is_admin() else "Limited Mode")
        self.admin_status.setObjectName("statusAdmin")
        self.status_bar.addPermanentWidget(self.admin_status)

        # Navigate to dashboard (refresh deferred via QTimer in navigate_to)
        self.navigate_to("dashboard")

    def closeEvent(self, event):
        """Accept close event – daemon threads exit automatically."""
        event.accept()

    def _create_page(self, page_id: str):
        """Lazily create a page instance on first navigation."""
        if page_id in self.pages:
            return self.pages[page_id]
        cls = self.PAGE_CLASSES.get(page_id)
        if cls is None:
            return None
        page = cls()
        self.pages[page_id] = page
        self.stack.addWidget(page)
        return page

    def navigate_to(self, page_id: str):
        """Navigate to a specific page (lazy-loads on first access)."""
        # Update button states
        for pid, btn in self.nav_map.items():
            btn.setChecked(pid == page_id)

        # Lazy-create page if needed
        page = self._create_page(page_id)
        if page:
            self.stack.setCurrentWidget(page)
            nav_text = self.nav_map[page_id].text().strip()
            self.status_label.setText(f"Active: {nav_text}")

            # Defer dashboard refresh to event loop — prevents segfault
            if page_id == "dashboard":
                QTimer.singleShot(200, page.refresh)


def run_app():
    """Launch the IT Support Toolkit application."""
    app = QApplication(sys.argv)
    app.setApplicationName("IT Support Toolkit")
    app.setOrganizationName("ITSToolkit")

    # Set app icon
    icon_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "assets", "icon.ico"
    )
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Show splash screen immediately
    splash = _create_splash()
    if splash:
        splash.show()
        app.processEvents()

    window = MainWindow(splash)
    window.show()

    if splash:
        splash.finish(window)

    sys.exit(app.exec())
