import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
from py_screen_grab.cli import (
    print_header,
    get_capture_mode,
    get_fps,
    get_duration,
    get_recording_mode
)

class TestCLI(unittest.TestCase):
    def test_print_header(self):
        """Test header printing."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            print_header()
            output = fake_out.getvalue()
            self.assertIn("PyScreenGrab", output)
            self.assertIn("Screen Recording Tool", output)

    def test_get_capture_mode_valid_input(self):
        """Test capture mode selection with valid input."""
        test_inputs = ['1', '2']
        expected_outputs = ['1', '2']
        
        for test_input, expected in zip(test_inputs, expected_outputs):
            with patch('builtins.input', return_value=test_input):
                result = get_capture_mode()
                self.assertEqual(result, expected)

    def test_get_capture_mode_invalid_input(self):
        """Test capture mode selection with invalid then valid input."""
        with patch('builtins.input', side_effect=['3', '0', '1']):
            result = get_capture_mode()
            self.assertEqual(result, '1')

    def test_get_fps_valid_input(self):
        """Test FPS input with valid values."""
        test_cases = [
            ('', 30),  # default value
            ('30', 30),
            ('60', 60),
            ('15', 15)
        ]
        
        for test_input, expected in test_cases:
            with patch('builtins.input', return_value=test_input):
                result = get_fps()
                self.assertEqual(result, expected)

    def test_get_fps_invalid_input(self):
        """Test FPS input with invalid then valid input."""
        with patch('builtins.input', side_effect=['0', '61', 'abc', '30']):
            result = get_fps()
            self.assertEqual(result, 30)

    def test_get_recording_mode_valid_input(self):
        """Test recording mode selection with valid input."""
        test_inputs = ['1', '2']
        expected_outputs = ['1', '2']
        
        for test_input, expected in zip(test_inputs, expected_outputs):
            with patch('builtins.input', return_value=test_input):
                result = get_recording_mode()
                self.assertEqual(result, expected)

    def test_get_duration_valid_input(self):
        """Test duration input with valid values."""
        test_cases = [
            ('', None),  # unlimited
            ('5', 5.0),
            ('2.5', 2.5)
        ]
        
        for test_input, expected in test_cases:
            with patch('builtins.input', return_value=test_input):
                result = get_duration()
                self.assertEqual(result, expected)

    def test_get_duration_invalid_input(self):
        """Test duration input with invalid then valid input."""
        with patch('builtins.input', side_effect=['-1', 'abc', '5']):
            result = get_duration()
            self.assertEqual(result, 5.0)

if __name__ == '__main__':
    unittest.main() 