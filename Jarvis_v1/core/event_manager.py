from datetime import datetime
from typing import Callable, Dict, List, Any


class EventManager:

    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}

    # =========================================================
    # REGISTER EVENT LISTENER
    # =========================================================

    def on(self, event_name: str, callback: Callable):
        """
        Register a callback for an event.
        """

        if event_name not in self.listeners:
            self.listeners[event_name] = []

        self.listeners[event_name].append(callback)

    # =========================================================
    # REMOVE EVENT LISTENER
    # =========================================================

    def off(self, event_name: str, callback: Callable):
        """
        Remove a previously registered callback.
        """

        if event_name not in self.listeners:
            return

        if callback in self.listeners[event_name]:
            self.listeners[event_name].remove(callback)

    # =========================================================
    # EMIT EVENT
    # =========================================================

    def emit(self, event_name: str, data: Any = None):
        """
        Trigger an event.
        """

        event = {
            "name": event_name,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }

        # print(f"\n⚡ Event: {event_name}")

        callbacks = self.listeners.get(event_name, [])

        for callback in callbacks:

            try:
                callback(event)

            except Exception as e:
                print(
                    f"❌ Event handler error "
                    f"[{event_name}]: {e}"
                )

    # =========================================================
    # LIST EVENTS
    # =========================================================

    def get_events(self):
        return list(self.listeners.keys())

    # =========================================================
    # CHECK EVENT
    # =========================================================

    def has_event(self, event_name: str) -> bool:
        return event_name in self.listeners