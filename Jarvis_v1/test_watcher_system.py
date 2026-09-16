from core.watcher_manager import WatcherManager
from tools.watchers.test_watcher import TestWatcher


def handle_event(name, data):

    print(
        f"📡 Watcher Event: {name}"
    )

    print(
        f"📦 Data: {data}"
    )


manager = WatcherManager()

watcher = TestWatcher(
    callback=handle_event
)

manager.register(watcher)

manager.start("test_watcher")

print(
    manager.list_watchers()
)

input(
    "\nPress ENTER to stop..."
)

manager.stop_all()