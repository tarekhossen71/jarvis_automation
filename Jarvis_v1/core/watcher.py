import threading
import time


class Watcher:

    def __init__(
        self,
        name,
        interval=10,
        callback=None,
    ):
        self.name = name
        self.interval = interval
        self.callback = callback

        self.running = False
        self.thread = None

    # =========================================================
    # WATCHER LOOP
    # =========================================================

    def _run(self):

        print(
            f"👁️ Watcher started: {self.name}"
        )

        while self.running:

            try:

                result = self.check()

                if result is not None and self.callback:

                    self.callback(
                        self.name,
                        result,
                    )

            except Exception as e:

                print(
                    f"❌ Watcher error "
                    f"[{self.name}]: {e}"
                )

            time.sleep(self.interval)

        print(
            f"👁️ Watcher stopped: {self.name}"
        )

    # =========================================================
    # CHECK
    # =========================================================

    def check(self):
        """
        Override this method in specific watchers.

        Example:
            EmailWatcher
            FileWatcher
            SecurityWatcher
        """

        return None

    # =========================================================
    # START
    # =========================================================

    def start(self):

        if self.running:
            return False

        self.running = True

        self.thread = threading.Thread(
            target=self._run,
            daemon=True,
        )

        self.thread.start()

        return True

    # =========================================================
    # STOP
    # =========================================================

    def stop(self):

        if not self.running:
            return False

        self.running = False

        return True

    # =========================================================
    # STATUS
    # =========================================================

    def status(self):

        return {
            "name": self.name,
            "running": self.running,
            "interval": self.interval,
        }