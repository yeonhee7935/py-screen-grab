import cv2
import asyncio
import time
from rx.subject import Subject
# convert it to a subject like a screen_grabber
# and use it in the webrtc_stream.py like webrtc = WebRTCStream(frame_subject)

class WebcamGrabber:
    def __init__(self, device_path="/dev/video0"):
        """웹캠 캡처를 위한 클래스 초기화"""
        self._frame_subject = Subject()
        self._is_capturing = False
        self.fps = 60  # 기본 FPS 설정
        self._cap = None
        self._device_path = device_path
    async def start_streaming(self) -> Subject:
        """비동기 프레임 스트리밍 시작
        
        Returns:
            Subject: 프레임 스트림을 위한 Observable
        """
        if self._is_capturing:
            return self._frame_subject

        self._cap = cv2.VideoCapture(self._device_path)
        if not self._cap.isOpened():
            raise RuntimeError("웹캠을 열 수 없습니다")

        self._is_capturing = True
        asyncio.create_task(self._capture_loop())
        return self._frame_subject

    async def stop_streaming(self) -> None:
        """스트리밍 중지 및 리소스 정리"""
        self._is_capturing = False
        if self._cap:
            self._cap.release()
            self._cap = None
        self._frame_subject.on_completed()

    async def _capture_loop(self) -> None:
        """메인 비동기 캡처 루프"""
        frame_time = 1 / self.fps
        last_frame_time = 0

        while self._is_capturing and self._cap and self._cap.isOpened():
            current_time = time.time()
            
            if current_time - last_frame_time < frame_time:
                await asyncio.sleep(frame_time - (current_time - last_frame_time))
                continue

            try:
                ret, frame = self._cap.read()
                if ret:
                    self._frame_subject.on_next(frame)
                    last_frame_time = time.time()
                    
            except Exception as e:
                print(f"캡처 루프 에러: {e}")
                break
 
