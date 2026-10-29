"""Cursor Motion Studio — Main Application

Ultra-smooth, modern desktop application with interactive clickable cards,
smart human-intervention auto-pause, real-time motion pattern preview canvas,
and premium glassmorphism styling with dark and light themes.
"""

from __future__ import annotations

import collections
import math
import os
import sys
import time
from typing import Optional

from PySide6.QtCore import (
    QEvent,
    QPointF,
    QRectF,
    QSize,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QIcon,
    QKeySequence,
    QLinearGradient,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
    QShortcut,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

import config
from motion_engine import MotionCalculator, MotionWorker


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller bundle."""
    try:
        base_path = sys._MEIPASS  # type: ignore
    except AttributeError:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


# ---------------------------------------------------------------------------
# Theme Stylesheets (Midnight Luxe & Aurora Glass)
# ---------------------------------------------------------------------------

DARK_THEME_STYLESHEET = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #090d16,
        stop:0.28 #0e1526,
        stop:0.68 #131b2e,
        stop:1 #0a0d17);
}

QWidget#CentralContainer {
    background: transparent;
}

QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    border: none;
    background: rgba(255, 255, 255, 0.04);
    width: 6px;
    margin: 2px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.22);
    min-height: 28px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(255, 255, 255, 0.42);
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Frosted Glass Cards with Specular Highlights */
QFrame.GlassCard {
    background-color: rgba(18, 24, 43, 0.78);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-top: 1px solid rgba(255, 255, 255, 0.17);
    border-radius: 14px;
}

QLabel {
    border: none;
    background: transparent;
}

QLabel#AppMainTitle {
    color: #f8fafc;
    font-size: 16px;
    font-weight: 800;
    letter-spacing: 0.4px;
}

QLabel#AppSubTitle {
    color: #94a3b8;
    font-size: 11px;
    font-weight: 500;
}

QLabel#BadgePro {
    color: #ffffff;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #8b5cf6);
    border-radius: 5px;
    font-size: 10px;
    font-weight: 800;
    padding: 2px 7px;
}

QLabel#SectionHeader {
    color: #a5b4fc;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.7px;
}

QLabel#TimerValueDisplay {
    color: #ffffff;
    font-size: 34px;
    font-weight: 800;
    font-family: 'Consolas', 'Segoe UI', monospace;
}

/* Preset Duration Pills */
QPushButton.PresetPill {
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 9px;
    color: #cbd5e1;
    font-size: 11px;
    font-weight: 700;
    padding: 6px 7px;
}
QPushButton.PresetPill:hover {
    background-color: rgba(99, 102, 241, 0.22);
    border-color: #818cf8;
    color: #ffffff;
}
QPushButton.PresetPill[selected="true"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f46e5, stop:1 #6366f1);
    border-color: #a5b4fc;
    color: #ffffff;
}

/* Quick Mode Switcher Pills in Preview Card */
QPushButton.QuickPreviewPill {
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 7px;
    color: #cbd5e1;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 8px;
}
QPushButton.QuickPreviewPill:hover {
    background-color: rgba(99, 102, 241, 0.26);
    border-color: #818cf8;
    color: #ffffff;
}
QPushButton.QuickPreviewPill[selected="true"] {
    background-color: rgba(99, 102, 241, 0.38);
    border: 1px solid #818cf8;
    color: #ffffff;
}

/* Speed Preset Pills */
QPushButton.SpeedPill {
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 7px;
    color: #cbd5e1;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 7px;
}
QPushButton.SpeedPill:hover {
    background-color: rgba(99, 102, 241, 0.25);
    border-color: #818cf8;
    color: #ffffff;
}
QPushButton.SpeedPill[selected="true"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f46e5, stop:1 #8b5cf6);
    border: 1px solid #a5b4fc;
    color: #ffffff;
}

/* SpinBox */
QSpinBox {
    background-color: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 8px;
    color: #f8fafc;
    font-size: 12px;
    font-weight: 700;
    padding: 3px 6px;
    min-width: 82px;
}
QSpinBox:hover {
    border-color: #818cf8;
}
QSpinBox::up-button, QSpinBox::down-button {
    background-color: rgba(255, 255, 255, 0.08);
    border: none;
    width: 16px;
    border-radius: 3px;
    margin: 1px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: rgba(99, 102, 241, 0.35);
}

/* Progress Bar */
QProgressBar {
    background-color: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 4px;
    height: 7px;
    text-align: center;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f46e5, stop:0.5 #8b5cf6, stop:1 #06b6d4);
    border-radius: 4px;
}

/* Hero Action Buttons */
QPushButton#StartActionBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4338ca, stop:0.5 #6366f1, stop:1 #06b6d4);
    color: #ffffff;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.6px;
    border: 1px solid rgba(255, 255, 255, 0.22);
    border-radius: 12px;
    padding: 11px 18px;
    min-height: 26px;
}
QPushButton#StartActionBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3730a3, stop:0.5 #4f46e5, stop:1 #0891b2);
    border-color: rgba(255, 255, 255, 0.38);
}
QPushButton#StartActionBtn:pressed {
    background: #312e81;
}
QPushButton#StartActionBtn:disabled {
    background: rgba(30, 41, 59, 0.6);
    color: #64748b;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

QPushButton#StopActionBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #dc2626, stop:1 #f43f5e);
    color: #ffffff;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.6px;
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 12px;
    padding: 11px 18px;
    min-height: 26px;
}
QPushButton#StopActionBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #b91c1c, stop:1 #e11d48);
}
QPushButton#StopActionBtn:disabled {
    background: rgba(30, 41, 59, 0.6);
    color: #64748b;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

/* Theme Toggle Button */
QPushButton#ThemeToggleBtn {
    background-color: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 8px;
    color: #cbd5e1;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 9px;
}
QPushButton#ThemeToggleBtn:hover {
    background-color: rgba(255, 255, 255, 0.15);
    border-color: #818cf8;
    color: #ffffff;
}

/* Status Pill */
QLabel#StatusPillLabel {
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.5px;
}

/* Checkbox */
QCheckBox {
    color: #f1f5f9;
    font-size: 12px;
    font-weight: 700;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1.5px solid #6366f1;
    background-color: rgba(15, 23, 42, 0.8);
}
QCheckBox::indicator:hover {
    border-color: #818cf8;
    background-color: rgba(30, 41, 75, 0.8);
}
QCheckBox::indicator:checked {
    background-color: #6366f1;
}

/* Telemetry Chips & Tech Stack in Specs Card (Dark Theme) */
QFrame#TelemetryChip {
    background-color: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
}
QLabel#TechChip {
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 6px;
    color: #cbd5e1;
    font-size: 9px;
    font-weight: 700;
    padding: 3px 7px;
}
QLabel#SafetyHintLabel {
    color: #818cf8;
    font-size: 10px;
    font-style: italic;
}
"""


LIGHT_THEME_STYLESHEET = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #eef2f8,
        stop:0.35 #e0e7f6,
        stop:0.7 #ede8f7,
        stop:1 #f3f0fa);
}

QWidget#CentralContainer {
    background: transparent;
}

QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    border: none;
    background: rgba(0, 0, 0, 0.04);
    width: 6px;
    margin: 2px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: rgba(0, 0, 0, 0.22);
    min-height: 28px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(0, 0, 0, 0.4);
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Frosted White Glass Cards */
QFrame.GlassCard {
    background-color: rgba(255, 255, 255, 0.76);
    border: 1.5px solid rgba(255, 255, 255, 0.95);
    border-radius: 14px;
}

QLabel {
    border: none;
    background: transparent;
}

QLabel#AppMainTitle {
    color: #1e1b4b;
    font-size: 16px;
    font-weight: 800;
    letter-spacing: 0.4px;
}

