from mss import mss
import numpy as np
import cv2
import time
from datetime import datetime
import os

class ScreenGrabber:
    def __init__(self):
        """Initialize the ScreenGrabber."""
        self.sct = mss()
        self.x_offset = 0
        self.y_offset = 0
        self.width = 640
        self.height = 480
        self.fps = 30
        
        self.save_dir = "recordings"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            print(f"Save directory created: {os.path.abspath(self.save_dir)}")
    
    def set_roi(self, x_offset, y_offset, width, height):
        """Set Region of Interest for screen capture.
        
        Args:
            x_offset (int): X coordinate of the top-left corner
            y_offset (int): Y coordinate of the top-left corner
            width (int): Width of the capture region
            height (int): Height of the capture region
        """
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.width = width
        self.height = height
    
    def set_fps(self, fps):
        """Set frames per second for recording.
        
        Args:
            fps (int): Frames per second (1-60)
            
        Raises:
            ValueError: If fps is not between 1 and 60
        """
        if not 1 <= fps <= 60:
            raise ValueError("FPS must be between 1 and 60")
        self.fps = fps
    
    def capture_screen(self):
        """Capture a single frame from the screen.
        
        Returns:
            numpy.ndarray: Captured frame as a numpy array
        """
        monitor = {
            "top": self.y_offset,
            "left": self.x_offset,
            "width": self.width,
            "height": self.height
        }
        screenshot = self.sct.grab(monitor)
        return np.array(screenshot)

    def preview_only(self):
        """Show preview window of the capture region."""
        try:
            print("Starting preview... (Press 'q' to quit)")
            cv2.namedWindow('Preview', cv2.WINDOW_NORMAL)
            
            while True:
                frame = self.capture_screen()
                cv2.imshow('Preview', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                time.sleep(1/self.fps)
                
        finally:
            cv2.destroyAllWindows()
            print("Preview ended")

    def start_recording(self, duration=None):
        """Start recording the screen.
        
        Args:
            duration (float, optional): Recording duration in seconds. 
                                     If None, records until 'q' is pressed.
        """
        try:
            filename = f"screen_recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            filepath = os.path.join(self.save_dir, filename)
            
            # Use default codec
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(filepath, fourcc, self.fps, (self.width, self.height))
            
            if not out.isOpened():
                # Try with most basic codec if failed
                fourcc = 0x7634706d  # direct value for mp4v
                out = cv2.VideoWriter(filepath, fourcc, self.fps, (self.width, self.height))
                
            if not out.isOpened():
                raise Exception("Cannot open VideoWriter. Try pip install opencv-python-headless")
            
            print(f"Recording started... (Press 'q' to stop)")
            print(f"Save path: {os.path.abspath(filepath)}")
            
            cv2.namedWindow('Recording', cv2.WINDOW_NORMAL)
            
            start_time = time.time()
            frame_count = 0
            
            while True:
                frame = self.capture_screen()
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                
                out.write(frame_bgr)
                frame_count += 1
                
                cv2.imshow('Recording', frame)
                
                elapsed_time = time.time() - start_time
                print(f"\rRecording... Elapsed time: {elapsed_time:.1f}s "
                      f"(Frames: {frame_count})", end='')
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                if duration and elapsed_time >= duration:
                    break
                
                time.sleep(1/self.fps)
                
        except Exception as e:
            print(f"\nError occurred: {e}")
        finally:
            out.release()
            cv2.destroyAllWindows()
            print(f"\nRecording completed!")
            print(f"Saved file: {os.path.abspath(filepath)}")
            print(f"Total {frame_count} frames recorded ({elapsed_time:.1f} seconds)") 