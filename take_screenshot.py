
import io
import subprocess
import sys

def ensure_pyautogui():
    try:
        import pyautogui
    except Exception:
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui"])
            import pyautogui  
        except Exception:
            raise
    return pyautogui

def take_screenshot_bytes():
    pyautogui = ensure_pyautogui()
    screenshot = pyautogui.screenshot()
    buf = io.BytesIO()
    screenshot.save(buf, format="PNG")
    return buf.getvalue()

class ScreenshotTaker:
    def take_screenshot(self) -> bytes:
        """Return PNG image bytes."""
        return take_screenshot_bytes()
