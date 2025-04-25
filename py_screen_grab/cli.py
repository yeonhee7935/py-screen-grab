# py_screen_grabber/cli.py

import asyncio
from py_screen_grab.screen_grabber import ScreenGrabber
from py_screen_grab.window_utils import get_monitor_list
from py_screen_grab.tools.preview_and_record import preview_and_record

def main() -> None:
    print("\n🎥 PyScreenGrab CLI")
    print("1. Monitor Capture")
    print("2. Window Capture")
    print("3. Custom ROI")
    mode = input("Select mode: ")

    grabber = ScreenGrabber()

    if mode == "1":
        monitors = get_monitor_list()
        for i, m in enumerate(monitors):
            print(f"{i}: {m['width']}x{m['height']}")
        idx = int(input("Select monitor index: "))
        grabber.set_monitor(idx)
    elif mode == "2":
        name = input("Enter window name (partial): ")
        grabber.set_window(name)
    else:
        x = int(input("X: "))
        y = int(input("Y: "))
        w = int(input("Width: "))
        h = int(input("Height: "))
        grabber.set_roi(x, y, w, h)

    fps = int(input("FPS (default 30): ") or 30)
    grabber.set_fps(fps)

    show = input("Show preview? (y/n): ").lower() == "y"
    save = input("Save to file? (y/n): ").lower() == "y"
    duration = float(input("Duration in seconds: ") or 10)

    asyncio.run(preview_and_record(grabber, duration=duration, save=save, show_preview=show))

if __name__ == "__main__":
    main()
