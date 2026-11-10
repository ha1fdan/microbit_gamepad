import unittest

from microbit_gamepad.protocol import AXIS_MAX, State, parse_line, tilt_to_axis


class ParseTests(unittest.TestCase):
    def test_good_line(self):
        self.assertEqual(parse_line("G 1 0 1 1 -120 340\r\n"), State(True, False, True, True, -120, 340))

    def test_garbage_is_ignored(self):
        for bad in ["", "MicroPython v1.18", "G 1 0 1", "G 1 0 0 -120 340", "G a b c d e f", "X 1 0 0 0 0"]:
            self.assertIsNone(parse_line(bad), bad)


class AxisTests(unittest.TestCase):
    def test_deadzone(self):
        self.assertEqual(tilt_to_axis(100), 0)
        self.assertEqual(tilt_to_axis(-120), 0)

    def test_full_and_clamp(self):
        self.assertEqual(tilt_to_axis(800), AXIS_MAX)
        self.assertEqual(tilt_to_axis(-5000), -AXIS_MAX)

    def test_invert(self):
        self.assertEqual(tilt_to_axis(800, invert=True), -AXIS_MAX)

    def test_monotonic(self):
        vals = [tilt_to_axis(mg) for mg in range(0, 1000, 50)]
        self.assertEqual(vals, sorted(vals))

    def test_bad_range(self):
        with self.assertRaises(ValueError):
            tilt_to_axis(100, deadzone=500, full=400)


if __name__ == "__main__":
    unittest.main()
