# py_screen_grabber/tools/profile_streaming.py

import asyncio
import os
import psutil
import threading
import signal 
import time
import GPUtil
from py_screen_grab.screen_grabber import ScreenGrabber

stop_event = threading.Event()
cpu_usages = []
gpu_usages = []
process = psutil.Process(os.getpid())

def monitor_cpu(interval: float = 0.5):
    while not stop_event.is_set():
        cpu = process.cpu_percent(interval=interval)
        cpu_usages.append(cpu)

def monitor_gpu(interval: float = 0.5):
    while not stop_event.is_set():
        gpus = GPUtil.getGPUs()
        if gpus:
            usage = gpus[0].load * 100  # 첫 번째 GPU
            gpu_usages.append(usage)
        time.sleep(interval)

async def profile_streaming(fps: int = 30):
    grabber = ScreenGrabber().set_monitor(0).set_fps(fps)

    def handle_sigint(sig, frame):
        print("\n[INTERRUPT] Ctrl+C received. Stopping...")
        stop_event.set()

    signal.signal(signal.SIGINT, handle_sigint)

    cpu_thread = threading.Thread(target=monitor_cpu)
    gpu_thread = threading.Thread(target=monitor_gpu)

    cpu_thread.start()
    gpu_thread.start()

    print(f"[START] Streaming started. Press Ctrl+C to stop.")
    await grabber.start_streaming()

    try:
        while not stop_event.is_set():
            await asyncio.sleep(0.1)
    finally:
        await grabber.stop_streaming()
        stop_event.set()

        cpu_thread.join()
        gpu_thread.join()

        if cpu_usages:
            print(f"\n[RESULT] Average CPU usage: {sum(cpu_usages)/len(cpu_usages):.2f}%")
            print(f"[RESULT] Max CPU usage: {max(cpu_usages):.2f}%")
        else:
            print("\n[RESULT] No CPU usage data was recorded.")

        if gpu_usages:
            print(f"[RESULT] Average GPU usage: {sum(gpu_usages)/len(gpu_usages):.2f}%")
            print(f"[RESULT] Max GPU usage: {max(gpu_usages):.2f}%")
        else:
            print("[RESULT] No GPU usage data was recorded.")

if __name__ == "__main__":
    asyncio.run(profile_streaming())
