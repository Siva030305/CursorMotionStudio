"""Configuration module for Cursor Motion Studio."""

APP_NAME = "Cursor Motion Studio"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Lightweight, offline Windows cursor motion controller"

# Window geometry
WINDOW_WIDTH = 460
WINDOW_HEIGHT = 650
MIN_WINDOW_WIDTH = 420
MIN_WINDOW_HEIGHT = 580

# Cursor boundary & movement limits
OPTIMAL_AVERAGE_RADIUS_PX = 7   # Smooth, natural average radius (strictly bounded <= 15)
DEFAULT_RADIUS_PX = 7

# Human interruption detection & auto-pause settings
HUMAN_PAUSE_RESUME_DELAY_SEC = 5.0  # Resume after 5 seconds of human inactivity
HUMAN_DISPLACEMENT_THRESHOLD_PX = 20  # Fast cursor shift detection threshold

# Timer constraints (minutes)
MIN_TIMER_MINUTES = 1
MAX_TIMER_MINUTES = 120
DEFAULT_TIMER_MINUTES = 15

# Supported Movement Modes
MODE_SHAKE = "Shake"
MODE_RANDOM = "Random"
MODE_CIRCLE = "Circle"
MODE_GENTLE = "Gentle"
MODE_HORIZONTAL = "Horizontal"

ALL_MODES = [
    MODE_SHAKE,
    MODE_RANDOM,
    MODE_CIRCLE,
    MODE_GENTLE,
    MODE_HORIZONTAL,
]

MODE_DESCRIPTIONS = {
    MODE_GENTLE: "Slow, natural breathing drift around cursor",
    MODE_CIRCLE: "Continuous circular orbital motion",
    MODE_RANDOM: "Organic pseudo-random drift bounded by radius",
    MODE_HORIZONTAL: "Smooth side-to-side sweep along the horizontal axis",
    MODE_SHAKE: "Fast micro-jitter oscillation around anchor point",
}

MODE_DETAILS = {
    MODE_GENTLE: {
        "title": "Gentle Drift",
        "icon": "🍃",
        "tag": "RECOMMENDED",
        "tag_bg": "#dbeafe",
        "tag_fg": "#1d4ed8",
        "desc": "Slow, natural breathing drift around cursor",
    },
    MODE_CIRCLE: {
        "title": "Circle Orbit",
        "icon": "⭕",
        "tag": "SMOOTH",
        "tag_bg": "#e0e7ff",
        "tag_fg": "#4338ca",
        "desc": "Continuous circular orbital motion",
    },
    MODE_RANDOM: {
        "title": "Random Wander",
        "icon": "🎲",
        "tag": "NATURAL",
        "tag_bg": "#dcfce7",
        "tag_fg": "#15803d",
        "desc": "Organic pseudo-random drift bounded by radius",
    },
    MODE_HORIZONTAL: {
        "title": "Horizontal Sweep",
        "icon": "↔️",
        "tag": "SWEEP",
        "tag_bg": "#fef3c7",
        "tag_fg": "#b45309",
        "desc": "Smooth side-to-side sweep along the horizontal axis",
    },
    MODE_SHAKE: {
        "title": "Rapid Shake",
        "icon": "⚡",
        "tag": "ACTIVE",
        "tag_bg": "#fee2e2",
        "tag_fg": "#b91c1c",
        "desc": "Fast micro-jitter oscillation around anchor point",
    },
}

# Technology Stack display items (Separate UI section)
TECH_STACK_ITEMS = [
    {
        "name": "Python",
        "tag": "3.10+",
        "role": "Core Engine",
        "icon": "python",
        "color": "#38bdf8",
    },
    {
        "name": "PySide6",
        "tag": "Qt6",
        "role": "Desktop UI",
        "icon": "qt",
        "color": "#4ade80",
    },
    {
        "name": "PyAutoGUI",
        "tag": "Native",
        "role": "Cursor Motion",
        "icon": "mouse",
        "color": "#facc15",
    },
    {
        "name": "PyInstaller",
        "tag": "Offline",
        "role": "Standalone Build",
        "icon": "box",
        "color": "#f472b6",
    },
]