QLabel#AppSubTitle {
    color: #4338ca;
    font-size: 11px;
    font-weight: 600;
}

QLabel#BadgePro {
    color: #ffffff;
    background-color: #6366f1;
    border-radius: 5px;
    font-size: 10px;
    font-weight: 800;
    padding: 2px 7px;
}

QLabel#SectionHeader {
    color: #312e81;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.7px;
}

QLabel#TimerValueDisplay {
    color: #1e1b4b;
    font-size: 34px;
    font-weight: 800;
    font-family: 'Consolas', 'Segoe UI', monospace;
}

/* Preset Duration Pills */
QPushButton.PresetPill {
    background-color: rgba(255, 255, 255, 0.88);
    border: 1.5px solid rgba(255, 255, 255, 0.95);
    border-radius: 9px;
    color: #374151;
    font-size: 11px;
    font-weight: 700;
    padding: 6px 7px;
}
QPushButton.PresetPill:hover {
    background-color: #ffffff;
    border-color: #818cf8;
    color: #4338ca;
}
QPushButton.PresetPill[selected="true"] {
    background-color: #6366f1;
    border-color: #4f46e5;
    color: #ffffff;
}

/* Quick Mode Switcher Pills in Preview Card */
QPushButton.QuickPreviewPill {
    background-color: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(203, 213, 225, 0.8);
    border-radius: 7px;
    color: #475569;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 8px;
}
QPushButton.QuickPreviewPill:hover {
    background-color: #ffffff;
    border-color: #818cf8;
    color: #312e81;
}
QPushButton.QuickPreviewPill[selected="true"] {
    background-color: #e0e7ff;
    border: 1px solid #6366f1;
    color: #4338ca;
}

/* Speed Preset Pills */
QPushButton.SpeedPill {
    background-color: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(203, 213, 225, 0.85);
    border-radius: 7px;
    color: #475569;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 7px;
}
QPushButton.SpeedPill:hover {
    background-color: #ffffff;
    border-color: #818cf8;
    color: #312e81;
}
QPushButton.SpeedPill[selected="true"] {
    background-color: #6366f1;
    border: 1px solid #4f46e5;
    color: #ffffff;
}

/* SpinBox */
QSpinBox {
    background-color: rgba(255, 255, 255, 0.95);
    border: 1.5px solid rgba(203, 213, 225, 0.85);
    border-radius: 8px;
    color: #1f2937;
    font-size: 12px;
    font-weight: 700;
    padding: 3px 6px;
    min-width: 82px;
}
QSpinBox:hover {
    border-color: #818cf8;
}
QSpinBox::up-button, QSpinBox::down-button {
    background-color: rgba(241, 245, 249, 0.9);
    border: none;
    width: 16px;
    border-radius: 3px;
    margin: 1px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: rgba(99, 102, 241, 0.2);
}

/* Progress Bar */
QProgressBar {
    background-color: rgba(226, 232, 240, 0.85);
    border: none;
    border-radius: 4px;
    height: 7px;
    text-align: center;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #ec4899);
    border-radius: 4px;
}

/* Hero Action Buttons */
QPushButton#StartActionBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f46e5, stop:0.5 #6366f1, stop:1 #06b6d4);
    color: #ffffff;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.6px;
    border: none;
    border-radius: 12px;
    padding: 11px 18px;
    min-height: 26px;
}
QPushButton#StartActionBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4338ca, stop:0.5 #4f46e5, stop:1 #0891b2);
}
QPushButton#StartActionBtn:pressed {
    background: #3730a3;
}
QPushButton#StartActionBtn:disabled {
    background: rgba(148, 163, 184, 0.65);
    color: #f1f5f9;
}

QPushButton#StopActionBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ef4444, stop:1 #f43f5e);
    color: #ffffff;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.6px;
    border: none;
    border-radius: 12px;
    padding: 11px 18px;
    min-height: 26px;
}
QPushButton#StopActionBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #dc2626, stop:1 #e11d48);
}
QPushButton#StopActionBtn:disabled {
    background: rgba(203, 213, 225, 0.65);
    color: #94a3b8;
}

/* Theme Toggle Button */
QPushButton#ThemeToggleBtn {
    background-color: rgba(255, 255, 255, 0.88);
    border: 1px solid rgba(203, 213, 225, 0.85);
    border-radius: 8px;
    color: #374151;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 9px;
}
QPushButton#ThemeToggleBtn:hover {
    background-color: #ffffff;
    border-color: #818cf8;
    color: #1e1b4b;
}

/* Status Pill */
QLabel#StatusPillLabel {
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.5px;
}

/* Checkbox */
QCheckBox {
    color: #1e1b4b;
    font-size: 12px;
    font-weight: 700;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1.5px solid #6366f1;
    background-color: #ffffff;
}
QCheckBox::indicator:hover {
    border-color: #4338ca;
    background-color: #f5f3ff;
}
QCheckBox::indicator:checked {
    background-color: #6366f1;
}

