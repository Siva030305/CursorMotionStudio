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
    """Pure mathematical motion generator for all cursor movement modes.
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

    def clamp(self, x: float, y: float, max_radius: Optional[float] = None) -> Tuple[int, int]:
        """Clamps (x, y) strictly within circular radius and desktop boundaries."""
        r_limit = max_radius if max_radius is not None else self.radius
        dx = x - self.anchor_x
        dy = y - self.anchor_y
        dist = math.hypot(dx, dy)
        if dist > r_limit and dist > 0:
            scale = r_limit / dist
            dx *= scale
            dy *= scale

        if r_limit <= 1.001:
            # Strictly enforce integer displacement never exceeds 1 pixel (no diagonal sqrt(2) overshoot)
            if abs(dx) >= abs(dy):
                final_x = self.anchor_x + (1 if dx > 0.3 else (-1 if dx < -0.3 else 0))
                final_y = self.anchor_y
            else:
                final_x = self.anchor_x
                final_y = self.anchor_y + (1 if dy > 0.3 else (-1 if dy < -0.3 else 0))
        else:
            final_x = int(round(self.anchor_x + dx))
            final_y = int(round(self.anchor_y + dy))

            # Guarantee integer pixel distance strictly never exceeds r_limit
            while math.hypot(final_x - self.anchor_x, final_y - self.anchor_y) > r_limit:
                dx *= 0.95
                dy *= 0.95
                final_x = int(round(self.anchor_x + dx))
                final_y = int(round(self.anchor_y + dy))

        # Clamp to screen boundary (leave 2px margin to prevent failsafe edge false-triggers)
        clamped_x = max(2, min(final_x, self.screen_width - 3))
        clamped_y = max(2, min(final_y, self.screen_height - 3))
        return clamped_x, clamped_y

    def get_relative_offset(self, mode: str, t: float) -> Tuple[float, float]:
        """Returns the continuous, unrounded (dx, dy) relative offset from the anchor.
        Guaranteed to be within circular radius (<= 15px).
        Used by the preview canvas for sub-pixel vector rendering and by next_point().
        """
        m = mode.strip().lower()
        r = float(self.radius)

        if "circle" in m:
            # Mode: Circle Orbit - Maximum speed smooth orbital motion (~1.5 to 9.0 rev/s)
            angle = t * 9.5
            dx = r * math.cos(angle)
            dy = r * math.sin(angle)
        elif "horizontal" in m or "sweep" in m:
            # Mode: Horizontal Sweep - Maximum speed smooth harmonic sweep (~1.9 to 11.5 sweeps/s)
            dx = r * math.sin(t * 12.0)
            dy = 0.0
        elif "shake" in m:
            # Mode: Rapid Shake - Maximum speed energetic tremor (up to 50+ Hz)
            shake_r = max(3.0, min(r * 0.55, 7.5))
            dx = shake_r * math.sin(t * 54.0)
            dy = (shake_r * 0.9) * math.cos(t * 64.0 + 0.7)
        elif "stealth" in m or "ghost" in m or "micro" in m or "1px" in m:
            # Mode: 1-Pixel Micro-Shake - Strictly 1.0px maximum displacement
            # Ultra-fast continuous micro-vibrations strictly within a 1-pixel radius.
            # At 250 Hz, cycles smoothly across 1-pixel offsets.
            # 100% imperceptible to human eyes from any distance while keeping OS continuously active.
            angle = t * 240.0
            dx = 1.0 * math.cos(angle)
            dy = 1.0 * math.sin(angle)
        elif "random" in m or "wander" in m:
            # Mode: Random Wander - Fast multi-octave continuous harmonic drift
            dx = r * (0.55 * math.sin(t * 5.5) + 0.45 * math.sin(t * 10.5 + 0.8))
            dy = r * (0.55 * math.cos(t * 5.2) + 0.45 * math.sin(t * 10.0 + 1.4))
        else:
            # Mode: Gentle Drift - Fast, fluid natural breathing curve
            dx = r * math.sin(t * 4.5)
            dy = (r * 0.85) * math.cos(t * 4.2)

        # Enforce strict circular radius bound
        dist = math.hypot(dx, dy)
        if dist > self.radius and dist > 0:
            scale = self.radius / dist
            dx *= scale
            dy *= scale

        return dx, dy

    def calculate_circle(self, t: float) -> Tuple[int, int]:
        """Mode: Circle Orbit - Continuous circular orbital motion."""
        return self.next_point(config.MODE_CIRCLE, t)

    def calculate_horizontal(self, t: float) -> Tuple[int, int]:
        """Mode: Horizontal Sweep - Smooth side-to-side sweep along horizontal axis."""
        return self.next_point(config.MODE_HORIZONTAL, t)

    def calculate_shake(self, t: float) -> Tuple[int, int]:
        """Mode: Rapid Shake - Fast micro-jitter tremor around anchor point."""
        return self.next_point(config.MODE_SHAKE, t)

    def calculate_stealth(self, t: float) -> Tuple[int, int]:
        """Mode: Stealth Micro-Shake - High-speed continuous micro-vibrations."""
        return self.next_point(config.MODE_STEALTH, t)

    def calculate_gentle(self, t: float) -> Tuple[int, int]:
        """Mode: Gentle Drift - Slow, continuous natural breathing curve."""
        return self.next_point(config.MODE_GENTLE, t)

    def calculate_random(self, t: float) -> Tuple[int, int]:
        """Mode: Random Wander - Multi-octave continuous harmonic drift."""
        return self.next_point(config.MODE_RANDOM, t)

    def next_point(self, mode: str, t: float) -> Tuple[int, int]:
        """Dispatches to the selected mode calculation and clamps to screen bounds."""
        dx, dy = self.get_relative_offset(mode, t)
        m = mode.strip().lower()
        max_r = 1.0 if ("stealth" in m or "ghost" in m or "micro" in m or "1px" in m) else self.radius
        return self.clamp(self.anchor_x + dx, self.anchor_y + dy, max_radius=max_r)


class MotionWorker(QThread):
    """High-precision QThread worker that drives butter-smooth cursor motion
    with human-intervention detection, dynamic speed control, and automatic 5-second idle resume.
    """

    status_changed = Signal(str, str)     # (status_title, message)
    cursor_moved = Signal(int, int)       # (x, y)
    stopped = Signal(str)                 # (stop_reason)
    error_occurred = Signal(str)          # (error_message)

    def __init__(
        self,
        mode: str,
        radius: int = config.OPTIMAL_AVERAGE_RADIUS_PX,
        speed_multiplier: float = config.DEFAULT_SPEED_MULTIPLIER,
        auto_pause_enabled: bool = True,
        parent: Optional[object] = None,
    ):
        super().__init__(parent)
        self.mode = mode
        self.radius = max(1, min(radius, 15))
        self.speed_multiplier = max(0.5, min(speed_multiplier, 10.0))
        self.auto_pause_enabled = auto_pause_enabled
        self._is_running = False
        self._anchor_x = 0
        self._anchor_y = 0

    def update_mode(self, mode: str):
        """Allows dynamically switching mode while running."""
        self.mode = mode

    def set_speed_multiplier(self, multiplier: float):
        """Allows dynamically scaling speed while running."""
        self.speed_multiplier = max(0.5, min(multiplier, 10.0))

    def set_auto_pause(self, enabled: bool):
        """Toggles the auto-pause on human intervention."""
        self.auto_pause_enabled = enabled

    def stop(self):
        """Signals the worker loop to terminate safely."""
        self._is_running = False

    def is_active(self) -> bool:
        return self._is_running

    def run(self):
        """Worker execution loop with 250Hz high-precision timing,
        hardware direct positioning, dynamic speed multiplier, and smart human intervention auto-pause.
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

            last_tick_time = time.monotonic()
            sim_time = 0.0
            last_target_x = self._anchor_x
            last_target_y = self._anchor_y

            # 250 FPS high-precision tick interval (4.0ms) for maximum speed with butter-smooth flow
            tick_interval = 0.004
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
                                last_tick_time = time.monotonic()
                                sim_time = 0.0
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

                # Increment simulated time continuously according to speed multiplier
                now = time.monotonic()
                dt = now - last_tick_time
                last_tick_time = now
                sim_time += dt * self.speed_multiplier

                # Calculate smooth continuous target point
                target_x, target_y = calc.next_point(self.mode, sim_time)

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
