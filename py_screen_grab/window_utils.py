import subprocess
from typing import Dict, Optional

def get_window_roi(window_name: str) -> Dict[str, any]:
    """Get window ROI information using wmctrl.
    
    Args:
        window_name (str): Name of the window to find
        
    Returns:
        Dict containing window information (id, x, y, width, height, name)
        
    Raises:
        Exception: If window is not found
    """
    result = subprocess.run(["wmctrl", "-lG"], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")
    
    for line in lines:
        parts = line.split(maxsplit=6)
        if len(parts) < 7:
            continue
        
        win_id, desktop, x, y, width, height, name = parts
        if window_name in name:
            name_parts = name.split(" ", 1)
            clean_name = name_parts[1] if len(name_parts) > 1 else name_parts[0]
            
            return {
                "id": win_id,
                "x": int(x),
                "y": int(y),
                "width": int(width),
                "height": int(height),
                "name": clean_name
            }
    
    raise Exception(f"Window '{window_name}' not found") 