/* Telemetry Chips & Tech Stack in Specs Card (Light Theme) */
QFrame#TelemetryChip {
    background-color: rgba(255, 255, 255, 0.88);
    border: 1px solid rgba(203, 213, 225, 0.85);
    border-radius: 8px;
}
QLabel#TechChip {
    background-color: rgba(241, 245, 249, 0.95);
    border: 1px solid rgba(203, 213, 225, 0.85);
    border-radius: 6px;
    color: #334155;
    font-size: 9px;
    font-weight: 700;
    padding: 3px 7px;
}
QLabel#SafetyHintLabel {
    color: #4f46e5;
    font-size: 10px;
    font-style: italic;
}
"""


# ---------------------------------------------------------------------------
# Motion Preview Canvas Widget
# ---------------------------------------------------------------------------

class MotionPreviewCanvas(QWidget):
    """Real-time motion pattern simulation canvas.
    Displays dynamic movement patterns for Circle, Horizontal Sweep, Rapid Shake,
    Stealth Micro-Shake, and other modes before starting cursor movement.
    Provides clear visual trajectory, animated cursor vector, and telemetry HUD
    without moving the actual desktop cursor.
    """

    def __init__(
        self,
        mode: str = config.MODE_CIRCLE,
        speed_multiplier: float = config.DEFAULT_SPEED_MULTIPLIER,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.mode = mode
        self.speed_multiplier = speed_multiplier
        self.setMinimumHeight(132)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Simulation calculator anchored at (0, 0)
        self.calc = MotionCalculator(anchor_x=0, anchor_y=0, radius=config.OPTIMAL_AVERAGE_RADIUS_PX)

        # High-refresh animation loop (60 FPS)
        self.sim_time: float = 0.0
        self.trail: collections.deque = collections.deque(maxlen=42)
        self.is_dark_theme: bool = True

        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start()

    def set_speed_multiplier(self, multiplier: float):
        self.speed_multiplier = max(0.5, min(multiplier, 10.0))
        self.update()

    def set_mode(self, mode: str):
        if self.mode != mode:
            self.mode = mode
            self.trail.clear()
            self.update()

    def set_dark_theme(self, is_dark: bool):
        self.is_dark_theme = is_dark
        self.update()

    def _on_tick(self):
        if not self.isVisible():
            return
        self.sim_time += 0.016 * self.speed_multiplier
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        w = float(self.width())
        h = float(self.height())
        cx = w / 2.0
        cy = h / 2.0

        meta = config.MODE_DETAILS.get(self.mode, {})
        mode_color_hex = meta.get("color", "#6366f1")
        accent_color = QColor(mode_color_hex)

        # 1. Canvas Background
        rect = QRectF(0, 0, w, h)
        if self.is_dark_theme:
            bg_grad = QLinearGradient(0, 0, 0, h)
            bg_grad.setColorAt(0.0, QColor(9, 14, 26, 245))
            bg_grad.setColorAt(1.0, QColor(14, 20, 36, 245))
            painter.setBrush(QBrush(bg_grad))
            painter.setPen(QPen(QColor(accent_color.red(), accent_color.green(), accent_color.blue(), 55), 1.2))
        else:
            bg_grad = QLinearGradient(0, 0, 0, h)
            bg_grad.setColorAt(0.0, QColor(241, 245, 249, 235))
            bg_grad.setColorAt(1.0, QColor(226, 232, 240, 235))
            painter.setBrush(QBrush(bg_grad))
            painter.setPen(QPen(QColor(accent_color.red(), accent_color.green(), accent_color.blue(), 75), 1.2))
        painter.drawRoundedRect(rect, 12, 12)

        # 2. Reticle & Safety Boundary Rings
        # Magnification scale: dynamically adapts to canvas height (3.5x to 4.8x)
        scale = min(4.8, max(3.5, (h - 48.0) / 32.0))

        # Faint dashed crosshairs
        cross_pen = QPen(
            QColor(255, 255, 255, 22) if self.is_dark_theme else QColor(30, 41, 59, 25),
            1,
            Qt.DashLine,
        )
        painter.setPen(cross_pen)
        painter.drawLine(QPointF(cx - 70, cy), QPointF(cx + 70, cy))
        painter.drawLine(QPointF(cx, cy - 54), QPointF(cx, cy + 54))

        # Concentric reference boundary rings (5px, 10px, 15px max limit)
        for r_px, alpha, style in [(5, 18, Qt.DotLine), (10, 28, Qt.DashLine), (15, 65, Qt.DashDotLine)]:
            ring_r = r_px * scale
            ring_pen = QPen(
                QColor(accent_color.red(), accent_color.green(), accent_color.blue(), alpha),
                1.0,
                style,
            )
            painter.setPen(ring_pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QPointF(cx, cy), ring_r, ring_r)

        # Subtle boundary label
        painter.setFont(QFont("Segoe UI", 7, QFont.Bold))
        painter.setPen(QColor(255, 255, 255, 45) if self.is_dark_theme else QColor(71, 85, 105, 75))
        painter.drawText(QRectF(cx + 15 * scale + 4, cy - 8, 80, 16), Qt.AlignLeft | Qt.AlignVCenter, "±15px limit")

        # Center anchor marker
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 180) if self.is_dark_theme else QColor(30, 41, 59, 180)))
        painter.drawEllipse(QPointF(cx, cy), 2.2, 2.2)

        # 2b. Static Trajectory Guide Geometry
        # Visualizes the ideal mathematical path with faint dashed accent lines
        guide_alpha = 42 if self.is_dark_theme else 60
        guide_pen = QPen(
            QColor(accent_color.red(), accent_color.green(), accent_color.blue(), guide_alpha),
            1.2,
            Qt.DashLine,
        )
        painter.setPen(guide_pen)
        painter.setBrush(Qt.NoBrush)

        m_lower = self.mode.lower()
        if "circle" in m_lower:
            orbit_r = self.calc.radius * scale
            painter.drawEllipse(QPointF(cx, cy), orbit_r, orbit_r)
        elif "horizontal" in m_lower or "sweep" in m_lower:
            sweep_r = self.calc.radius * scale
            painter.drawLine(QPointF(cx - sweep_r, cy), QPointF(cx + sweep_r, cy))
            painter.drawLine(QPointF(cx - sweep_r, cy - 4), QPointF(cx - sweep_r, cy + 4))
            painter.drawLine(QPointF(cx + sweep_r, cy - 4), QPointF(cx + sweep_r, cy + 4))
        elif "shake" in m_lower:
            shake_r = max(3.0, min(self.calc.radius * 0.55, 7.5)) * scale
            painter.drawEllipse(QPointF(cx, cy), shake_r, shake_r * 0.9)
        elif "stealth" in m_lower or "ghost" in m_lower or "micro" in m_lower or "1px" in m_lower:
            micro_r = 1.0 * scale
            painter.drawEllipse(QPointF(cx, cy), micro_r, micro_r)

        # 3. Compute Current Mathematical Simulation Offset
        dx, dy = self.calc.get_relative_offset(self.mode, self.sim_time)
        curr_x = cx + dx * scale
        curr_y = cy + dy * scale
        self.trail.append((curr_x, curr_y))

        # 4. Draw Motion Trail with Fading Alpha
        trail_len = len(self.trail)
        if trail_len > 1:
            for i in range(1, trail_len):
                p0 = self.trail[i - 1]
                p1 = self.trail[i]
                frac = i / float(trail_len)
                alpha = int(frac * 210)
                width = 1.0 + frac * 1.8
                trail_color = QColor(accent_color.red(), accent_color.green(), accent_color.blue(), alpha)
                painter.setPen(QPen(trail_color, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawLine(QPointF(p0[0], p0[1]), QPointF(p1[0], p1[1]))

        # 5. Draw Glowing Cursor Indicator at (curr_x, curr_y)
        # Soft radial neon glow
        glow_grad = QRadialGradient(curr_x, curr_y, 16)
        glow_grad.setColorAt(0.0, QColor(accent_color.red(), accent_color.green(), accent_color.blue(), 130))
        glow_grad.setColorAt(1.0, QColor(accent_color.red(), accent_color.green(), accent_color.blue(), 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(glow_grad))
        painter.drawEllipse(QPointF(curr_x, curr_y), 16, 16)

        # Vector Cursor Pointer
        cursor_path = QPainterPath()
        cursor_path.moveTo(curr_x, curr_y)
        cursor_path.lineTo(curr_x, curr_y + 13)
        cursor_path.lineTo(curr_x + 3.6, curr_y + 9.8)
        cursor_path.lineTo(curr_x + 6.8, curr_y + 15.2)
        cursor_path.lineTo(curr_x + 9.2, curr_y + 14.0)
        cursor_path.lineTo(curr_x + 6.0, curr_y + 8.8)
        cursor_path.lineTo(curr_x + 11.0, curr_y + 8.8)
        cursor_path.closeSubpath()

        # Drop shadow for cursor
        shadow_path = QPainterPath(cursor_path)
        shadow_path.translate(1.0, 1.2)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 75)))
        painter.drawPath(shadow_path)

        # Crisp white cursor body
        painter.setPen(QPen(QColor(15, 23, 42, 220), 1.2))
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawPath(cursor_path)

        # 6. HUD Overlays
        # Top-left HUD badge: "● PREVIEW: CIRCLE ORBIT"
        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        # Pulsing green dot
        pulse = 0.5 + 0.5 * math.sin(self.sim_time * 6.0)
        dot_alpha = int(140 + 115 * pulse)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(34, 197, 94, dot_alpha)))
        painter.drawEllipse(QPointF(14, 16), 3.5, 3.5)

        title_text = f"PREVIEW: {meta.get('title', self.mode).upper()}"
        painter.setPen(QColor(248, 250, 252, 230) if self.is_dark_theme else QColor(30, 41, 59, 230))
        painter.drawText(QRectF(22, 9, 210, 16), Qt.AlignLeft | Qt.AlignVCenter, title_text)

        # Top-right HUD: Telemetry (dx, dy, radius, speed)
        speed_tag = f"MAX {self.speed_multiplier:.1f}x ⚡" if self.speed_multiplier >= 5.0 else f"{self.speed_multiplier:.1f}x"
        hud_telemetry = f"dX: {dx:+4.1f}px  dY: {dy:+4.1f}px  |  {speed_tag}"
        painter.setFont(QFont("Consolas", 8, QFont.Bold))
        if self.is_dark_theme:
            painter.setPen(QColor(accent_color.red(), accent_color.green(), accent_color.blue(), 240))
        else:
            painter.setPen(QColor(30, 41, 59, 230))
        painter.drawText(QRectF(w - 260, 9, 248, 16), Qt.AlignRight | Qt.AlignVCenter, hud_telemetry)

        # Bottom-left: Pattern dynamics tip
        tip_text = meta.get("preview_tip", "Bounded mathematical motion")
        painter.setFont(QFont("Segoe UI", 7, QFont.Normal))
        painter.setPen(QColor(148, 163, 184, 210) if self.is_dark_theme else QColor(100, 116, 139, 210))
        painter.drawText(QRectF(14, h - 22, 260, 16), Qt.AlignLeft | Qt.AlignVCenter, tip_text)

        # Bottom-right: Simulation reassurance badge
        status_text = "SIMULATED • 0 HARDWARE CLICKS"
        painter.setFont(QFont("Segoe UI", 7, QFont.Bold))
        painter.setPen(QColor(52, 211, 153, 210) if self.is_dark_theme else QColor(5, 150, 105, 210))
        painter.drawText(QRectF(w - 210, h - 22, 198, 16), Qt.AlignRight | Qt.AlignVCenter, status_text)


# ---------------------------------------------------------------------------
# Interactive Mode Card Widget
# ---------------------------------------------------------------------------

class ModeCardWidget(QFrame):
    """Interactive clickable card widget for selecting a cursor movement mode."""

    card_selected = Signal(str)

    def __init__(
        self,
        mode_key: str,
        title: str,
        icon: str,
        desc: str,
        tag: str,
        tag_bg: str,
        tag_fg: str,
        color: str,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.mode_key = mode_key
        self.title = title
        self.icon = icon
        self.desc = desc
        self.tag = tag
        self.tag_bg = tag_bg
        self.tag_fg = tag_fg
        self.accent_color = color
        self.is_selected = False
        self.is_dark_theme = True

        self.setCursor(Qt.PointingHandCursor)
        self._setup_ui()
        self.update_visual_state()

    def _setup_ui(self):
        self.setObjectName("ModeCardFrame")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # Left: Icon inside rounded circle
        self.icon_badge = QLabel(self.icon)
        self.icon_badge.setFixedSize(34, 34)
        self.icon_badge.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon_badge)

        # Middle: Title and description
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        self.title_label = QLabel(self.title)
        text_layout.addWidget(self.title_label)

        self.desc_label = QLabel(self.desc)
        self.desc_label.setWordWrap(True)
        text_layout.addWidget(self.desc_label)

        layout.addLayout(text_layout, 1)

        # Right: Tag pill + selection radio circle
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)
        right_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.tag_pill = QLabel(self.tag)
        self.tag_pill.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.tag_pill)

        self.radio_indicator = QLabel("○")
        self.radio_indicator.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.radio_indicator)

        layout.addLayout(right_layout)

    def set_theme(self, is_dark: bool):
        self.is_dark_theme = is_dark
        self.update_visual_state()

    def set_selected(self, selected: bool):
        self.is_selected = selected
        self.update_visual_state()

    def update_visual_state(self, is_hover: bool = False):
        if self.is_dark_theme:
            # Dark Theme Palette
            if self.is_selected:
                self.setStyleSheet(
                    f"QFrame#ModeCardFrame {{ "
                    f"   background-color: rgba(30, 42, 75, 0.95); "
                    f"   border: 2px solid {self.accent_color}; "
                    f"   border-radius: 12px; "
                    f"}} "
                    f"QLabel {{ border: none; background: transparent; }}"
                )
                self.icon_badge.setStyleSheet(
                    f"font-size: 17px; background-color: rgba(99, 102, 241, 0.25); "
                    f"border: 1px solid {self.accent_color}; border-radius: 17px;"
                )
                self.title_label.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: 800;")
                self.desc_label.setStyleSheet("color: #cbd5e1; font-size: 10px; font-weight: 500;")
                self.radio_indicator.setText("●")
                self.radio_indicator.setStyleSheet(f"color: {self.accent_color}; font-size: 15px; font-weight: 800;")
            elif is_hover:
                self.setStyleSheet(
                    f"QFrame#ModeCardFrame {{ "
                    f"   background-color: rgba(30, 41, 70, 0.85); "
                    f"   border: 1.5px solid #818cf8; "
                    f"   border-radius: 12px; "
                    f"}} "
                    f"QLabel {{ border: none; background: transparent; }}"
                )
                self.icon_badge.setStyleSheet(
                    "font-size: 17px; background-color: rgba(255, 255, 255, 0.10); "
                    "border-radius: 17px; border: none;"
                )
                self.title_label.setStyleSheet("color: #f8fafc; font-size: 13px; font-weight: 700;")
                self.desc_label.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: 500;")
                self.radio_indicator.setText("○")
                self.radio_indicator.setStyleSheet("color: #818cf8; font-size: 14px;")
            else:
                self.setStyleSheet(
                    "QFrame#ModeCardFrame { "
                    "   background-color: rgba(22, 30, 52, 0.65); "
                    "   border: 1px solid rgba(255, 255, 255, 0.08); "
                    "   border-radius: 12px; "
                    "} "
                    "QLabel { border: none; background: transparent; }"
                )
                self.icon_badge.setStyleSheet(
                    "font-size: 17px; background-color: rgba(255, 255, 255, 0.05); "
                    "border-radius: 17px; border: none;"
                )
                self.title_label.setStyleSheet("color: #f1f5f9; font-size: 13px; font-weight: 700;")
                self.desc_label.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: 500;")
                self.radio_indicator.setText("○")
                self.radio_indicator.setStyleSheet("color: #475569; font-size: 14px;")

            self.tag_pill.setStyleSheet(
                f"background-color: {self.tag_bg}; color: {self.tag_fg}; "
                f"border-radius: 5px; font-size: 9px; font-weight: 700; padding: 2px 6px; border: none;"
            )
        else:
            # Light Theme Palette
            if self.is_selected:
                self.setStyleSheet(
                    "QFrame#ModeCardFrame { "
                    "   background-color: #ffffff; "
                    "   border: 2px solid #6366f1; "
                    "   border-radius: 12px; "
                    "} "
                    "QLabel { border: none; background: transparent; }"
                )
                self.icon_badge.setStyleSheet(
                    "font-size: 17px; background-color: #e0e7ff; "
                    "border: 1px solid #c7d2fe; border-radius: 17px;"
                )
                self.title_label.setStyleSheet("color: #4338ca; font-size: 13px; font-weight: 800;")
                self.desc_label.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 500;")
                self.radio_indicator.setText("●")
                self.radio_indicator.setStyleSheet("color: #6366f1; font-size: 15px; font-weight: 800;")
            elif is_hover:
                self.setStyleSheet(
                    "QFrame#ModeCardFrame { "
                    "   background-color: rgba(255, 255, 255, 0.94); "
                    "   border: 1.5px solid #818cf8; "
                    "   border-radius: 12px; "
                    "} "
                    "QLabel { border: none; background: transparent; }"
                )
                self.icon_badge.setStyleSheet(
                    "font-size: 17px; background-color: rgba(99, 102, 241, 0.16); "
                    "border-radius: 17px; border: none;"
                )
                self.title_label.setStyleSheet("color: #312e81; font-size: 13px; font-weight: 700;")
                self.desc_label.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 500;")
                self.radio_indicator.setText("○")
                self.radio_indicator.setStyleSheet("color: #818cf8; font-size: 14px;")
            else:
                self.setStyleSheet(
                    "QFrame#ModeCardFrame { "
                    "   background-color: rgba(255, 255, 255, 0.82); "
                    "   border: 1.5px solid rgba(255, 255, 255, 0.95); "
                    "   border-radius: 12px; "
                    "} "
                    "QLabel { border: none; background: transparent; }"
                )
                self.icon_badge.setStyleSheet(
                    "font-size: 17px; background-color: rgba(241, 245, 249, 0.9); "
                    "border-radius: 17px; border: none;"
                )
                self.title_label.setStyleSheet("color: #1e1b4b; font-size: 13px; font-weight: 700;")
                self.desc_label.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 500;")
                self.radio_indicator.setText("○")
                self.radio_indicator.setStyleSheet("color: #cbd5e1; font-size: 14px;")

            meta = config.MODE_DETAILS.get(self.mode_key, {})
            tag_bg_light = meta.get("tag_bg_light", "#e0e7ff")
            tag_fg_light = meta.get("tag_fg_light", "#4338ca")
            self.tag_pill.setStyleSheet(
                f"background-color: {tag_bg_light}; color: {tag_fg_light}; "
                f"border-radius: 5px; font-size: 9px; font-weight: 700; padding: 2px 6px; border: none;"
            )

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.card_selected.emit(self.mode_key)
        super().mousePressEvent(event)

    def enterEvent(self, event):
        if not self.is_selected:
            self.update_visual_state(is_hover=True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.is_selected:
            self.update_visual_state(is_hover=False)
        super().leaveEvent(event)


# ---------------------------------------------------------------------------
# Main Application Window
# ---------------------------------------------------------------------------

class CursorMotionStudio(QMainWindow):
    """Main Application Window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.APP_NAME)
        self.resize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.setMinimumSize(config.MIN_WINDOW_WIDTH, config.MIN_WINDOW_HEIGHT)

        # Set Window Icon
        icon_path = resource_path(os.path.join("assets", "icons", "app_icon.ico"))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Active Theme (Default: Dark Obsidian Luxe)
        self.is_dark_theme: bool = True

        # Motion worker & timer variables
        self.worker: Optional[MotionWorker] = None
        self.timer = QTimer(self)
        self.timer.setInterval(250)
        self.timer.timeout.connect(self._on_timer_tick)

        self.duration_seconds: int = config.DEFAULT_TIMER_MINUTES * 60
        self.start_timestamp: float = 0.0
        self.is_running: bool = False
        self.is_infinite: bool = False
        self.selected_mode: str = config.MODE_CIRCLE

        self.mode_cards: dict[str, ModeCardWidget] = {}
        self.preset_buttons: dict[int, QPushButton] = {}
        self.quick_preview_buttons: dict[str, QPushButton] = {}
        self.speed_buttons: dict[float, QPushButton] = {}
        self.speed_multiplier: float = config.DEFAULT_SPEED_MULTIPLIER

        # Responsive layout state
        self._is_wide_layout: bool = False
        self._layout_initialized: bool = False
        self.specs_subtitles: list[QLabel] = []
        self.specs_version_lbl: Optional[QLabel] = None

        self._setup_ui()
        self._setup_shortcuts()
        self.apply_theme(dark=True)
        self._update_status("Ready", "#e0e7ff", "#4338ca")

    def _setup_ui(self):
        # Central widget with scroll area for scaling safety
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setCentralWidget(self.scroll)

        self.container = QWidget()
        self.container.setObjectName("CentralContainer")
        self.scroll.setWidget(self.container)

        self.root_layout = QVBoxLayout(self.container)
        self.root_layout.setContentsMargins(18, 16, 18, 16)
        self.root_layout.setSpacing(12)

        # -------------------------------------------------------------------
        # 1. Header Card (Spans full width in wide/maximized mode)
        # -------------------------------------------------------------------
        self.header_card = QFrame()
        self.header_card.setProperty("class", "GlassCard")
        self.header_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header_layout = QHBoxLayout(self.header_card)
        header_layout.setContentsMargins(14, 10, 14, 10)
        header_layout.setSpacing(8)
        header_layout.setAlignment(Qt.AlignVCenter)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        app_title = QLabel(config.APP_NAME)
        app_title.setObjectName("AppMainTitle")
        badge_pro = QLabel("PRO")
        badge_pro.setObjectName("BadgePro")
        badge_pro.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        title_row.addWidget(app_title)
        title_row.addWidget(badge_pro, 0, Qt.AlignVCenter)
        title_row.addStretch()

        subtitle = QLabel("Autonomous Keep-Alive & Motion Preview Studio")
        subtitle.setObjectName("AppSubTitle")
        title_col.addLayout(title_row)
        title_col.addWidget(subtitle)
        header_layout.addLayout(title_col)

        # Status badge pill
        self.status_badge = QLabel("READY")
        self.status_badge.setObjectName("StatusPillLabel")
        self.status_badge.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        header_layout.addWidget(self.status_badge, 0, Qt.AlignVCenter)

        # Theme switcher toggle button
        self.theme_toggle_btn = QPushButton("🌙 Dark")
        self.theme_toggle_btn.setObjectName("ThemeToggleBtn")
        self.theme_toggle_btn.setCursor(Qt.PointingHandCursor)
        self.theme_toggle_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.theme_toggle_btn.setToolTip("Toggle Dark / Light Theme")
        self.theme_toggle_btn.clicked.connect(self._toggle_theme)
        header_layout.addWidget(self.theme_toggle_btn, 0, Qt.AlignVCenter)

        self.root_layout.addWidget(self.header_card)

        # Responsive layout containers (Compact single-column & Wide dual-column)
        self.compact_vbox = QVBoxLayout()
        self.compact_vbox.setSpacing(12)
        self.root_layout.addLayout(self.compact_vbox)

        self.wide_hbox = QHBoxLayout()
        self.wide_hbox.setSpacing(16)
        self.left_vbox = QVBoxLayout()
        self.left_vbox.setSpacing(12)
        self.right_vbox = QVBoxLayout()
        self.right_vbox.setSpacing(12)
        self.wide_hbox.addLayout(self.left_vbox, 1)
        self.wide_hbox.addLayout(self.right_vbox, 1)
        self.root_layout.addLayout(self.wide_hbox)
        self.root_layout.addStretch(1)

        # -------------------------------------------------------------------
        # 2. Timer Card (Duration Config & Countdown Display)
        # -------------------------------------------------------------------
        self.timer_card = QFrame()
        self.timer_card.setProperty("class", "GlassCard")
        timer_layout = QVBoxLayout(self.timer_card)
        timer_layout.setContentsMargins(14, 12, 14, 12)
        timer_layout.setSpacing(8)

        timer_header_row = QHBoxLayout()
        timer_header = QLabel("RUN DURATION & COUNTDOWN")
        timer_header.setObjectName("SectionHeader")
        timer_header_row.addWidget(timer_header)
        timer_header_row.addStretch()

        self.timer_spin = QSpinBox()
        self.timer_spin.setRange(config.MIN_TIMER_MINUTES, config.MAX_TIMER_MINUTES)
        self.timer_spin.setValue(config.DEFAULT_TIMER_MINUTES)
        self.timer_spin.setSuffix(" min")
        self.timer_spin.valueChanged.connect(self._on_timer_spin_changed)
        timer_header_row.addWidget(self.timer_spin)
        timer_layout.addLayout(timer_header_row)

        # Preset Duration Pills
        preset_row = QHBoxLayout()
        preset_row.setSpacing(5)
        presets = [("∞ Infinite", 0), ("15 Mins", 15), ("30 Mins", 30), ("1 Hour", 60), ("2 Hours", 120)]
        for label, val in presets:
            btn = QPushButton(label)
            btn.setProperty("class", "PresetPill")
            if val == config.DEFAULT_TIMER_MINUTES:
                btn.setProperty("selected", "true")
            else:
                btn.setProperty("selected", "false")
            btn.clicked.connect(lambda checked=False, v=val: self._set_timer_preset(v))
            preset_row.addWidget(btn)
            self.preset_buttons[val] = btn
        timer_layout.addLayout(preset_row)

        # Digital Countdown Readout
        timer_center_row = QHBoxLayout()
        self.timer_display = QLabel("00:15:00")
        self.timer_display.setObjectName("TimerValueDisplay")
        timer_center_row.addStretch()
        timer_center_row.addWidget(self.timer_display)
        timer_center_row.addStretch()
        timer_layout.addLayout(timer_center_row)

        self.timer_hint = QLabel("CLICK START TO KEEP SYSTEM ACTIVE & AWAKE")
        self.timer_hint.setStyleSheet("color: #818cf8; font-size: 10px; font-weight: 700; letter-spacing: 0.5px;")
        self.timer_hint.setAlignment(Qt.AlignCenter)
        timer_layout.addWidget(self.timer_hint)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        timer_layout.addWidget(self.progress_bar)

        # -------------------------------------------------------------------
        # 3. Motion Pattern Preview Canvas Card
        # -------------------------------------------------------------------
        self.preview_card = QFrame()
        self.preview_card.setProperty("class", "GlassCard")
        preview_layout = QVBoxLayout(self.preview_card)
        preview_layout.setContentsMargins(14, 12, 14, 12)
        preview_layout.setSpacing(8)

        # Preview header row with quick pattern preview pills
        preview_header_row = QHBoxLayout()
        preview_header = QLabel("MOTION PATTERN PREVIEW")
        preview_header.setObjectName("SectionHeader")
        preview_header_row.addWidget(preview_header)
        preview_header_row.addStretch()

        # Quick Preview Pills (Circle, Sweep, Shake, 1px Shake)
        quick_patterns = [
            ("⭕ Circle", config.MODE_CIRCLE),
            ("↔️ Sweep", config.MODE_HORIZONTAL),
            ("⚡ Shake", config.MODE_SHAKE),
            ("👻 1px Shake", config.MODE_STEALTH),
        ]
        for label, m_key in quick_patterns:
            btn = QPushButton(label)
            btn.setProperty("class", "QuickPreviewPill")
            btn.setCursor(Qt.PointingHandCursor)
            if m_key == self.selected_mode:
                btn.setProperty("selected", "true")
            else:
                btn.setProperty("selected", "false")
            btn.clicked.connect(lambda checked=False, k=m_key: self._on_quick_preview_clicked(k))
            preview_header_row.addWidget(btn)
            self.quick_preview_buttons[m_key] = btn

        preview_layout.addLayout(preview_header_row)

        # Real-time Simulation Canvas
        self.preview_canvas = MotionPreviewCanvas(
            mode=self.selected_mode,
            speed_multiplier=self.speed_multiplier,
            parent=self,
        )
        preview_layout.addWidget(self.preview_canvas)

        # Dynamic Speed Multiplier Row
        speed_row = QHBoxLayout()
        speed_row.setSpacing(5)
        speed_label = QLabel("SPEED MULTIPLIER")
        speed_label.setObjectName("SectionHeader")
        speed_row.addWidget(speed_label)
        speed_row.addStretch()

        for label, val in config.SPEED_PRESETS:
            btn = QPushButton(label)
            btn.setProperty("class", "SpeedPill")
            btn.setCursor(Qt.PointingHandCursor)
            if val == self.speed_multiplier:
                btn.setProperty("selected", "true")
            else:
                btn.setProperty("selected", "false")
            btn.clicked.connect(lambda checked=False, v=val: self._set_speed_preset(v))
            speed_row.addWidget(btn)
            self.speed_buttons[val] = btn

        preview_layout.addLayout(speed_row)

        # -------------------------------------------------------------------
        # 4. Select Motion Pattern Card (Interactive Clickable Mode Cards)
        # -------------------------------------------------------------------
        self.mode_card = QFrame()
        self.mode_card.setProperty("class", "GlassCard")
        mode_layout = QVBoxLayout(self.mode_card)
        mode_layout.setContentsMargins(14, 12, 14, 12)
        mode_layout.setSpacing(7)

        mode_header_row = QHBoxLayout()
        mode_header = QLabel("SELECT MOTION PATTERN")
        mode_header.setObjectName("SectionHeader")
        mode_header_row.addWidget(mode_header)
        mode_header_row.addStretch()
        safe_badge = QLabel("100% Zero Clicks")
        safe_badge.setStyleSheet("color: #34d399; font-size: 10px; font-weight: 700;")
        mode_header_row.addWidget(safe_badge)
        mode_layout.addLayout(mode_header_row)

        mode_order = [
            config.MODE_CIRCLE,
            config.MODE_HORIZONTAL,
            config.MODE_SHAKE,
            config.MODE_STEALTH,
            config.MODE_GENTLE,
            config.MODE_RANDOM,
        ]

        for m_key in mode_order:
            meta = config.MODE_DETAILS.get(m_key, {
                "title": f"{m_key} Mode",
                "icon": "✨",
                "tag": "ACTIVE",
                "tag_bg": "rgba(99, 102, 241, 0.2)",
                "tag_fg": "#818cf8",
                "color": "#6366f1",
                "desc": config.MODE_DESCRIPTIONS.get(m_key, ""),
            })

            card = ModeCardWidget(
                mode_key=m_key,
                title=meta["title"],
                icon=meta["icon"],
                desc=meta["desc"],
                tag=meta["tag"],
                tag_bg=meta["tag_bg"],
                tag_fg=meta["tag_fg"],
                color=meta.get("color", "#6366f1"),
            )
            card.card_selected.connect(self._on_mode_card_selected)
            if m_key == self.selected_mode:
                card.set_selected(True)

            self.mode_cards[m_key] = card
            mode_layout.addWidget(card)

        # -------------------------------------------------------------------
        # 5. Smart Auto-Pause Feature Card
        # -------------------------------------------------------------------
        self.pause_card = QFrame()
        self.pause_card.setProperty("class", "GlassCard")
        pause_layout = QVBoxLayout(self.pause_card)
        pause_layout.setContentsMargins(14, 10, 14, 10)
        pause_layout.setSpacing(4)

        self.auto_pause_check = QCheckBox("Auto-pause when I physically move the mouse")
        self.auto_pause_check.setChecked(True)
        self.auto_pause_check.setCursor(Qt.PointingHandCursor)
        self.auto_pause_check.toggled.connect(self._on_auto_pause_toggled)
        pause_layout.addWidget(self.auto_pause_check)

        self.pause_desc = QLabel("Temporarily pauses motion while you work, then automatically resumes after 5 seconds of inactivity.")
        self.pause_desc.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: 500; margin-left: 26px;")
        self.pause_desc.setWordWrap(True)
        pause_layout.addWidget(self.pause_desc)

        # -------------------------------------------------------------------
        # 6. Action Panel (Start / Stop + Emergency Hint)
        # -------------------------------------------------------------------
        self.actions_panel = QWidget()
        actions_panel_layout = QVBoxLayout(self.actions_panel)
        actions_panel_layout.setContentsMargins(0, 0, 0, 0)
        actions_panel_layout.setSpacing(6)

        actions_btn_row = QHBoxLayout()
        actions_btn_row.setSpacing(12)

        self.start_btn = QPushButton("▶  START MOTION (ENTER)")
        self.start_btn.setObjectName("StartActionBtn")
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.clicked.connect(self.start_motion)
        actions_btn_row.addWidget(self.start_btn, 3)

        self.stop_btn = QPushButton("⏹  STOP")
        self.stop_btn.setObjectName("StopActionBtn")
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_motion)
        actions_btn_row.addWidget(self.stop_btn, 1)

        actions_panel_layout.addLayout(actions_btn_row)

        self.safety_hint = QLabel("Emergency Stop: Press ESC or push mouse to any screen corner")
        self.safety_hint.setObjectName("SafetyHintLabel")
        self.safety_hint.setAlignment(Qt.AlignCenter)
        actions_panel_layout.addWidget(self.safety_hint)

        # -------------------------------------------------------------------
        # 7. Engine Telemetry & System Specs Card (Wide / Maximized View)
        # -------------------------------------------------------------------
        self.specs_card = self._create_specs_card()

        # Apply initial layout
        self._apply_responsive_layout(is_wide=False)

    def _create_specs_card(self) -> QFrame:
        """Creates the engine specifications and telemetry card for wide/maximized view."""
        card = QFrame()
        card.setProperty("class", "GlassCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        header_row = QHBoxLayout()
        header = QLabel("ENGINE SPECIFICATIONS & SAFETY")
        header.setObjectName("SectionHeader")
        header_row.addWidget(header)
        header_row.addStretch()
        self.specs_version_lbl = QLabel(f"v{config.APP_VERSION}")
        self.specs_version_lbl.setStyleSheet("color: #a5b4fc; font-size: 10px; font-weight: 700;")
        header_row.addWidget(self.specs_version_lbl)
        layout.addLayout(header_row)

        # 2x2 Telemetry Grid
        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(6)

        telemetry_items = [
            ("⚡ 250 Hz Pacing", "4ms hardware loop", "#38bdf8"),
            ("🛡️ Bounded Travel", "Strictly ≤ 15px radius", "#34d399"),
            ("👻 1-Pixel Precision", "Zero human visibility", "#c084fc"),
            ("🔒 100% Offline", "Zero network / telemetry", "#fbbf24"),
        ]
        self.specs_subtitles = []
        for idx, (title, subtitle, color) in enumerate(telemetry_items):
            box = QFrame()
            box.setObjectName("TelemetryChip")
            b_layout = QVBoxLayout(box)
            b_layout.setContentsMargins(8, 6, 8, 6)
            b_layout.setSpacing(2)
            t_lbl = QLabel(title)
            t_lbl.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: 800;")
            s_lbl = QLabel(subtitle)
            s_lbl.setStyleSheet("color: #94a3b8; font-size: 9px; font-weight: 500;")
            self.specs_subtitles.append(s_lbl)
            b_layout.addWidget(t_lbl)
            b_layout.addWidget(s_lbl)
            grid.addWidget(box, idx // 2, idx % 2)

        layout.addLayout(grid)

        # Tech Stack Pills Row
        tech_row = QHBoxLayout()
        tech_row.setSpacing(6)
        for item in config.TECH_STACK_ITEMS:
            chip = QLabel(f"{item['name']} {item['tag']}")
            chip.setObjectName("TechChip")
            tech_row.addWidget(chip)
        tech_row.addStretch()
        layout.addLayout(tech_row)

        return card

    def _apply_responsive_layout(self, is_wide: bool):
        """Seamlessly adapts layout between compact (single column) and wide (dual column)."""
        if is_wide == self._is_wide_layout and self._layout_initialized:
            return

        self._is_wide_layout = is_wide
        self._layout_initialized = True

        if is_wide:
            self.container.setMaximumWidth(1160)
            self.preview_canvas.setFixedHeight(190)

            # Remove from compact layout
            self.compact_vbox.removeWidget(self.timer_card)
            self.compact_vbox.removeWidget(self.preview_card)
            self.compact_vbox.removeWidget(self.mode_card)
            self.compact_vbox.removeWidget(self.pause_card)
            self.compact_vbox.removeWidget(self.actions_panel)

            # Add to wide columns
            self.left_vbox.addWidget(self.timer_card)
            self.left_vbox.addWidget(self.preview_card)
            self.left_vbox.addWidget(self.pause_card)
            self.left_vbox.addWidget(self.actions_panel)

            self.right_vbox.addWidget(self.mode_card)
            self.right_vbox.addWidget(self.specs_card)

            self.specs_card.setVisible(True)
        else:
            self.container.setMaximumWidth(540)
            self.preview_canvas.setFixedHeight(132)

            # Remove from wide columns
            self.left_vbox.removeWidget(self.timer_card)
            self.left_vbox.removeWidget(self.preview_card)
            self.left_vbox.removeWidget(self.pause_card)
            self.left_vbox.removeWidget(self.actions_panel)

            self.right_vbox.removeWidget(self.mode_card)
            self.right_vbox.removeWidget(self.specs_card)

            # Add to compact layout
            self.compact_vbox.addWidget(self.timer_card)
            self.compact_vbox.addWidget(self.preview_card)
            self.compact_vbox.addWidget(self.mode_card)
            self.compact_vbox.addWidget(self.pause_card)
            self.compact_vbox.addWidget(self.actions_panel)

            self.specs_card.setVisible(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        is_wide = (self.width() >= 860) or self.isMaximized()
        self._apply_responsive_layout(is_wide)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.WindowStateChange:
            is_wide = (self.width() >= 860) or self.isMaximized()
            self._apply_responsive_layout(is_wide)

    def _setup_shortcuts(self):
        """Emergency stop shortcut: ESC key stops motion immediately."""
        self.esc_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.esc_shortcut.activated.connect(self._on_emergency_esc)

        self.return_shortcut = QShortcut(QKeySequence(Qt.Key_Return), self)
        self.return_shortcut.activated.connect(self._on_enter_pressed)

    def _toggle_theme(self):
        """Toggles between Dark Obsidian Luxe and Light Aurora Glass themes."""
        self.is_dark_theme = not self.is_dark_theme
        self.apply_theme(self.is_dark_theme)

    def apply_theme(self, dark: bool):
        """Applies stylesheet and visual updates for the active theme."""
        self.is_dark_theme = dark
        if dark:
            QApplication.instance().setStyleSheet(DARK_THEME_STYLESHEET)
            self.theme_toggle_btn.setText("🌙 Dark")
            self.timer_hint.setStyleSheet("color: #818cf8; font-size: 10px; font-weight: 700; letter-spacing: 0.5px;")
            self.pause_desc.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: 500; margin-left: 26px;")
            self.safety_hint.setStyleSheet("color: #818cf8; font-size: 10px; font-style: italic;")
        else:
            QApplication.instance().setStyleSheet(LIGHT_THEME_STYLESHEET)
            self.theme_toggle_btn.setText("☀️ Light")
            self.timer_hint.setStyleSheet("color: #4f46e5; font-size: 10px; font-weight: 700; letter-spacing: 0.5px;")
            self.pause_desc.setStyleSheet("color: #475569; font-size: 10px; font-weight: 500; margin-left: 26px;")
            self.safety_hint.setStyleSheet("color: #312e81; font-size: 10px; font-style: italic;")

        # Update preview canvas theme
        self.preview_canvas.set_dark_theme(dark)

        # Update all mode cards theme
        for card in self.mode_cards.values():
            card.set_theme(dark)

        # Update telemetry specs card theme
        if self.specs_version_lbl:
            self.specs_version_lbl.setStyleSheet(
                "color: #a5b4fc; font-size: 10px; font-weight: 700;" if dark else "color: #4f46e5; font-size: 10px; font-weight: 700;"
            )
        for s_lbl in self.specs_subtitles:
            s_lbl.setStyleSheet(
                "color: #94a3b8; font-size: 9px; font-weight: 500;" if dark else "color: #64748b; font-size: 9px; font-weight: 500;"
            )

    def _on_enter_pressed(self):
        if not self.is_running:
            self.start_motion()

    def _on_emergency_esc(self):
        if self.is_running:
            self._update_status("Stopped", "#fee2e2", "#dc2626")
            self.stop_motion()

    def _update_status(self, badge_text: str, bg_color: str, text_color: str):
        self.status_badge.setText(badge_text.upper())
        self.status_badge.setStyleSheet(
            f"background-color: {bg_color}; color: {text_color};"
        )

    def _on_quick_preview_clicked(self, mode_key: str):
        """Handles selecting one of the quick preview buttons."""
        self._set_active_mode(mode_key)

    def _on_mode_card_selected(self, mode_key: str):
        """Handles selecting a mode card."""
        self._set_active_mode(mode_key)

    def _set_active_mode(self, mode_key: str):
        """Synchronizes selected mode across preview canvas, quick pills, and mode cards."""
        self.selected_mode = mode_key

        # Update mode cards
        for key, card in self.mode_cards.items():
            card.set_selected(key == mode_key)

        # Update quick preview pills
        for key, btn in self.quick_preview_buttons.items():
            is_match = (key == mode_key)
            btn.setProperty("selected", "true" if is_match else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # Update real-time preview canvas
        self.preview_canvas.set_mode(mode_key)

        # Update running worker if active
        if self.worker and self.is_running:
            self.worker.update_mode(mode_key)
            self._update_status(f"Running ({mode_key})", "rgba(16, 185, 129, 0.25)", "#34d399")

    def _on_auto_pause_toggled(self, checked: bool):
        if self.worker and self.is_running:
            self.worker.set_auto_pause(checked)

    def _on_timer_spin_changed(self, minutes: int):
        if not self.is_running:
            self.is_infinite = False
            self.duration_seconds = minutes * 60
            self._update_timer_display(self.duration_seconds)
            self.progress_bar.setValue(100)
            self.timer_hint.setText("CLICK START TO KEEP SYSTEM ACTIVE & AWAKE")

            # Update preset buttons state
            for val, btn in self.preset_buttons.items():
                is_match = (val == minutes)
                btn.setProperty("selected", "true" if is_match else "false")
                btn.style().unpolish(btn)
                btn.style().polish(btn)

    def _set_speed_preset(self, speed: float):
        """Updates speed multiplier across preview canvas and active motion worker."""
        self.speed_multiplier = speed
        for val, btn in self.speed_buttons.items():
            is_match = (val == speed)
            btn.setProperty("selected", "true" if is_match else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.preview_canvas.set_speed_multiplier(speed)
        if self.worker and self.is_running:
            self.worker.set_speed_multiplier(speed)

    def _set_timer_preset(self, minutes: int):
        if not self.is_running:
            if minutes == 0:
                self.is_infinite = True
                self.timer_display.setText("∞ Infinite")
                self.timer_hint.setText("INFINITE MODE • RUNS CONTINUOUSLY UNTIL YOU CLICK STOP")
                self.progress_bar.setValue(100)

                for val, btn in self.preset_buttons.items():
                    btn.setProperty("selected", "true" if val == 0 else "false")
                    btn.style().unpolish(btn)
                    btn.style().polish(btn)
            else:
                self.is_infinite = False
                self.timer_hint.setText("CLICK START TO KEEP SYSTEM ACTIVE & AWAKE")
                self.timer_spin.setValue(minutes)

    def _update_timer_display(self, seconds_left: int):
        hrs = seconds_left // 3600
        mins = (seconds_left % 3600) // 60
        secs = seconds_left % 60
        if hrs > 0:
            self.timer_display.setText(f"{hrs:02d}:{mins:02d}:{secs:02d}")
        else:
            self.timer_display.setText(f"{mins:02d}:{secs:02d}")

    def get_current_mode(self) -> str:
        return self.selected_mode

    def start_motion(self):
        """Starts cursor movement and countdown timer."""
        if self.is_running:
            return

        self.is_running = True
        self.start_timestamp = time.monotonic()

        if self.is_infinite:
            self.duration_seconds = 0
            self.timer_display.setText("∞ 00:00:00")
            self.timer_hint.setText("INFINITE MODE RUNNING • CLICK STOP OR PRESS ESC TO END")
            self.progress_bar.setValue(100)
        else:
            self.duration_seconds = self.timer_spin.value() * 60
            self.timer_hint.setText("COUNTDOWN ACTIVE • CLICK STOP OR PRESS ESC TO END")

        # Update UI Controls State
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.timer_spin.setEnabled(False)

        current_mode = self.get_current_mode()
        self._update_status(f"Running ({current_mode})", "rgba(16, 185, 129, 0.25)", "#34d399")

        # Start Worker Thread with average optimal radius, active speed, and auto-pause setting
        self.worker = MotionWorker(
            mode=current_mode,
            radius=config.OPTIMAL_AVERAGE_RADIUS_PX,
            speed_multiplier=self.speed_multiplier,
            auto_pause_enabled=self.auto_pause_check.isChecked(),
        )
        self.worker.status_changed.connect(self._on_worker_status)
        self.worker.stopped.connect(self._on_worker_stopped)
        self.worker.error_occurred.connect(self._on_worker_error)
        self.worker.start()

        # Start countdown display timer
        self.timer.start()

    def stop_motion(self):
        """Stops cursor movement and restores controls to ready state."""
        self.is_running = False
        self.timer.stop()

        if self.worker:
            self.worker.stop()
            self.worker.wait(500)
            self.worker = None

        # Reset Controls
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.timer_spin.setEnabled(True)

        if self.is_infinite:
            self.timer_display.setText("∞ Infinite")
            self.timer_hint.setText("INFINITE MODE • RUNS CONTINUOUSLY UNTIL YOU CLICK STOP")
            self.progress_bar.setValue(100)
        else:
            self._update_timer_display(self.timer_spin.value() * 60)
            self.progress_bar.setValue(100)
            self.timer_hint.setText("CLICK START TO KEEP SYSTEM ACTIVE & AWAKE")

        self._update_status("Stopped", "rgba(99, 102, 241, 0.2)", "#818cf8")

    def _on_timer_tick(self):
        """Accurate monotonic countdown calculation or infinite elapsed counter."""
        if not self.is_running:
            return

        if self.is_infinite:
            elapsed = int(time.monotonic() - self.start_timestamp)
            hrs = elapsed // 3600
            mins = (elapsed % 3600) // 60
            secs = elapsed % 60
            self.timer_display.setText(f"∞ {hrs:02d}:{mins:02d}:{secs:02d}")
            self.progress_bar.setValue(100)
        else:
            elapsed = time.monotonic() - self.start_timestamp
            remaining = self.duration_seconds - elapsed

            if remaining <= 0:
                # Time expired: automatically stop movement
                self._update_timer_display(0)
                self.progress_bar.setValue(0)
                self._update_status("Completed", "rgba(59, 130, 246, 0.25)", "#60a5fa")
                self.stop_motion()
            else:
                sec_left = int(remaining)
                self._update_timer_display(sec_left)
                pct = int((remaining / self.duration_seconds) * 100)
                self.progress_bar.setValue(max(0, min(100, pct)))

    def _on_worker_status(self, title: str, msg: str):
        if "Running" in title:
            self._update_status(f"Running ({self.selected_mode})", "rgba(16, 185, 129, 0.25)", "#34d399")
        elif "Paused" in title:
            self._update_status(title, "rgba(245, 158, 11, 0.25)", "#fbbf24")
        elif "Stopped" in title:
            self._update_status("Stopped", "rgba(239, 68, 68, 0.25)", "#f87171")

    def _on_worker_stopped(self, reason: str):
        if self.is_running:
            self.stop_motion()
            if "Emergency" in reason:
                self._update_status("Failsafe Stop", "rgba(239, 68, 68, 0.25)", "#f87171")

    def _on_worker_error(self, err_msg: str):
        self._update_status("Error", "rgba(239, 68, 68, 0.25)", "#f87171")
        self.stop_motion()

    def closeEvent(self, event):
        """Ensure clean thread termination on application close."""
        self.stop_motion()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    font = QFont("Segoe UI", 9)
    app.setFont(font)

    window = CursorMotionStudio()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
