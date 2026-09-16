from core.watcher_manager import WatcherManager
from tools.watchers.startup_watcher import StartupWatcher


def callback(name, data):
    print(f"\n🛡️ Startup Event: {name}")
    print(f"📦 Data: {data}")


manager = WatcherManager()

watcher = StartupWatcher(
    callback=callback
)

manager.register(watcher)

print(
    manager.start("startup_watcher")
)

print(
    manager.list_watchers()
)

input("\nPress ENTER to stop...")

print(
    manager.stop("startup_watcher")
)