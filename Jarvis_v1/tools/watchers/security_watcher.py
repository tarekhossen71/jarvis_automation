import psutil

from core.watcher import Watcher
from tools.watchers.security_analyzer import SecurityAnalyzer


class SecurityWatcher(Watcher):

    def __init__(self, callback=None):
        super().__init__(
            name="security_watcher",
            interval=5,
            callback=callback,
        )

        self.known_processes = set()

        self._load_existing_processes()

    def _load_existing_processes(self):

        for process in psutil.process_iter(
            ["pid", "name", "exe"]
        ):
            try:
                pid = process.info["pid"]

                if pid:
                    self.known_processes.add(pid)

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ):
                continue

    def check(self):

        events = []
        current_pids = set()

        try:
            processes = psutil.process_iter(
                ["pid", "name", "exe"]
            )
        except Exception as e:

            print(
                f"❌ SecurityWatcher process scan error: {e}"
            )

            return None

        for process in processes:

            try:

                pid = process.info["pid"]
                name = process.info["name"]
                exe = process.info["exe"]

                if not pid:
                    continue

                current_pids.add(pid)

                # New process detected
                if pid not in self.known_processes:

                    process_data = {
                        "type": "SECURITY_PROCESS_STARTED",
                        "pid": pid,
                        "name": name,
                        "path": exe,
                    }

                    analysis = SecurityAnalyzer.analyze(
                        process_data
                    )

                    process_data["risk"] = analysis["risk"]
                    process_data["reason"] = analysis["reason"]

                    events.append(process_data)

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ):
                continue

            except Exception as e:

                print(
                    f"❌ SecurityWatcher process error: {e}"
                )

        self.known_processes = current_pids

        if not events:
            return None

        return {
            "events": events,
            "count": len(events),
        }