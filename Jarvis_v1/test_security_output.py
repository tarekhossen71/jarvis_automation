from core.security_event_manager import SecurityEventManager


# =========================================================
# MOCK JARVIS OUTPUT
# =========================================================

class TestOutput:

    def speak(self, message):

        print(
            f"\n🤖 JARVIS VOICE: {message}"
        )

    def text(self, message):

        print(
            f"\n🤖 JARVIS TEXT: {message}"
        )


output = TestOutput()


# =========================================================
# SECURITY ALERT HANDLER
# =========================================================

def security_alert_handler(
    event,
    policy,
):

    risk = policy.get(
        "risk",
        "UNKNOWN",
    )

    action = policy.get(
        "action",
        "UNKNOWN",
    )

    source = event.get(
        "source",
        "unknown",
    )

    event_type = event.get(
        "type",
        "security event",
    )

    reason = event.get(
        "reason",
        "",
    )

    message = (
        f"Security alert. "
        f"Risk level {risk}. "
        f"Source {source}. "
        f"Event {event_type}. "
        f"{reason}"
    )

    # Text output
    output.text(message)

    # Voice output
    output.speak(message)


# =========================================================
# SECURITY EVENT MANAGER
# =========================================================

manager = SecurityEventManager(
    alert_callback=security_alert_handler,
)


# =========================================================
# TEST MEDIUM
# =========================================================

print("\n=== MEDIUM EVENT ===")

manager.handle_event(
    "startup_watcher",
    {
        "events": [
            {
                "type": "SECURITY_STARTUP_ITEM_ADDED",
                "risk": "MEDIUM",
                "reason": "Startup item type is not recognized.",
            }
        ]
    },
)


# =========================================================
# TEST HIGH
# =========================================================

print("\n=== HIGH EVENT ===")

manager.handle_event(
    "security_watcher",
    {
        "events": [
            {
                "type": "SECURITY_PROCESS_STARTED",
                "risk": "HIGH",
                "reason": "Suspicious executable location.",
            }
        ]
    },
)


# =========================================================
# TEST CRITICAL
# =========================================================

print("\n=== CRITICAL EVENT ===")

manager.handle_event(
    "network_watcher",
    {
        "events": [
            {
                "type": "SECURITY_NETWORK_CONNECTION",
                "risk": "CRITICAL",
                "reason": "Critical security event.",
            }
        ]
    },
)


# =========================================================
# TEST LOW
# =========================================================

print("\n=== LOW EVENT ===")

manager.handle_event(
    "security_watcher",
    {
        "events": [
            {
                "type": "SECURITY_PROCESS_STARTED",
                "risk": "LOW",
                "reason": "Known Windows system executable.",
            }
        ]
    },
)