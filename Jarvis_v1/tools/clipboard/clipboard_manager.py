import os
import json
import time
import threading
from datetime import datetime

import pyperclip


# =========================================================
# CONFIGURATION
# =========================================================

HISTORY_FILE = os.path.join(
    os.getcwd(),
    "data",
    "clipboard_history.json"
)

MAX_HISTORY = 100

_monitor_thread = None
_monitor_running = False

_history_lock = threading.Lock()


# =========================================================
# STORAGE
# =========================================================

def ensure_storage():
    directory = os.path.dirname(HISTORY_FILE)

    os.makedirs(
        directory,
        exist_ok=True
    )

    if not os.path.exists(HISTORY_FILE):
        with open(
            HISTORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                [],
                file,
                ensure_ascii=False,
                indent=2
            )


def load_history():
    ensure_storage()

    try:
        with _history_lock:
            with open(
                HISTORY_FILE,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

        if not isinstance(data, list):
            return []

        return data

    except Exception:
        return []


def save_history(history):
    ensure_storage()

    with _history_lock:
        with open(
            HISTORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                history,
                file,
                ensure_ascii=False,
                indent=2
            )


# =========================================================
# HISTORY
# =========================================================

def add_to_history(text: str):
    """
    Save actual clipboard content to history.
    """

    text = text or ""

    if not text.strip():
        return

    history = load_history()

    # Ignore duplicate consecutive clipboard content.
    if history:
        latest = history[0]

        if latest.get("text") == text:
            return

    item = {
        "text": text,
        "copied_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    }

    history.insert(
        0,
        item
    )

    history = history[:MAX_HISTORY]

    save_history(history)


# =========================================================
# READ CLIPBOARD
# =========================================================

def read_clipboard():
    try:
        text = pyperclip.paste()

        if text is None:
            text = ""

        return {
            "success": True,
            "text": text,
            "length": len(text),
            "message": (
                "Clipboard is empty."
                if not text
                else "Clipboard text read successfully."
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# COPY TO CLIPBOARD
# =========================================================

def copy_to_clipboard(text: str):
    try:
        text = text or ""

        pyperclip.copy(text)

        # Save exactly what was intentionally copied.
        add_to_history(text)

        return {
            "success": True,
            "text": text,
            "message": "Text copied to clipboard.",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# CLEAR CLIPBOARD
# =========================================================

def clear_clipboard():
    try:
        pyperclip.copy("")

        return {
            "success": True,
            "message": "Clipboard cleared.",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# GET HISTORY
# =========================================================

def get_clipboard_history(limit: int = 10):
    try:
        history = load_history()

        limit = max(
            1,
            min(
                int(limit),
                MAX_HISTORY
            )
        )

        items = history[:limit]

        return {
            "success": True,
            "count": len(items),
            "items": items,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# SEARCH HISTORY
# =========================================================

def search_clipboard_history(query: str):
    try:
        query = (query or "").strip()

        if not query:
            return {
                "success": False,
                "error": "Search query cannot be empty.",
            }

        history = load_history()

        query_lower = query.lower()

        results = [
            item
            for item in history
            if query_lower in item.get(
                "text",
                ""
            ).lower()
        ]

        return {
            "success": True,
            "query": query,
            "count": len(results),
            "items": results,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# DELETE HISTORY
# =========================================================

def delete_clipboard_history():
    """
    Delete all saved clipboard history.
    """

    try:
        save_history([])

        return {
            "success": True,
            "message": "Clipboard history deleted.",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# BACKGROUND MONITOR
# =========================================================

def _clipboard_monitor():
    """
    Monitor real Windows clipboard changes.

    Only actual clipboard content is stored.
    JARVIS commands themselves are never stored
    unless they actually become clipboard content.
    """

    global _monitor_running

    try:
        last_text = pyperclip.paste()
    except Exception:
        last_text = ""

    while _monitor_running:

        try:
            current_text = pyperclip.paste()

            if current_text != last_text:

                last_text = current_text

                if current_text and current_text.strip():

                    add_to_history(
                        current_text
                    )

        except Exception:
            pass

        time.sleep(0.5)


# =========================================================
# START MONITOR
# =========================================================

def start_clipboard_monitor():
    global _monitor_thread
    global _monitor_running

    if _monitor_running:
        return {
            "success": True,
            "running": True,
            "message": (
                "Clipboard monitor is already running."
            ),
        }

    try:
        ensure_storage()

        _monitor_running = True

        _monitor_thread = threading.Thread(
            target=_clipboard_monitor,
            daemon=True,
            name="JARVIS-Clipboard-Monitor"
        )

        _monitor_thread.start()

        return {
            "success": True,
            "running": True,
            "message": (
                "Clipboard monitor started."
            ),
        }

    except Exception as e:

        _monitor_running = False

        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# STOP MONITOR
# =========================================================

def stop_clipboard_monitor():
    global _monitor_running

    _monitor_running = False

    return {
        "success": True,
        "running": False,
        "message": (
            "Clipboard monitor stopped."
        ),
    }


# =========================================================
# MONITOR STATUS
# =========================================================

def clipboard_monitor_status():

    return {
        "success": True,
        "running": _monitor_running,
        "history_file": HISTORY_FILE,
    }