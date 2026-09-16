import time

from core.watcher_manager import WatcherManager
from core.security_event_manager import SecurityEventManager

from tools.watchers.security_watcher import SecurityWatcher
from tools.watchers.network_watcher import NetworkWatcher
from tools.watchers.startup_watcher import StartupWatcher


# =========================================================
# CENTRAL SECURITY EVENT MANAGER
# =========================================================

def security_callback(event):

    print("\n" + "=" * 60)
    print("🛡️ CENTRAL SECURITY EVENT")
    print("=" * 60)

    print(f"Source : {event['source']}")
    print(f"Type   : {event['type']}")
    print(f"Risk   : {event['risk']}")
    print(f"Reason : {event['reason']}")

    print("Data   :")
    print(event["data"])


security_manager = SecurityEventManager(
    callback=security_callback
)


# =========================================================
# WATCHER CALLBACK
# =========================================================

def watcher_callback(watcher_name, data):

    security_manager.handle_event(
        watcher_name,
        data,
    )


# =========================================================
# WATCHER MANAGER
# =========================================================

manager = WatcherManager()


# =========================================================
# CREATE WATCHERS
# =========================================================

security_watcher = SecurityWatcher(
    callback=watcher_callback
)

network_watcher = NetworkWatcher(
    callback=watcher_callback
)

startup_watcher = StartupWatcher(
    callback=watcher_callback
)


# =========================================================
# REGISTER
# =========================================================

print("\n=== REGISTER WATCHERS ===")

print(
    manager.register(
        security_watcher
    )
)

print(
    manager.register(
        network_watcher
    )
)

print(
    manager.register(
        startup_watcher
    )
)


# =========================================================
# START
# =========================================================

print("\n=== START WATCHERS ===")

print(
    manager.start(
        "security_watcher"
    )
)

print(
    manager.start(
        "network_watcher"
    )
)

print(
    manager.start(
        "startup_watcher"
    )
)


# =========================================================
# STATUS
# =========================================================

print("\n=== WATCHER STATUS ===")

print(
    manager.list_watchers()
)


# =========================================================
# WAIT
# =========================================================

print("\n👁️ All security watchers are running.")
print("Waiting for security events...")
print("Press ENTER to stop.\n")


input()


# =========================================================
# STOP
# =========================================================

print("\n=== STOP WATCHERS ===")

print(
    manager.stop_all()
)


# =========================================================
# SECURITY MANAGER STATUS
# =========================================================

print("\n=== SECURITY MANAGER STATUS ===")

print(
    security_manager.status()
)


# =========================================================
# RECENT EVENTS
# =========================================================

print("\n=== RECENT SECURITY EVENTS ===")

for event in security_manager.get_events():

    print(
        event
    )