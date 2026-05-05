# MythosEngine/gui/theme.py
"""
MythosEngine Design System v2
─────────────────────────────
A polished, modern dark/light theme inspired by Linear, Discord, and Obsidian.
Apply via:  theme.apply(app, "Dark")  or  theme.apply(app, "Light")
"""

# ── Shared accents ────────────────────────────────────────────────────────────
ACCENT_PUR = "#7C5CFC"
ACCENT_PUR_H = "#6844F0"
ACCENT_PUR_SOFT = "rgba(124, 92, 252, 0.12)"
ACCENT_GRN = "#34D399"
ACCENT_GRN_H = "#10B981"
DANGER = "#F87171"
DANGER_H = "#EF4444"
SUCCESS = "#34D399"
WARNING = "#FBBF24"

# ── Dark palette ──────────────────────────────────────────────────────────────
# Color gaps are wide (~10-15 per channel) so surfaces are clearly distinct
# without needing borders — inspired by Discord / Linear depth model.
_DARK = dict(
    BG_BASE="#0D0D14",  # deepest background (content area)
    BG_SURFACE="#16161F",  # sidebar, panels — noticeable step up
    BG_CARD="#1E1E2A",  # cards, elevated containers
    BG_ELEVATED="#272738",  # inputs, dropdowns, form fields
    BG_HOVER="#303046",  # hover state for interactive elements
    BG_ACTIVE="#3A3A54",  # pressed/active state
    BG_TABLE_ALT="#1A1A24",  # alternating table rows
    ACCENT_PUR=ACCENT_PUR,
    ACCENT_PUR_H=ACCENT_PUR_H,
    ACCENT_PUR_SOFT=ACCENT_PUR_SOFT,
    ACCENT_GRN=ACCENT_GRN,
    ACCENT_GRN_H=ACCENT_GRN_H,
    BORDER="#2E2E42",  # subtle separators when needed
    BORDER_SUBTLE="#24243A",  # very faint dividers
    BORDER_FOCUS=ACCENT_PUR,
    TEXT_PRIMARY="#ECEEF4",
    TEXT_SECONDARY="#A0A4B8",
    TEXT_MUTED="#606480",
    TEXT_DIM="#8B8FA8",
    DANGER=DANGER,
    DANGER_H=DANGER_H,
    SUCCESS=SUCCESS,
    SCROLLBAR="#33334A",
    SCROLLBAR_H="#464660",
)

# ── Light palette ─────────────────────────────────────────────────────────────
_LIGHT = dict(
    BG_BASE="#F2F2F8",
    BG_SURFACE="#FFFFFF",
    BG_CARD="#E8E8F2",
    BG_ELEVATED="#DDDDE8",
    BG_HOVER="#D4D4E2",
    BG_ACTIVE="#C8C4E8",
    BG_TABLE_ALT="#F6F6FC",
    ACCENT_PUR=ACCENT_PUR,
    ACCENT_PUR_H=ACCENT_PUR_H,
    ACCENT_PUR_SOFT="rgba(124, 92, 252, 0.08)",
    ACCENT_GRN="#10B981",
    ACCENT_GRN_H="#059669",
    BORDER="#D0D0E0",
    BORDER_SUBTLE="#DCDCE8",
    BORDER_FOCUS=ACCENT_PUR,
    TEXT_PRIMARY="#1A1A2E",
    TEXT_SECONDARY="#5A5E78",
    TEXT_MUTED="#8B8FA0",
    TEXT_DIM="#9CA0B4",
    DANGER="#EF4444",
    DANGER_H="#DC2626",
    SUCCESS="#10B981",
    SCROLLBAR="#CBCBD8",
    SCROLLBAR_H="#B4B4C8",
)

