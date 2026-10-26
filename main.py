"""Cursor Motion Studio — Main Application

Ultra-smooth, modern desktop application with interactive clickable cards,
smart human-intervention auto-pause (resuming after 5s idle), and clean glassmorphism.
"""

from __future__ import annotations

import os
import sys

# Suppress DPI conflict warnings on Windows before PySide6 loads
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "PassThrough"

import time
from typing import Optional

from PySide6.QtCore import (
    QSize,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QIcon,
    QKeySequence,
    QMouseEvent,
    QShortcut,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

import config
from motion_engine import MotionWorker


# Refined Glassmorphism stylesheet
GLASS_STYLESHEET = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #8ea5eb,
        stop:0.32 #9d85ea,
        stop:0.68 #b592f2,
        stop:1 #f8b4b4);
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
    background: rgba(255, 255, 255, 0.25);
    width: 6px;
    margin: 2px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.7);
    min-height: 30px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: #ffffff;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Base Glass Cards */
QFrame.GlassCard {
    background-color: rgba(255, 255, 255, 0.65);
    border: 1.5px solid rgba(255, 255, 255, 0.88);
    border-radius: 16px;
}

QLabel {
    border: none;
    background: transparent;
}

/* Header Text */
QLabel#AppMainTitle {
    color: #1e1b4b;
    font-size: 17px;
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
    letter-spacing: 0.6px;
    text-transform: uppercase;
}

QLabel#TimerValueDisplay {
    color: #1e1b4b;
    font-size: 34px;
    font-weight: 800;
    font-family: 'Consolas', 'Segoe UI', monospace;
}

