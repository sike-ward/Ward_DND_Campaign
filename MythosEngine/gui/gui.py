# MythosEngine/gui/gui.py

from PyQt6.QtGui import (
    QAction,
    QFont,
    QKeySequence,
    QPainter,
    QPen,
)
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from MythosEngine.gui.browse.controller_browse import BrowseController
from MythosEngine.gui.browse.view_browse import BrowseView
from MythosEngine.gui.chat.controller_chat import ChatController
from MythosEngine.gui.chat.view_chat import ChatView
from MythosEngine.gui.create.controller_create import CreateController
from MythosEngine.gui.create.view_create import CreateView
from MythosEngine.gui.dashboard.controller_dashboard import DashboardController
from MythosEngine.gui.dashboard.view_dashboard import DashboardView
from MythosEngine.gui.settings.controller_settings import SettingsController
from MythosEngine.gui.settings.view_settings import SettingsView
from MythosEngine.gui.universe.timeline.controller_timeline import TimelineController
from MythosEngine.gui.universe.timeline.view_timeline import TimelineView
from MythosEngine.gui.widgets import Divider, NavButton, Tok

# ── Nav item definition ────────────────────────────────────────────────────────
_NAV_ITEMS = [
    ("🏠", "Dashboard"),
    ("✦", "AI"),
    ("📖", "Browse"),
    ("✨", "Create"),
    ("🌌", "Universe"),
]

_NAV_BOTTOM = [
    ("⚙️", "Settings"),
]


# ── Custom-painted sidebar ────────────────────────────────────────────────────


