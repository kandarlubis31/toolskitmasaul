"""Main application window with modern sidebar navigation."""

import os
import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QStatusBar, QSystemTrayIcon, QMenu,
    QLabel, QFrame, QPushButton, QSplashScreen, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QTimer, QRect, QPropertyAnimation, QEasingCurve,
    QParallelAnimationGroup
)
from PyQt6.QtGui import (
    QIcon, QPixmap, QColor, QFont, QPainter, QBrush,
    QPainterPath, QLinearGradient, QAction, QPen
)

from ui.pages import (
    DashboardPage, HardwarePage, SoftwarePage, NetworkPage,
    RemotePage, RepairPage, CleanerPage, SecurityPage, LogsPage, SettingsPage
)
from utils.config import get_settings, save_settings
from utils.permissions import is_admin


# ── Constants ──

SIDEBAR_EXPANDED = 195
SIDEBAR_COLLAPSED = 50
SPLASH_W = 520
SPLASH_H = 340


def _get_project_root():
    """Absolute path to the project root."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── Logo Drawing ─────────────────────────────────────

def _create_logo_pixmap(size: int = 48) -> QPixmap:
    """Draw a professional shield-with-gear logo using QPainter."""
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    cx, cy = size / 2.0, size / 2.0
    outer = size * 0.46
    inner = size * 0.28

    shield = QPainterPath()
    shield.moveTo(cx, size * 0.04)
    shield.cubicTo(cx - outer * 0.8, size * 0.04,
                   cx - outer, size * 0.25, cx - outer, size * 0.45)
    shield.lineTo(cx - outer, size * 0.60)
    shield.quadTo(cx - outer * 0.7, size * 0.82, cx, size * 0.96)
    shield.quadTo(cx + outer * 0.7, size * 0.82, cx + outer, size * 0.60)
    shield.lineTo(cx + outer, size * 0.45)
    shield.cubicTo(cx + outer, size * 0.25,
                   cx + outer * 0.8, size * 0.04, cx, size * 0.04)
    shield.closeSubpath()

    grad = QLinearGradient(cx, 0, cx, size)
    grad.setColorAt(0.0, QColor("#cba6f7"))
    grad.setColorAt(0.5, QColor("#f38ba8"))
    grad.setColorAt(1.0, QColor("#f38ba8"))
    p.setBrush(QBrush(grad))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawPath(shield)

    p.setBrush(QBrush(QColor("#1e1e2e")))
    teeth = 8
    for i in range(teeth):
        angle = (i / teeth) * 2 * math.pi - math.pi / 2
        a1 = angle - math.pi / (teeth * 2.2)
        a2 = angle + math.pi / (teeth * 2.2)
        path = QPainterPath()
        path.moveTo(cx, cy)
        path.arcTo(cx - inner * 1.15, cy - inner * 1.15,
                   inner * 2.3, inner * 2.3,
                   -math.degrees(a1), -math.degrees(a2 - a1))
        path.closeSubpath()
        p.drawPath(path)

    p.setBrush(QBrush(QColor("#1e1e2e")))
    p.drawEllipse(QRect(int(cx - inner * 0.85), int(cy - inner * 0.85),
                         int(inner * 1.7), int(inner * 1.7)))
    p.setBrush(QBrush(QColor("#cdd6f4")))
    p.drawEllipse(QRect(int(cx - inner * 0.22), int(cy - inner * 0.22),
                         int(inner * 0.44), int(inner * 0.44)))
    p.end()
    return pix


# ── Professional Splash Screen ────────────────────────

class ProfessionalSplash(QSplashScreen):
    """A polished splash screen with gradient background, logo, and loading status."""

    def __init__(self):
        pix = QPixmap(SPLASH_W, SPLASH_H)
        pix.fill(Qt.GlobalColor.transparent)
        super().__init__(pix)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.SplashScreen
            | Qt.WindowType.FramelessWindowHint
        )
        self._status = "Loading..."
        self._progress = 0
        self._draw_splash()

    def _draw_splash(self):
        """Paint the splash screen with gradient, logo, and status."""
        pix = QPixmap(SPLASH_W, SPLASH_H)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background gradient
        bg_grad = QLinearGradient(0, 0, 0, SPLASH_H)
        bg_grad.setColorAt(0.0, QColor("#11111b"))
        bg_grad.setColorAt(0.55, QColor("#1e1e2e"))
        bg_grad.setColorAt(1.0, QColor("#181825"))
        p.setBrush(QBrush(bg_grad))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, SPLASH_W, SPLASH_H, 16, 16)

        # Subtle top accent line
        accent_grad = QLinearGradient(0, 0, SPLASH_W, 0)
        accent_grad.setColorAt(0.0, QColor("#cba6f7"))
        accent_grad.setColorAt(0.5, QColor("#f38ba8"))
        accent_grad.setColorAt(1.0, QColor("#cba6f7"))
        p.setBrush(QBrush(accent_grad))
        p.drawRect(0, 0, SPLASH_W, 3)

        # Logo (center, large)
        logo_size = 100
        logo_pix = _create_logo_pixmap(logo_size)
        logo_x = (SPLASH_W - logo_size) // 2
        logo_y = 48
        p.drawPixmap(logo_x, logo_y, logo_pix)

        # App title
        p.setPen(QColor("#cdd6f4"))
        title_font = QFont("Segoe UI", 22, QFont.Weight.Bold)
        p.setFont(title_font)
        p.drawText(QRect(0, logo_y + logo_size + 14, SPLASH_W, 32),
                   Qt.AlignmentFlag.AlignCenter, "IT Support Toolkit")

        # Version subtitle
        p.setPen(QColor("#89b4fa"))
        ver_font = QFont("Segoe UI", 11)
        p.setFont(ver_font)
        p.drawText(QRect(0, logo_y + logo_size + 44, SPLASH_W, 22),
                   Qt.AlignmentFlag.AlignCenter, "v2.0  ·  Enterprise Diagnostics")

        # Divider line
        p.setPen(QPen(QColor("#313244"), 1))
        div_y = SPLASH_H - 68
        p.drawLine(40, div_y, SPLASH_W - 40, div_y)

        # Loading status text
        p.setPen(QColor("#a6adc8"))
        status_font = QFont("Segoe UI", 10)
        p.setFont(status_font)
        p.drawText(QRect(30, div_y + 10, SPLASH_W - 60, 22),
                   Qt.AlignmentFlag.AlignLeft, self._status)

        # Progress bar
        bar_x, bar_y = 30, SPLASH_H - 30
        bar_w, bar_h = SPLASH_W - 60, 5
        # Background
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor("#313244")))
        p.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 3, 3)
        # Fill
        if self._progress > 0:
            bar_grad = QLinearGradient(bar_x, 0, bar_x + bar_w, 0)
            bar_grad.setColorAt(0.0, QColor("#cba6f7"))
            bar_grad.setColorAt(1.0, QColor("#f38ba8"))
            p.setBrush(QBrush(bar_grad))
            fill_w = int(bar_w * self._progress / 100)
            p.drawRoundedRect(bar_x, bar_y, fill_w, bar_h, 3, 3)

        p.end()
        self.setPixmap(pix)

    def show_status(self, message: str, progress: int = -1):
        """Update splash status text and optional progress (0-100)."""
        self._status = message
        if progress >= 0:
            self._progress = progress
        self._draw_splash()
        QApplication.instance().processEvents()


# ── Widgets ───────────────────────────────────────────

class LogoLabel(QLabel):
    """Displays the app logo with fallback."""

    def __init__(self, size: int = 48, parent=None):
        super().__init__(parent)
        self.setFixedSize(size + 4, size + 4)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        try:
            pix = _create_logo_pixmap(size)
            self.setPixmap(pix)
        except Exception:
            self.setText("🛠")
            self.setStyleSheet("font-size: 32px;")


class SidebarButton(QPushButton):
    """Sidebar nav button — supports collapsed icon-only mode."""

    def __init__(self, page_id: str, text: str, icon: str = "", parent=None):
        super().__init__(parent)
        self.page_id = page_id
        self.full_text = text
        self.icon_emoji = icon
        self._collapsed = False
        self._show_full()
        self.setMinimumHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setCheckable(True)

    def _show_full(self):
        self.setText(f"  {self.icon_emoji}  {self.full_text}")
        self.setToolTip("")

    def _show_collapsed(self):
        self.setText(f"  {self.icon_emoji}")
        self.setToolTip(self.full_text)

    def set_collapsed(self, collapsed: bool):
        if collapsed != self._collapsed:
            self._collapsed = collapsed
            if collapsed:
                self._show_collapsed()
            else:
                self._show_full()


# ── Main Window ──────────────────────────────────────

class MainWindow(QMainWindow):
    """Main app window — collapsible sidebar, system tray, dynamic theme."""

    PAGE_CLASSES = {
        "dashboard": DashboardPage,    "hardware": HardwarePage,
        "software": SoftwarePage,      "network": NetworkPage,
        "remote": RemotePage,          "repair": RepairPage,
        "cleaner": CleanerPage,        "security": SecurityPage,
        "logs": LogsPage,              "settings": SettingsPage,
    }

    def __init__(self, splash=None):
        super().__init__()
        self._splash = splash
        self._sidebar_collapsed = False
        self._current_theme = "dark"

        self.setWindowTitle("IT Support Toolkit")
        self.setMinimumSize(900, 620)
        self.resize(1300, 820)
        self.setObjectName("mainWindow")

        self._load_theme()
        self.setup_ui()
        self.setup_tray()

        if self._splash:
            self._splash.show_status("Ready", 100)

    # ── Theme ──────────────────────────────────────────

    def _load_theme(self):
        try:
            settings = get_settings()
            self._current_theme = settings.get("theme", "dark")
        except Exception:
            self._current_theme = "dark"
        self._apply_stylesheet()

    def _apply_stylesheet(self):
        root = _get_project_root()
        path = os.path.join(root, "ui",
            "styles_light.qss" if self._current_theme == "light" else "styles.qss")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
            except Exception:
                pass

    def apply_theme(self, theme: str):
        self._current_theme = theme
        self._apply_stylesheet()
        try:
            settings = get_settings()
            settings["theme"] = theme
            save_settings(settings)
        except Exception:
            pass

    # ── System Tray ───────────────────────────────────

    def setup_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self._tray = None
            return
        icon_path = os.path.join(_get_project_root(), "assets", "icon.ico")
        icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
        self._tray = QSystemTrayIcon(icon, self)
        self._tray.setToolTip("IT Support Toolkit")
        menu = QMenu()
        show_action = QAction("Show", self)
        show_action.triggered.connect(self._show_from_tray)
        menu.addAction(show_action)
        menu.addSeparator()
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self._quit_app)
        menu.addAction(quit_action)
        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_from_tray()

    def _show_from_tray(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _quit_app(self):
        if self._tray:
            self._tray.hide()
        QApplication.instance().quit()

    def closeEvent(self, event):
        if self._tray and self._tray.isVisible():
            event.ignore()
            self.hide()
            self._tray.showMessage(
                "IT Support Toolkit",
                "App minimized to tray. Double-click to restore.",
                QSystemTrayIcon.MessageIcon.Information, 2000)
        else:
            event.accept()

    # ── UI Setup ──────────────────────────────────────

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ───────────────────────────────────
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setMinimumWidth(SIDEBAR_EXPANDED)
        self.sidebar.setMaximumWidth(SIDEBAR_EXPANDED)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Title + logo
        self.sidebar_title_frame = QFrame()
        self.sidebar_title_frame.setObjectName("sidebarTitle")
        stf_layout = QHBoxLayout(self.sidebar_title_frame)
        stf_layout.setContentsMargins(8, 8, 8, 6)
        stf_layout.setSpacing(8)
        self.logo_label = LogoLabel(36)
        stf_layout.addWidget(self.logo_label)
        self.sidebar_text_container = QWidget()
        stc_layout = QVBoxLayout(self.sidebar_text_container)
        stc_layout.setContentsMargins(0, 0, 0, 0)
        stc_layout.setSpacing(0)
        self.app_title_label = QLabel("IT Support\nToolkit")
        self.app_title_label.setObjectName("sidebarAppTitle")
        self.version_label = QLabel("v2.0 Enterprise")
        self.version_label.setObjectName("sidebarVersion")
        stc_layout.addWidget(self.app_title_label)
        stc_layout.addWidget(self.version_label)
        stf_layout.addWidget(self.sidebar_text_container)
        stf_layout.addStretch()
        sidebar_layout.addWidget(self.sidebar_title_frame)

        # Nav buttons
        nav_items = [
            ("dashboard", "🏠", "Dashboard"),       ("hardware", "🖥", "Hardware"),
            ("software", "📦", "Software"),         ("network", "🌐", "Network"),
            ("remote", "🖥", "Remote"),             ("repair", "🔧", "Repair Tools"),
            ("cleaner", "🧹", "Cleaner"),           ("security", "🛡", "Security Audit"),
            ("logs", "📋", "Event Logs"),           ("settings", "⚙", "Settings"),
        ]
        self.nav_group = QFrame()
        self.nav_group.setObjectName("navGroup")
        nav_group_layout = QVBoxLayout(self.nav_group)
        nav_group_layout.setContentsMargins(4, 4, 4, 4)
        nav_group_layout.setSpacing(1)

        self.nav_map = {}
        self.nav_buttons = []
        for page_id, icon, text in nav_items:
            btn = SidebarButton(page_id, text, icon)
            btn.clicked.connect(lambda checked, pid=page_id: self.navigate_to(pid))
            nav_group_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            self.nav_map[page_id] = btn
        nav_group_layout.addStretch()
        sidebar_layout.addWidget(self.nav_group)

        # Admin badge
        admin_badge = QLabel(" 🛡️ Admin " if is_admin() else " ⚠️ Limited ")
        admin_badge.setObjectName("adminBadge" if is_admin() else "limitedBadge")
        admin_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        admin_badge.setFixedHeight(28)
        sidebar_layout.addWidget(admin_badge)
        main_layout.addWidget(self.sidebar)

        # ── Content Area (responsive, no global scroll) ──
        content = QFrame()
        content.setObjectName("contentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Header bar with hamburger
        header_bar = QFrame()
        header_bar.setObjectName("contentHeader")
        header_bar.setFixedHeight(40)
        hb_layout = QHBoxLayout(header_bar)
        hb_layout.setContentsMargins(4, 4, 8, 4)
        hb_layout.setSpacing(8)
        self.hamburger_btn = QPushButton("☰")
        self.hamburger_btn.setObjectName("hamburgerBtn")
        self.hamburger_btn.setFixedSize(32, 32)
        self.hamburger_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hamburger_btn.setToolTip("Toggle Sidebar (Ctrl+B)")
        self.hamburger_btn.clicked.connect(self.toggle_sidebar)
        hb_layout.addWidget(self.hamburger_btn)
        self.breadcrumb = QLabel("Dashboard")
        self.breadcrumb.setObjectName("breadcrumb")
        hb_layout.addWidget(self.breadcrumb)
        hb_layout.addStretch()
        content_layout.addWidget(header_bar)

        # Page stack — fills remaining space, no scroll wrapper
        self.stack = QStackedWidget()
        self.stack.setObjectName("pageStack")
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.pages = {}
        self._create_page("dashboard")
        content_layout.addWidget(self.stack, 1)

        main_layout.addWidget(content, 1)

        # ── Status Bar ────────────────────────────────
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        self.admin_status = QLabel("Administrator" if is_admin() else "Limited Mode")
        self.admin_status.setObjectName("statusAdmin")
        self.status_bar.addPermanentWidget(self.admin_status)

        self.navigate_to("dashboard")

    # ── Sidebar Toggle ────────────────────────────────

    def toggle_sidebar(self):
        self._sidebar_collapsed = not self._sidebar_collapsed
        target = SIDEBAR_COLLAPSED if self._sidebar_collapsed else SIDEBAR_EXPANDED
        for btn in self.nav_buttons:
            btn.set_collapsed(self._sidebar_collapsed)
        self.sidebar_text_container.setVisible(not self._sidebar_collapsed)
        self.app_title_label.setVisible(not self._sidebar_collapsed)
        self.version_label.setVisible(not self._sidebar_collapsed)
        try:
            group = QParallelAnimationGroup()
            for prop in (b"minimumWidth", b"maximumWidth"):
                anim = QPropertyAnimation(self.sidebar, prop)
                anim.setDuration(200)
                anim.setStartValue(self.sidebar.width())
                anim.setEndValue(target)
                anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
                group.addAnimation(anim)
            group.start()
        except Exception:
            self.sidebar.setMinimumWidth(target)
            self.sidebar.setMaximumWidth(target)

    # ── Page Navigation ───────────────────────────────

    def _create_page(self, page_id: str):
        if page_id in self.pages:
            return self.pages[page_id]
        cls = self.PAGE_CLASSES.get(page_id)
        if cls is None:
            return None
        page = cls()
        if page_id == "settings":
            page.theme_changed.connect(self.apply_theme)
        self.pages[page_id] = page
        self.stack.addWidget(page)
        return page

    def navigate_to(self, page_id: str):
        for pid, btn in self.nav_map.items():
            btn.setChecked(pid == page_id)
        page = self._create_page(page_id)
        if page:
            self.stack.setCurrentWidget(page)
            nav_text = self.nav_map[page_id].full_text
            self.status_label.setText(f"Active: {nav_text}")
            self.breadcrumb.setText(nav_text)
            if page_id == "dashboard":
                QTimer.singleShot(200, page.refresh)


# ── App Entry Point ──────────────────────────────────

def run_app():
    """Launch the IT Support Toolkit application."""
    app = QApplication(sys.argv)
    app.setApplicationName("IT Support Toolkit")
    app.setOrganizationName("ITSToolkit")
    app.setQuitOnLastWindowClosed(False)

    icon_path = os.path.join(_get_project_root(), "assets", "icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # ── Professional Splash ──────────────────────────
    splash = None
    try:
        splash = ProfessionalSplash()
        splash.show()
        app.processEvents()

        splash.show_status("Initializing engine...", 15)
        app.processEvents()

        splash.show_status("Loading UI components...", 40)
        app.processEvents()

        splash.show_status("Building main window...", 65)
        window = MainWindow(splash)
        app.processEvents()

        splash.show_status("Starting services...", 90)
        app.processEvents()

        window.show()
        splash.finish(window)
    except Exception:
        # Fallback — simple splash
        if splash:
            try:
                splash.finish(QMainWindow())
            except Exception:
                pass
        splash2 = None
        try:
            pix = QPixmap(500, 260)
            pix.fill(QColor("#1e1e2e"))
            splash2 = QSplashScreen(pix)
            splash2.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint
                                   | Qt.WindowType.SplashScreen
                                   | Qt.WindowType.FramelessWindowHint)
            splash2.setFont(QFont("Segoe UI", 11))
            splash2.showMessage("\n\n\nIT Support Toolkit\nv2.0 Enterprise\n\nLoading...",
                                Qt.AlignmentFlag.AlignCenter, QColor("#cdd6f4"))
            splash2.show()
            app.processEvents()
        except Exception:
            pass
        window = MainWindow()
        window.show()
        if splash2:
            splash2.finish(window)

    sys.exit(app.exec())
