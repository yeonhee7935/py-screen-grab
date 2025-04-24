import asyncio
from py_screen_grab.screen_grabber import ScreenGrabber
from line_profiler import profile
@profile
async def test_start_streaming(max_frames: int = 30):
    grabber = ScreenGrabber(width=1920, height=1080, fps=30, show_cursor=True)
    frame_subject = await grabber.start_streaming()

    frame_count = 0
    done = asyncio.Event()

    def on_next(frame):
        nonlocal frame_count
        frame_count += 1
        print(f"Frame {frame_count} received.")
        if frame_count >= max_frames:
            asyncio.create_task(grabber.stop_streaming())

    def on_error(e):
        print(f"Error: {e}")
        done.set()

    def on_completed():
        print("Streaming stopped.")
        done.set()

    frame_subject.subscribe(on_next=on_next, on_error=on_error, on_completed=on_completed)
    await done.wait()


# asyncio 이벤트 루프 실행
if __name__ == "__main__":
    asyncio.run(test_start_streaming())