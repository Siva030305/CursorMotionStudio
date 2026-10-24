"""Cursor motion engine for Cursor Motion Studio.

Provides safe, bounded, ultra-smooth mathematical cursor movements
and a QThread worker that supports human-intervention auto-pause.
"""

from __future__ import annotations

import math
import time
from typing import Optional, Tuple

try:
    import pyautogui
    # Disable PyAutoGUI's default 0.1s pause for responsive, fluid motion
    pyautogui.PAUSE = 0
    pyautogui.FAILSAFE = True
except ImportError:
    pyautogui = None

try:
    from PySide6.QtCore import QThread, Signal
except ImportError:
    # Fallback dummy class for headless tests or pre-installation check
    class QThread:
        def __init__(self, parent=None):
            pass
        def start(self): pass
        def wait(self): pass
    def Signal(*args):
        class _Signal:
            def emit(self, *a, **k): pass
            def connect(self, slot): pass
        return _Signal()

import config


class MotionCalculator:
    """Pure mathematical motion generator for all 5 movement modes.
    Guarantees that calculated coordinates remain strictly bounded
    within the configured radius and screen limits with ultra-smooth continuity.
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
        self.radius = max(1, min(radius, 15))  # Enforce max 15px radius
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
        eff_radius = max(1.0, float(self.radius))
        dx = eff_radius * math.sin(t * 0.9)
        dy = eff_radius * math.cos(t * 0.7)
        return self.clamp(self.anchor_x + dx, self.anchor_y + dy)

    def calculate_circle(self, t: float) -> Tuple[int, int]:
        """Mode: Circle Orbit - Continuous circular orbital motion."""
        angle = t * 1.2
        dx = self.radius * math.cos(angle)
        dy = self.radius * math.sin(angle)
        return self.clamp(self.anchor_x + dx, self.anchor_y + dy)

    def calculate_random(self, t: float) -> Tuple[int, int]:
        """Mode: Random Wander - Multi-octave continuous harmonic drift."""
        r = float(self.radius)
        dx = r * (0.6 * math.sin(t * 1.1) + 0.4 * math.sin(t * 2.3 + 0.7))
        dy = r * (0.6 * math.cos(t * 0.9) + 0.4 * math.cos(t * 1.7 + 1.3))
        return self.clamp(self.anchor_x + dx, self.anchor_y + dy)

    def calculate_horizontal(self, t: float) -> Tuple[int, int]:
        """Mode: Horizontal Sweep - Smooth side-to-side sine oscillation."""
        dx = self.radius * math.sin(t * 1.5)
        return self.clamp(self.anchor_x + dx, self.anchor_y)

    def calculate_shake(self, t: float) -> Tuple[int, int]:
        """Mode: Rapid Shake - Fast micro-vibration oscillation."""
        r = max(1.0, self.radius * 0.7)
        dx = r * math.sin(t * 18.0)
        dy = r * math.cos(t * 22.0)
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
    """QThread worker that drives ultra-smooth cursor motion with
    human-intervention detection and automatic 5-second idle resume.
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
        """Worker execution loop with high-frequency 50Hz smooth updates
        and human intervention auto-pause.
        """
        if pyautogui is None:
            self.error_occurred.emit("PyAutoGUI is not available.")
            self.stopped.emit("PyAutoGUI missing")
            return

        self._is_running = True
        try:
            # Anchor to initial cursor position
            initial_pos = pyautogui.position()
            self._anchor_x = int(initial_pos.x)
            self._anchor_y = int(initial_pos.y)

            screen_size = pyautogui.size()
            screen_w = int(screen_size.width)
            screen_h = int(screen_size.height)

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

            # 50 Hz update interval (~20ms) for cinematic, butter-smooth motion
            tick_interval = 0.020

            while self._is_running:
                now = time.monotonic()

                # Check if human moved the cursor away while running
                if self.auto_pause_enabled:
                    current_mouse = pyautogui.position()
                    dist_from_target = math.hypot(
                        current_mouse.x - last_target_x,
                        current_mouse.y - last_target_y,
                    )

                    # If cursor moved unexpectedly beyond threshold, human is actively using it!
                    if dist_from_target > config.HUMAN_DISPLACEMENT_THRESHOLD_PX:
                        self.status_changed.emit("Paused", "Human active • Auto-paused")

                        last_activity_time = time.monotonic()
                        last_human_pos = (current_mouse.x, current_mouse.y)

                        # Pause loop: monitor until human has stopped moving for 5 seconds
                        while self._is_running and self.auto_pause_enabled:
                            time.sleep(0.08)
                            sample_pos = pyautogui.position()

                            # If mouse is still moving (movement > 3px), refresh activity timer
                            if math.hypot(sample_pos.x - last_human_pos[0], sample_pos.y - last_human_pos[1]) > 3:
                                last_activity_time = time.monotonic()
                                last_human_pos = (sample_pos.x, sample_pos.y)

                            idle_sec = time.monotonic() - last_activity_time
                            remaining = max(0.0, config.HUMAN_PAUSE_RESUME_DELAY_SEC - idle_sec)

                            if idle_sec < config.HUMAN_PAUSE_RESUME_DELAY_SEC:
                                secs_display = int(math.ceil(remaining))
                                self.status_changed.emit("Paused", f"User active • Resuming in {secs_display}s")
                            else:
                                # 5 seconds of inactivity passed! Resume motion at current cursor position
                                calc.anchor_x = sample_pos.x
                                calc.anchor_y = sample_pos.y
                                last_target_x = sample_pos.x
                                last_target_y = sample_pos.y
                                start_time = time.monotonic()
                                self.status_changed.emit("Running", f"Active: {self.mode} Mode")
                                break

                        if not self._is_running:
                            break

                # Calculate smooth continuous point
                elapsed = time.monotonic() - start_time
                target_x, target_y = calc.next_point(self.mode, elapsed)

                try:
                    pyautogui.moveTo(target_x, target_y)
                    last_target_x = target_x
                    last_target_y = target_y
                    self.cursor_moved.emit(target_x, target_y)
                except pyautogui.FailSafeException:
                    self.status_changed.emit("Stopped", "Emergency Stop Triggered")
                    self.stopped.emit("Emergency Stop: Cursor moved to screen corner")
                    return
                except Exception as e:
                    self.error_occurred.emit(f"Cursor error: {str(e)}")
                    self.stopped.emit("Cursor move error")
                    return

                time.sleep(tick_interval)

            self.status_changed.emit("Stopped", "Motion stopped")
            self.stopped.emit("Normal stop")

        except Exception as e:
            self.error_occurred.emit(f"Worker failure: {str(e)}")
            self.stopped.emit(f"Error: {str(e)}")
        finally:
            self._is_running = False
