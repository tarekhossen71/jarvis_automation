import time

from core.event_manager import EventManager
from core.automation_engine import AutomationEngine
from core.scheduler import Scheduler


# =========================================================
# EVENT SYSTEM
# =========================================================

events = EventManager()

automation = AutomationEngine(
    event_manager=events
)


# =========================================================
# TEST AUTOMATION
# =========================================================

automation.register(
    name="Test Notification",
    event="test_event",
    action=lambda event: print(
        "🤖 JARVIS: Test automation executed."
    ),
)


# =========================================================
# TEST EVENT
# =========================================================

events.emit(
    "test_event",
    {
        "message": "Hello from JARVIS"
    }
)


# =========================================================
# TEST SCHEDULER
# =========================================================

scheduler = Scheduler()


def scheduled_task():

    print(
        "🤖 JARVIS: Scheduled task executed."
    )


scheduler.every(
    seconds=5,
    callback=scheduled_task,
    name="Test Job",
)

scheduler.start()


# =========================================================
# KEEP PROGRAM RUNNING
# =========================================================

try:

    while True:
        time.sleep(1)

except KeyboardInterrupt:

    scheduler.stop()

    print(
        "\n🤖 JARVIS automation test stopped."
    )