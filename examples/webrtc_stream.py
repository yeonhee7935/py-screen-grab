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

class WebRTCStream:
    def __init__(self, frame_subject: Subject):
        """Initialize WebRTC stream handler
        
        Args:
            frame_subject (Subject): Observable stream of frames
        """
        self.frame_subject = frame_subject
        self._current_frame = None
        self._frame_ready = asyncio.Event()
        self.pc = None
        self._connection_ready = asyncio.Event()
        self._connection_closed = asyncio.Event()
        self.ice_candidates = []  # Store ICE candidates
        self._active = False  # 스트리밍 활성 상태
        self._last_frame_time = 0  # 마지막 프레임 처리 시간
        
        # Configure Google's public STUN server using RTCConfiguration
        self.rtc_configuration = RTCConfiguration(
            iceServers=[
                RTCIceServer(
                    urls=["stun:stun.l.google.com:19302"],
                    username="",  # STUN 서버는 credentials 불필요
                    credential=""
                )
            ]
        )
        
        # Subscribe to frame stream
        self.frame_subject.subscribe(
            on_next=self._update_frame,
            on_error=self._handle_error
        )

    def _update_frame(self, frame: np.ndarray) -> None:
        """Handle incoming frames
        
        Args:
            frame (np.ndarray): BGR format frame
        """
        try:
            # Ensure frame dimensions and data type are correct
            if not isinstance(frame, np.ndarray):
                logger.error("Frame must be numpy array")
                return
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Ensure frame dimensions are even (VP8 requirement)
            height, width = frame_rgb.shape[:2]
            if width % 2 == 1 or height % 2 == 1:
                width = width - (width % 2)
                height = height - (height % 2)
                frame_rgb = frame_rgb[:height, :width]

            # Create VideoFrame with RGB format
            video_frame = VideoFrame.from_ndarray(
                frame_rgb,
                format="rgb24"  # Changed from bgr24 to rgb24
            )
            
            # Set timing info
            video_frame.pts = int(time.time() * 90000)  # 90kHz clock rate
            video_frame.time_base = fractions.Fraction(1, 90000)
            
            self._current_frame = video_frame
            self._frame_ready.set()
            self._last_frame_time = time.time()
            
        except Exception as e:
            logger.error(f"Error updating frame: {e}")

    def _handle_error(self, error: Exception) -> None:
        """Handle stream errors
        
        Args:
            error (Exception): Error from frame stream
        """
        logger.error(f"Stream error: {error}")
        self._frame_ready.set()

    def create_track(self) -> VideoStreamTrack:
        """Create WebRTC video track
        
        Returns:
            VideoStreamTrack: Track for WebRTC connection
        """
        class ScreenVideoTrack(VideoStreamTrack):
            kind = "video"

            def __init__(self, stream):
                super().__init__()
                self.stream = stream
                self._timestamp = 0
                self._last_frame_time = 0
                self._fps = 30

            async def recv(self):
                try:
                    frame_interval = 1 / self._fps
                    
                    while True:
                        if not self.stream._active:
                            break

                        try:
                            await asyncio.wait_for(
                                self.stream._frame_ready.wait(), 
                                timeout=frame_interval
                            )
                            self.stream._frame_ready.clear()
                            
                            current_time = time.time()
                            if self._last_frame_time and (current_time - self._last_frame_time) < frame_interval:
                                await asyncio.sleep(frame_interval - (current_time - self._last_frame_time))
                            
                            frame = self.stream._current_frame
                            if frame is None:
                                # Create black frame with correct format
                                frame = VideoFrame(width=640, height=480, format="rgb24")
                                frame.planes[0].update(np.zeros((480, 640, 3), dtype=np.uint8))
                            
                            frame.pts = self._timestamp
                            self._timestamp += int(90000 / self._fps)
                            frame.time_base = fractions.Fraction(1, 90000)
                            
                            self._last_frame_time = time.time()
                            return frame
                            
                        except asyncio.TimeoutError:
                            # Create black frame on timeout
                            frame = VideoFrame(width=640, height=480, format="rgb24")
                            frame.planes[0].update(np.zeros((480, 640, 3), dtype=np.uint8))
                            frame.pts = self._timestamp
                            self._timestamp += int(90000 / self._fps)
                            frame.time_base = fractions.Fraction(1, 90000)
                            return frame
                            
                except Exception as e:
                    logger.error(f"Error in track recv: {e}")
                    raise

        return ScreenVideoTrack(self)

    async def start(self) -> str:
        """Start WebRTC connection and generate local SDP
        
        Returns:
            str: Local SDP offer in JSON format
        """
        if self.pc:
            await self.stop()
        
        self._active = True  # 스트리밍 활성화
        logger.info("Creating new RTCPeerConnection...")
        self.pc = RTCPeerConnection(configuration=self.rtc_configuration)
        
        # Keep connection alive with periodic checks
        asyncio.create_task(self._keep_alive())
        
        # Monitor connection state
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

        # Monitor ICE connection state
        @self.pc.on("iceconnectionstatechange")
        async def on_iceconnectionstatechange():
            logger.info(f"ICE connection state: {self.pc.iceConnectionState}")
            if self.pc.iceConnectionState == "disconnected":
                # Try to restart ICE
                await self.pc.restartIce()

        # Add video track
        logger.info("Adding video track...")
        self.pc.addTrack(self.create_track())
        
        # Create and set local description
        logger.info("Creating offer...")
        offer = await self.pc.createOffer()
        logger.info("Setting local description...")
        await self.pc.setLocalDescription(offer)
        
        # Wait for ICE gathering
        logger.info("Waiting for ICE gathering to complete...")
        await self._gather_candidates()
        
        # Prepare offer data
        offer_data = {
            "sdp": self.pc.localDescription.sdp,
            "type": self.pc.localDescription.type,
        }
        
        logger.info("Offer generated successfully")
        return json.dumps(offer_data)

    async def handle_answer(self, answer_sdp: str) -> None:
        """Handle remote SDP answer and wait for connection
        
        Args:
            answer_sdp (str): Remote SDP answer in JSON format
        """
        try:
            answer = json.loads(answer_sdp)
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
        """Keep the connection alive with periodic checks"""
        while self._active and self.pc:
            try:
                if self.pc.connectionState == "connected":
                    # Send empty frame if needed
                    if time.time() - getattr(self, '_last_frame_time', 0) > 1:
                        frame = VideoFrame(width=640, height=480)
                        self._current_frame = frame
                        self._frame_ready.set()
                        self._last_frame_time = time.time()
                
                elif self.pc.connectionState in ["failed", "closed"]:
                    logger.error(f"Connection lost: {self.pc.connectionState}")
                    break
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in keep_alive: {e}")
                break

    async def stop(self) -> None:
        """Stop WebRTC connection and cleanup resources"""
        self._active = False  # 스트리밍 비활성화
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
        """Wait for ICE candidate gathering completion"""
        candidates = []

        @self.pc.on("icecandidate")
        def on_ice_candidate(candidate):
            if candidate:
                candidates.append(candidate)
                logger.debug(f"New ICE candidate: {candidate}")

        # Wait for ICE gathering to complete
        while self.pc.iceGatheringState != "complete":
            await asyncio.sleep(0.1)
        
        logger.info(f"ICE gathering completed with {len(candidates)} candidates")