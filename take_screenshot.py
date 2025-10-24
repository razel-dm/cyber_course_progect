import io
import subprocess
import sys
import pyautogui


def ensure_pyautogui():
    try:
        import pyautogui
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui"])
        import pyautogui
    return pyautogui

def take_screenshot(filename):
    pyautogui = ensure_pyautogui()
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
class ScreenshotTaker:
    def take_screenshot(self):
    
        screenshot = pyautogui.screenshot()
        screenshot_data = io.BytesIO()
        screenshot.save(screenshot_data, format='PNG')
        return screenshot_data.getvalue()