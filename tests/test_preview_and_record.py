# py_screen_grabber/test/test_preview_and_record.py

import unittest
import os

from py_screen_grab.screen_grabber import ScreenGrabber
from py_screen_grab.tools.preview_and_record import preview_and_record

class TestPreviewAndRecord(unittest.IsolatedAsyncioTestCase):
    async def test_preview_and_record_runs(self):
        filename = "recordings/test_output.avi"
        grabber = ScreenGrabber().set_monitor(0).set_fps(10)
        # 녹화 시작
        await preview_and_record(
            grabber,
            duration=3.0,
            save=True,
            show_preview=False,
            filename=filename
        )

        # 파일이 생성됐는지 확인
        self.assertTrue(os.path.exists(filename))

if __name__ == "__main__":
    unittest.main()
