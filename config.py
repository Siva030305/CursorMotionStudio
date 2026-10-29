"""Configuration module for Cursor Motion Studio."""

APP_NAME = "Cursor Motion Studio"
APP_VERSION = "1.3.0"
APP_DESCRIPTION = "Ultra-smooth, modern desktop cursor motion controller"

# Window geometry
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 840
MIN_WINDOW_WIDTH = 460
MIN_WINDOW_HEIGHT = 680

# Cursor boundary & movement limits
OPTIMAL_AVERAGE_RADIUS_PX = 12  # Smooth, fluid radius (strictly bounded <= 15)
DEFAULT_RADIUS_PX = 12

# Speed presets & multiplier (engineered for maximum smooth velocity)
DEFAULT_SPEED_MULTIPLIER = 2.0  # High-speed default
SPEED_PRESETS = [
    ("1.0x Standard", 1.0),
    ("2.0x High", 2.0),
    ("3.5x Very High", 3.5),
    ("6.0x Maximum ⚡", 6.0),
]

# Human interruption detection & auto-pause settings
HUMAN_PAUSE_RESUME_DELAY_SEC = 5.0  # Resume after 5 seconds of human inactivity
HUMAN_DISPLACEMENT_THRESHOLD_PX = 25  # Fast cursor shift detection threshold

# Timer constraints (minutes)
MIN_TIMER_MINUTES = 1
MAX_TIMER_MINUTES = 120
DEFAULT_TIMER_MINUTES = 15

# Supported Movement Modes
MODE_CIRCLE = "Circle"
MODE_HORIZONTAL = "Horizontal"
MODE_SHAKE = "Shake"
MODE_STEALTH = "Stealth"
MODE_GENTLE = "Gentle"
MODE_RANDOM = "Random"

ALL_MODES = [
    MODE_CIRCLE,
    MODE_HORIZONTAL,
    MODE_SHAKE,
    MODE_STEALTH,
    MODE_GENTLE,
    MODE_RANDOM,
]

MODE_DESCRIPTIONS = {
    MODE_CIRCLE: "Continuous circular orbital motion",
    MODE_HORIZONTAL: "Smooth side-to-side sweep along the horizontal axis",
    MODE_SHAKE: "Fast micro-jitter tremor around anchor point",
    MODE_STEALTH: "Strictly 1-pixel continuous micro-shake — 100% imperceptible at distance",
    MODE_GENTLE: "Slow, natural breathing drift around cursor",
    MODE_RANDOM: "Organic pseudo-random drift bounded by radius",
}

MODE_DETAILS = {
    MODE_CIRCLE: {
        "title": "Circle Orbit",
        "icon": "⭕",
        "tag": "SMOOTH",
        "tag_bg": "rgba(6, 182, 212, 0.20)",
        "tag_fg": "#22d3ee",
        "tag_bg_light": "#e0f2fe",
        "tag_fg_light": "#0284c7",
        "color": "#06b6d4",
        "desc": "Continuous circular orbital motion",
        "preview_tip": "Uniform angular orbital path",
    },
    MODE_HORIZONTAL: {
        "title": "Horizontal Sweep",
        "icon": "↔️",
        "tag": "SWEEP",
        "tag_bg": "rgba(245, 158, 11, 0.20)",
        "tag_fg": "#fbbf24",
        "tag_bg_light": "#fef3c7",
        "tag_fg_light": "#d97706",
        "color": "#f59e0b",
        "desc": "Smooth side-to-side sweep along the horizontal axis",
        "preview_tip": "Lateral harmonic oscillation",
    },
    MODE_SHAKE: {
        "title": "Rapid Shake",
        "icon": "⚡",
        "tag": "ACTIVE",
        "tag_bg": "rgba(244, 63, 94, 0.20)",
        "tag_fg": "#fb7185",
        "tag_bg_light": "#fee2e2",
        "tag_fg_light": "#e11d48",
        "color": "#f43f5e",
        "desc": "Fast micro-jitter tremor around anchor point",
        "preview_tip": "Dynamic high-frequency tremor",
    },
    MODE_STEALTH: {
        "title": "1-Pixel Micro-Shake",
        "icon": "👻",
        "tag": "1-PIXEL",
        "tag_bg": "rgba(168, 85, 247, 0.20)",
        "tag_fg": "#c084fc",
        "tag_bg_light": "#f3e8ff",
        "tag_fg_light": "#9333ea",
        "color": "#a855f7",
        "desc": "Strictly 1-pixel continuous micro-shake — 100% imperceptible at distance",
        "preview_tip": "Strictly 1-pixel micro-vibration imperceptible at distance",
    },
    MODE_GENTLE: {
        "title": "Gentle Drift",
        "icon": "🍃",
        "tag": "NATURAL",
        "tag_bg": "rgba(16, 185, 129, 0.20)",
        "tag_fg": "#34d399",
        "tag_bg_light": "#d1fae5",
        "tag_fg_light": "#059669",
        "color": "#10b981",
        "desc": "Slow, natural breathing drift around cursor",
        "preview_tip": "Harmonious Lissajous breathing path",
    },
    MODE_RANDOM: {
        "title": "Random Wander",
        "icon": "🎲",
        "tag": "ORGANIC",
        "tag_bg": "rgba(99, 102, 241, 0.20)",
        "tag_fg": "#818cf8",
        "tag_bg_light": "#e0e7ff",
        "tag_fg_light": "#4f46e5",
        "color": "#6366f1",
        "desc": "Organic pseudo-random drift bounded by radius",
        "preview_tip": "Multi-octave continuous harmonic drift",
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
