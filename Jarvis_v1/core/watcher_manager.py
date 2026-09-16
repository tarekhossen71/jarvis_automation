class WatcherManager:

    def __init__(self):

        self.watchers = {}

    # =========================================================
    # REGISTER
    # =========================================================

    def register(self, watcher):

        name = watcher.name

        if name in self.watchers:

            return {
                "success": False,
                "error": (
                    f"Watcher '{name}' "
                    f"already exists."
                ),
            }

        self.watchers[name] = watcher

        print(
            f"👁️ Watcher registered: {name}"
        )

        return {
            "success": True,
            "name": name,
        }

    # =========================================================
    # START
    # =========================================================

    def start(self, name):

        watcher = self.watchers.get(name)

        if not watcher:

            return {
                "success": False,
                "error": (
                    f"Watcher '{name}' "
                    f"not found."
                ),
            }

        started = watcher.start()

        return {
            "success": started,
            "name": name,
            "running": watcher.running,
        }

    # =========================================================
    # STOP
    # =========================================================

    def stop(self, name):

        watcher = self.watchers.get(name)

        if not watcher:

            return {
                "success": False,
                "error": (
                    f"Watcher '{name}' "
                    f"not found."
                ),
            }

        stopped = watcher.stop()

        return {
            "success": stopped,
            "name": name,
            "running": watcher.running,
        }

    # =========================================================
    # STATUS
    # =========================================================

    def status(self, name):

        watcher = self.watchers.get(name)

        if not watcher:

            return {
                "success": False,
                "error": (
                    f"Watcher '{name}' "
                    f"not found."
                ),
            }

        return {
            "success": True,
            **watcher.status(),
        }

    # =========================================================
    # LIST
    # =========================================================

    def list_watchers(self):

        result = []

        for watcher in self.watchers.values():

            result.append(
                watcher.status()
            )

        return {
            "success": True,
            "count": len(result),
            "watchers": result,
        }

    # =========================================================
    # STOP ALL
    # =========================================================

    def stop_all(self):

        for watcher in self.watchers.values():

            watcher.stop()

        return {
            "success": True,
            "message": "All watchers stopped.",
        }