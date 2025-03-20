from py_screen_grab import ScreenGrabber

# 1. 기본 기능 테스트
grabber = ScreenGrabber()

# 2. 미리보기 테스트 (3초)
print("미리보기 테스트를 시작합니다. 'q'를 누르면 종료됩니다.")
grabber.preview_only()

# 3. 녹화 테스트 (3초)
print("\n3초 녹화 테스트를 시작합니다.")
grabber.start_recording(duration=3)

# 4. ROI(Region of Interest) 테스트
print("\n특정 영역 녹화 테스트를 시작합니다.")
grabber.set_roi(100, 100, 800, 600)  # 화면의 특정 영역 설정
grabber.start_recording(duration=3)