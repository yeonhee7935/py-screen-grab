import os
import cv2
import numpy as np
import mss
import time
import asyncio   
from datetime import datetime
from typing import Optional, Dict, Any, Union
from rx.subject import Subject
from rx.scheduler.eventloop import AsyncIOScheduler
from .window_utils import get_window_roi

# Window decoration constants
DECORATION_OFFSET_X = 12  # Horizontal offset for window decorations
DECORATION_OFFSET_Y = 40  # Vertical offset for title bar

# TODO: 특정 화면을 선택할 수 있는 기능 추가(ex: 듀얼모니터, 싱글모니터1,2)
# TODO: 커서 색상 선택할 수 있는 기능 추가
class ScreenGrabber:
    def __init__(self, left=0, top=0, width=640, height=480, fps=30, enable_logging=True, show_cursor=False) -> None:
        """Initialize screen grabber with reactive streaming support
        
        Args:
            left (int): Left coordinate of capture region
            top (int): Top coordinate of capture region
            width (int): Width of capture region
            height (int): Height of capture region
            fps (int): Target frames per second
            enable_logging (bool): Whether to enable logging (default: True)
            show_cursor (bool): Whether to show cursor (default: False)
        """
        self.sct = mss.mss()
        self.fps = fps
        self.roi = {"left": left, "top": top, "width": width, "height": height}
        self.enable_logging = enable_logging  # Add logging control
        self.show_cursor = show_cursor
        
        # Create directory for recordings
        self.save_dir = os.path.join(os.getcwd(), "recordings")
        os.makedirs(self.save_dir, exist_ok=True)
        
        # Initialize reactive streaming components
        self._frame_subject = Subject()
        self._is_capturing = False
        self._scheduler = AsyncIOScheduler(asyncio.get_event_loop())

    def _log(self, message: str) -> None:
        """Log a message if logging is enabled."""
        if self.enable_logging:
            print(message)

    def set_roi(self, x, y, w, h, adjust_for_decorations=True) -> 'ScreenGrabber':
        """Set region of interest for capture.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            w (int): Width
            h (int): Height
            adjust_for_decorations (bool): Whether to adjust for window decorations
            
        Returns:
            ScreenGrabber: self for method chaining
            
        Raises:
            ValueError: If width or height is not positive
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
        return self

    def set_fps(self, fps) -> 'ScreenGrabber':
        """Set frames per second for recording.
        
        Args:
            fps (int): Frames per second (1-60)
            
        Returns:
            ScreenGrabber: self for method chaining
            
        Raises:
            ValueError: If fps is not between 1 and 60
        """
        if not 1 <= fps <= 60:
            raise ValueError("FPS must be between 1 and 60")
        self.fps = fps
        return self

    def set_window(self, window_name: str) -> 'ScreenGrabber':
        """Set ROI based on window name.
        
        Args:
            window_name (str): Name of the window to capture
            
        Returns:
            ScreenGrabber: self for method chaining
            
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
            self._log(f"Window '{window_info['name']}' selected for capture")
            return self
        except Exception as e:
            raise Exception(f"Failed to set window: {str(e)}")

    def record(self, duration=None, show_preview=True, save_to_file=True) -> Union[str, None]:
        """Record or preview the screen.
        
        Args:
            duration (float, optional): Recording duration in seconds. If None, continues until interrupted.
            show_preview (bool): Whether to show preview window. Defaults to True.
            save_to_file (bool): Whether to save recording to a file. If False, only shows preview.
            
        Returns:
            str: Path to the recorded file if save_to_file is True
            None: If save_to_file is False
        """
        if not save_to_file:
            self._show_preview()
            return None
        
        return self._record_to_file(duration, show_preview)

    async def start_streaming(self) -> Subject:
        """Start async frame streaming
        
        Returns:
            Subject: Observable stream of frames
        """
        if self._is_capturing:
            return self._frame_subject

        self._is_capturing = True
        asyncio.create_task(self._capture_loop())
        return self._frame_subject

    async def stop_streaming(self) -> None:
        """Stop streaming and cleanup resources"""
        self._is_capturing = False
        self._frame_subject.on_completed()

    def _draw_cursor_on_frame(self, frame: np.ndarray) -> None:
        """Draw cursor on the frame if show_cursor is True."""
        import pyautogui
        
        try:
            cursor_x, cursor_y = pyautogui.position()
            if (self.roi["left"] <= cursor_x < self.roi["left"] + self.roi["width"] and
                self.roi["top"] <= cursor_y < self.roi["top"] + self.roi["height"]):
                relative_x = cursor_x - self.roi["left"]
                relative_y = cursor_y - self.roi["top"]
                cv2.circle(frame, (relative_x, relative_y), 8, (0, 255, 0), -1)  # Red circle
        except Exception as e:
            self._log(f"Error capturing cursor: {e}")

    def _capture_frame(self) -> np.ndarray:
        """Capture single frame
        
        Returns:
            np.ndarray: Captured frame in BGR format
        """
        screenshot = self.sct.grab(self.roi)
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)
        if self.show_cursor:
            self._draw_cursor_on_frame(frame)
        return frame

    async def _capture_loop(self) -> None:
        """Main async capture loop using only Subject"""
        frame_time = 1 / self.fps
        last_frame_time = 0

        while self._is_capturing:
            current_time = time.time()
            
            # Maintain consistent FPS
            if current_time - last_frame_time < frame_time:
                await asyncio.sleep(frame_time - (current_time - last_frame_time))
                continue

            try:
                frame = self._capture_frame()
                self._log(f"Captured frame at {time.time()} {frame.shape}")
                
                # Emit the frame to subscribers
                self._frame_subject.on_next(frame)
                last_frame_time = time.time()
                    
            except Exception as e:
                self._log(f"Error in capture loop: {e}")
                self._frame_subject.on_error(e)
                break

    def _setup_preview_window(self, frame) -> str:
        """Set up preview window with appropriate size and position.
        
        Args:
            frame (np.ndarray): Frame to display in preview window
            
        Returns:
            str: Window name
        """
        window_name = 'Preview (Press q to quit)'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        # If frame size is too large, resize it
        h, w = frame.shape[:2]
        max_height = 480
        if h > max_height:
            scale = max_height / h
            new_w = int(w * scale)
            new_h = max_height
            cv2.resizeWindow(window_name, new_w, new_h)
        
        # Move window to right bottom
        screen = self.sct.monitors[0]   
        screen_w, screen_h = screen["width"], screen["height"]
        window_w = min(w, int(screen_w * 0.3))  # 30% of screen width
        window_h = min(h, int(screen_h * 0.3))  # 30% of screen height
        
        # Resize window
        cv2.resizeWindow(window_name, window_w, window_h)
        
        # Set window position to right bottom
        x = screen_w - window_w - 50  # 50 pixel gap from right
        y = screen_h - window_h - 50  # 50 pixel gap from bottom
        cv2.moveWindow(window_name, x, y)
        
        return window_name

    def _show_preview(self) -> None:
        """Show preview of the capture region without recording.
        
        Returns:
            None
        """
        first_frame = True
        window_name = None
        
        try:
            while True:
                frame = self._capture_frame()
                
                if first_frame:
                    window_name = self._setup_preview_window(frame)
                    first_frame = False
                
                cv2.imshow(window_name, frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            cv2.destroyAllWindows()

    def _record_to_file(self, duration=None, show_preview=True) -> str:
        """Record the screen to a file.
        
        Args:
            duration (float, optional): Recording duration in seconds. If None, records until interrupted.
            show_preview (bool): Whether to show preview window while recording.
            
        Returns:
            str: Path to the recorded file
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
                frame = self._capture_frame()
                
                if show_preview:
                    if first_frame:
                        window_name = self._setup_preview_window(frame)
                        first_frame = False
                    cv2.imshow(window_name, frame)
                    
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
            self._log("\nRecording interrupted by user")
        finally:
            out.release()
            cv2.destroyAllWindows()
            self._log(f"\nRecording saved to: {filename}")
            return filename