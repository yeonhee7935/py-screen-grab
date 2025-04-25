# py_screen_grabber/test/test_screen_grabber.py

import unittest
import asyncio
import gi 

gi.require_version("Gst", "1.0")
gi.require_version('GstApp', '1.0')
from gi.repository import Gst
from py_screen_grab.screen_grabber import ScreenGrabber

class TestScreenGrabber(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.grabber = ScreenGrabber().set_monitor(0).set_fps(10)
        self.subject = await self.grabber.start_streaming()
        self.frame_count = 0
        self.done = asyncio.Event()
        self.loop = asyncio.get_running_loop()

    async def asyncTearDown(self):
        await self.grabber.stop_streaming()

    def _on_next(self, buffer: Gst.Buffer) -> None:
        self.frame_count += 1
        print(f"[Test] Frame #{self.frame_count}")
        if self.frame_count >= 5:
            self.loop.call_soon_threadsafe(
                lambda: asyncio.create_task(self.grabber.stop_streaming())
            )
            self.loop.call_soon_threadsafe(self.done.set)

    def _on_error(self, e: Exception) -> None:
        print(f"[Test] Error: {e}")
        self.done.set()

    def _on_completed(self) -> None:
        print("[Test] Completed.")
        self.done.set()

    async def test_stream_emits_frames(self):
        self.subject.subscribe(
            on_next=self._on_next,
            on_error=self._on_error,
            on_completed=self._on_completed,
        )

        try:
            await asyncio.wait_for(self.done.wait(), timeout=10)
        except asyncio.TimeoutError:
            self.fail("Timed out waiting for frames.")

        self.assertGreaterEqual(self.frame_count, 1, "No frames were emitted")

if __name__ == "__main__":
    unittest.main()