class _SidebarFrame(QFrame):
    """Sidebar frame with painted gradient background and subtle right glow."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("_SidebarFrame")
        self.setFixedWidth(250)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Solid surface color — relies on color contrast with BG_BASE
        p.fillRect(0, 0, w, h, Tok.BG_SURFACE)

        # Very subtle right edge separator (1px, barely visible)
        p.setPen(QPen(Tok.BORDER_SUBTLE, 1))
        p.drawLine(w - 1, 0, w - 1, h)

        p.end()


class LoreMainApp(QMainWindow):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.ai = ctx.ai
        self.storage = ctx.storage
        self._config = ctx.config

        self.setWindowTitle(getattr(ctx.config, "APP_NAME", "MythosEngine"))
        self.resize(1280, 800)
        self.setMinimumSize(900, 600)

        # ── Central widget: sidebar + content ─────────────────────────────────
        root_widget = QWidget()
        root_layout = QHBoxLayout(root_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setCentralWidget(root_widget)

        # ── Sidebar ───────────────────────────────────────────────────────────
        sidebar = _SidebarFrame()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 26, 16, 20)
        sidebar_layout.setSpacing(3)

        # Branding — custom painted
        logo = QLabel("⚡ MythosEngine")
        logo_font = QFont("Segoe UI", 15)
        logo_font.setWeight(QFont.Weight.Bold)
        logo.setFont(logo_font)
        logo.setStyleSheet(f"color: {Tok.TEXT.name()}; background: transparent; padding: 4px 0;")
        sidebar_layout.addWidget(logo)

        tagline = QLabel("Your world. Your story.")
        tagline_font = QFont("Segoe UI", 8)
        tagline.setFont(tagline_font)
        tagline.setStyleSheet(f"color: {Tok.TEXT_MUTED.name()}; background: transparent;")
        sidebar_layout.addWidget(tagline)

        sidebar_layout.addSpacing(24)

        # Nav section label
        nav_section = QLabel("NAVIGATION")
        nav_section_font = QFont("Segoe UI", 7)
        nav_section_font.setWeight(QFont.Weight.Bold)
        nav_section_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.5)
        nav_section.setFont(nav_section_font)
        nav_section.setStyleSheet(f"color: {Tok.TEXT_MUTED.name()}; background: transparent; padding: 0 6px;")
        sidebar_layout.addWidget(nav_section)
        sidebar_layout.addSpacing(8)

        # Main nav buttons — using custom NavButton
        self._nav_buttons: dict[str, NavButton] = {}
        self._stack_index: dict[str, int] = {}
        self.tabs: dict[str, QWidget] = {}

        for icon, label in _NAV_ITEMS:
            btn = NavButton(icon, label)
            btn.clicked.connect(lambda checked, lbl=label: self._switch_to(lbl))
            sidebar_layout.addWidget(btn)
            sidebar_layout.addSpacing(2)
            self._nav_buttons[label] = btn

        # Spacer pushes Settings to bottom
        sidebar_layout.addStretch(1)

        # Divider
        sidebar_layout.addWidget(Divider())
        sidebar_layout.addSpacing(8)

        for icon, label in _NAV_BOTTOM:
            btn = NavButton(icon, label)
            btn.clicked.connect(lambda checked, lbl=label: self._switch_to(lbl))
            sidebar_layout.addWidget(btn)
            self._nav_buttons[label] = btn

        sidebar_layout.addSpacing(4)

        # Logout button — using NavButton with ghost style
        self._btn_logout = NavButton("🚪", "Log Out")
        self._btn_logout.clicked.connect(self._on_logout)
        sidebar_layout.addWidget(self._btn_logout)

        root_layout.addWidget(sidebar)

        # ── Content stack ─────────────────────────────────────────────────────
        self._stack = QStackedWidget()
        root_layout.addWidget(self._stack, 1)

        # ── Build all views ───────────────────────────────────────────────────
        self._build_views()

        # ── Status Bar ────────────────────────────────────────────────────────
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")

        # ── Menu bar ──────────────────────────────────────────────────────────
        self._setup_menubar()

        # ── Start on Dashboard ────────────────────────────────────────────────
        startup = getattr(self._config, "STARTUP_TAB", "Dashboard")
        self._switch_to(startup if startup in self._nav_buttons else "Dashboard")

    # ── View construction ──────────────────────────────────────────────────────

    def _add_view(self, label: str, view: QWidget):
        idx = self._stack.addWidget(view)
        self._stack_index[label] = idx
        self.tabs[label] = view

    def _build_views(self):
        # Dashboard
        dash_view = DashboardView(self._stack, self._config)
        DashboardController(dash_view, self.ctx)
        self._add_view("Dashboard", dash_view)

        # AI Chat
        ai_view = ChatView(self._stack, self._config)
        ChatController(ai_view, self.ctx)
        self._add_view("AI", ai_view)

        # Browse
        browse_view = BrowseView(self._stack, self._config)
        self.browse_controller = BrowseController(browse_view, self.ctx)
        self._add_view("Browse", browse_view)

        # Create
        create_view = CreateView(self._stack, self._config)
        CreateController(create_view, self.ctx)
        self._add_view("Create", create_view)

        # Universe / Timeline
        universe_view = TimelineView(self._stack, self._config)
        TimelineController(universe_view, self.ctx)
        self._add_view("Universe", universe_view)

        # Settings
        settings_view = SettingsView(self._stack, self.ctx)
        SettingsController(settings_view, self.ctx)
        self._add_view("Settings", settings_view)

    # ── Navigation ─────────────────────────────────────────────────────────────

    def _switch_to(self, label: str):
        if label not in self._stack_index:
            return
        self._stack.setCurrentIndex(self._stack_index[label])
        for name, btn in self._nav_buttons.items():
            btn.set_active(name == label)
        self.statusbar.showMessage(label)

    # ── Menu bar ───────────────────────────────────────────────────────────────

    def _setup_menubar(self):
        menubar = QMenuBar(self)

        # File menu
        file_menu = QMenu("File", self)

        new_a = QAction("New Note", self)
        new_a.setShortcut(QKeySequence("Ctrl+N"))
        new_a.triggered.connect(self._menu_new_note)
        file_menu.addAction(new_a)

        import_a = QAction("Import Note", self)
        import_a.setShortcut(QKeySequence("Ctrl+I"))
        import_a.triggered.connect(self._menu_import_note)
        file_menu.addAction(import_a)

        export_a = QAction("Export Note", self)
        import_a.setShortcut(QKeySequence("Ctrl+E"))
        export_a.triggered.connect(self._menu_export_note)
        file_menu.addAction(export_a)

        file_menu.addSeparator()

        exit_a = QAction("Exit", self)
        exit_a.triggered.connect(self.close)
        file_menu.addAction(exit_a)

        menubar.addMenu(file_menu)

        # View menu
        view_menu = QMenu("View", self)
        for icon, label in _NAV_ITEMS + _NAV_BOTTOM:
            a = QAction(f"{icon}  {label}", self)
            a.triggered.connect(lambda checked, lbl=label: self._switch_to(lbl))
            view_menu.addAction(a)
        menubar.addMenu(view_menu)

        self.setMenuBar(menubar)

    # ── Menu actions ────────────────────────────────────────────────────────────

    def _menu_new_note(self):
        self._switch_to("Browse")
        if hasattr(self, "browse_controller"):
            self.browse_controller.new_note()

    def _menu_import_note(self):
        self._switch_to("Browse")
        if hasattr(self, "browse_controller"):
            self.browse_controller.import_notes()

    def _menu_export_note(self):
        self._switch_to("Browse")
        if hasattr(self, "browse_controller"):
            self.browse_controller.export_notes()

    def _on_logout(self) -> None:
        """Trigger logout via AuthManager — the session_ended signal handles the rest."""
        from PyQt6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "Log Out",
            "Are you sure you want to log out?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.ctx.auth.logout(self.ctx.current_user_id)

    def show_status(self, msg: str, timeout: int = 4000):
        self.statusbar.showMessage(msg, timeout)
