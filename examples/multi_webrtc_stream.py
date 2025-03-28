from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack, RTCConfiguration, RTCIceServer
from av import VideoFrame
import asyncio
import numpy as np
from rx.subject import Subject
import json
import logging
import time
import fractions
import cv2 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiWebRTCStream:
    def __init__(self, frame_subjects: dict[str, Subject]):
        """여러 미디어 스트림을 처리하는 WebRTC 핸들러 초기화
        
        Args:
            frame_subjects (dict[str, Subject]): 스트림 ID와 프레임 Subject 매핑
        """
        self.frame_subjects = frame_subjects
        self._current_frames = {stream_id: None for stream_id in frame_subjects.keys()}
        self._frame_ready = {stream_id: asyncio.Event() for stream_id in frame_subjects.keys()}
        self.pc = None
        self._connection_ready = asyncio.Event()
        self._connection_closed = asyncio.Event()
        self.ice_candidates = []
        self._active = True
        self._last_frame_times = {stream_id: 0 for stream_id in frame_subjects.keys()}
        
        # STUN 서버 설정
        self.rtc_configuration = RTCConfiguration(
            iceServers=[
                RTCIceServer(
                    urls=["stun:stun.l.google.com:19302"],
                    username="",
                    credential=""
                )
            ]
        )
        
        # 각 스트림 구독
        for stream_id, subject in frame_subjects.items():
            subject.subscribe(
                on_next=lambda frame, sid=stream_id: self._update_frame(frame, sid),
                on_error=self._handle_error
            )

    def _update_frame(self, frame: np.ndarray, stream_id: str) -> None:
        """특정 스트림의 프레임 업데이트 처리
        
        Args:
            frame (np.ndarray): BGR 형식 프레임
            stream_id (str): 스트림 식별자
        """
        try:
            if not isinstance(frame, np.ndarray):
                logger.error(f"Frame must be numpy array for stream {stream_id}")
                return
            
            # BGR to RGB 변환
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # VP8 요구사항을 위한 짝수 차원 보장
            height, width = frame_rgb.shape[:2]
            if width % 2 == 1 or height % 2 == 1:
                width = width - (width % 2)
                height = height - (height % 2)
                frame_rgb = frame_rgb[:height, :width]

            # 프레임 크기 조정 (필요한 경우)
            target_width, target_height = 640, 480
            if frame_rgb.shape[1] != target_width or frame_rgb.shape[0] != target_height:
                frame_rgb = cv2.resize(frame_rgb, (target_width, target_height))

            # VideoFrame 생성
            video_frame = VideoFrame.from_ndarray(
                frame_rgb,
                format="rgb24"
            )
            
            # 타이밍 정보 설정
            current_time = time.time()
            video_frame.pts = int(current_time * 90000)
            video_frame.time_base = fractions.Fraction(1, 90000)
            
            # 프레임 업데이트
            self._current_frames[stream_id] = video_frame
            self._frame_ready[stream_id].set()
            self._last_frame_times[stream_id] = current_time
            
        except Exception as e:
            logger.error(f"Error updating frame for stream {stream_id}: {e}")
            # 에러 발생 시 빈 프레임 생성
            frame = VideoFrame(width=640, height=480, format="rgb24")
            frame.planes[0].update(np.zeros((480, 640, 3), dtype=np.uint8))
            self._current_frames[stream_id] = frame
            self._frame_ready[stream_id].set()
            self._last_frame_times[stream_id] = time.time()

    def _handle_error(self, error: Exception) -> None:
        """스트림 에러 처리
        
        Args:
            error (Exception): 프레임 스트림 에러
        """
        logger.error(f"Stream error: {error}")

    def create_track(self, stream_id: str) -> VideoStreamTrack:
        """특정 스트림을 위한 WebRTC 비디오 트랙 생성"""
        class StreamVideoTrack(VideoStreamTrack):
            kind = "video"

            def __init__(self, stream, sid):
                super().__init__()
                self.stream = stream
                self.stream_id = sid
                self._timestamp = 0
                self._last_frame_time = 0
                self._fps = 30
                # 트랙의 메타데이터 설정
                self.meta = sid  # 이 부분이 중요합니다
                # 스트림 ID 설정
                self._stream_id = f"stream_{sid}"  # 각 트랙마다 고유한 스트림 ID 생성

            async def recv(self):
                try:
                    frame_interval = 1 / self._fps
                    
                    while True:
                        if not self.stream._active:
                            break

                        try:
                            await asyncio.wait_for(
                                self.stream._frame_ready[self.stream_id].wait(), 
                                timeout=frame_interval
                            )
                            self.stream._frame_ready[self.stream_id].clear()
                            
                            current_time = time.time()
                            if self._last_frame_time and (current_time - self._last_frame_time) < frame_interval:
                                await asyncio.sleep(frame_interval - (current_time - self._last_frame_time))
                            
                            frame = self.stream._current_frames[self.stream_id]
                            if frame is None:
                                frame = VideoFrame(width=640, height=480, format="rgb24")
                                frame.planes[0].update(np.zeros((480, 640, 3), dtype=np.uint8))
                            
                            frame.pts = self._timestamp
                            self._timestamp += int(90000 / self._fps)
                            frame.time_base = fractions.Fraction(1, 90000)
                            
                            self._last_frame_time = time.time()
                            return frame
                            
                        except asyncio.TimeoutError:
                            frame = VideoFrame(width=640, height=480, format="rgb24")
                            frame.planes[0].update(np.zeros((480, 640, 3), dtype=np.uint8))
                            frame.pts = self._timestamp
                            self._timestamp += int(90000 / self._fps)
                            frame.time_base = fractions.Fraction(1, 90000)
                            return frame
                            
                except Exception as e:
                    logger.error(f"Error in track recv for stream {self.stream_id}: {e}")
                    raise

        track = StreamVideoTrack(self, stream_id)
        return track

    async def start(self) -> str:
        """WebRTC 연결 시작 및 로컬 SDP 생성
        
        Returns:
            str: JSON 형식의 로컬 SDP offer와 메타데이터
        """
        if self.pc:
            await self.stop()
        
        self._active = True
        logger.info("Creating new RTCPeerConnection...")
        self.pc = RTCPeerConnection(configuration=self.rtc_configuration)
        
        # 연결 상태 모니터링
        asyncio.create_task(self._keep_alive())
        
        @self.pc.on("connectionstatechange")
        async def on_connectionstatechange():
            logger.info(f"Connection state changed to: {self.pc.connectionState}")
            if self.pc.connectionState == "connected":
                self._connection_ready.set()
            elif self.pc.connectionState == "closed":
                self._connection_closed.set()
            elif self.pc.connectionState == "failed":
                logger.error("Connection failed")
                await self.stop()

        @self.pc.on("iceconnectionstatechange")
        async def on_iceconnectionstatechange():
            logger.info(f"ICE connection state: {self.pc.iceConnectionState}")
            if self.pc.iceConnectionState == "disconnected":
                await self.pc.restartIce()

        # 트랙과 메타데이터를 저장할 딕셔너리
        tracks = {}
        media_stream_metadata = {}
        
        # 각 스트림에 대한 트랙 추가
        for subject_id in self.frame_subjects.keys():
            track = self.create_track(subject_id)
            tracks[track.id] = subject_id
            self.pc.addTrack(track)
        
        # 로컬 description 생성 및 설정
        logger.info("Creating offer...")
        offer = await self.pc.createOffer()
        logger.info("Setting local description...")
        await self.pc.setLocalDescription(offer)
        
        # ICE 수집 대기
        logger.info("Waiting for ICE gathering to complete...")
        await self._gather_candidates()
        
        # 트랙의 실제 stream ID를 사용하여 메타데이터 설정
        for track_id, subject_id in tracks.items(): 
            # track.id는 트랙의 고유 ID입니다
            # track의 stream ID를 가져옵니다 (SDP에서 msid 값)
            media_stream_metadata[track_id] =  subject_id
            
        
        offer_data = {
            "kind": "sessionDescription",
            "sessionDescription": {
                "sdp": self.pc.localDescription.sdp,
                "type": self.pc.localDescription.type,
            },
            "mediaStreamMetadata": media_stream_metadata
        }
        
        logger.info("Offer generated successfully with metadata")
        return json.dumps(offer_data)

    def _get_stream_id_from_track(self, track) -> str:
        """트랙의 stream ID를 SDP에서 추출"""
        sdp = self.pc.localDescription.sdp
        track_id = track.id
        
        # SDP에서 해당 트랙의 msid를 찾습니다
        for line in sdp.split('\n'):
            if 'msid:' in line and track_id in line:
                # msid:<stream_id> <track_id> 형식에서 stream_id를 추출
                stream_id = line.split('msid:')[1].split()[0]
                return stream_id
        
        # stream ID를 찾지 못한 경우 track ID를 반환
        return track_id

    async def handle_answer(self, answer_sdp: str) -> None:
        """원격 SDP answer 처리 및 연결 대기
        
        Args:
            answer_sdp (str): JSON 형식의 원격 SDP answer와 메타데이터
        """
        try:
            answer_data = json.loads(answer_sdp)
            answer = answer_data["sessionDescription"]
            
            # 메타데이터 처리 (필요한 경우)
            if "mediaStreamMetadata" in answer_data:
                media_metadata = answer_data["mediaStreamMetadata"]
                logger.info(f"Received stream metadata: {media_metadata}")
                # 여기서 메타데이터를 저장하거나 처리할 수 있습니다
            
            logger.info("Setting remote description...")
            await self.pc.setRemoteDescription(
                RTCSessionDescription(sdp=answer["sdp"], type=answer["type"])
            )
            
            # ICE 연결 대기
            logger.info("Waiting for ICE connection...")
            async def wait_for_ice_connected():
                while True:
                    if self.pc.iceConnectionState == "connected":
                        return True
                    if self.pc.iceConnectionState == "failed":
                        return False
                    await asyncio.sleep(0.1)

            try:
                ice_connected = await asyncio.wait_for(wait_for_ice_connected(), timeout=50.0)
                if not ice_connected:
                    raise ConnectionError("ICE Connection failed")
                logger.info("ICE Connection established")
                
                # 연결 설정 대기
                await asyncio.wait_for(self._connection_ready.wait(), timeout=50.0)
                logger.info("WebRTC connection established successfully")
                
            except asyncio.TimeoutError:
                raise ConnectionError("Connection establishment timed out")

        except Exception as e:
            logger.error(f"Error in handle_answer: {e}")
            await self.stop()
            raise

    async def _keep_alive(self):
        """연결 유지를 위한 주기적 체크"""
        while self._active and self.pc:
            try:
                if self.pc.connectionState == "connected":
                    # 각 스트림에 대해 빈 프레임 전송
                    for stream_id in self.frame_subjects.keys():
                        if time.time() - self._last_frame_times[stream_id] > 1:
                            frame = VideoFrame(width=640, height=480)
                            self._current_frames[stream_id] = frame
                            self._frame_ready[stream_id].set()
                            self._last_frame_times[stream_id] = time.time()
                
                elif self.pc.connectionState in ["failed", "closed"]:
                    logger.error(f"Connection lost: {self.pc.connectionState}")
                    break
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in keep_alive: {e}")
                break

    async def stop(self) -> None:
        """WebRTC 연결 중지 및 리소스 정리"""
        self._active = False
        if self.pc:
            if not self._connection_closed.is_set():
                logger.info("Closing peer connection...")
                await self.pc.close()
                try:
                    await asyncio.wait_for(self._connection_closed.wait(), timeout=3.0)
                except asyncio.TimeoutError:
                    logger.warning("Connection close timed out")
            self.pc = None

    async def _gather_candidates(self):
        """ICE candidate 수집 완료 대기"""
        candidates = []

        @self.pc.on("icecandidate")
        def on_ice_candidate(candidate):
            if candidate:
                candidates.append(candidate)
                logger.debug(f"New ICE candidate: {candidate}")

        while self.pc.iceGatheringState != "complete":
            await asyncio.sleep(0.1)
        
        logger.info(f"ICE gathering completed with {len(candidates)} candidates") 