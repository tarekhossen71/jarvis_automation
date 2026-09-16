from core.watcher import Watcher


class TestWatcher(Watcher):

    def __init__(self, callback=None):

        super().__init__(
            name="test_watcher",
            interval=5,
            callback=callback,
        )

        self.counter = 0

    def check(self):

        self.counter += 1

        return {
            "counter": self.counter,
            "message": "Watcher is alive",
        }