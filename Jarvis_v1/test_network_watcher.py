from core.watcher_manager import WatcherManager
from tools.watchers.network_watcher import NetworkWatcher


def handle_event(name, data):

    print(f"\n🌐 Network Event: {name}")
    print(f"📦 Data: {data}")


manager = WatcherManager()

watcher = NetworkWatcher(
    callback=handle_event
)

manager.register(watcher)

manager.start("network_watcher")

print(manager.list_watchers())

input("\nPress ENTER to stop...")

manager.stop_all()