import asyncio
from typing import Optional
from rx.subject import Subject
from rx.scheduler.eventloop import AsyncIOScheduler
from typing_extensions import TypedDict

import gi
gi.require_version("Gst", "1.0")
gi.require_version('GstApp', '1.0')
from gi.repository import Gst, GLib, GstApp

from py_screen_grab.window_utils import get_window_roi, get_monitor_list

DECORATION_OFFSET_X = 12
DECORATION_OFFSET_Y = 40

class ROI(TypedDict):
    x: int
    y: int
    width: int
    height: int

class ScreenGrabber:
    def __init__(self, left: int = 0, top: int = 0, width: int = 640, height: int = 480,
                 fps: int = 30, enable_logging: bool = True, show_cursor: bool = False) -> None:
        Gst.init(None)  
        self.fps = fps
        self.roi:ROI = {"x": left, "y": top, "width": width, "height": height}
        self.enable_logging = enable_logging
        self.show_cursor = show_cursor
        self._frame_subject: Subject = Subject()
        self._is_capturing = False
        self._scheduler = AsyncIOScheduler(asyncio.get_event_loop())
        self.pipeline: Optional[Gst.Pipeline] = None
        self.loop:Optional[GLib.MainLoop] = None
        self.bus: Optional[Gst.Bus] = None
    
    def _log(self, msg: str) -> None:
        if self.enable_logging:
            print(f"[ScreenGrabber] {msg}")

    def set_roi(self, x: int, y: int, w: int, h: int, adjust_for_decorations: bool = True) -> 'ScreenGrabber':
        if adjust_for_decorations:
            x -= DECORATION_OFFSET_X
            y -= DECORATION_OFFSET_Y * 2
            w += DECORATION_OFFSET_X
            h += DECORATION_OFFSET_Y
        self.roi = {"left": max(0, x), "top": max(0, y), "width": w, "height": h}
        self._log(f"ROI set to: {self.roi}")
        return self

    def set_fps(self, fps: int) -> 'ScreenGrabber':
        if not 1 <= fps <= 60:
            raise ValueError("FPS must be between 1 and 60")
        self.fps = fps
        return self
        
    def set_window(self, window_name: str) -> 'ScreenGrabber':
        window_info = get_window_roi(window_name)
        return self.set_roi(window_info["x"], window_info["y"],
                                window_info["width"], window_info["height"],
                                adjust_for_decorations=True)
        
    def set_monitor(self, monitor_number: int) -> 'ScreenGrabber':
        monitors = get_monitor_list()
        if monitor_number < 0 or monitor_number >= len(monitors):
            raise ValueError(f"Monitor {monitor_number} not found")
        monitor = monitors[monitor_number]
        return self.set_roi(monitor["left"], monitor["top"],
                            monitor["width"], monitor["height"],
                            adjust_for_decorations=False)
        
    def _create_pipeline_string(self) -> str:
        return (
            f"ximagesrc display-name=:0 use-damage=false show-pointer={str(self.show_cursor).lower()} "
            f"startx={self.roi['left']} starty={self.roi['top']} "
            f"endx={self.roi['left'] + self.roi['width']} endy={self.roi['top'] + self.roi['height']} ! "
            f"videoconvert ! videorate ! video/x-raw,framerate={self.fps}/1 ! "
            f"videoconvert ! appsink name=appsink emit-signals=true max-buffers=1 drop=true sync=false"
        )
        
    async def start_streaming(self) -> Subject:
        if self._is_capturing:
            return self._frame_subject
        self._is_capturing = True
        pipeline_str = self._create_pipeline_string()
        self.pipeline = Gst.parse_launch(pipeline_str)
        appsink = self.pipeline.get_by_name("appsink")
        appsink.connect("new-sample", self._on_new_sample, None)
        self.loop = GLib.MainLoop()
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self._on_bus_message, None)
        self.pipeline.set_state(Gst.State.PLAYING)
        asyncio.create_task(self._run_glib_loop())
        return self._frame_subject
    
    def _on_new_sample(self, sink: GstApp.AppSink, data: None) -> Gst.FlowReturn:
        sample = sink.emit("pull-sample")
        if sample:
            buffer  = sample.get_buffer()
            self._frame_subject.on_next(buffer)
            return Gst.FlowReturn.OK
        return Gst.FlowReturn.ERROR
    
    def _on_bus_message(  
        self, bus: Gst.Bus, message: Gst.Message, data: None
    ) -> None:
        if message.type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            self._log(f"Error: {err}, Debug: {debug}")
            if self.loop and self.loop.is_running():
                self.loop.quit()
            self._frame_subject.on_error(Exception("GStreamer error"))
        elif message.type == Gst.MessageType.EOS:
            self._log(f"EOS: End of stream")
            if self.loop and self.loop.is_running():
                self.loop.quit()
            self._frame_subject.on_completed()
        return True
    
    async def _run_glib_loop(self) -> None:
        try:
            while self._is_capturing and self.loop:
                context = GLib.MainContext.default()
                while context.pending():
                    context.iteration(False)
                await asyncio.sleep(0.01)
        except Exception as e:
            self._frame_subject.on_error(e)

    async def stop_streaming(self) -> None:
        if not self._is_capturing:
            return
        self._is_capturing = False
        if self.pipeline:
            self.pipeline.send_event(Gst.Event.new_eos())
            await asyncio.sleep(0.5)
            self.pipeline.set_state(Gst.State.NULL)
            if self.bus:
                self.bus.remove_signal_watch()
            if self.loop and self.loop.is_running():
                self.loop.quit()
        self._frame_subject.on_completed()