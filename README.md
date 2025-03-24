# PyScreenGrab

A simple and efficient screen recording tool written in Python.

![PyPI](https://img.shields.io/pypi/v/py-screen-grab)
[![PyPI Downloads](https://static.pepy.tech/badge/py-screen-grab)](https://pepy.tech/projects/py-screen-grab)
![License](https://img.shields.io/pypi/l/py-screen-grab)

## Features

- Full screen or custom region recording
- Preview mode before recording
- Adjustable FPS (1-60)
- Timed recording option
- Simple command-line interface
- Easy-to-use Python API

## Installation

```bash
pip install py-screen-grab
```

## Usage

### Command Line Interface

Simply run:

```bash
py-screen-grab
```

Follow the interactive prompts to:

1. Choose between full screen or custom region
2. Select monitor (for full screen)
3. Set FPS
4. Choose between preview or recording mode
5. Set recording duration (optional)

### Python API

```python
from py_screen_grab import ScreenGrabber

# Create a screen grabber instance
grabber = ScreenGrabber()

# Set custom region (optional)
grabber.set_roi(x=100, y=100, width=800, height=600)

# Set FPS (optional, default is 30)
grabber.set_fps(30)

# Preview only
grabber.preview_only()

# Or start recording
grabber.start_recording(duration=10)  # Record for 10 seconds
# Or record until 'q' is pressed
grabber.start_recording()  # No duration means record until 'q' is pressed
```

## Requirements

- Python 3.6 or higher
- OpenCV
- NumPy
- MSS (screen capture library)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
