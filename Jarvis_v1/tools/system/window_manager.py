# tools/system/window_manager.py

import ctypes
import psutil
import win32gui
import win32process


user32 = ctypes.windll.user32

SW_SHOWMINIMIZED = 2
SW_MAXIMIZE = 3
SW_RESTORE = 9

# =========================================================
# INTERNAL HELPERS
# =========================================================

def _get_window_process_name(hwnd):
    """Get the process name of a window."""

    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        process = psutil.Process(pid)

        return process.name().lower()

    except Exception:
        return ""


def _get_visible_windows():
    """Return visible application windows."""

    windows = []

    def callback(hwnd, _):
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return True

            title = win32gui.GetWindowText(hwnd).strip()

            if not title:
                return True

            process_name = _get_window_process_name(hwnd)

            windows.append({
                "hwnd": hwnd,
                "title": title,
                "process": process_name,
            })

        except Exception:
            pass

        return True

    win32gui.EnumWindows(callback, None)

    return windows


def _find_window(application):
    """Find a window by application/process/title."""

    application = application.lower().strip()

    windows = _get_visible_windows()

    # Exact process match
    for window in windows:
        process = window["process"]

        if process == application:
            return window

        if process == f"{application}.exe":
            return window

    # Partial process match
    for window in windows:
        process = window["process"]

        if application in process:
            return window

    # Title match
    for window in windows:
        title = window["title"].lower()

        if application in title:
            return window

    return None


# =========================================================
# LIST WINDOWS
# =========================================================

def get_open_windows():
    """
    Get currently visible application windows.
    """

    windows = _get_visible_windows()

    result = []

    for window in windows:
        result.append({
            "title": window["title"],
            "process": window["process"],
        })

    return {
        "success": True,
        "windows": result,
        "count": len(result),
    }


# =========================================================
# MINIMIZE
# =========================================================
def minimize_window(window_name: str):
    """
    Minimize an already open Windows window.
    Only use when the user explicitly asks to minimize a window.
    """

    window = _find_window(window_name)

    if not window:
        return {
            "success": False,
            "error": f"Could not find window: {window_name}",
        }

    try:
        win32gui.ShowWindow(
            window["hwnd"],
            SW_SHOWMINIMIZED,
        )

        return {
            "success": True,
            "message": f"Minimized {window['title']}.",
            "window_name": window_name,
            "title": window["title"],
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def maximize_window(window_name: str):
    """
    Maximize an already open Windows window.
    Only use when the user explicitly asks to maximize a window.
    """

    window = _find_window(window_name)

    if not window:
        return {
            "success": False,
            "error": f"Could not find window: {window_name}",
        }

    try:
        win32gui.ShowWindow(
            window["hwnd"],
            SW_MAXIMIZE,
        )

        return {
            "success": True,
            "message": f"Maximized {window['title']}.",
            "window_name": window_name,
            "title": window["title"],
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def restore_window(window_name: str):
    """
    Restore an already open Windows window.
    Only use when the user explicitly asks to restore a window.
    """

    window = _find_window(window_name)

    if not window:
        return {
            "success": False,
            "error": f"Could not find window: {window_name}",
        }

    try:
        win32gui.ShowWindow(
            window["hwnd"],
            SW_RESTORE,
        )

        win32gui.SetForegroundWindow(
            window["hwnd"]
        )

        return {
            "success": True,
            "message": f"Restored {window['title']}.",
            "window_name": window_name,
            "title": window["title"],
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def focus_window(window_name: str):
    """
    Switch to an already open Windows window.
    Only use when the user explicitly asks to switch or focus a window.
    """

    window = _find_window(window_name)

    if not window:
        return {
            "success": False,
            "error": f"Could not find window: {window_name}",
        }

    try:
        hwnd = window["hwnd"]

        win32gui.ShowWindow(
            hwnd,
            win32gui.SW_RESTORE,
        )

        win32gui.SetForegroundWindow(hwnd)

        return {
            "success": True,
            "message": f"Switched to {window['title']}.",
            "window_name": window_name,
            "title": window["title"],
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
# =========================================================
# SHOW DESKTOP
# =========================================================

def show_desktop():
    """
    Minimize all open windows and show the desktop.
    """

    try:
        # Win + D
        user32.keybd_event(0x5B, 0, 0, 0)
        user32.keybd_event(0x44, 0, 0, 0)
        user32.keybd_event(0x44, 0, 2, 0)
        user32.keybd_event(0x5B, 0, 2, 0)

        return {
            "success": True,
            "message": "Desktop is now visible.",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }