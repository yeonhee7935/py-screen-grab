import subprocess

def get_window_roi(window_name: str):
    result = subprocess.run(["wmctrl", "-lG"], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")
    
    windows = []
    for line in lines:
        parts = line.split(maxsplit=6)  # ID, desktop, x, y, width, height, name
        if len(parts) < 7:
            continue
        
        win_id, desktop, x, y, width, height, name = parts
        if window_name in name:
            name_parts = name.split(" ", 1)  # 첫 번째 공백을 기준으로 나누기
            clean_name = name_parts[1] if len(name_parts) > 1 else name_parts[0]
            
            return {
                "id": win_id,
                "x": int(x),
                "y": int(y),
                "width": int(width),
                "height": int(height),
                "name": clean_name
            }
    
    raise Exception(f"Window {window_name} not found")

window_name = input("Enter window name: ")
roi = get_window_roi(window_name)
