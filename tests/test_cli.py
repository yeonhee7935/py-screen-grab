import unittest
from unittest.mock import patch, MagicMock
from py_screen_grab import cli

class TestCLIMain(unittest.TestCase):
    @patch("py_screen_grab.cli.preview_and_record")
    @patch("py_screen_grab.cli.get_monitor_list", return_value=[
        {"left": 0, "top": 0, "width": 1920, "height": 1080},
        {"left": 1920, "top": 0, "width": 1920, "height": 1080}
    ])
    @patch("py_screen_grab.cli.ScreenGrabber")
    @patch("builtins.input")
    def test_main_monitor_mode(self, mock_input, mock_grabber_class, mock_monitors, mock_preview):
        mock_input.side_effect = [
            "1",  # Monitor capture
            "0",  # Monitor index
            "30",  # FPS
            "y",   # Show preview
            "n",   # Save to file
            "3"    # Duration
        ]

        mock_grabber = MagicMock()
        mock_grabber_class.return_value = mock_grabber

        try:
            cli.main()
        except Exception as e:
            self.fail(f"CLI monitor mode failed: {e}")

        mock_grabber.set_monitor.assert_called_with(0)
        mock_grabber.set_fps.assert_called_with(30)
        mock_preview.assert_called_once()

    @patch("py_screen_grab.cli.preview_and_record")
    @patch("py_screen_grab.cli.ScreenGrabber")
    @patch("builtins.input")
    def test_main_window_mode(self, mock_input, mock_grabber_class, mock_preview):
        mock_input.side_effect = [
            "2",       # Window capture
            "Chrome",  # Window name
            "25",      # FPS
            "n",       # Show preview
            "y",       # Save
            "5"        # Duration
        ]

        mock_grabber = MagicMock()
        mock_grabber_class.return_value = mock_grabber

        cli.main()

        mock_grabber.set_window.assert_called_with("Chrome")
        mock_grabber.set_fps.assert_called_with(25)
        mock_preview.assert_called_once()

    @patch("py_screen_grab.cli.preview_and_record")
    @patch("py_screen_grab.cli.ScreenGrabber")
    @patch("builtins.input")
    def test_main_custom_roi(self, mock_input, mock_grabber_class, mock_preview):
        mock_input.side_effect = [
            "3",    # Custom ROI
            "100",  # X
            "200",  # Y
            "640",  # Width
            "480",  # Height
            "15",   # FPS
            "y",    # Show preview
            "y",    # Save
            "2"     # Duration
        ]

        mock_grabber = MagicMock()
        mock_grabber_class.return_value = mock_grabber

        cli.main()

        mock_grabber.set_roi.assert_called_with(100, 200, 640, 480)
        mock_grabber.set_fps.assert_called_with(15)
        mock_preview.assert_called_once()

if __name__ == '__main__':
    unittest.main()
