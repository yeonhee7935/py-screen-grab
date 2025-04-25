# py_screen_grabber/tools/preview_and_record.py

import asyncio
import cv2
import numpy as np
import os
from datetime import datetime

import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst
from py_screen_grab.screen_grabber import ScreenGrabber

def buffer_to_ndarray(buffer: Gst.Buffer, width: int, height: int) -> np.ndarray:
    """
    Convert Gst.Buffer to np.ndarray, handling dynamic number of channels (RGB/RGBA).

    Args:
        buffer: GStreamer buffer
        width: expected frame width
        height: expected frame height

    Returns:
        np.ndarray (BGR): OpenCV-compatible frame
    """
    success, map_info = buffer.map(Gst.MapFlags.READ)
    if not success:
        raise RuntimeError("Failed to map Gst.Buffer")

    try:
        raw = np.frombuffer(map_info.data, dtype=np.uint8)
        channels = raw.size // (width * height)
        frame = raw.reshape((height, width, channels))

        if channels in (3, 4):
            return frame[:, :, :3]
        else:
            raise ValueError(f"Unsupported channel count: {channels}")
    finally:
        buffer.unmap(map_info)


async def preview_and_record(
    grabber: ScreenGrabber,
    duration: float = 10.0,
    save: bool = True,
    show_preview: bool = True,
    filename: str = None
) -> None:
    subject = await grabber.start_streaming()

    os.makedirs("recordings", exist_ok=True)
    filename = filename or f"recordings/gstreamer_recording_{datetime.now().strftime('%H%M%S')}.avi"
    ext = os.path.splitext(filename)[1].lower()

    writer = None
    if save:
        if ext == ".avi":
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")  
        elif ext == ".mp4":
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")  
        else:
            raise ValueError("Unsupported extension. Use .avi or .mp4")

        writer = cv2.VideoWriter(
            filename,
            fourcc,
            grabber.fps,
            (grabber.roi["width"], grabber.roi["height"])
        )

    done = asyncio.Event()

    def on_next(buffer: Gst.Buffer) -> None:
        frame = buffer_to_ndarray(buffer, grabber.roi["width"], grabber.roi["height"])

        if show_preview:
            cv2.imshow("Preview", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                asyncio.create_task(grabber.stop_streaming())
                done.set()

        if save and writer:
            writer.write(frame)

    subject.subscribe(
        on_next=on_next,
        on_error=lambda e: done.set(),
        on_completed=lambda: done.set()
    )

    try:
        await asyncio.wait_for(done.wait(), timeout=duration)
    except asyncio.TimeoutError:
        await grabber.stop_streaming()
    finally:
        if writer:
            writer.release()
        cv2.destroyAllWindows()
        print(f"[Done] Recording {'saved to ' + filename if save else 'finished without saving'}.")
