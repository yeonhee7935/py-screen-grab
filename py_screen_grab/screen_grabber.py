import os
import cv2
import numpy as np
import mss
import time
from datetime import datetime

class ScreenGrabber:
    def __init__(self):
        """Initialize screen grabber with default settings."""
        self.sct = mss.mss()
        self.fps = 30
        self.roi = {"left": 0, "top": 0, "width": 640, "height": 480}
        
        # Create save directory if it doesn't exist
        self.save_dir = os.path.join(os.getcwd(), "recordings")
        os.makedirs(self.save_dir, exist_ok=True)

    def set_roi(self, x, y, w, h):
        """Set region of interest for capture."""
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
        
        # 프레임 크기가 너무 크면 축소
        h, w = frame.shape[:2]
        max_height = 480
        if h > max_height:
            scale = max_height / h
            new_w = int(w * scale)
            new_h = max_height
            cv2.resizeWindow(window_name, new_w, new_h)
        
        # 창을 오른쪽 하단으로 이동
        screen = self.sct.monitors[0]  # 주 모니터 정보
        screen_w, screen_h = screen["width"], screen["height"]
        window_w = min(w, int(screen_w * 0.3))  # 화면 너비의 30%
        window_h = min(h, int(screen_h * 0.3))  # 화면 높이의 30%
        
        # 창 크기 조정
        cv2.resizeWindow(window_name, window_w, window_h)
        
        # 창 위치 설정 (오른쪽 하단)
        x = screen_w - window_w - 50  # 오른쪽에서 50픽셀 여백
        y = screen_h - window_h - 50  # 아래에서 50픽셀 여백
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

    def start_recording(self, duration=None):
        """Start recording the screen.
        
        Args:
            duration (float, optional): Recording duration in seconds. If None, records until interrupted.
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
                
                if first_frame:
                    window_name = self._setup_preview_window(frame)
                    first_frame = False
                
                cv2.imshow(window_name, frame)
                out.write(frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
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