"""Unit tests for MotionCalculator in Cursor Motion Studio."""

import math
import unittest
from motion_engine import MotionCalculator
import config


class TestMotionCalculator(unittest.TestCase):
    def setUp(self):
        self.screen_w = 1920
        self.screen_h = 1080
        self.anchor_x = 500
        self.anchor_y = 500
        self.radius = config.OPTIMAL_AVERAGE_RADIUS_PX
        self.calc = MotionCalculator(
            anchor_x=self.anchor_x,
            anchor_y=self.anchor_y,
            radius=self.radius,
            screen_width=self.screen_w,
            screen_height=self.screen_h,
        )

    def test_radius_boundary(self):
        """Verify points never exceed configured radius."""
        for mode in config.ALL_MODES:
            for i in range(100):
                t = i * 0.05
                x, y = self.calc.next_point(mode, t)
                dist = math.hypot(x - self.anchor_x, y - self.anchor_y)
                self.assertLessEqual(dist, self.radius, f"Mode {mode} exceeded radius at t={t}")

    def test_screen_clamping(self):
        """Verify coordinates stay within screen boundaries."""
        calc = MotionCalculator(5, 5, radius=15, screen_width=100, screen_height=100)
        cx, cy = calc.clamp(-10, -10)
        self.assertGreaterEqual(cx, 2)
        self.assertGreaterEqual(cy, 2)

        cx, cy = calc.clamp(200, 200)
        self.assertLessEqual(cx, 97)
        self.assertLessEqual(cy, 97)

    def test_circle_orbit_trajectory(self):
        """Verify Circle mode generates a circular orbit."""
        dx, dy = self.calc.get_relative_offset(config.MODE_CIRCLE, 0.0)
        dist = math.hypot(dx, dy)
        self.assertAlmostEqual(dist, self.radius, places=1)

    def test_horizontal_sweep_trajectory(self):
        """Verify Horizontal mode only moves along horizontal axis."""
        for i in range(20):
            t = i * 0.1
            dx, dy = self.calc.get_relative_offset(config.MODE_HORIZONTAL, t)
            self.assertEqual(dy, 0.0)
            self.assertLessEqual(abs(dx), self.radius)

    def test_stealth_strictly_1_pixel(self):
        """Verify 1-Pixel Micro-Shake strictly never exceeds 1.0 pixel displacement."""
        displacements = []
        for i in range(100):
            t = i * 0.01
            dx, dy = self.calc.get_relative_offset(config.MODE_STEALTH, t)
            dist_float = math.hypot(dx, dy)
            # Mathematical offset must strictly equal 1.0 pixel
            self.assertLessEqual(dist_float, 1.0001, f"Float offset exceeded 1.0px at t={t}: {dist_float}")
            displacements.append(dist_float)

            # Integer hardware screen coordinate must strictly never exceed 1.0 pixel
            x, y = self.calc.next_point(config.MODE_STEALTH, t)
            dist_int = math.hypot(x - self.anchor_x, y - self.anchor_y)
            self.assertLessEqual(dist_int, 1.0001, f"Integer screen displacement exceeded 1px at t={t}: {dist_int}")

        # Verify active oscillation (reaches 1.0px)
        max_disp = max(displacements)
        self.assertAlmostEqual(max_disp, 1.0, places=3)

    def test_rapid_shake_bounded(self):
        """Verify Rapid Shake is fast and strictly bounded."""
        for i in range(50):
            t = i * 0.02
            dx, dy = self.calc.get_relative_offset(config.MODE_SHAKE, t)
            dist = math.hypot(dx, dy)
            self.assertLessEqual(dist, self.radius)


if __name__ == "__main__":
    unittest.main()
