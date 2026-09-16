import os
import winreg

from core.watcher import Watcher
from tools.watchers.startup_analyzer import StartupAnalyzer


class StartupWatcher(Watcher):

    def __init__(self, callback=None):

        super().__init__(
            name="startup_watcher",
            interval=10,
            callback=callback,
        )

        self.known_items = set()

        self._load_existing_items()

    REGISTRY_LOCATIONS = [
        (
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            "HKCU_RUN",
        ),
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            "HKLM_RUN",
        ),
        (
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\RunOnce",
            "HKCU_RUNONCE",
        ),
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"Software\Microsoft\Windows\CurrentVersion\RunOnce",
            "HKLM_RUNONCE",
        ),
    ]

    def _read_registry_items(self):

        items = []

        for hive, subkey, location_name in self.REGISTRY_LOCATIONS:

            try:

                with winreg.OpenKey(
                    hive,
                    subkey,
                    0,
                    winreg.KEY_READ,
                ) as key:

                    index = 0

                    while True:

                        try:

                            name, value, _ = winreg.EnumValue(
                                key,
                                index,
                            )

                            items.append({
                                "location": location_name,
                                "name": name,
                                "value": str(value),
                            })

                            index += 1

                        except OSError:
                            break

            except (
                FileNotFoundError,
                PermissionError,
                OSError,
            ):
                continue

        return items

    def _get_startup_folder(self):

        startup_folder = os.path.join(
            os.environ.get(
                "APPDATA",
                "",
            ),
            r"Microsoft\Windows\Start Menu\Programs\Startup",
        )

        return startup_folder

    def _read_startup_folder(self):

        items = []

        folder = self._get_startup_folder()

        if not folder or not os.path.isdir(folder):
            return items

        try:

            for filename in os.listdir(folder):

                full_path = os.path.join(
                    folder,
                    filename,
                )

                items.append({
                    "location": "USER_STARTUP_FOLDER",
                    "name": filename,
                    "value": full_path,
                })

        except (
            PermissionError,
            OSError,
        ):
            pass

        return items

    def _get_items(self):

        items = []

        items.extend(
            self._read_registry_items()
        )

        items.extend(
            self._read_startup_folder()
        )

        return items

    def _item_key(self, item):

        return (
            item.get("location"),
            item.get("name"),
            item.get("value"),
        )

    def _load_existing_items(self):

        items = self._get_items()

        for item in items:

            key = self._item_key(item)

            self.known_items.add(key)

    def check(self):

        events = []

        current_items = set()

        items = self._get_items()

        for item in items:

            key = self._item_key(item)

            if not key:
                continue

            current_items.add(key)

            if key not in self.known_items:

                analysis = StartupAnalyzer.analyze(
                    item
                )

                events.append({
                    "type": "SECURITY_STARTUP_ITEM_ADDED",
                    "location": item["location"],
                    "name": item["name"],
                    "value": item["value"],
                    "risk": analysis["risk"],
                    "reason": analysis["reason"],
                })

        self.known_items = current_items

        if not events:
            return None

        return {
            "events": events,
            "count": len(events),
        }