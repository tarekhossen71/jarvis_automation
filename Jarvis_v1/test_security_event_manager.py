from core.security_event_manager import SecurityEventManager


def callback(event):

    print("\n🛡️ Central Security Event")
    print(f"Source : {event['source']}")
    print(f"Type   : {event['type']}")
    print(f"Risk   : {event['risk']}")
    print(f"Reason : {event['reason']}")


manager = SecurityEventManager(
    callback=callback
)


# ---------------------------------------------------------
# Process event
# ---------------------------------------------------------

process_event = {
    "events": [
        {
            "type": "SECURITY_PROCESS_STARTED",
            "pid": 1234,
            "name": "unknown.exe",
            "path": r"C:\Temp\unknown.exe",
            "risk": "MEDIUM",
            "reason": "Executable is running from a temporary directory.",
        }
    ],
    "count": 1,
}


print("\n=== PROCESS EVENT ===")

print(
    manager.handle_event(
        "security_watcher",
        process_event,
    )
)


# ---------------------------------------------------------
# Network event
# ---------------------------------------------------------

network_event = {
    "events": [
        {
            "type": "SECURITY_NETWORK_CONNECTION",
            "pid": 5678,
            "process": "Code.exe",
            "remote_ip": "20.184.175.12",
            "remote_port": 443,
            "status": "ESTABLISHED",
            "risk": "LOW",
            "reason": "Standard HTTPS connection.",
        }
    ],
    "count": 1,
}


print("\n=== NETWORK EVENT ===")

print(
    manager.handle_event(
        "network_watcher",
        network_event,
    )
)


# ---------------------------------------------------------
# Startup event
# ---------------------------------------------------------

startup_event = {
    "events": [
        {
            "type": "SECURITY_STARTUP_ITEM_ADDED",
            "location": "USER_STARTUP_FOLDER",
            "name": "jarvis_test.txt",
            "value": r"C:\Users\Tarek\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\jarvis_test.txt",
            "risk": "MEDIUM",
            "reason": "Startup item type is not recognized.",
        }
    ],
    "count": 1,
}


print("\n=== STARTUP EVENT ===")

print(
    manager.handle_event(
        "startup_watcher",
        startup_event,
    )
)


# ---------------------------------------------------------
# Status
# ---------------------------------------------------------

print("\n=== STATUS ===")

print(
    manager.status()
)


# ---------------------------------------------------------
# Recent events
# ---------------------------------------------------------

print("\n=== RECENT EVENTS ===")

for event in manager.get_events():

    print(
        event
    )