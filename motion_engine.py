"""Cursor motion engine for Cursor Motion Studio.

Provides safe, bounded, butter-smooth mathematical cursor movements
and a high-precision QThread worker supporting human-intervention auto-pause.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import math
import time
from typing import Optional, Tuple

try:
    import pyautogui
    pyautogui.PAUSE = 0
    pyautogui.FAILSAFE = True
except ImportError:
    pyautogui = None

try:
    from PySide6.QtCore import QThread, Signal
except ImportError:
    class QThread:
        def __init__(self, parent=None): pass
        def start(self): pass
        def wait(self): pass
    def Signal(*args):
        class _Signal:
            def emit(self, *a, **k): pass
            def connect(self, slot): pass
        return _Signal()

import config


# Win32 high-performance cursor structures and bindings
class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


def get_system_cursor_pos() -> Tuple[int, int]:
    """Retrieve absolute hardware cursor position with microsecond latency."""
    try:
        pt = POINT()
        if ctypes.windll.user32.GetCursorPos(ctypes.byref(pt)):
            return int(pt.x), int(pt.y)
    except Exception:
        pass
    if pyautogui is not None:
        p = pyautogui.position()
        return int(p.x), int(p.y)
    return (0, 0)


def set_system_cursor_pos(x: int, y: int) -> bool:
    """Set absolute hardware cursor position immediately without wrapper overhead."""
    try:
        if ctypes.windll.user32.SetCursorPos(x, y):
            return True
    except Exception:
        pass
    if pyautogui is not None:
        try:
            pyautogui.moveTo(x, y)
            return True
        except Exception:
            return False
    return False


def get_screen_resolution() -> Tuple[int, int]:
    """Get screen dimensions (width, height)."""
    try:
        w = ctypes.windll.user32.GetSystemMetrics(0)
        h = ctypes.windll.user32.GetSystemMetrics(1)
        if w > 0 and h > 0:
            return int(w), int(h)
    except Exception:
        pass
    if pyautogui is not None:
        s = pyautogui.size()
        return int(s.width), int(s.height)
    return (1920, 1080)


class MotionCalculator:
    """Pure mathematical motion generator for all 5 movement modes.
    Guarantees that calculated coordinates remain strictly bounded
    within the configured radius (<= 15px) and screen limits with fluid continuity.
    """

    def __init__(
        self,
        anchor_x: int,
        anchor_y: int,
        radius: int = config.OPTIMAL_AVERAGE_RADIUS_PX,
        screen_width: int = 1920,
        screen_height: int = 1080,
    ):
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.radius = max(1, min(radius, 15))  # Enforce strict max 15px radius
        self.screen_width = max(100, screen_width)
        self.screen_height = max(100, screen_height)

    def clamp(self, x: float, y: float) -> Tuple[int, int]:
        """Clamps (x, y) strictly within circular radius and desktop boundaries."""
        dx = x - self.anchor_x
        dy = y - self.anchor_y
        dist = math.hypot(dx, dy)
        if dist > self.radius and dist > 0:
            scale = self.radius / dist
            dx *= scale
            dy *= scale

        final_x = int(round(self.anchor_x + dx))
        final_y = int(round(self.anchor_y + dy))

        # Guarantee integer pixel distance strictly never exceeds self.radius
        while math.hypot(final_x - self.anchor_x, final_y - self.anchor_y) > self.radius:
            dx *= 0.95
            dy *= 0.95
            final_x = int(round(self.anchor_x + dx))
            final_y = int(round(self.anchor_y + dy))

        # Clamp to screen boundary (leave 2px margin to prevent failsafe edge false-triggers)
        clamped_x = max(2, min(final_x, self.screen_width - 3))
        clamped_y = max(2, min(final_y, self.screen_height - 3))
        return clamped_x, clamped_y

    def calculate_gentle(self, t: float) -> Tuple[int, int]:
        """Mode: Gentle Drift - Slow, continuous natural breathing curve."""
        r = float(self.radius)
        # Harmonious Lissajous frequencies prevent quantization freeze
        dx = r * math.sin(t * 2.2)
        dy = (r * 0.85) * math.cos(t * 2.1)
        return self.clamp(self.anchor_x + dx, self.anchor_y + dy)

    def calculate_circle(self, t: float) -> Tuple[int, int]:
        """Mode: Circle Orbit - Continuous circular orbital motion."""
        # Smooth continuous revolution every ~2.4 seconds
        angle = t * 2.6
        dx = self.radius * math.cos(angle)
        dy = self.radius * math.sin(angle)
        return self.clamp(self.anchor_x + dx, self.anchor_y + dy)

    def calculate_random(self, t: float) -> Tuple[int, int]:
        """Mode: Random Wander - Multi-octave continuous harmonic drift."""
        r = float(self.radius)
        dx = r * (0.55 * math.sin(t * 2.8) + 0.45 * math.sin(t * 5.2 + 0.8))
        dy = r * (0.55 * math.cos(t * 2.7) + 0.45 * math.sin(t * 5.0 + 1.4))
        return self.clamp(self.anchor_x + dx, self.anchor_y + dy)

    def calculate_horizontal(self, t: float) -> Tuple[int, int]:
        """Mode: Horizontal Sweep - Smooth side-to-side sweep along horizontal axis."""
        dx = self.radius * math.sin(t * 3.6)
        return self.clamp(self.anchor_x + dx, self.anchor_y)

    def calculate_shake(self, t: float) -> Tuple[int, int]:
        """Mode: Rapid Shake - Fast micro-vibration oscillation."""
        r = max(2.0, self.radius * 0.5)
        dx = r * math.sin(t * 24.0)
        dy = r * math.cos(t * 28.0)
        return self.clamp(self.anchor_x + dx, self.anchor_y + dy)

    def next_point(self, mode: str, t: float) -> Tuple[int, int]:
        """Dispatches to the selected mode calculation."""
        m = mode.strip().lower()
        if "gentle" in m:
            return self.calculate_gentle(t)
        elif "circle" in m:
            return self.calculate_circle(t)
        elif "random" in m:
            return self.calculate_random(t)
        elif "horizontal" in m:
            return self.calculate_horizontal(t)
        elif "shake" in m:
            return self.calculate_shake(t)
        return self.calculate_gentle(t)


class MotionWorker(QThread):
    """High-precision QThread worker that drives butter-smooth cursor motion
    with human-intervention detection and automatic 5-second idle resume.
    """

    status_changed = Signal(str, str)     # (status_title, message)
    cursor_moved = Signal(int, int)       # (x, y)
    stopped = Signal(str)                 # (stop_reason)
    error_occurred = Signal(str)          # (error_message)

    def __init__(
        self,
        mode: str,
        radius: int = config.OPTIMAL_AVERAGE_RADIUS_PX,
        auto_pause_enabled: bool = True,
        parent: Optional[object] = None,
    ):
        super().__init__(parent)
        self.mode = mode
        self.radius = max(1, min(radius, 15))
        self.auto_pause_enabled = auto_pause_enabled
        self._is_running = False
        self._anchor_x = 0
        self._anchor_y = 0

    def update_mode(self, mode: str):
        """Allows dynamically switching mode while running."""
        self.mode = mode

    def set_auto_pause(self, enabled: bool):
        """Toggles the auto-pause on human intervention."""
        self.auto_pause_enabled = enabled

    def stop(self):
        """Signals the worker loop to terminate safely."""
        self._is_running = False

    def is_active(self) -> bool:
        return self._is_running

    def run(self):
        """Worker execution loop with 60Hz high-precision timing,
        hardware direct positioning, and smart human intervention auto-pause.
        """
        # Enable 1ms OS timer resolution on Windows for stutter-free timing
        has_winmm = False
        try:
            ctypes.windll.winmm.timeBeginPeriod(1)
            has_winmm = True
        except Exception:
            pass

        self._is_running = True
        try:
            # Anchor to initial cursor position
            self._anchor_x, self._anchor_y = get_system_cursor_pos()
            screen_w, screen_h = get_screen_resolution()

            calc = MotionCalculator(
                anchor_x=self._anchor_x,
                anchor_y=self._anchor_y,
                radius=self.radius,
                screen_width=screen_w,
                screen_height=screen_h,
            )

            self.status_changed.emit("Running", f"Active: {self.mode} Mode")

            start_time = time.monotonic()
            last_target_x = self._anchor_x
            last_target_y = self._anchor_y

            # 60 FPS update interval (~16.6ms) for fluid, seamless motion
            tick_interval = 0.016
            next_tick_time = time.monotonic()

            while self._is_running:
                # Check if human physically moved cursor away
                if self.auto_pause_enabled:
                    current_x, current_y = get_system_cursor_pos()
                    dist_from_target = math.hypot(
                        current_x - last_target_x,
                        current_y - last_target_y,
                    )

                    # If cursor moved unexpectedly beyond threshold, human is actively using it
                    if dist_from_target > config.HUMAN_DISPLACEMENT_THRESHOLD_PX:
                        self.status_changed.emit("Paused", "Human active • Auto-paused")

                        last_activity_time = time.monotonic()
                        last_human_pos = (current_x, current_y)
                        last_emitted_sec = -1

                        # Pause loop: monitor until human has stopped moving for 5 seconds
                        while self._is_running and self.auto_pause_enabled:
                            time.sleep(0.08)
                            sample_x, sample_y = get_system_cursor_pos()

                            # If mouse is still moving (movement > 3px), refresh activity timer
                            if math.hypot(sample_x - last_human_pos[0], sample_y - last_human_pos[1]) > 3:
                                last_activity_time = time.monotonic()
                                last_human_pos = (sample_x, sample_y)

                            idle_sec = time.monotonic() - last_activity_time
                            remaining = max(0.0, config.HUMAN_PAUSE_RESUME_DELAY_SEC - idle_sec)

                            if idle_sec < config.HUMAN_PAUSE_RESUME_DELAY_SEC:
                                secs_display = int(math.ceil(remaining))
                                if secs_display != last_emitted_sec:
                                    self.status_changed.emit("Paused", f"User active • Resuming in {secs_display}s")
                                    last_emitted_sec = secs_display
                            else:
                                # 5 seconds of inactivity passed! Resume motion at current cursor position
                                calc.anchor_x = sample_x
                                calc.anchor_y = sample_y
                                last_target_x = sample_x
                                last_target_y = sample_y
                                start_time = time.monotonic()
                                next_tick_time = time.monotonic()
                                self.status_changed.emit("Running", f"Active: {self.mode} Mode")
                                break

                        if not self._is_running:
                            break

                # Emergency corner check (pushing cursor to any screen corner stops engine)
                curr_x, curr_y = get_system_cursor_pos()
                if (curr_x <= 1 and curr_y <= 1) or \
                   (curr_x >= screen_w - 2 and curr_y <= 1) or \
                   (curr_x <= 1 and curr_y >= screen_h - 2) or \
                   (curr_x >= screen_w - 2 and curr_y >= screen_h - 2):
                    # Check if this was a deliberate corner push
                    if math.hypot(curr_x - self._anchor_x, curr_y - self._anchor_y) > 50:
                        self.status_changed.emit("Stopped", "Emergency Stop Triggered")
                        self.stopped.emit("Emergency Stop: Cursor moved to screen corner")
                        return

                # Calculate smooth continuous target point
                elapsed = time.monotonic() - start_time
                target_x, target_y = calc.next_point(self.mode, elapsed)

                # Direct hardware position update
                set_system_cursor_pos(target_x, target_y)
                last_target_x = target_x
                last_target_y = target_y

                # Precision frame pacing
                next_tick_time += tick_interval
                sleep_dur = next_tick_time - time.monotonic()
                if sleep_dur > 0.001:
                    time.sleep(sleep_dur)
                else:
                    # Catch up if running slightly behind
                    next_tick_time = time.monotonic()

            self.status_changed.emit("Stopped", "Motion stopped")
            self.stopped.emit("Normal stop")

        except Exception as e:
            self.error_occurred.emit(f"Worker failure: {str(e)}")
            self.stopped.emit(f"Error: {str(e)}")
        finally:
            self._is_running = False
            if has_winmm:
                try:
                    ctypes.windll.winmm.timeEndPeriod(1)
                except Exception:
                    pass
