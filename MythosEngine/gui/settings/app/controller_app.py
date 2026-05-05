# MythosEngine/gui/settings/app/controller_app.py
from PyQt6.QtCore import QObject
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication


class AppSettingsController(QObject):
    def __init__(self, view, ctx, app=None):
        super().__init__()
        self.view = view
        self.ctx = ctx
        self.config = ctx.config
        self.app = app or QApplication.instance()

        # Load saved values into the UI without triggering callbacks
        self._loading = True
        self._load_saved_values()
        self._loading = False

        # Connect signals after loading to avoid false saves on init
        self.view.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        self.view.font_size_combo.currentTextChanged.connect(self.on_font_size_changed)
        self.view.compact_mode_checkbox.toggled.connect(self.on_compact_mode_changed)
        self.view.tooltips_checkbox.toggled.connect(self.on_tooltips_changed)
        self.view.startup_tab_combo.currentTextChanged.connect(self.on_startup_tab_changed)

    def _load_saved_values(self):
        theme = getattr(self.config, "THEME", "Dark")
        fsize = getattr(self.config, "FONT_SIZE", "Small")
        compact = getattr(self.config, "COMPACT_MODE", False)
        tips = getattr(self.config, "SHOW_TOOLTIPS", True)
        startup = getattr(self.config, "STARTUP_TAB", "Dashboard")

        idx = self.view.theme_combo.findText(theme)
        if idx >= 0:
            self.view.theme_combo.setCurrentIndex(idx)

        idx = self.view.font_size_combo.findText(fsize)
        if idx >= 0:
            self.view.font_size_combo.setCurrentIndex(idx)

        self.view.compact_mode_checkbox.setChecked(compact)
        self.view.tooltips_checkbox.setChecked(tips)

        idx = self.view.startup_tab_combo.findText(startup)
        if idx >= 0:
            self.view.startup_tab_combo.setCurrentIndex(idx)

    def on_theme_changed(self, theme: str):
        if self._loading:
            return
        self.config.THEME = theme
        from MythosEngine.gui import theme as _theme

        _theme.apply(self.app, theme)

    def on_font_size_changed(self, size: str):
        if self._loading:
            return
        self.config.FONT_SIZE = size
        font_map = {"Small": 10, "Medium": 12, "Large": 14}
        pt = font_map.get(size, 10)
        self.app.setFont(QFont("Segoe UI", pt))

    def on_compact_mode_changed(self, enabled: bool):
        if self._loading:
            return
        self.config.COMPACT_MODE = enabled
        # Re-apply current theme (compact mode is a preference only; no visual override)
        from MythosEngine.gui import theme as _theme

        _theme.apply(self.app, getattr(self.config, "THEME", "Dark"))

    def on_tooltips_changed(self, enabled: bool):
        if self._loading:
            return
        self.config.SHOW_TOOLTIPS = enabled
        # No reliable global toggle in Qt — just persist the preference

    def on_startup_tab_changed(self, tab: str):
        if self._loading:
            return
        self.config.STARTUP_TAB = tab
