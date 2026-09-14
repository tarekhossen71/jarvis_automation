import threading
import time

import psutil

from tools.notifications.notification_manager import show_notification


_monitor_thread = None
_monitor_running = False
_monitor_lock = threading.Lock()

_monitor_settings = {
    "cpu_threshold": 90,
    "ram_threshold": 90,
    "disk_threshold": 90,
    "battery_threshold": 20,
    "interval": 30,
}

_alert_state = {
    "cpu": False,
    "ram": False,
    "disk": False,
    "battery": False,
    "internet": False,
}


def _check_internet():
    try:
        import socket

        socket.create_connection(
            ("8.8.8.8", 53),
            timeout=3,
        )

        return True

    except Exception:
        return False


def _check_system():

    cpu = psutil.cpu_percent(interval=1)

    memory = psutil.virtual_memory()
    ram = memory.percent

    disk = psutil.disk_usage("C:\\")
    disk_percent = disk.percent

    battery = psutil.sensors_battery()

    battery_percent = None
    battery_plugged = None

    if battery:
        battery_percent = round(battery.percent, 1)
        battery_plugged = battery.power_plugged

    internet = _check_internet()

    return {
        "cpu_percent": round(cpu, 1),
        "ram_percent": round(ram, 1),
        "disk_percent": round(disk_percent, 1),
        "battery_percent": battery_percent,
        "battery_plugged": battery_plugged,
        "internet_connected": internet,
    }


def _send_alert(alert_type, title, message):

    with _monitor_lock:

        if _alert_state.get(alert_type):
            return

        _alert_state[alert_type] = True

    show_notification(
        title,
        message,
    )


def _reset_alert(alert_type):

    with _monitor_lock:
        _alert_state[alert_type] = False


def _monitor_worker():

    global _monitor_running

    while _monitor_running:

        try:

            data = _check_system()

            cpu = data["cpu_percent"]
            ram = data["ram_percent"]
            disk = data["disk_percent"]
            battery = data["battery_percent"]
            plugged = data["battery_plugged"]
            internet = data["internet_connected"]

            # CPU
            if cpu >= _monitor_settings["cpu_threshold"]:

                _send_alert(
                    "cpu",
                    "JARVIS CPU Alert",
                    f"CPU usage is high: {cpu}%",
                )

            else:
                _reset_alert("cpu")

            # RAM
            if ram >= _monitor_settings["ram_threshold"]:

                _send_alert(
                    "ram",
                    "JARVIS RAM Alert",
                    f"RAM usage is high: {ram}%",
                )

            else:
                _reset_alert("ram")

            # Disk
            if disk >= _monitor_settings["disk_threshold"]:

                _send_alert(
                    "disk",
                    "JARVIS Disk Alert",
                    f"Disk usage is high: {disk}%",
                )

            else:
                _reset_alert("disk")

            # Battery
            if (
                battery is not None
                and battery <= _monitor_settings["battery_threshold"]
                and not plugged
            ):

                _send_alert(
                    "battery",
                    "JARVIS Battery Alert",
                    f"Battery is low: {battery}%",
                )

            else:
                _reset_alert("battery")

            # Internet
            if not internet:

                _send_alert(
                    "internet",
                    "JARVIS Internet Alert",
                    "Internet connection appears to be unavailable.",
                )

            else:
                _reset_alert("internet")

        except Exception:
            pass

        time.sleep(
            _monitor_settings["interval"]
        )


def start_system_monitor():

    global _monitor_thread
    global _monitor_running

    with _monitor_lock:

        if _monitor_running:

            return {
                "success": True,
                "message": "System monitoring is already running.",
            }

        _monitor_running = True

        _monitor_thread = threading.Thread(
            target=_monitor_worker,
            daemon=True,
        )

        _monitor_thread.start()

    return {
        "success": True,
        "message": "System monitoring started.",
        "settings": _monitor_settings.copy(),
    }


def stop_system_monitor():

    global _monitor_running

    with _monitor_lock:
        if not _monitor_running:

            return {
                "success": True,
                "message": "System monitoring is already stopped.",
            }

        _monitor_running = False

    return {
        "success": True,
        "message": "System monitoring stopped.",
    }


def system_monitor_status():

    with _monitor_lock:
        running = _monitor_running

    return {
        "success": True,
        "running": running,
        "settings": _monitor_settings.copy(),
    }


def set_monitor_thresholds(
    cpu_threshold: float = 90,
    ram_threshold: float = 90,
    disk_threshold: float = 90,
    battery_threshold: float = 20,
    interval: int = 30,
):

    try:

        cpu_threshold = float(cpu_threshold)
        ram_threshold = float(ram_threshold)
        disk_threshold = float(disk_threshold)
        battery_threshold = float(battery_threshold)
        interval = int(interval)

        if not 1 <= cpu_threshold <= 100:
            return {
                "success": False,
                "error": "CPU threshold must be between 1 and 100.",
            }

        if not 1 <= ram_threshold <= 100:
            return {
                "success": False,
                "error": "RAM threshold must be between 1 and 100.",
            }

        if not 1 <= disk_threshold <= 100:
            return {
                "success": False,
                "error": "Disk threshold must be between 1 and 100.",
            }

        if not 1 <= battery_threshold <= 100:
            return {
                "success": False,
                "error": "Battery threshold must be between 1 and 100.",
            }

        if interval < 5:
            return {
                "success": False,
                "error": "Monitoring interval must be at least 5 seconds.",
            }

        with _monitor_lock:

            _monitor_settings["cpu_threshold"] = cpu_threshold
            _monitor_settings["ram_threshold"] = ram_threshold
            _monitor_settings["disk_threshold"] = disk_threshold
            _monitor_settings["battery_threshold"] = battery_threshold
            _monitor_settings["interval"] = interval

        return {
            "success": True,
            "message": "Monitoring thresholds updated.",
            "settings": _monitor_settings.copy(),
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }