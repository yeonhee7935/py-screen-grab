from .screen_grabber import ScreenGrabber
from .window_utils import get_window

def print_header():
    """Print program header."""
    print("\n" + "="*40)
    print("         PyScreenGrab v1.0")
    print("         Screen Recording Tool")
    print("="*40 + "\n")

def get_monitor_info(grabber):
    """Display available monitor information and return selected monitor info."""
    print("\n[Available Monitors]")
    print("-" * 50)
    for i, monitor in enumerate(grabber.sct.monitors):
        print(f"Monitor {i}:")
        print(f"  ▶ Position: ({monitor['left']}, {monitor['top']})")
        print(f"  ▶ Size: {monitor['width']}x{monitor['height']}")
    print("-" * 50)
    
    while True:
        try:
            monitor_idx = int(input("\nSelect monitor number (starting from 0): "))
            if 0 <= monitor_idx < len(grabber.sct.monitors):
                return grabber.sct.monitors[monitor_idx]
            print("❌ Invalid monitor number. Please try again.")
        except ValueError:
            print("❌ Please enter a number.")

def get_custom_roi():
    """Get coordinates and size for custom region of interest."""
    print("\n[Custom Region Settings]")
    print("-" * 30)
    try:
        x = int(input("X coordinate: "))
        y = int(input("Y coordinate: "))
        w = int(input("Width: "))
        h = int(input("Height: "))
        if w <= 0 or h <= 0:
            raise ValueError("Width and height must be positive numbers.")
        return x, y, w, h
    except ValueError as e:
        print(f"❌ Invalid input: {e}")
        print("Using default values (0, 0, 640, 480)")
        return 0, 0, 640, 480

def get_capture_mode():
    """Select capture mode."""
    print("\n[Select Capture Mode]")
    print("1. Full Screen")
    print("2. Custom Region")
    print("3. Window Capture")
    
    while True:
        choice = input("\nChoice (1 or 2 or 3): ")
        if choice in ['1', '2', '3']:
            return choice
        print("❌ Invalid choice. Please enter 1 or 2.")

def get_fps():
    """Get FPS value."""
    while True:
        try:
            fps_input = input("\nSet FPS (default 30): ").strip()
            if not fps_input:
                return 30
            fps = int(fps_input)
            if 1 <= fps <= 60:
                return fps
            print("❌ FPS must be between 1 and 60.")
        except ValueError:
            print("❌ Please enter a valid number.")

def get_recording_mode():
    """Select recording mode."""
    print("\n[Select Recording Mode]")
    print("1. Preview Only")
    print("2. Start Recording")
    
    while True:
        mode = input("\nChoice (1 or 2): ")
        if mode in ['1', '2']:
            return mode
        print("❌ Invalid choice. Please enter 1 or 2.")

def get_duration():
    """Get recording duration."""
    while True:
        try:
            duration = input("\nEnter recording duration in seconds (Press Enter for unlimited): ").strip()
            if not duration:
                return None
            duration_float = float(duration)
            if duration_float > 0:
                return duration_float
            print("❌ Duration must be a positive number.")
        except ValueError:
            print("❌ Please enter a valid number.")

def get_show_preview():
    """Select whether to show preview during recording."""
    print("\n[Show Preview]")
    print("1. Yes")
    print("2. No")
    
    while True:
        choice = input("\nChoice (1 or 2): ")
        if choice in ['1', '2']:
            return choice == '1'  # Return True for 'Yes', False for 'No'
        print("❌ Invalid choice. Please enter 1 or 2.")

def main():
    """Main CLI entry point."""
    try:
        print_header()
        grabber = ScreenGrabber()
        
        # Set capture region
        capture_mode = get_capture_mode()
        if capture_mode == "2":
            x, y, w, h = get_custom_roi()
            grabber.set_roi(x, y, w, h)
        elif capture_mode == "3":
            window_list = get_window()
            print("\n[Available Windows]")
            print("-" * 50)
            for i, window in enumerate(window_list):
                print(f"Window {i}: {window}")
            window_name = input("\nEnter window name to capture: ")
            grabber.set_window(window_name)
        else:
            monitor = get_monitor_info(grabber)
            grabber.set_roi(monitor["left"], monitor["top"], 
                          monitor["width"], monitor["height"])
        
        # Set FPS
        fps = get_fps()
        grabber.set_fps(fps)
        
        # Select and execute recording mode
        mode = get_recording_mode()
        if mode == "1":
            # Preview only
            grabber.record(save_to_file=False)
        else:
            duration = get_duration()
            show_preview = get_show_preview()
            print("\nRecording started!")
            if not show_preview:
                print("Press Ctrl+C to stop recording")
            grabber.record(duration, show_preview)
            
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        print("\nExiting program.")

if __name__ == "__main__":
    main() 