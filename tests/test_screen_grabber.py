import unittest
import os
import numpy as np
from py_screen_grab.screen_grabber import ScreenGrabber, DECORATION_OFFSET_X, DECORATION_OFFSET_Y

class TestScreenGrabber(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.grabber = ScreenGrabber()
        self.test_roi = (0, 0, 640, 480)
        self.test_fps = 30

    def tearDown(self):
        """Clean up after each test method."""
        self.grabber = None

    def test_init(self):
        """Test ScreenGrabber initialization."""
        self.assertIsNotNone(self.grabber.sct)
        self.assertTrue(os.path.exists(self.grabber.save_dir))
        self.assertEqual(self.grabber.fps, 30)  # default fps

    def test_set_fps(self):
        """Test setting FPS."""
        result = self.grabber.set_fps(self.test_fps)
        self.assertEqual(self.grabber.fps, self.test_fps)
        self.assertEqual(result, self.grabber)  # Test method chaining

    def test_invalid_fps(self):
        """Test setting invalid FPS values."""
        with self.assertRaises(ValueError):
            self.grabber.set_fps(0)
        with self.assertRaises(ValueError):
            self.grabber.set_fps(-1)
        with self.assertRaises(ValueError):
            self.grabber.set_fps(61)

    def test_capture_frame(self):
        """Test screen capture functionality."""
        x, y, w, h = self.test_roi
        self.grabber.set_roi(x, y, w, h, adjust_for_decorations=False)
        frame = self.grabber._capture_frame()  # Access internal method
        
        # Check frame properties
        self.assertIsInstance(frame, np.ndarray)
        self.assertEqual(frame.shape[0], h)  # height
        self.assertEqual(frame.shape[1], w)  # width
        self.assertEqual(frame.shape[2], 3)  # RGB channels

    def test_invalid_roi(self):
        """Test setting invalid ROI values."""
        with self.assertRaises(ValueError):
            self.grabber.set_roi(0, 0, -1, 480, adjust_for_decorations=False)
        with self.assertRaises(ValueError):
            self.grabber.set_roi(0, 0, 640, -1, adjust_for_decorations=False)

    def test_basic_roi_adjustments(self):
        """Test basic ROI adjustments without decoration compensation."""
        screen = self.grabber.sct.monitors[0]
        screen_width = screen['width']
        screen_height = screen['height']

        test_cases = [
            {
                "name": "negative coordinates",
                "input": (-100, -100, 640, 480),
                "expected": {"left": 0, "top": 0, "width": 640, "height": 480}
            },
            {
                "name": "exceeding width",
                "input": (100, 100, screen_width + 100, 480),
                "expected": {"left": 100, "top": 100, "width": screen_width - 100, "height": 480}
            },
            {
                "name": "exceeding height",
                "input": (100, 100, 640, screen_height + 100),
                "expected": {"left": 100, "top": 100, "width": 640, "height": screen_height - 100}
            },
            {
                "name": "valid coordinates",
                "input": (100, 100, 300, 200),
                "expected": {"left": 100, "top": 100, "width": 300, "height": 200}
            }
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                x, y, w, h = case["input"]
                result = self.grabber.set_roi(x, y, w, h, adjust_for_decorations=False)
                self.assertEqual(self.grabber.roi, case["expected"])
                self.assertEqual(result, self.grabber)  # Test method chaining

    def test_roi_with_decoration_adjustment(self):
        """Test ROI adjustments with window decoration compensation."""
        original_x, original_y = 100, 100
        original_w, original_h = 300, 200
        
        result = self.grabber.set_roi(
            original_x, 
            original_y, 
            original_w, 
            original_h, 
            adjust_for_decorations=True
        )
        
        expected_roi = {
            "left": original_x - DECORATION_OFFSET_X,
            "top": original_y - DECORATION_OFFSET_Y * 2,
            "width": original_w + (DECORATION_OFFSET_X),
            "height": original_h + DECORATION_OFFSET_Y
        }
        
        self.assertEqual(self.grabber.roi, expected_roi)
        self.assertEqual(result, self.grabber)  # Test method chaining

    def test_roi_without_decoration_adjustment(self):
        """Test ROI adjustments without window decoration compensation."""
        original_x, original_y = 100, 100
        original_w, original_h = 300, 200
        
        result = self.grabber.set_roi(
            original_x, 
            original_y, 
            original_w, 
            original_h, 
            adjust_for_decorations=False
        )
        
        expected_roi = {
            "left": original_x,
            "top": original_y,
            "width": original_w,
            "height": original_h
        }
        
        self.assertEqual(self.grabber.roi, expected_roi)
        self.assertEqual(result, self.grabber)  # Test method chaining

    def test_decoration_adjustment_with_screen_bounds(self):
        """Test window decoration compensation with screen boundary checks."""
        screen = self.grabber.sct.monitors[0]
        screen_width = screen['width']
        screen_height = screen['height']

        # Test case near screen edges
        self.grabber.set_roi(
            10,  # Very close to left edge
            10,  # Very close to top edge
            300,
            200,
            adjust_for_decorations=True
        )

        # Should not go below 0 for x and y
        self.assertGreaterEqual(self.grabber.roi["left"], 0)
        self.assertGreaterEqual(self.grabber.roi["top"], 0)

        # Test case near screen edges (right and bottom)
        self.grabber.set_roi(
            screen_width - 100,  # Close to right edge
            screen_height - 100,  # Close to bottom edge
            300,
            200,
            adjust_for_decorations=True
        )

        # Should not exceed screen dimensions
        self.assertLessEqual(
            self.grabber.roi["left"] + self.grabber.roi["width"],
            screen_width
        )
        self.assertLessEqual(
            self.grabber.roi["top"] + self.grabber.roi["height"],
            screen_height
        )

if __name__ == '__main__':
    unittest.main() 