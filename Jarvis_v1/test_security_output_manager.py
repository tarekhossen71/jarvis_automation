from core.security_event_manager import SecurityEventManager
from output.output_manager import OutputManager


output_manager = OutputManager()

# Force text mode for this test.
output_manager.set_mode("text")


security_manager = SecurityEventManager(
    output_manager=output_manager,
)


print("\n=== LOW EVENT ===")

security_manager.handle_event(
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


print("\n=== MEDIUM EVENT ===")

security_manager.handle_event(
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


print("\n=== HIGH EVENT ===")

security_manager.handle_event(
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


print("\n=== CRITICAL EVENT ===")

security_manager.handle_event(
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


print("\n=== STATUS ===")

print(
    security_manager.status()
)