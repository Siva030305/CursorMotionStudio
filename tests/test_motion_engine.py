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


if __name__ == "__main__":
    unittest.main()
