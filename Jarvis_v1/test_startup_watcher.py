from core.watcher_manager import WatcherManager
from tools.watchers.startup_watcher import StartupWatcher


def handle_event(name, data):

    print(f"\n🛡️ Startup Event: {name}")
    print(f"📦 Data: {data}")


manager = WatcherManager()

watcher = StartupWatcher(
    callback=handle_event
)

manager.register(watcher)

manager.start("startup_watcher")

print(manager.list_watchers())

input("\nPress ENTER to stop...")

manager.stop_all()