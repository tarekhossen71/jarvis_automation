import os
import json
import uuid
import time
import threading
from datetime import datetime, timedelta

from plyer import notification


# =========================================================
# CONFIGURATION
# =========================================================

REMINDER_FILE = os.path.join(
    os.getcwd(),
    "data",
    "reminders.json"
)

CHECK_INTERVAL = 5

_reminder_thread = None
_reminder_running = False

_reminder_lock = threading.Lock()


# =========================================================
# STORAGE
# =========================================================

def ensure_storage():
    directory = os.path.dirname(REMINDER_FILE)

    os.makedirs(
        directory,
        exist_ok=True
    )

    if not os.path.exists(REMINDER_FILE):
        with open(
            REMINDER_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                [],
                file,
                ensure_ascii=False,
                indent=2
            )


def load_reminders():
    ensure_storage()

    try:
        with _reminder_lock:
            with open(
                REMINDER_FILE,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

        if not isinstance(data, list):
            return []

        return data

    except Exception:
        return []


def save_reminders(reminders):
    ensure_storage()

    with _reminder_lock:
        with open(
            REMINDER_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                reminders,
                file,
                ensure_ascii=False,
                indent=2
            )


# =========================================================
# DATE / TIME HELPERS
# =========================================================

def parse_datetime(date_time: str):
    """
    Parse common date/time formats.

    Supported examples:

    2026-09-15 10:30
    2026-09-15 18:00
    2026-09-15T10:30
    """

    date_time = (date_time or "").strip()

    if not date_time:
        raise ValueError(
            "Date and time are required."
        )

    formats = [
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%d/%m/%Y %H:%M",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(
                date_time,
                fmt
            )
        except ValueError:
            continue

    raise ValueError(
        "Invalid date/time format. "
        "Use YYYY-MM-DD HH:MM."
    )


def format_datetime(value):
    return datetime.fromisoformat(
        value
    ).strftime(
        "%Y-%m-%d %I:%M %p"
    )


# =========================================================
# CREATE REMINDER
# =========================================================

def create_reminder(
    title: str,
    date_time: str,
    description: str = ""
):
    """
    Create a persistent reminder.
    """

    try:
        title = (title or "").strip()

        if not title:
            return {
                "success": False,
                "error": "Reminder title cannot be empty.",
            }

        reminder_time = parse_datetime(
            date_time
        )

        if reminder_time <= datetime.now():
            return {
                "success": False,
                "error": (
                    "Reminder date and time must be "
                    "in the future."
                ),
            }

        reminder = {
            "id": uuid.uuid4().hex[:8],
            "title": title,
            "description": (
                description or ""
            ).strip(),
            "date_time": reminder_time.isoformat(
                timespec="seconds"
            ),
            "created_at": datetime.now().isoformat(
                timespec="seconds"
            ),
            "completed": False,
            "notified": False,
        }

        reminders = load_reminders()

        reminders.append(
            reminder
        )

        reminders.sort(
            key=lambda item: item["date_time"]
        )

        save_reminders(
            reminders
        )

        return {
            "success": True,
            "reminder": reminder,
            "message": (
                f"Reminder '{title}' created for "
                f"{format_datetime(reminder['date_time'])}."
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# LIST REMINDERS
# =========================================================

def list_reminders(
    include_completed: bool = False
):
    """
    List saved reminders.
    """

    try:
        reminders = load_reminders()

        if not include_completed:
            reminders = [
                reminder
                for reminder in reminders
                if not reminder.get(
                    "completed",
                    False
                )
            ]

        reminders.sort(
            key=lambda item: item["date_time"]
        )

        return {
            "success": True,
            "count": len(reminders),
            "reminders": reminders,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# CREATE RELATIVE REMINDER
# =========================================================

def create_relative_reminder(
    title: str,
    amount,
    unit: str,
    description: str = ""
):
    """
    Create a reminder using relative time.

    Examples:

    30 seconds
    1 minute
    0.5 minutes
    2 hours
    1 day
    """

    try:
        title = (title or "").strip()
        unit = (unit or "").strip().lower()

        if not title:
            return {
                "success": False,
                "error": "Reminder title cannot be empty.",
            }

        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return {
                "success": False,
                "error": "Reminder time amount must be a number.",
            }

        if amount <= 0:
            return {
                "success": False,
                "error": "Reminder time must be greater than zero.",
            }

        # -------------------------------------------------
        # NORMALIZE UNIT
        # -------------------------------------------------

        if unit in (
            "second",
            "seconds",
            "sec",
            "secs",
        ):
            delta = timedelta(
                seconds=amount
            )

        elif unit in (
            "minute",
            "minutes",
            "min",
            "mins",
        ):
            delta = timedelta(
                minutes=amount
            )

        elif unit in (
            "hour",
            "hours",
            "hr",
            "hrs",
        ):
            delta = timedelta(
                hours=amount
            )

        elif unit in (
            "day",
            "days",
        ):
            delta = timedelta(
                days=amount
            )

        else:
            return {
                "success": False,
                "error": (
                    "Unsupported time unit. "
                    "Use seconds, minutes, hours, or days."
                ),
            }

        reminder_time = (
            datetime.now() + delta
        )

        # -------------------------------------------------
        # USE EXISTING REMINDER CREATION
        # -------------------------------------------------

        return create_reminder(
            title=title,
            date_time=reminder_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            description=description,
        )

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }

    
# =========================================================
# FIND REMINDER
# =========================================================

def find_reminder(query: str):
    """
    Find reminders by title, description, or ID.
    """

    try:
        query = (query or "").strip()

        if not query:
            return {
                "success": False,
                "error": "Search query cannot be empty.",
            }

        query_lower = query.lower()

        reminders = load_reminders()

        results = [
            reminder
            for reminder in reminders
            if (
                query_lower
                in reminder.get(
                    "title",
                    ""
                ).lower()
                or
                query_lower
                in reminder.get(
                    "description",
                    ""
                ).lower()
                or
                query_lower
                == reminder.get(
                    "id",
                    ""
                ).lower()
            )
        ]

        return {
            "success": True,
            "query": query,
            "count": len(results),
            "reminders": results,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# CANCEL REMINDER
# =========================================================

def cancel_reminder(reminder_id: str):
    """
    Cancel a reminder by ID.
    """

    try:
        reminder_id = (
            reminder_id or ""
        ).strip().lower()

        if not reminder_id:
            return {
                "success": False,
                "error": "Reminder ID is required.",
            }

        reminders = load_reminders()

        for reminder in reminders:

            if reminder.get(
                "id",
                ""
            ).lower() == reminder_id:

                if reminder.get(
                    "completed",
                    False
                ):
                    return {
                        "success": False,
                        "error": (
                            "This reminder is already completed."
                        ),
                    }

                reminder["completed"] = True
                reminder["cancelled"] = True
                reminder["cancelled_at"] = (
                    datetime.now().isoformat(
                        timespec="seconds"
                    )
                )

                save_reminders(
                    reminders
                )

                return {
                    "success": True,
                    "reminder": reminder,
                    "message": (
                        f"Reminder '{reminder['title']}' "
                        f"has been cancelled."
                    ),
                }

        return {
            "success": False,
            "error": (
                f"Reminder '{reminder_id}' was not found."
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# DELETE REMINDER
# =========================================================

def delete_reminder(reminder_id: str):
    """
    Permanently remove a reminder from storage.
    """

    try:
        reminder_id = (
            reminder_id or ""
        ).strip().lower()

        if not reminder_id:
            return {
                "success": False,
                "error": "Reminder ID is required.",
            }

        reminders = load_reminders()

        remaining = []
        deleted = None

        for reminder in reminders:

            if reminder.get(
                "id",
                ""
            ).lower() == reminder_id:

                deleted = reminder

            else:
                remaining.append(
                    reminder
                )

        if deleted is None:
            return {
                "success": False,
                "error": (
                    f"Reminder '{reminder_id}' was not found."
                ),
            }

        save_reminders(
            remaining
        )

        return {
            "success": True,
            "deleted": deleted,
            "message": (
                f"Reminder '{deleted['title']}' deleted."
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# COMPLETE REMINDER
# =========================================================

def complete_reminder(reminder_id: str):
    """
    Mark a reminder as completed.
    """

    try:
        reminder_id = (
            reminder_id or ""
        ).strip().lower()

        if not reminder_id:
            return {
                "success": False,
                "error": "Reminder ID is required.",
            }

        reminders = load_reminders()

        for reminder in reminders:

            if reminder.get(
                "id",
                ""
            ).lower() == reminder_id:

                reminder["completed"] = True
                reminder["completed_at"] = (
                    datetime.now().isoformat(
                        timespec="seconds"
                    )
                )

                save_reminders(
                    reminders
                )

                return {
                    "success": True,
                    "reminder": reminder,
                    "message": (
                        f"Reminder '{reminder['title']}' "
                        f"marked as completed."
                    ),
                }

        return {
            "success": False,
            "error": (
                f"Reminder '{reminder_id}' was not found."
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# DUE REMINDERS
# =========================================================

def get_due_reminders():
    """
    Get reminders that are due and have not
    been notified yet.
    """

    try:
        now = datetime.now()

        reminders = load_reminders()

        due = []

        for reminder in reminders:

            if reminder.get(
                "completed",
                False
            ):
                continue

            if reminder.get(
                "notified",
                False
            ):
                continue

            reminder_time = datetime.fromisoformat(
                reminder["date_time"]
            )

            if reminder_time <= now:

                due.append(
                    reminder
                )

        return {
            "success": True,
            "count": len(due),
            "reminders": due,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# WINDOWS NOTIFICATION
# =========================================================

def send_reminder_notification(reminder):
    """
    Show a Windows desktop notification.
    """

    try:

        title = (
            "JARVIS Reminder"
        )

        message = reminder.get(
            "title",
            "Reminder"
        )

        description = reminder.get(
            "description",
            ""
        )

        if description:
            message += (
                f"\n{description}"
            )

        notification.notify(
            title=title,
            message=message,
            app_name="JARVIS",
            timeout=10,
        )

        return True

    except Exception as e:

        print(
            f"Reminder notification error: {e}"
        )

        return False


# =========================================================
# MARK NOTIFIED
# =========================================================

def mark_reminder_notified(
    reminder_id: str
):
    """
    Mark a reminder as notified.
    """

    reminders = load_reminders()

    for reminder in reminders:

        if reminder.get(
            "id",
            ""
        ).lower() == reminder_id.lower():

            reminder["notified"] = True
            reminder["notified_at"] = (
                datetime.now().isoformat(
                    timespec="seconds"
                )
            )

            save_reminders(
                reminders
            )

            return True

    return False


# =========================================================
# BACKGROUND MONITOR
# =========================================================

def _reminder_monitor():
    global _reminder_running

    while _reminder_running:

        try:

            result = get_due_reminders()

            if result.get(
                "success"
            ):

                for reminder in result.get(
                    "reminders",
                    []
                ):

                    notification_sent = (
                        send_reminder_notification(
                            reminder
                        )
                    )

                    if notification_sent:

                        mark_reminder_notified(
                            reminder["id"]
                        )

        except Exception as e:

            print(
                f"Reminder monitor error: {e}"
            )

        time.sleep(
            CHECK_INTERVAL
        )


# =========================================================
# START MONITOR
# =========================================================

def start_reminder_monitor():
    global _reminder_thread
    global _reminder_running

    if _reminder_running:
        return {
            "success": True,
            "running": True,
            "message": (
                "Reminder monitor is already running."
            ),
        }

    try:

        ensure_storage()

        _reminder_running = True

        _reminder_thread = threading.Thread(
            target=_reminder_monitor,
            daemon=True,
            name="JARVIS-Reminder-Monitor"
        )

        _reminder_thread.start()

        return {
            "success": True,
            "running": True,
            "message": (
                "Reminder monitor started."
            ),
        }

    except Exception as e:

        _reminder_running = False

        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# STOP MONITOR
# =========================================================

def stop_reminder_monitor():
    global _reminder_running

    _reminder_running = False

    return {
        "success": True,
        "running": False,
        "message": (
            "Reminder monitor stopped."
        ),
    }


# =========================================================
# MONITOR STATUS
# =========================================================

def reminder_monitor_status():

    return {
        "success": True,
        "running": _reminder_running,
        "reminder_file": REMINDER_FILE,
    }