/* Duration Preset Pills */
QPushButton.PresetPill {
    background-color: rgba(255, 255, 255, 0.85);
    border: 1.5px solid rgba(255, 255, 255, 0.95);
    border-radius: 10px;
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

/* SpinBox */
QSpinBox {
    background-color: rgba(255, 255, 255, 0.92);
    border: 1.5px solid rgba(255, 255, 255, 1.0);
    border-radius: 8px;
    color: #1f2937;
    font-size: 12px;
    font-weight: 700;
    padding: 4px 8px;
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
    letter-spacing: 0.5px;
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
    letter-spacing: 0.5px;
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

/* Status Pill */
QLabel#StatusPillLabel {
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 800;
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
    image: none;
}
"""


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller bundle."""
    try:
        base_path = sys._MEIPASS  # type: ignore
    except AttributeError:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


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
        self.is_selected = False

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
        self.icon_badge.setStyleSheet(
            "font-size: 17px; background-color: rgba(99, 102, 241, 0.12); "
            "border-radius: 17px; border: none;"
        )
        layout.addWidget(self.icon_badge)

        # Middle: Title and description
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("color: #1e1b4b; font-size: 13px; font-weight: 700; border: none; background: transparent;")
        text_layout.addWidget(self.title_label)

        self.desc_label = QLabel(self.desc)
        self.desc_label.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 500; border: none; background: transparent;")
        self.desc_label.setWordWrap(True)
        text_layout.addWidget(self.desc_label)

        layout.addLayout(text_layout, 1)

        # Right: Tag pill + selection radio circle
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)
        right_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.tag_pill = QLabel(self.tag)
        self.tag_pill.setStyleSheet(
            f"background-color: {self.tag_bg}; color: {self.tag_fg}; "
            f"border-radius: 5px; font-size: 9px; font-weight: 700; padding: 2px 6px; border: none;"
        )
        self.tag_pill.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.tag_pill)

        self.radio_indicator = QLabel("○")
        self.radio_indicator.setAlignment(Qt.AlignCenter)
        self.radio_indicator.setStyleSheet("color: #94a3b8; font-size: 14px; font-weight: 700; border: none; background: transparent;")
        right_layout.addWidget(self.radio_indicator)

        layout.addLayout(right_layout)

    def set_selected(self, selected: bool):
        self.is_selected = selected
        self.update_visual_state()

    def update_visual_state(self, is_hover: bool = False):
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
            self.title_label.setStyleSheet("color: #4338ca; font-size: 13px; font-weight: 800; border: none; background: transparent;")
            self.desc_label.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 500; border: none; background: transparent;")
            self.radio_indicator.setText("●")
            self.radio_indicator.setStyleSheet("color: #6366f1; font-size: 15px; font-weight: 800; border: none; background: transparent;")
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
            self.title_label.setStyleSheet("color: #312e81; font-size: 13px; font-weight: 700; border: none; background: transparent;")
            self.desc_label.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 500; border: none; background: transparent;")
            self.radio_indicator.setText("○")
            self.radio_indicator.setStyleSheet("color: #818cf8; font-size: 14px; border: none; background: transparent;")
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
            self.title_label.setStyleSheet("color: #1e1b4b; font-size: 13px; font-weight: 700; border: none; background: transparent;")
            self.desc_label.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 500; border: none; background: transparent;")
            self.radio_indicator.setText("○")
            self.radio_indicator.setStyleSheet("color: #cbd5e1; font-size: 14px; border: none; background: transparent;")

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

        # Motion worker & timer variables
        self.worker: Optional[MotionWorker] = None
        self.timer = QTimer(self)
        self.timer.setInterval(250)
        self.timer.timeout.connect(self._on_timer_tick)

        self.duration_seconds: int = config.DEFAULT_TIMER_MINUTES * 60
        self.start_timestamp: float = 0.0
        self.is_running: bool = False
        self.is_infinite: bool = False
        self.selected_mode: str = config.MODE_GENTLE

        self.mode_cards: dict[str, ModeCardWidget] = {}
        self.preset_buttons: dict[int, QPushButton] = {}

        self._setup_ui()
        self._setup_shortcuts()
        self._update_status("Ready", "#e0e7ff", "#4338ca")

    def _setup_ui(self):
        # Central widget with scroll area for scaling safety
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setCentralWidget(scroll)

        container = QWidget()
        container.setObjectName("CentralContainer")
        scroll.setWidget(container)

        root_layout = QVBoxLayout(container)
        root_layout.setContentsMargins(18, 16, 18, 16)
        root_layout.setSpacing(12)

        # 1. Header Card
        header_card = QFrame()
        header_card.setProperty("class", "GlassCard")
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(14, 12, 14, 12)
        header_layout.setSpacing(8)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        app_title = QLabel(config.APP_NAME)
        app_title.setObjectName("AppMainTitle")
        badge_pro = QLabel("PRO")
        badge_pro.setObjectName("BadgePro")
        title_row.addWidget(app_title)
        title_row.addWidget(badge_pro)
        title_row.addStretch()

        subtitle = QLabel("Autonomous Keep-Alive & Anti-Sleep Engine")
        subtitle.setObjectName("AppSubTitle")
        title_col.addLayout(title_row)
        title_col.addWidget(subtitle)
        header_layout.addLayout(title_col)

        # Status badge pill
        self.status_badge = QLabel("READY")
        self.status_badge.setObjectName("StatusPillLabel")
        header_layout.addWidget(self.status_badge)
        root_layout.addWidget(header_card)

        # 2. Timer Card (Duration Config & Countdown Display)
        timer_card = QFrame()
        timer_card.setProperty("class", "GlassCard")
        timer_layout = QVBoxLayout(timer_card)
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
        self.timer_hint.setStyleSheet("color: #4f46e5; font-size: 10px; font-weight: 700; letter-spacing: 0.5px;")
        self.timer_hint.setAlignment(Qt.AlignCenter)
        timer_layout.addWidget(self.timer_hint)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        timer_layout.addWidget(self.progress_bar)

        root_layout.addWidget(timer_card)

        # 3. Motion Patterns Card (Interactive Clickable Mode Cards)
        mode_card = QFrame()
        mode_card.setProperty("class", "GlassCard")
        mode_layout = QVBoxLayout(mode_card)
        mode_layout.setContentsMargins(14, 12, 14, 12)
        mode_layout.setSpacing(7)

        mode_header_row = QHBoxLayout()
        mode_header = QLabel("SELECT MOTION PATTERN")
        mode_header.setObjectName("SectionHeader")
        mode_header_row.addWidget(mode_header)
        mode_header_row.addStretch()
        safe_badge = QLabel("100% Zero Clicks")
        safe_badge.setStyleSheet("color: #059669; font-size: 10px; font-weight: 700;")
        mode_header_row.addWidget(safe_badge)
        mode_layout.addLayout(mode_header_row)

        mode_order = [
            config.MODE_GENTLE,
            config.MODE_CIRCLE,
            config.MODE_RANDOM,
            config.MODE_HORIZONTAL,
            config.MODE_SHAKE,
        ]

        for m_key in mode_order:
            meta = config.MODE_DETAILS.get(m_key, {
                "title": f"{m_key} Mode",
                "icon": "✨",
                "tag": "ACTIVE",
                "tag_bg": "#e0e7ff",
                "tag_fg": "#4338ca",
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
            )
            card.card_selected.connect(self._on_mode_card_selected)
            if m_key == self.selected_mode:
                card.set_selected(True)

            self.mode_cards[m_key] = card
            mode_layout.addWidget(card)

        root_layout.addWidget(mode_card)

        # 4. Smart Auto-Pause Feature Card
        pause_card = QFrame()
        pause_card.setProperty("class", "GlassCard")
        pause_layout = QVBoxLayout(pause_card)
        pause_layout.setContentsMargins(14, 10, 14, 10)
        pause_layout.setSpacing(4)

        self.auto_pause_check = QCheckBox("Auto-pause when I physically move the mouse")
        self.auto_pause_check.setChecked(True)
        self.auto_pause_check.setCursor(Qt.PointingHandCursor)
        self.auto_pause_check.toggled.connect(self._on_auto_pause_toggled)
        pause_layout.addWidget(self.auto_pause_check)

        pause_desc = QLabel("Temporarily pauses motion while you work, then automatically resumes after 5 seconds of inactivity.")
        pause_desc.setStyleSheet("color: #475569; font-size: 10px; font-weight: 500; margin-left: 26px;")
        pause_desc.setWordWrap(True)
        pause_layout.addWidget(pause_desc)

        root_layout.addWidget(pause_card)

        # 5. Action Buttons (Start / Stop)
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)

        self.start_btn = QPushButton("▶  START MOTION (ENTER)")
        self.start_btn.setObjectName("StartActionBtn")
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.clicked.connect(self.start_motion)
        actions_layout.addWidget(self.start_btn, 3)

        self.stop_btn = QPushButton("⏹  STOP")
        self.stop_btn.setObjectName("StopActionBtn")
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_motion)
        actions_layout.addWidget(self.stop_btn, 1)

        root_layout.addLayout(actions_layout)

        # Safety & Emergency hints
        safety_hint = QLabel("Emergency Stop: Press ESC or push mouse to any screen corner")
        safety_hint.setStyleSheet("color: #312e81; font-size: 10px; font-style: italic;")
        safety_hint.setAlignment(Qt.AlignCenter)
        root_layout.addWidget(safety_hint)

    def _setup_shortcuts(self):
        """Emergency stop shortcut: ESC key stops motion immediately."""
        self.esc_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.esc_shortcut.activated.connect(self._on_emergency_esc)

        self.return_shortcut = QShortcut(QKeySequence(Qt.Key_Return), self)
        self.return_shortcut.activated.connect(self._on_enter_pressed)

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

    def _on_mode_card_selected(self, mode_key: str):
        """Handles selecting a mode card."""
        self.selected_mode = mode_key
        for key, card in self.mode_cards.items():
            card.set_selected(key == mode_key)

        if self.worker and self.is_running:
            self.worker.update_mode(mode_key)

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
        self._update_status(f"Running ({current_mode})", "#dcfce7", "#15803d")

        # Start Worker Thread with average optimal radius and auto-pause setting
        self.worker = MotionWorker(
            mode=current_mode,
            radius=config.OPTIMAL_AVERAGE_RADIUS_PX,
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

        self._update_status("Stopped", "#e0e7ff", "#4338ca")

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
                self._update_status("Completed", "#dbeafe", "#1e40af")
                self.stop_motion()
            else:
                sec_left = int(remaining)
                self._update_timer_display(sec_left)
                pct = int((remaining / self.duration_seconds) * 100)
                self.progress_bar.setValue(max(0, min(100, pct)))

    def _on_worker_status(self, title: str, msg: str):
        if "Running" in title:
            self._update_status(f"Running ({self.selected_mode})", "#dcfce7", "#15803d")
        elif "Paused" in title:
            self._update_status(title, "#fef3c7", "#b45309")
        elif "Stopped" in title:
            self._update_status("Stopped", "#fee2e2", "#dc2626")

    def _on_worker_stopped(self, reason: str):
        if self.is_running:
            self.stop_motion()
            if "Emergency" in reason:
                self._update_status("Failsafe Stop", "#fee2e2", "#b91c1c")

    def _on_worker_error(self, err_msg: str):
        self._update_status("Error", "#fee2e2", "#b91c1c")
        self.stop_motion()

    def closeEvent(self, event):
        """Ensure clean thread termination on application close."""
        self.stop_motion()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(GLASS_STYLESHEET)

    font = QFont("Segoe UI", 9)
    app.setFont(font)

    window = CursorMotionStudio()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
