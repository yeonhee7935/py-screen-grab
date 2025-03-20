import unittest
import os
import numpy as np
from py_screen_grab.screen_grabber import ScreenGrabber

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

    def test_set_roi(self):
        """Test setting region of interest."""
        x, y, w, h = self.test_roi
        self.grabber.set_roi(x, y, w, h)
        self.assertEqual(self.grabber.roi, {"left": x, "top": y, "width": w, "height": h})

    def test_set_fps(self):
        """Test setting FPS."""
        self.grabber.set_fps(self.test_fps)
        self.assertEqual(self.grabber.fps, self.test_fps)

    def test_set_invalid_fps(self):
        """Test setting invalid FPS values."""
        with self.assertRaises(ValueError):
            self.grabber.set_fps(0)
        with self.assertRaises(ValueError):
            self.grabber.set_fps(-1)
        with self.assertRaises(ValueError):
            self.grabber.set_fps(61)

    def test_capture_screen(self):
        """Test screen capture functionality."""
        x, y, w, h = self.test_roi
        self.grabber.set_roi(x, y, w, h)
        frame = self.grabber.capture_screen()
        
        # Check frame properties
        self.assertIsInstance(frame, np.ndarray)
        self.assertEqual(frame.shape[0], h)  # height
        self.assertEqual(frame.shape[1], w)  # width
        self.assertEqual(frame.shape[2], 3)  # RGB channels

    def test_set_invalid_roi(self):
        """Test setting invalid ROI values."""
        with self.assertRaises(ValueError):
            self.grabber.set_roi(0, 0, -1, 480)
        with self.assertRaises(ValueError):
            self.grabber.set_roi(0, 0, 640, -1)

if __name__ == '__main__':
    unittest.main() 