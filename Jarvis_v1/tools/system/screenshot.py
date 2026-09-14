
import os
from datetime import datetime

import pyautogui


def take_screenshot():
    """
    Capture the current screen and save it
    inside the screenshots folder.
    """

    try:
        screenshot_dir = os.path.join(
            os.getcwd(),
            "screenshots"
        )

        os.makedirs(
            screenshot_dir,
            exist_ok=True
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        filename = f"screenshot_{timestamp}.png"

        filepath = os.path.join(
            screenshot_dir,
            filename
        )

        print("📸 Taking screenshot...")

        screenshot = pyautogui.screenshot()

        screenshot.save(filepath)

        print(
            f"✅ Screenshot saved: {filepath}"
        )

        return {
            "success": True,
            "message": "Screenshot captured successfully.",
            "file": filepath,
        }

    except Exception as e:

        print(
            f"❌ Screenshot Error: {type(e).__name__}: {e}"
        )

        return {
            "success": False,
            "message": "Screenshot capture failed.",
            "error_type": type(e).__name__,
            "error": str(e),
        }
