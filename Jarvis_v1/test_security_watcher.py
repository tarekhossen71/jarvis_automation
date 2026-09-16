from core.watcher_manager import WatcherManager
from tools.watchers.security_watcher import SecurityWatcher


def handle_event(name, data):

    print(
        f"\n🛡️ Security Event: {name}"
    )

    print(
        f"📦 Data: {data}"
    )


manager = WatcherManager()

watcher = SecurityWatcher(
    callback=handle_event
)

manager.register(watcher)

manager.start(
    "security_watcher"
)

print(
    manager.list_watchers()
)

input(
    "\nPress ENTER to stop..."
)

manager.stop_all()