import threading
import time
import uuid
from datetime import datetime, timedelta

from winotify import Notification, audio


_timers = {}
_timers_lock = threading.Lock()


def show_notification(
    title: str,
    message: str,
):
    """
    Show a Windows desktop notification.
    """

    try:
        toast = Notification(
            app_id="JARVIS",
            title=title,
            msg=message,
        )

        toast.set_audio(
            audio.Default,
            loop=False,
        )

        toast.show()

        return {
            "success": True,
            "message": "Notification shown.",
            "title": title,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def _timer_worker(timer_id, title, message, delay_seconds):
    try:
        time.sleep(delay_seconds)

        with _timers_lock:
            timer = _timers.get(timer_id)

            if not timer:
                return

            if timer.get("cancelled"):
                _timers.pop(timer_id, None)
                return

            timer["status"] = "completed"

        show_notification(
            title,
            message,
        )

        with _timers_lock:
            _timers.pop(timer_id, None)

    except Exception:
        with _timers_lock:
            _timers.pop(timer_id, None)


def set_timer(
    minutes: float,
    message: str,
    title: str = "JARVIS Timer",
):
    """
    Set a background timer in minutes.
    """

    try:
        minutes = float(minutes)

        if minutes <= 0:
            return {
                "success": False,
                "error": "Timer duration must be greater than zero.",
            }

        timer_id = str(uuid.uuid4())[:8]

        seconds = minutes * 60
        due_time = datetime.now() + timedelta(
            seconds=seconds
        )

        timer_data = {
            "id": timer_id,
            "title": title,
            "message": message,
            "minutes": minutes,
            "created_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "due_at": due_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "status": "running",
            "cancelled": False,
        }

        with _timers_lock:
            _timers[timer_id] = timer_data

        thread = threading.Thread(
            target=_timer_worker,
            args=(
                timer_id,
                title,
                message,
                seconds,
            ),
            daemon=True,
        )

        thread.start()

        return {
            "success": True,
            "message": f"Timer set for {minutes:g} minute(s).",
            "timer": timer_data,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def list_timers():
    """
    Return all active timers.
    """

    with _timers_lock:
        timers = [
            timer.copy()
            for timer in _timers.values()
            if timer.get("status") == "running"
        ]

    return {
        "success": True,
        "timers": timers,
        "count": len(timers),
    }


def cancel_timer(timer_id: str):
    """
    Cancel an active timer.
    """

    timer_id = str(timer_id).strip()

    with _timers_lock:
        timer = _timers.get(timer_id)

        if not timer:
            return {
                "success": False,
                "error": f"Timer '{timer_id}' not found.",
            }

        timer["cancelled"] = True
        timer["status"] = "cancelled"

        timer_copy = timer.copy()

        _timers.pop(timer_id, None)

    return {
        "success": True,
        "message": f"Timer {timer_id} cancelled.",
        "timer": timer_copy,
    }