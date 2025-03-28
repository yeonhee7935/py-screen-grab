# PyScreenGrab

A simple and efficient screen recording and streaming tool written in Python.

![PyPI](https://img.shields.io/pypi/v/py-screen-grab)
[![PyPI Downloads](https://static.pepy.tech/badge/py-screen-grab)](https://pepy.tech/projects/py-screen-grab)
![License](https://img.shields.io/pypi/l/py-screen-grab)

<br/>
<br/>

## ✨ Features

- Multiple capture modes(Full Screen/Custom Region/Window)
- Local video recording
- Preview mode
- Adjustable FPS (1-60)
- Timed recording option
- Simple command-line interface
- Reactive streaming support

- 🔴 **Note**: Window capture may not work properly with virtual monitors; use a physical monitor for best results)

<br/>
<br/>

## 📦 Installation

```bash
pip install py-screen-grab
```

<br/>
<br/>

## 🚀 Usage

### Command Line Interface

Simply run:

```bash
screengrab
```

Follow the interactive prompts to:

1. Select capture mode (Full Screen/Custom Region/Window)
2. Choose monitor or set region
3. Set FPS
4. Choose recording mode (Preview/Record)
5. Set recording duration (optional)

### Python API

#### 1. Local Recording Example

```python
from py_screen_grab import ScreenGrabber

# Method chaining for setup
grabber = ScreenGrabber()\
    .set_roi(x=100, y=100, width=800, height=600)\
    .set_fps(30)

# Record with preview
grabber.record(duration=10, show_preview=True)
```

#### 2. Window Capture Example

```python
from py_screen_grab import ScreenGrabber

# Capture a specific window
grabber = ScreenGrabber()\
    .set_window("Window Title")\
    .set_fps(30)

# Record with preview
grabber.record(duration=10, show_preview=True)
```

#### 3. Streaming Example

```python
from py_screen_grab import ScreenGrabber

# Start streaming
grabber = ScreenGrabber()\
    .set_roi(x=0, y=0, width=1920, height=1080)\
    .set_fps(30)

# Start streaming with preview
grabber.stream(show_preview=True)
```

<br/>
<br/>

## 📋 Requirements

- wmctrl (required for window management on Linux, especially 🐧**Ubuntu**)
- Python 3.6 or higher
- OpenCV
- NumPy
- MSS (screen capture library)
- aiortc (for WebRTC streaming)
- rx (for reactive streaming)

<br/>
<br/>

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<br/>
<br/>

## 🤝 Contributing

We welcome contributions to this project! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to get started.
