import pytest
import asyncio
import numpy as np
from rx.subject import Subject
from ..webrtc_stream import WebRTCStream

@pytest.fixture
def frame_subject():
    return Subject()

@pytest.fixture
def webrtc_stream(frame_subject):
    return WebRTCStream(frame_subject)

@pytest.mark.asyncio
async def test_webrtc_stream_creation(webrtc_stream):
    assert webrtc_stream is not None
    assert webrtc_stream.pc is None

@pytest.mark.asyncio
async def test_webrtc_offer_generation(webrtc_stream):
    offer_sdp = await webrtc_stream.start()
    assert offer_sdp is not None
    assert "sdp" in offer_sdp
    assert "type" in offer_sdp

@pytest.mark.asyncio
async def test_frame_handling(webrtc_stream):
    # 테스트용 프레임 생성
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # 프레임 전송
    webrtc_stream.frame_subject.on_next(test_frame)
    
    # 프레임 수신 확인
    assert webrtc_stream._current_frame is not None

@pytest.mark.asyncio
async def test_webrtc_cleanup(webrtc_stream):
    await webrtc_stream.start()
    assert webrtc_stream.pc is not None
    
    await webrtc_stream.stop()
    assert webrtc_stream.pc is None 