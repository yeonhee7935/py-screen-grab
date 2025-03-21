import os
import cv2
import numpy as np
import mss
import time
from datetime import datetime
from typing import Optional
from .window_utils import get_window_roi

# Window decoration constants
DECORATION_OFFSET_X = 12  # 좌우 보정값
DECORATION_OFFSET_Y = 40  # 상단 타이틀바 보정값

class ScreenGrabber:
    def __init__(self, left=0, top=0, width=640, height=480, fps=30):
        """Initialize screen grabber with default settings."""
        self.sct = mss.mss()
        self.fps = fps
        self.roi = {"left": left, "top": top, "width": width, "height": height}
        
        # Create save directory if it doesn't exist
        self.save_dir = os.path.join(os.getcwd(), "recordings")
        os.makedirs(self.save_dir, exist_ok=True)

    def set_roi(self, x, y, w, h, adjust_for_decorations=True):
        """Set region of interest for capture.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            w (int): Width
            h (int): Height
            adjust_for_decorations (bool): Whether to adjust for window decorations
        """
        screen = self.sct.monitors[0]
        screen_width = screen['width']
        screen_height = screen['height']
        
        if adjust_for_decorations:
            x -= DECORATION_OFFSET_X
            y -= DECORATION_OFFSET_Y * 2
            w += DECORATION_OFFSET_X 
            h += DECORATION_OFFSET_Y 
        
        # Adjust coordinates and dimensions to fit within the screen
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x + w > screen_width:
            w = screen_width - x
        if y + h > screen_height:
            h = screen_height - y
        if w <= 0 or h <= 0:
            raise ValueError("Width and height must be positive numbers")
        
        self.roi = {"left": x, "top": y, "width": w, "height": h}

    def set_fps(self, fps):
        """Set frames per second for recording."""
        if not 1 <= fps <= 60:
            raise ValueError("FPS must be between 1 and 60")
        self.fps = fps

    def capture_screen(self):
        """Capture a single frame from the screen."""
        screenshot = self.sct.grab(self.roi)
        # Convert from BGRA to BGR
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)
        return frame

    def _setup_preview_window(self, frame):
        """Set up preview window with appropriate size and position."""
        window_name = 'Preview (Press q to quit)'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        # if frame size is too large, resize it
        h, w = frame.shape[:2]
        max_height = 480
        if h > max_height:
            scale = max_height / h
            new_w = int(w * scale)
            new_h = max_height
            cv2.resizeWindow(window_name, new_w, new_h)
        
        # move window to right bottom
        screen = self.sct.monitors[0]   
        screen_w, screen_h = screen["width"], screen["height"]
        window_w = min(w, int(screen_w * 0.3))  # 화면 너비의 30%
        window_h = min(h, int(screen_h * 0.3))  # 화면 높이의 30%
        
        # resize window
        cv2.resizeWindow(window_name, window_w, window_h)
        
        # set window position to right bottom
        x = screen_w - window_w - 50  # 50 pixel gap from right
        y = screen_h - window_h - 50  # 50 pixel gap from bottom
        cv2.moveWindow(window_name, x, y)
        
        return window_name

    def preview_only(self):
        """Show preview of the capture region."""
        first_frame = True
        window_name = None
        
        try:
            while True:
                frame = self.capture_screen()
                
                if first_frame:
                    window_name = self._setup_preview_window(frame)
                    first_frame = False
                
                cv2.imshow(window_name, frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            cv2.destroyAllWindows()

    def start_recording(self, duration=None, show_preview=True):
        """Start recording the screen.
        
        Args:
            duration (float, optional): Recording duration in seconds. If None, records until interrupted.
            show_preview (bool): Whether to show preview window while recording. Defaults to True.
        """
        filename = os.path.join(
            self.save_dir,
            f"screen_recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        )
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filename, fourcc, self.fps, 
                            (self.roi["width"], self.roi["height"]))
        
        start_time = time.time()
        frame_time = 1 / self.fps
        first_frame = True
        window_name = None
        
        try:
            while True:
                frame_start = time.time()
                frame = self.capture_screen()
                
                if show_preview:
                    if first_frame:
                        window_name = self._setup_preview_window(frame)
                        first_frame = False
                    cv2.imshow(window_name, frame)
                    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else: 
                    if time.time() - start_time > 0.1:  
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                
                out.write(frame)
                
                if duration and (time.time() - start_time) >= duration:
                    break
                    
                # Maintain consistent FPS
                time_elapsed = time.time() - frame_start
                if time_elapsed < frame_time:
                    time.sleep(frame_time - time_elapsed)
                    
        except KeyboardInterrupt:
            print("\nRecording interrupted by user")
        finally:
            out.release()
            cv2.destroyAllWindows()
            print(f"\nRecording saved to: {filename}") 

    def set_window(self, window_name: str) -> None:
        """Set ROI based on window name using wmctrl.
        
        Args:
            window_name (str): Name of the window to capture
            
        Raises:
            Exception: If window is not found or setting ROI fails
        """
        try:
            window_info = get_window_roi(window_name)
            self.set_roi(
                x=window_info["x"],
                y=window_info["y"],
                w=window_info["width"],
                h=window_info["height"],
                adjust_for_decorations=True
            )
            print(f"Window '{window_info['name']}' selected for capture")
        except Exception as e:
            raise Exception(f"Failed to set window: {str(e)}") 