# ── Backward-compat module-level names (dark values) ─────────────────────────
BG_BASE = _DARK["BG_BASE"]
BG_SURFACE = _DARK["BG_SURFACE"]
BG_CARD = _DARK["BG_CARD"]
BG_HOVER = _DARK["BG_HOVER"]
BG_ACTIVE = _DARK["BG_ACTIVE"]
BG_ELEVATED = _DARK["BG_ELEVATED"]
BORDER = _DARK["BORDER"]
BORDER_FOCUS = _DARK["BORDER_FOCUS"]
TEXT_PRIMARY = _DARK["TEXT_PRIMARY"]
TEXT_MUTED = _DARK["TEXT_MUTED"]
TEXT_DIM = _DARK["TEXT_DIM"]
SCROLLBAR_HANDLE = _DARK["SCROLLBAR"]


# ── QSS template ──────────────────────────────────────────────────────────────
def _build(p: dict) -> str:
    return f"""

/* ═══════════════════════════════════════════════════════════════════════════
   GLOBAL — borderless-first philosophy: surfaces separated by color, not lines
   ═══════════════════════════════════════════════════════════════════════════ */
* {{
    font-family: "Segoe UI", "Inter", "SF Pro Display", "Helvetica Neue", sans-serif;
    font-size: 10.5pt;
    color: {p["TEXT_PRIMARY"]};
    outline: none;
}}

QWidget {{
    background-color: {p["BG_BASE"]};
    border: none;
}}

QMainWindow {{
    background-color: {p["BG_BASE"]};
}}


/* ═══════════════════════════════════════════════════════════════════════════
   SIDEBAR & NAVIGATION
   ═══════════════════════════════════════════════════════════════════════════ */
#Sidebar {{
    background-color: {p["BG_SURFACE"]};
    border: none;
}}

#NavSectionLabel {{
    color: {p["TEXT_MUTED"]};
    font-size: 7pt;
    font-weight: 700;
    letter-spacing: 1.5px;
    background: transparent;
    padding: 0 4px;
}}

#AppLogo {{
    color: {p["TEXT_PRIMARY"]};
    font-size: 15pt;
    font-weight: 700;
    letter-spacing: 0.5px;
    background: transparent;
    padding: 4px 0;
}}

#AppTagline {{
    color: {p["TEXT_MUTED"]};
    font-size: 8pt;
    background: transparent;
}}

#NavDivider {{
    background-color: {p["BORDER_SUBTLE"]};
    max-height: 1px;
    min-height: 1px;
    border: none;
    margin: 4px 12px;
}}

#NavBtn {{
    background: transparent;
    border: none;
    border-radius: 8px;
    padding: 9px 14px;
    text-align: left;
    color: {p["TEXT_DIM"]};
    font-size: 10pt;
    font-weight: 500;
}}

#NavBtn:hover {{
    background-color: {p["BG_HOVER"]};
    color: {p["TEXT_PRIMARY"]};
}}

#NavBtn[active="true"] {{
    background-color: {p["ACCENT_PUR_SOFT"]};
    color: {p["ACCENT_PUR"]};
    font-weight: 600;
    border-left: 3px solid {p["ACCENT_PUR"]};
    padding-left: 11px;
}}

#NavBtnBottom {{
    background: transparent;
    border: none;
    border-radius: 8px;
    padding: 9px 14px;
    text-align: left;
    color: {p["TEXT_MUTED"]};
    font-size: 10pt;
}}

#NavBtnBottom:hover {{
    background-color: {p["BG_HOVER"]};
    color: {p["TEXT_PRIMARY"]};
}}


/* ═══════════════════════════════════════════════════════════════════════════
   BUTTONS — PRIMARY (default)
   ═══════════════════════════════════════════════════════════════════════════ */
QPushButton {{
    background-color: {p["ACCENT_PUR"]};
    color: #FFFFFF;
    border: none;
    border-radius: 7px;
    padding: 7px 18px;
    font-weight: 600;
    font-size: 9.5pt;
    min-height: 34px;
}}

QPushButton:hover {{
    background-color: {p["ACCENT_PUR_H"]};
}}

QPushButton:pressed {{
    background-color: #5B35E0;
}}

QPushButton:disabled {{
    background-color: {p["BG_ELEVATED"]};
    color: {p["TEXT_MUTED"]};
}}

/* ── Secondary ─────────────────────────────────────────────────────────── */
QPushButton[secondary="true"] {{
    background-color: {p["BG_ELEVATED"]};
    color: {p["TEXT_SECONDARY"]};
    border: none;
    font-weight: 500;
}}

QPushButton[secondary="true"]:hover {{
    background-color: {p["BG_HOVER"]};
    color: {p["TEXT_PRIMARY"]};
}}

/* ── Danger ────────────────────────────────────────────────────────────── */
QPushButton[danger="true"] {{
    background-color: transparent;
    color: {p["DANGER"]};
    border: none;
}}

QPushButton[danger="true"]:hover {{
    background-color: {p["DANGER"]};
    color: white;
}}

/* ── Green / Success ───────────────────────────────────────────────────── */
QPushButton[green="true"] {{
    background-color: {p["ACCENT_GRN"]};
    color: white;
    border: none;
}}

QPushButton[green="true"]:hover {{
    background-color: {p["ACCENT_GRN_H"]};
}}


/* ═══════════════════════════════════════════════════════════════════════════
   TOOLBAR BUTTONS — compact, subtle (browse bars, debug controls)
   ═══════════════════════════════════════════════════════════════════════════ */
QPushButton[toolbar="true"] {{
    background-color: {p["BG_ELEVATED"]};
    color: {p["TEXT_SECONDARY"]};
    border: none;
    border-radius: 6px;
    padding: 4px 12px;
    font-size: 9pt;
    font-weight: 500;
    min-height: 28px;
    max-height: 30px;
}}

QPushButton[toolbar="true"]:hover {{
    background-color: {p["BG_HOVER"]};
    color: {p["ACCENT_PUR"]};
}}

QPushButton[toolbar="true"]:pressed {{
    background-color: {p["BG_ACTIVE"]};
}}

QPushButton[toolbar="true"]:disabled {{
    color: {p["TEXT_MUTED"]};
}}

QPushButton[toolbar-primary="true"] {{
    background-color: {p["ACCENT_PUR"]};
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 4px 14px;
    font-size: 9pt;
    font-weight: 600;
    min-height: 28px;
    max-height: 30px;
}}

QPushButton[toolbar-primary="true"]:hover {{
    background-color: {p["ACCENT_PUR_H"]};
}}

QPushButton[toolbar-danger="true"] {{
    background-color: transparent;
    color: {p["DANGER"]};
    border: none;
    border-radius: 6px;
    padding: 4px 12px;
    font-size: 9pt;
    font-weight: 500;
    min-height: 28px;
    max-height: 30px;
}}

QPushButton[toolbar-danger="true"]:hover {{
    background-color: {p["DANGER"]};
    color: white;
}}


/* ═══════════════════════════════════════════════════════════════════════════
   TABLE ACTION BUTTONS — inline in table rows (Role, Reset PW, etc.)
   ═══════════════════════════════════════════════════════════════════════════ */
QPushButton[role="action"] {{
    background-color: {p["BG_ELEVATED"]};
    color: {p["TEXT_SECONDARY"]};
    border: none;
    border-radius: 6px;
    padding: 4px 14px;
    font-size: 8.5pt;
    font-weight: 500;
    min-height: 28px;
    min-width: 64px;
}}

QPushButton[role="action"]:hover {{
    background-color: {p["BG_HOVER"]};
    color: {p["ACCENT_PUR"]};
}}

QPushButton[role="action-danger"] {{
    background-color: transparent;
    color: {p["DANGER"]};
    border: none;
    border-radius: 6px;
    padding: 4px 14px;
    font-size: 8.5pt;
    font-weight: 500;
    min-height: 28px;
    min-width: 64px;
}}

QPushButton[role="action-danger"]:hover {{
    background-color: {p["DANGER"]};
    color: white;
}}

QPushButton[role="action-enable"] {{
    background-color: {p["ACCENT_GRN"]};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 4px 14px;
    font-size: 8.5pt;
    font-weight: 500;
    min-height: 28px;
    min-width: 64px;
}}

QPushButton[role="action-enable"]:hover {{
    background-color: {p["ACCENT_GRN_H"]};
}}


/* ═══════════════════════════════════════════════════════════════════════════
   INPUTS — borderless by default, subtle focus indicator
   ═══════════════════════════════════════════════════════════════════════════ */
QTextEdit, QLineEdit, QPlainTextEdit {{
    background-color: {p["BG_ELEVATED"]};
    border: 2px solid transparent;
    border-radius: 10px;
    padding: 10px 14px;
    color: {p["TEXT_PRIMARY"]};
    selection-background-color: {p["ACCENT_PUR"]};
    selection-color: white;
    min-height: 20px;
}}

QLineEdit {{
    min-height: 22px;
}}

QTextEdit:focus, QLineEdit:focus, QPlainTextEdit:focus {{
    border: 2px solid {p["BORDER_FOCUS"]};
}}

QTextEdit[readonly="true"], QTextBrowser {{
    background-color: {p["BG_CARD"]};
    border: none;
    border-radius: 10px;
    color: {p["TEXT_PRIMARY"]};
    padding: 14px 16px;
}}


/* ═══════════════════════════════════════════════════════════════════════════
   COMBOBOX — borderless, bg-differentiated
   ═══════════════════════════════════════════════════════════════════════════ */
QComboBox {{
    background-color: {p["BG_ELEVATED"]};
    border: 2px solid transparent;
    border-radius: 10px;
    padding: 8px 14px;
    color: {p["TEXT_PRIMARY"]};
    min-height: 36px;
}}

QComboBox:hover {{ background-color: {p["BG_ELEVATED"]}; }}
QComboBox:focus {{ border-color: {p["BORDER_FOCUS"]}; }}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox QAbstractItemView {{
    background-color: {p["BG_ELEVATED"]};
    border: 1px solid {p["BORDER_SUBTLE"]};
    border-radius: 8px;
    color: {p["TEXT_PRIMARY"]};
    selection-background-color: {p["BG_ACTIVE"]};
    selection-color: {p["ACCENT_PUR"]};
    padding: 4px;
    outline: none;
}}


/* ═══════════════════════════════════════════════════════════════════════════
   LISTS & TREES — borderless, subtle bg
   ═══════════════════════════════════════════════════════════════════════════ */
QListWidget, QTreeWidget {{
    background-color: {p["BG_CARD"]};
    border: none;
    border-radius: 8px;
    color: {p["TEXT_PRIMARY"]};
    outline: none;
    padding: 4px;
}}

QListWidget::item, QTreeWidget::item {{
    padding: 6px 8px;
    border-radius: 6px;
}}

QListWidget::item:hover, QTreeWidget::item:hover {{
    background-color: {p["BG_HOVER"]};
}}

QListWidget::item:selected, QTreeWidget::item:selected {{
    background-color: {p["ACCENT_PUR_SOFT"]};
    color: {p["ACCENT_PUR"]};
}}

QTreeWidget::branch {{
    background: transparent;
}}


/* ═══════════════════════════════════════════════════════════════════════════
   TABLES — clean, borderless outer, subtle row dividers
   ═══════════════════════════════════════════════════════════════════════════ */
QTableWidget {{
    background-color: {p["BG_CARD"]};
    alternate-background-color: {p["BG_TABLE_ALT"]};
    border: none;
    border-radius: 8px;
    gridline-color: {p["BORDER_SUBTLE"]};
    color: {p["TEXT_PRIMARY"]};
    outline: none;
}}

QTableWidget::item {{
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid {p["BORDER_SUBTLE"]};
    color: {p["TEXT_PRIMARY"]};
}}

QTableWidget::item:hover {{
    background-color: {p["BG_HOVER"]};
}}

QTableWidget::item:selected {{
    background-color: {p["ACCENT_PUR_SOFT"]};
    color: {p["ACCENT_PUR"]};
}}

QHeaderView {{
    background-color: transparent;
    border: none;
}}

QHeaderView::section {{
    background-color: {p["BG_SURFACE"]};
    color: {p["TEXT_MUTED"]};
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 0.8px;
    padding: 10px 12px;
    border: none;
    border-bottom: 1px solid {p["BORDER_SUBTLE"]};
    border-right: none;
    text-transform: uppercase;
}}

QHeaderView::section:hover {{
    color: {p["TEXT_SECONDARY"]};
}}

QTableCornerButton::section {{
    background-color: {p["BG_SURFACE"]};
    border: none;
    border-bottom: 1px solid {p["BORDER_SUBTLE"]};
}}


/* ═══════════════════════════════════════════════════════════════════════════
   TABS — clean underline style, no pane border
   ═══════════════════════════════════════════════════════════════════════════ */
QTabWidget::pane {{
    background-color: {p["BG_BASE"]};
    border: none;
    border-radius: 0px;
    top: 0px;
}}

QTabBar {{
    background: transparent;
}}

QTabBar::tab {{
    background: transparent;
    color: {p["TEXT_MUTED"]};
    padding: 10px 20px;
    border: none;
    border-bottom: 2px solid transparent;
    margin-right: 2px;
    font-weight: 500;
}}

QTabBar::tab:selected {{
    color: {p["ACCENT_PUR"]};
    border-bottom: 2px solid {p["ACCENT_PUR"]};
    font-weight: 600;
}}

QTabBar::tab:hover:!selected {{
    color: {p["TEXT_PRIMARY"]};
    border-bottom: 2px solid {p["BORDER_SUBTLE"]};
}}


/* ═══════════════════════════════════════════════════════════════════════════
   SCROLLBARS — thin, minimal
   ═══════════════════════════════════════════════════════════════════════════ */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 4px 1px;
}}

QScrollBar::handle:vertical {{
    background: {p["SCROLLBAR"]};
    border-radius: 3px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{ background: {p["SCROLLBAR_H"]}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}

QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
    margin: 1px 4px;
}}

QScrollBar::handle:horizontal {{
    background: {p["SCROLLBAR"]};
    border-radius: 3px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{ background: {p["SCROLLBAR_H"]}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: none; }}


/* ═══════════════════════════════════════════════════════════════════════════
   CHECKBOX
   ═══════════════════════════════════════════════════════════════════════════ */
QCheckBox {{
    color: {p["TEXT_PRIMARY"]};
    spacing: 8px;
    background: transparent;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 2px solid {p["BORDER"]};
    background-color: {p["BG_ELEVATED"]};
}}

QCheckBox::indicator:checked {{
    background-color: {p["ACCENT_PUR"]};
    border-color: {p["ACCENT_PUR"]};
}}

QCheckBox::indicator:hover {{
    border-color: {p["ACCENT_PUR"]};
}}


/* ═══════════════════════════════════════════════════════════════════════════
   LABELS
   ═══════════════════════════════════════════════════════════════════════════ */
QLabel {{
    background: transparent;
    color: {p["TEXT_PRIMARY"]};
    border: none;
}}

QLabel[role="filter-label"] {{
    color: {p["TEXT_DIM"]};
    font-size: 9pt;
}}

QLabel[role="muted"] {{
    color: {p["TEXT_MUTED"]};
    font-size: 9pt;
}}

QLabel[role="subtitle"] {{
    color: {p["TEXT_SECONDARY"]};
    font-size: 10pt;
}}


/* ═══════════════════════════════════════════════════════════════════════════
   GROUPBOX — borderless card sections, bg-differentiated
   ═══════════════════════════════════════════════════════════════════════════ */
QGroupBox {{
    border: none;
    border-radius: 12px;
    margin-top: 14px;
    padding: 20px 18px 16px 18px;
    background: {p["BG_CARD"]};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 12px;
    color: {p["ACCENT_PUR"]};
    font-weight: 600;
    font-size: 9pt;
}}


/* ═══════════════════════════════════════════════════════════════════════════
   CARDS & FRAMES — borderless, rely on shadow + bg color
   ═══════════════════════════════════════════════════════════════════════════ */
QFrame[card="true"] {{
    background-color: {p["BG_CARD"]};
    border: none;
    border-radius: 10px;
}}

#InputFrame {{
    background-color: {p["BG_CARD"]};
    border: 2px solid transparent;
    border-radius: 10px;
}}

#InputFrame:focus-within {{
    border-color: {p["BORDER_FOCUS"]};
}}

QSplitter::handle {{
    background-color: {p["BORDER_SUBTLE"]};
}}

QSplitter::handle:horizontal {{ width: 1px; }}
QSplitter::handle:vertical {{ height: 1px; }}

QFrame[frameShape="4"],
QFrame[frameShape="5"] {{
    color: {p["BORDER_SUBTLE"]};
    border: none;
    background-color: {p["BORDER_SUBTLE"]};
    max-height: 1px;
    min-height: 1px;
}}


/* ═══════════════════════════════════════════════════════════════════════════
   MENUS
   ═══════════════════════════════════════════════════════════════════════════ */
QMenuBar {{
    background-color: {p["BG_SURFACE"]};
    color: {p["TEXT_DIM"]};
    border: none;
    padding: 2px 0;
}}

QMenuBar::item {{
    padding: 6px 14px;
    background: transparent;
    border-radius: 5px;
}}

QMenuBar::item:selected {{
    background-color: {p["BG_HOVER"]};
    color: {p["TEXT_PRIMARY"]};
}}

QMenu {{
    background-color: {p["BG_ELEVATED"]};
    border: 1px solid {p["BORDER_SUBTLE"]};
    border-radius: 8px;
    padding: 6px;
}}

QMenu::item {{
    padding: 8px 20px 8px 12px;
    border-radius: 5px;
    color: {p["TEXT_PRIMARY"]};
}}

QMenu::item:selected {{
    background-color: {p["ACCENT_PUR_SOFT"]};
    color: {p["ACCENT_PUR"]};
}}

QMenu::separator {{
    height: 1px;
    background-color: {p["BORDER_SUBTLE"]};
    margin: 4px 8px;
}}


/* ═══════════════════════════════════════════════════════════════════════════
   SLIDERS
   ═══════════════════════════════════════════════════════════════════════════ */
QSlider::groove:horizontal {{
    background: {p["BG_ELEVATED"]};
    height: 4px;
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background: {p["ACCENT_PUR"]};
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}

QSlider::sub-page:horizontal {{
    background: {p["ACCENT_PUR"]};
    border-radius: 2px;
}}


/* ═══════════════════════════════════════════════════════════════════════════
   TOOLTIPS / STATUS / DIALOGS
   ═══════════════════════════════════════════════════════════════════════════ */
QToolTip {{
    background-color: {p["BG_ELEVATED"]};
    color: {p["TEXT_PRIMARY"]};
    border: 1px solid {p["BORDER_SUBTLE"]};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 9pt;
}}

QStatusBar {{
    background-color: {p["BG_SURFACE"]};
    color: {p["TEXT_MUTED"]};
    border: none;
    font-size: 8pt;
    padding: 2px 8px;
}}

QDialog {{
    background-color: {p["BG_SURFACE"]};
    border: none;
    border-radius: 12px;
}}

QMessageBox {{
    background-color: {p["BG_SURFACE"]};
}}

QMessageBox QPushButton {{
    min-width: 80px;
}}


/* ═══════════════════════════════════════════════════════════════════════════
   SCROLL AREA
   ═══════════════════════════════════════════════════════════════════════════ */
QScrollArea {{
    background: transparent;
    border: none;
}}

QScrollArea > QWidget > QWidget {{
    background: transparent;
}}


/* ═══════════════════════════════════════════════════════════════════════════
   PROGRESS BAR
   ═══════════════════════════════════════════════════════════════════════════ */
QProgressBar {{
    background-color: {p["BG_ELEVATED"]};
    border: none;
    border-radius: 5px;
    text-align: center;
    color: {p["TEXT_PRIMARY"]};
    min-height: 18px;
}}

QProgressBar::chunk {{
    background-color: {p["ACCENT_PUR"]};
    border-radius: 4px;
}}


/* ═══════════════════════════════════════════════════════════════════════════
   SPIN BOX
   ═══════════════════════════════════════════════════════════════════════════ */
QSpinBox, QDoubleSpinBox {{
    background-color: {p["BG_ELEVATED"]};
    border: 2px solid transparent;
    border-radius: 10px;
    padding: 8px 14px;
    color: {p["TEXT_PRIMARY"]};
    min-height: 36px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {p["BORDER_FOCUS"]};
}}


/* ═══════════════════════════════════════════════════════════════════════════
   STACKED WIDGET — content area (no border)
   ═══════════════════════════════════════════════════════════════════════════ */
QStackedWidget {{
    background-color: {p["BG_BASE"]};
    border: none;
}}


/* ═══════════════════════════════════════════════════════════════════════════
   TABLE CELL WIDGET CONTAINER — transparent for action buttons
   ═══════════════════════════════════════════════════════════════════════════ */
QTableWidget QWidget {{
    background: transparent;
}}


/* ═══════════════════════════════════════════════════════════════════════════
   TOOL BUTTON — clean, borderless
   ═══════════════════════════════════════════════════════════════════════════ */
QToolButton {{
    background: transparent;
    border: none;
    border-radius: 6px;
    padding: 6px 10px;
    color: {p["TEXT_PRIMARY"]};
    font-weight: 600;
}}

QToolButton:hover {{
    background-color: {p["BG_HOVER"]};
}}

QToolButton:checked {{
    color: {p["ACCENT_PUR"]};
}}


/* ═══════════════════════════════════════════════════════════════════════════
   CUSTOM WIDGET OVERRIDES — prevent QSS from fighting QPainter widgets
   These use objectName selectors to ensure our paintEvent controls rendering.
   ═══════════════════════════════════════════════════════════════════════════ */
#_GlowButton {{
    background: transparent;
    border: none;
    color: transparent;
    padding: 0;
    margin: 0;
    min-height: 0;
    max-height: 16777215;
}}

#_NavButton {{
    background: transparent;
    border: none;
    color: transparent;
    padding: 0;
    margin: 0;
}}

#_ShadowCard {{
    background: transparent;
    border: none;
    padding: 0;
}}

#_StatCard {{
    background: transparent;
    border: none;
    padding: 0;
}}

#_StatusBadge {{
    background: transparent;
    border: none;
    padding: 0;
    margin: 0;
}}

#_AvatarCircle {{
    background: transparent;
    border: none;
    padding: 0;
    margin: 0;
}}

#_SidebarFrame {{
    background: transparent;
    border: none;
}}
"""


# ── Pre-built stylesheets ─────────────────────────────────────────────────────
STYLESHEET = _build(_DARK)
STYLESHEET_DARK = STYLESHEET
STYLESHEET_LIGHT = _build(_LIGHT)


def apply(app, theme: str = "Dark"):
    """Apply the named theme stylesheet to the QApplication."""
    if theme.lower() == "light":
        app.setStyleSheet(STYLESHEET_LIGHT)
    else:
        app.setStyleSheet(STYLESHEET_DARK)
