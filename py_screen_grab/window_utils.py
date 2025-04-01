import subprocess
from typing import Dict, Optional, List

def get_window() -> List[str]:
    """Get a list of all window names using wmctrl.
    
    Returns:
내용ㅇ        List[str]: A list of window names currently available.
    """
    result = subprocess.run(["wmctrl", "-lG"], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")
    windows = []
    for line in lines:
        parts = line.split(maxsplit=6)
        if len(parts) < 7:
            continue
        
        name_parts = parts[6].split(" ", 1)
        clean_name = name_parts[1] if len(name_parts) > 1 else name_parts[0]
            
        windows.append(clean_name)
    
    return windows

def get_window_roi(window_name: str) -> Dict[str, any]:
    """Get the region of interest (ROI) of a specific window using wmctrl.
    
    Args:
        window_name (str): The name of the window to find.
        
    Returns:
        Dict[str, any]: A dictionary containing the window's information:
            - id (str): The window ID.
            - x (int): The X coordinate of the window's top-left corner.
            - y (int): The Y coordinate of the window's top-left corner.
            - width (int): The width of the window.
            - height (int): The height of the window.
            - name (str): The cleaned name of the window.
        
    Raises:
        Exception: If the specified window is not found.
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