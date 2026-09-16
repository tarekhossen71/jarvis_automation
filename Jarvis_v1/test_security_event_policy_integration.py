from core.security_event_manager import SecurityEventManager


# =========================================================
# NORMAL EVENT CALLBACK
# =========================================================

def event_callback(event):

    print("\n🛡️ SECURITY EVENT")

    print(
        f"Source : {event['source']}"
    )

    print(
        f"Type   : {event['type']}"
    )

    print(
        f"Risk   : {event['risk']}"
    )

    print(
        f"Reason : {event['reason']}"
    )


# =========================================================
# ALERT CALLBACK
# =========================================================

def alert_callback(
    event,
    policy,
):

    print("\n🚨 SECURITY ALERT")

    print(
        f"Risk   : {policy['risk']}"
    )

    print(
        f"Action : {policy['action']}"
    )

    print(
        f"Source : {event['source']}"
    )

    print(
        f"Type   : {event['type']}"
    )

    print(
        f"Reason : {event['reason']}"
    )


# =========================================================
# MANAGER
# =========================================================

manager = SecurityEventManager(
    callback=event_callback,
    alert_callback=alert_callback,
)


# =========================================================
# TEST EVENTS
# =========================================================

test_events = [

    {
        "source": "security_watcher",
        "type": "SECURITY_PROCESS_STARTED",
        "risk": "LOW",
        "reason": "Known Windows system executable.",
    },

    {
        "source": "startup_watcher",
        "type": "SECURITY_STARTUP_ITEM_ADDED",
        "risk": "MEDIUM",
        "reason": "Startup item type is not recognized.",
    },

    {
        "source": "security_watcher",
        "type": "SECURITY_PROCESS_STARTED",
        "risk": "HIGH",
        "reason": "Suspicious executable location.",
    },

    {
        "source": "network_watcher",
        "type": "SECURITY_NETWORK_CONNECTION",
        "risk": "CRITICAL",
        "reason": "Critical security event.",
    },

]


# =========================================================
# PROCESS EVENTS
# =========================================================

for event in test_events:

    print("\n" + "=" * 60)

    print(
        f"Processing: {event['risk']}"
    )

    result = manager.handle_event(
        event["source"],
        {
            "events": [event]
        },
    )

    print("\nManager Result:")

    print(result)


# =========================================================
# FINAL STATUS
# =========================================================

print("\n" + "=" * 60)

print("FINAL STATUS")

print(
    manager.status()
)