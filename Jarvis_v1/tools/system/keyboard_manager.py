import time

import pyautogui


# =========================================================
# TYPE TEXT
# =========================================================

def type_text(text: str):
    """
    Type text using the keyboard into the currently focused application.
    """

    if not text:
        return {
            "success": False,
            "error": "No text provided.",
        }

    try:
        pyautogui.write(
            text,
            interval=0.01,
        )

        return {
            "success": True,
            "message": "Text typed successfully.",
            "text": text,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# PRESS KEY
# =========================================================

def press_key(key: str):
    """
    Press a single keyboard key.
    """

    if not key:
        return {
            "success": False,
            "error": "No key provided.",
        }

    try:
        pyautogui.press(key.lower())

        return {
            "success": True,
            "message": f"Pressed {key}.",
            "key": key,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# HOTKEY
# =========================================================

def hotkey(keys: str):
    """
    Press a keyboard shortcut such as ctrl+c, ctrl+v, alt+tab.
    """

    if not keys:
        return {
            "success": False,
            "error": "No hotkey provided.",
        }

    try:
        key_list = [
            key.strip().lower()
            for key in keys.split("+")
            if key.strip()
        ]

        if not key_list:
            return {
                "success": False,
                "error": "Invalid hotkey.",
            }

        pyautogui.hotkey(*key_list)

        return {
            "success": True,
            "message": f"Pressed {keys}.",
            "keys": key_list,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }