# MythosEngine/gui/widgets.py
"""
Premium custom-painted widget library.
──────────────────────────────────────
These widgets use QPainter + QGraphicsDropShadowEffect to achieve
visual quality comparable to Electron apps (Obsidian, Discord, Linear).

Usage:
    from MythosEngine.gui.widgets import ShadowCard, StatusBadge, GlowButton, AvatarCircle
"""

from __future__ import annotations

from PyQt6.QtCore import (
    QRectF,
    Qt,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontMetrics,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# ─────────────────────────────────────────────────────────────────────────────
# Color helpers
# ─────────────────────────────────────────────────────────────────────────────


def _qc(hex_or_rgba: str) -> QColor:
    """Parse '#RRGGBB' or 'rgba(r,g,b,a)' into QColor."""
    s = hex_or_rgba.strip()
    if s.startswith("rgba("):
        parts = s[5:-1].split(",")
        r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
        a = int(float(parts[3].strip()) * 255)
        return QColor(r, g, b, a)
    return QColor(s)


def _with_alpha(color: QColor, alpha: int) -> QColor:
    """Return a copy of *color* with a new alpha (0-255)."""
    c = QColor(color)
    c.setAlpha(alpha)
    return c


# ─────────────────────────────────────────────────────────────────────────────
# Design tokens  (importable, overridable for light theme later)
# ─────────────────────────────────────────────────────────────────────────────


class Tok:
    """Mutable design-token store — call Tok.set_dark() or Tok.set_light()."""

    # ── dark defaults — wide color gaps for borderless surface separation ──
    BG_BASE = QColor("#0D0D14")
    BG_SURFACE = QColor("#16161F")
    BG_CARD = QColor("#1E1E2A")
    BG_ELEVATED = QColor("#272738")
    BG_HOVER = QColor("#303046")

    ACCENT = QColor("#7C5CFC")
    ACCENT_HOVER = QColor("#6844F0")
    ACCENT_SOFT = QColor(124, 92, 252, 30)  # ~12% opacity
    ACCENT_GLOW = QColor(124, 92, 252, 50)

    GREEN = QColor("#34D399")
    GREEN_HOVER = QColor("#10B981")
    RED = QColor("#F87171")
    RED_HOVER = QColor("#EF4444")
    YELLOW = QColor("#FBBF24")
    BLUE = QColor("#60A5FA")

    TEXT = QColor("#ECEEF4")
    TEXT_SEC = QColor("#A0A4B8")
    TEXT_MUTED = QColor("#606480")
    TEXT_DIM = QColor("#8B8FA8")

    BORDER = QColor("#2E2E42")
    BORDER_SUBTLE = QColor("#24243A")

    # Visible on dark bg: use colored glow, not black
    SHADOW = QColor(100, 80, 200, 80)  # purple-ish glow
    SHADOW_ACCENT = QColor(124, 92, 252, 90)
    SHADOW_CARD = QColor(0, 0, 0, 140)  # deeper for cards

    @classmethod
    def set_dark(cls):
        cls.BG_BASE = QColor("#0D0D14")
        cls.BG_SURFACE = QColor("#16161F")
        cls.BG_CARD = QColor("#1E1E2A")
        cls.BG_ELEVATED = QColor("#272738")
        cls.BG_HOVER = QColor("#303046")
        cls.TEXT = QColor("#ECEEF4")
        cls.TEXT_SEC = QColor("#A0A4B8")
        cls.TEXT_MUTED = QColor("#606480")
        cls.BORDER = QColor("#2E2E42")
        cls.SHADOW = QColor(100, 80, 200, 80)
        cls.SHADOW_CARD = QColor(0, 0, 0, 140)

    @classmethod
    def set_light(cls):
        cls.BG_BASE = QColor("#F2F2F8")
        cls.BG_SURFACE = QColor("#FFFFFF")
        cls.BG_CARD = QColor("#E8E8F2")
        cls.BG_ELEVATED = QColor("#DDDDE8")
        cls.BG_HOVER = QColor("#D4D4E2")
        cls.TEXT = QColor("#1A1A2E")
        cls.TEXT_SEC = QColor("#5A5E78")
        cls.TEXT_MUTED = QColor("#8B8FA0")
        cls.BORDER = QColor("#D0D0E0")
        cls.SHADOW = QColor(0, 0, 0, 50)
        cls.SHADOW_CARD = QColor(0, 0, 0, 50)


# ═════════════════════════════════════════════════════════════════════════════
#  ShadowCard — elevated container with real drop shadow
# ═════════════════════════════════════════════════════════════════════════════


class ShadowCard(QFrame):
    """
    A rounded card with a real QGraphicsDropShadowEffect.

    Parameters
    ----------
    radius : corner radius (default 14)
    shadow_blur : shadow radius (default 24)
    shadow_color : QColor for shadow
    accent_top : optional QColor for a 3px accent stripe at top
    parent : QWidget
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        radius: int = 14,
        shadow_blur: int = 28,
        shadow_color: QColor | None = None,
        accent_top: QColor | None = None,
    ):
        super().__init__(parent)
        self.setObjectName("_ShadowCard")
        self._radius = radius
        self._accent_top = accent_top

        # Real drop shadow — colored glow visible on dark backgrounds
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(shadow_blur)
        shadow.setOffset(0, 6)
        shadow.setColor(shadow_color or Tok.SHADOW_CARD)
        self.setGraphicsEffect(shadow)

    def set_accent_top(self, color: QColor | None):
        self._accent_top = color
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect()).adjusted(2, 2, -2, -2)  # inset for shadow

        # Card background — borderless, shadow provides separation
        path = QPainterPath()
        path.addRoundedRect(rect, self._radius, self._radius)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(Tok.BG_CARD))
        p.drawPath(path)

        # Optional accent stripe at top
        if self._accent_top:
            stripe = QPainterPath()
            stripe_rect = QRectF(rect.x(), rect.y(), rect.width(), self._radius * 2)
            stripe.addRoundedRect(stripe_rect, self._radius, self._radius)

            clip_rect = QRectF(rect.x(), rect.y(), rect.width(), 4)
            clip_path = QPainterPath()
            clip_path.addRect(clip_rect)

            final = stripe & clip_path
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(self._accent_top))
            p.drawPath(final)

        p.end()


# ═════════════════════════════════════════════════════════════════════════════
#  StatusBadge — colored pill (Active, Disabled, admin, gm, player)
# ═════════════════════════════════════════════════════════════════════════════

# Predefined badge styles
_BADGE_STYLES = {
    "active": {"bg": QColor(52, 211, 153, 30), "fg": QColor("#34D399"), "border": QColor(52, 211, 153, 60)},
    "disabled": {"bg": QColor(248, 113, 113, 25), "fg": QColor("#F87171"), "border": QColor(248, 113, 113, 50)},
    "admin": {"bg": QColor(124, 92, 252, 25), "fg": QColor("#7C5CFC"), "border": QColor(124, 92, 252, 50)},
    "gm": {"bg": QColor(251, 191, 36, 25), "fg": QColor("#FBBF24"), "border": QColor(251, 191, 36, 50)},
    "player": {"bg": QColor(96, 165, 250, 25), "fg": QColor("#60A5FA"), "border": QColor(96, 165, 250, 50)},
    "expired": {"bg": QColor(139, 143, 168, 20), "fg": QColor("#8B8FA8"), "border": QColor(139, 143, 168, 40)},
    "revoked": {"bg": QColor(248, 113, 113, 20), "fg": QColor("#F87171"), "border": QColor(248, 113, 113, 40)},
    "used": {"bg": QColor(139, 143, 168, 20), "fg": QColor("#8B8FA8"), "border": QColor(139, 143, 168, 40)},
}


class StatusBadge(QWidget):
    """
    Painted pill-shaped status badge.

    Usage:
        badge = StatusBadge("Active", "active")
        badge = StatusBadge("Admin", "admin")
        badge = StatusBadge("Custom", bg=QColor(...), fg=QColor(...))
    """

    def __init__(
        self,
        text: str,
        style_key: str | None = None,
        *,
        bg: QColor | None = None,
        fg: QColor | None = None,
        border: QColor | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setObjectName("_StatusBadge")
        self._text = text

        if style_key and style_key.lower() in _BADGE_STYLES:
            s = _BADGE_STYLES[style_key.lower()]
            self._bg = bg or s["bg"]
            self._fg = fg or s["fg"]
            self._border = border or s["border"]
        else:
            self._bg = bg or QColor(124, 92, 252, 25)
            self._fg = fg or QColor("#7C5CFC")
            self._border = border or QColor(124, 92, 252, 50)

        font = QFont("Segoe UI", 8)
        font.setWeight(QFont.Weight.DemiBold)
        fm = QFontMetrics(font)
        text_w = fm.horizontalAdvance(text)
        self.setFixedSize(text_w + 20, 24)
        self.setFont(font)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(0.5, 0.5, self.width() - 1, self.height() - 1)

        # Pill background
        p.setPen(QPen(self._border, 1.0))
        p.setBrush(QBrush(self._bg))
        p.drawRoundedRect(rect, rect.height() / 2, rect.height() / 2)

        # Text
        p.setPen(QPen(self._fg))
        p.setFont(self.font())
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._text)
        p.end()


# ═════════════════════════════════════════════════════════════════════════════
#  AvatarCircle — circular avatar with initials
# ═════════════════════════════════════════════════════════════════════════════

# Hash username to a pleasant hue
_AVATAR_HUES = [
    QColor("#7C5CFC"),  # purple
    QColor("#34D399"),  # green
    QColor("#60A5FA"),  # blue
    QColor("#F87171"),  # red
    QColor("#FBBF24"),  # yellow
    QColor("#F472B6"),  # pink
    QColor("#A78BFA"),  # light purple
    QColor("#38BDF8"),  # sky
]


class AvatarCircle(QWidget):
    """
    Circular avatar with colored background and initials.

    Usage:
        avatar = AvatarCircle("John Doe", size=36)
    """

    def __init__(self, name: str, size: int = 36, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("_AvatarCircle")
        self._name = name
        self._size = size
        self._initials = self._get_initials(name)
        self._color = _AVATAR_HUES[hash(name) % len(_AVATAR_HUES)]
        self.setFixedSize(size, size)

    @staticmethod
    def _get_initials(name: str) -> str:
        parts = name.strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return name[:2].upper() if name else "?"

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        s = self._size
        center = QRectF(0, 0, s, s)

        # Colored circle
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(self._color))
        p.drawEllipse(center)

        # Initials text
        font = QFont("Segoe UI", int(s * 0.35))
        font.setWeight(QFont.Weight.Bold)
        p.setFont(font)
        p.setPen(QPen(QColor("#FFFFFF")))
        p.drawText(center, Qt.AlignmentFlag.AlignCenter, self._initials)
        p.end()


# ═════════════════════════════════════════════════════════════════════════════
#  GlowButton — premium painted button with subtle glow on hover
# ═════════════════════════════════════════════════════════════════════════════


class GlowButton(QPushButton):
    """
    Custom-painted button with smooth gradient fill and glow effect on hover.

    Variants:
        "primary"   — accent purple fill, white text
        "secondary" — transparent fill, border, muted text
        "danger"    — red outline, red text → filled on hover
        "success"   — green fill, white text
        "ghost"     — no border, just text
    """

    def __init__(self, text: str, variant: str = "primary", parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setObjectName("_GlowButton")
        self._variant = variant
        self._hover = False
        self._pressed = False
        self._radius = 8

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(36)

        font = QFont("Segoe UI", 9)
        font.setWeight(QFont.Weight.DemiBold)
        self.setFont(font)

    def enterEvent(self, event):
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self._pressed = True
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._pressed = False
        self.update()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(1, 1, self.width() - 2, self.height() - 2)
        r = self._radius
        v = self._variant

        bg, fg, border_c = self._get_colors()

        # Glow effect on hover for primary/success — bright colored halo
        if self._hover and v in ("primary", "success"):
            # Outer glow ring
            glow_rect = rect.adjusted(-6, -6, 6, 6)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(_with_alpha(bg, 45)))
            p.drawRoundedRect(glow_rect, r + 6, r + 6)
            # Inner glow ring
            glow_rect2 = rect.adjusted(-3, -3, 3, 3)
            p.setBrush(QBrush(_with_alpha(bg, 30)))
            p.drawRoundedRect(glow_rect2, r + 3, r + 3)

        # Main body
        if border_c:
            p.setPen(QPen(border_c, 1.2))
        else:
            p.setPen(Qt.PenStyle.NoPen)

        if self._pressed:
            bg = bg.darker(120)

        # Use gradient fill for primary/success for premium feel
        if v in ("primary", "success") and bg.alpha() > 200:
            grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            lighter = QColor(bg)
            lighter.setRed(min(255, lighter.red() + 20))
            lighter.setGreen(min(255, lighter.green() + 15))
            lighter.setBlue(min(255, lighter.blue() + 20))
            grad.setColorAt(0.0, lighter)
            grad.setColorAt(1.0, bg)
            p.setBrush(QBrush(grad))
        else:
            p.setBrush(QBrush(bg))

        p.drawRoundedRect(rect, r, r)

        # Text
        p.setPen(QPen(fg))
        p.setFont(self.font())
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())
        p.end()

    def _get_colors(self):
        """Return (bg, fg, border_or_None) based on variant and state."""
        v = self._variant
        h = self._hover

        if v == "primary":
            bg = Tok.ACCENT_HOVER if h else Tok.ACCENT
            return bg, QColor("#FFFFFF"), None

        elif v == "secondary":
            bg = Tok.BG_HOVER if h else Tok.BG_ELEVATED
            fg = Tok.TEXT if h else Tok.TEXT_SEC
            border = Tok.ACCENT if h else Tok.BORDER
            return bg, fg, border

        elif v == "danger":
            if h:
                return Tok.RED, QColor("#FFFFFF"), None
            return QColor(0, 0, 0, 0), Tok.RED, Tok.RED

        elif v == "success":
            bg = Tok.GREEN_HOVER if h else Tok.GREEN
            return bg, QColor("#FFFFFF"), None

        elif v == "ghost":
            bg = Tok.BG_HOVER if h else QColor(0, 0, 0, 0)
            fg = Tok.TEXT if h else Tok.TEXT_DIM
            return bg, fg, None

        # fallback = primary
        bg = Tok.ACCENT_HOVER if h else Tok.ACCENT
        return bg, QColor("#FFFFFF"), None


# ═════════════════════════════════════════════════════════════════════════════
#  SectionHeader — consistent page header with title + subtitle
# ═════════════════════════════════════════════════════════════════════════════


class SectionHeader(QWidget):
    """
    Consistent page/section header: large title + muted subtitle.
    """

    def __init__(self, title: str, subtitle: str = "", parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(6)

        self._title_label = QLabel(title)
        font_t = QFont("Segoe UI", 20)
        font_t.setWeight(QFont.Weight.Bold)
        self._title_label.setFont(font_t)
        self._title_label.setStyleSheet(f"color: {Tok.TEXT.name()}; background: transparent;")
        layout.addWidget(self._title_label)

        if subtitle:
            self._sub_label = QLabel(subtitle)
            font_s = QFont("Segoe UI", 10)
            self._sub_label.setFont(font_s)
            self._sub_label.setStyleSheet(f"color: {Tok.TEXT_SEC.name()}; background: transparent;")
            layout.addWidget(self._sub_label)

    def set_title(self, text: str):
        self._title_label.setText(text)


# ═════════════════════════════════════════════════════════════════════════════
#  StatCard — dashboard metric card with icon, value, and accent color
# ═════════════════════════════════════════════════════════════════════════════


class StatCard(ShadowCard):
    """
    Dashboard stat card with accent top stripe, icon, big number, and label.

    Usage:
        card = StatCard("📝", "Notes", "42", accent=QColor("#7C5CFC"))
    """

    def __init__(
        self,
        icon: str,
        label: str,
        value: str = "—",
        accent: QColor | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent, radius=14, shadow_blur=26, accent_top=accent)
        self.setObjectName("_StatCard")
        self._accent = accent or Tok.ACCENT
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(140)

        inner = QVBoxLayout(self)
        inner.setContentsMargins(24, 24, 24, 20)
        inner.setSpacing(8)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 20pt; background: transparent;")
        inner.addWidget(icon_lbl)

        self._value_label = QLabel(value)
        font_v = QFont("Segoe UI", 28)
        font_v.setWeight(QFont.Weight.Bold)
        self._value_label.setFont(font_v)
        self._value_label.setStyleSheet(f"color: {self._accent.name()}; background: transparent;")
        inner.addWidget(self._value_label)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {Tok.TEXT_MUTED.name()}; font-size: 9pt; background: transparent;")
        inner.addWidget(lbl)

    def set_value(self, value: str):
        self._value_label.setText(value)


# ═════════════════════════════════════════════════════════════════════════════
#  NavButton — custom-painted sidebar navigation button
# ═════════════════════════════════════════════════════════════════════════════


class NavButton(QPushButton):
    """
    Sidebar nav button with custom-painted active indicator and smooth hover.
    """

    def __init__(self, icon: str, label: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("_NavButton")
        self._icon = icon
        self._label = label
        self._active = False
        self._hover = False
        self._radius = 10

        self.setText(f"  {icon}   {label}")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(44)

        font = QFont("Segoe UI", 10)
        font.setWeight(QFont.Weight.Medium)
        self.setFont(font)

    @property
    def active(self):
        return self._active

    def set_active(self, active: bool):
        self._active = active
        if active:
            f = self.font()
            f.setWeight(QFont.Weight.DemiBold)
            self.setFont(f)
        else:
            f = self.font()
            f.setWeight(QFont.Weight.Medium)
            self.setFont(f)
        self.update()

    def enterEvent(self, event):
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        rect = QRectF(4, 1, w - 8, h - 2)
        r = self._radius

        if self._active:
            # Active state — soft accent bg + left indicator bar
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(Tok.ACCENT_SOFT))
            p.drawRoundedRect(rect, r, r)

            # Left indicator bar
            bar_rect = QRectF(2, h * 0.2, 3, h * 0.6)
            p.setBrush(QBrush(Tok.ACCENT))
            p.drawRoundedRect(bar_rect, 1.5, 1.5)

            # Text in accent color
            fg = Tok.ACCENT
        elif self._hover:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(Tok.BG_HOVER))
            p.drawRoundedRect(rect, r, r)
            fg = Tok.TEXT
        else:
            fg = Tok.TEXT_DIM

        # Draw text
        p.setPen(QPen(fg))
        p.setFont(self.font())
        text_rect = QRectF(18, 0, w - 24, h)
        p.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self.text())
        p.end()


# ═════════════════════════════════════════════════════════════════════════════
#  Divider — subtle horizontal line
# ═════════════════════════════════════════════════════════════════════════════


class Divider(QWidget):
    """A 1px themed horizontal divider."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setFixedHeight(1)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setPen(QPen(Tok.BORDER, 1))
        p.drawLine(12, 0, self.width() - 12, 0)
        p.end()
