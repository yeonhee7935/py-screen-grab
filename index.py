from mss import mss
import numpy as np
import cv2
import time
from datetime import datetime
import os

class ScreenGrabber:
    def __init__(self):
        self.sct = mss()
        self.x_offset = 0
        self.y_offset = 0
        self.width = 640
        self.height = 480
        self.fps = 30
        
        self.save_dir = "recordings"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            print(f"저장 경로 생성됨: {os.path.abspath(self.save_dir)}")
    
    def set_roi(self, x_offset, y_offset, width, height):
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.width = width
        self.height = height
    
    def set_fps(self, fps):
        self.fps = fps
    
    def capture_screen(self):
        monitor = {
            "top": self.y_offset,
            "left": self.x_offset,
            "width": self.width,
            "height": self.height
        }
        screenshot = self.sct.grab(monitor)
        return np.array(screenshot)

    def preview_only(self):
        try:
            print("미리보기 시작... ('q' 키를 누르면 종료)")
            cv2.namedWindow('Preview', cv2.WINDOW_NORMAL)
            
            while True:
                frame = self.capture_screen()
                cv2.imshow('Preview', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                time.sleep(1/self.fps)
                
        finally:
            cv2.destroyAllWindows()
            print("미리보기 종료")

    def start_recording(self, duration=None):
        try:
            filename = f"screen_recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            filepath = os.path.join(self.save_dir, filename)
            
            # 기본 코덱 사용
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(filepath, fourcc, self.fps, (self.width, self.height))
            
            if not out.isOpened():
                # 실패시 가장 기본적인 코덱으로 시도
                fourcc = 0x7634706d  # mp4v의 직접 값
                out = cv2.VideoWriter(filepath, fourcc, self.fps, (self.width, self.height))
                
            if not out.isOpened():
                raise Exception("VideoWriter를 열 수 없습니다. pip install opencv-python-headless를 시도해보세요.")
            
            print(f"녹화 시작... ('q' 키를 누르면 종료)")
            print(f"저장 경로: {os.path.abspath(filepath)}")
            
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
                print(f"\r녹화 중... 경과 시간: {elapsed_time:.1f}초 "
                      f"(프레임: {frame_count})", end='')
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                if duration and elapsed_time >= duration:
                    break
                
                time.sleep(1/self.fps)
                
        except Exception as e:
            print(f"\n오류 발생: {e}")
        finally:
            out.release()
            cv2.destroyAllWindows()
            print(f"\n녹화 완료!")
            print(f"저장된 파일: {os.path.abspath(filepath)}")
            print(f"총 {frame_count}프레임 녹화됨 ({elapsed_time:.1f}초)")

def print_header():
    print("\n" + "="*40)
    print("         PyScreenGrab v1.0")
    print("         화면 녹화 프로그램")
    print("="*40 + "\n")

def get_monitor_info(grabber):
    """사용 가능한 모니터 정보를 출력하고 선택된 모니터 정보를 반환합니다."""
    print("\n[사용 가능한 모니터]")
    print("-" * 50)
    for i, monitor in enumerate(grabber.sct.monitors):
        print(f"모니터 {i}:")
        print(f"  ▶ 위치: ({monitor['left']}, {monitor['top']})")
        print(f"  ▶ 크기: {monitor['width']}x{monitor['height']}")
    print("-" * 50)
    
    while True:
        try:
            monitor_idx = int(input("\n캡처할 모니터 번호 선택 (0부터 시작): "))
            if 0 <= monitor_idx < len(grabber.sct.monitors):
                return grabber.sct.monitors[monitor_idx]
            print("❌ 잘못된 모니터 번호입니다. 다시 선택해주세요.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")

def get_custom_roi():
    """사용자 지정 영역의 좌표와 크기를 입력받아 반환합니다."""
    print("\n[사용자 지정 영역 설정]")
    print("-" * 30)
    try:
        x = int(input("X 좌표: "))
        y = int(input("Y 좌표: "))
        w = int(input("너비: "))
        h = int(input("높이: "))
        if w <= 0 or h <= 0:
            raise ValueError("너비와 높이는 양수여야 합니다.")
        return x, y, w, h
    except ValueError as e:
        print(f"❌ 잘못된 입력입니다: {e}")
        print("기본값으로 설정합니다 (0, 0, 640, 480)")
        return 0, 0, 640, 480

def get_capture_mode():
    """캡처 모드를 선택받습니다."""
    print("\n[캡처 모드 선택]")
    print("1. 전체 화면")
    print("2. 사용자 지정 영역")
    
    while True:
        choice = input("\n선택 (1 또는 2): ")
        if choice in ['1', '2']:
            return choice
        print("❌ 잘못된 선택입니다. 1 또는 2를 입력해주세요.")

def get_fps():
    """FPS 값을 입력받습니다."""
    while True:
        try:
            fps_input = input("\nFPS 설정 (기본 30): ").strip()
            if not fps_input:
                return 30
            fps = int(fps_input)
            if 1 <= fps <= 60:
                return fps
            print("❌ FPS는 1~60 사이의 값이어야 합니다.")
        except ValueError:
            print("❌ 올바른 숫자를 입력해주세요.")

def get_recording_mode():
    """녹화 모드를 선택받습니다."""
    print("\n[녹화 모드 선택]")
    print("1. 미리보기만")
    print("2. 녹화 시작")
    
    while True:
        mode = input("\n선택 (1 또는 2): ")
        if mode in ['1', '2']:
            return mode
        print("❌ 잘못된 선택입니다. 1 또는 2를 입력해주세요.")

def get_duration():
    """녹화 시간을 입력받습니다."""
    while True:
        try:
            duration = input("\n녹화 시간(초) 입력 (Enter 키는 무제한): ").strip()
            if not duration:
                return None
            duration_float = float(duration)
            if duration_float > 0:
                return duration_float
            print("❌ 녹화 시간은 양수여야 합니다.")
        except ValueError:
            print("❌ 올바른 숫자를 입력해주세요.")

def main():
    try:
        print_header()
        grabber = ScreenGrabber()
        
        # 캡처 영역 설정
        capture_mode = get_capture_mode()
        if capture_mode == "2":
            x, y, w, h = get_custom_roi()
            grabber.set_roi(x, y, w, h)
        else:
            monitor = get_monitor_info(grabber)
            grabber.set_roi(monitor["left"], monitor["top"], 
                          monitor["width"], monitor["height"])
        
        # FPS 설정
        fps = get_fps()
        grabber.set_fps(fps)
        
        # 녹화 모드 선택 및 실행
        mode = get_recording_mode()
        if mode == "1":
            grabber.preview_only()
        else:
            duration = get_duration()
            grabber.start_recording(duration)
            
    except KeyboardInterrupt:
        print("\n\n프로그램이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}")
    finally:
        print("\n프로그램을 종료합니다.")

if __name__ == "__main__":
    main()