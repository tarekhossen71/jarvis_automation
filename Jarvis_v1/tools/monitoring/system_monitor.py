import threading
import time

import psutil

from tools.notifications.notification_manager import show_notification


_monitor_thread = None
_monitor_running = False
_monitor_lock = threading.Lock()

_event_manager = None

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


def set_event_manager(event_manager):
    """
    Connect System Monitor with JARVIS EventManager.
    """

    global _event_manager

    _event_manager = event_manager

    return {
        "success": True,
        "message": "System Monitor connected to EventManager.",
    }


def _emit_event(event_name, data):

    if _event_manager is None:
        return

    try:

        _event_manager.emit(
            event_name,
            data,
        )

    except Exception as e:

        print(
            f"❌ System Monitor event error: {e}"
        )


def _check_internet():
    try:
        import requests

        response = requests.get(
            "https://www.google.com",
            timeout=5,
        )

        return response.status_code == 200

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

        battery_percent = round(
            battery.percent,
            1,
        )

        battery_plugged = battery.power_plugged

    internet = _check_internet()

    return {

        "cpu_percent": round(
            cpu,
            1,
        ),

        "ram_percent": round(
            ram,
            1,
        ),

        "disk_percent": round(
            disk_percent,
            1,
        ),

        "battery_percent": battery_percent,

        "battery_plugged": battery_plugged,

        "internet_connected": internet,
    }


def _send_alert(
    alert_type,
    title,
    message,
    event_name,
    data,
):

    with _monitor_lock:

        if _alert_state.get(alert_type):

            return

        _alert_state[alert_type] = True

    # Desktop notification
    show_notification(
        title,
        message,
    )

    # EventManager
    _emit_event(
        event_name,
        data,
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

            # =====================================
            # GENERIC SYSTEM MONITOR EVENT
            # =====================================

            _emit_event(
                "SYSTEM_MONITOR",
                {
                    "cpu": data["cpu_percent"],
                    "ram": data["ram_percent"],
                    "disk": data["disk_percent"],
                    "battery": data["battery_percent"],
                    "internet_connected": data[
                        "internet_connected"
                    ],
                },
            )
            
            internet = data["internet_connected"]

            # =====================================
            # CPU
            # =====================================
            # print(
            #     f"🔎 CPU CHECK: "
            #     f"cpu={cpu}% | "
            #     f"threshold={_monitor_settings['cpu_threshold']}% | "
            #     f"alert_state={_alert_state['cpu']}"
            # )

            if cpu >= _monitor_settings["cpu_threshold"]:
                
                _send_alert(

                    "cpu",

                    "JARVIS CPU Alert",

                    f"CPU usage is high: {cpu}%",

                    "CPU_HIGH",

                    {
                        "cpu_percent": cpu,
                        "threshold": _monitor_settings[
                            "cpu_threshold"
                        ],
                    },
                )

            else:

                _reset_alert("cpu")

            # =====================================
            # RAM
            # =====================================

            if ram >= _monitor_settings["ram_threshold"]:

                _send_alert(

                    "ram",

                    "JARVIS RAM Alert",

                    f"RAM usage is high: {ram}%",

                    "RAM_HIGH",

                    {
                        "ram_percent": ram,
                        "threshold": _monitor_settings[
                            "ram_threshold"
                        ],
                    },
                )

            else:

                _reset_alert("ram")

            # =====================================
            # DISK
            # =====================================

            if disk >= _monitor_settings["disk_threshold"]:

                _send_alert(

                    "disk",

                    "JARVIS Disk Alert",

                    f"Disk usage is high: {disk}%",

                    "DISK_HIGH",

                    {
                        "disk_percent": disk,
                        "threshold": _monitor_settings[
                            "disk_threshold"
                        ],
                    },
                )

            else:

                _reset_alert("disk")

            # =====================================
            # BATTERY
            # =====================================

            if (

                battery is not None

                and battery
                <= _monitor_settings[
                    "battery_threshold"
                ]

                and not plugged

            ):

                _send_alert(

                    "battery",

                    "JARVIS Battery Alert",

                    f"Battery is low: {battery}%",

                    "BATTERY_LOW",

                    {
                        "battery_percent": battery,
                        "threshold": _monitor_settings[
                            "battery_threshold"
                        ],
                        "plugged": plugged,
                    },
                )

            else:

                _reset_alert("battery")

            # =====================================
            # INTERNET
            # =====================================

            if not internet:

                _send_alert(

                    "internet",

                    "JARVIS Internet Alert",

                    "Internet connection appears to be unavailable.",

                    "INTERNET_DOWN",

                    {
                        "internet_connected": False,
                    },
                )

            else:

                _reset_alert("internet")

        except Exception as e:

            print(
                f"❌ System Monitor error: {e}"
            )

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

        cpu_threshold = float(
            cpu_threshold
        )

        ram_threshold = float(
            ram_threshold
        )

        disk_threshold = float(
            disk_threshold
        )

        battery_threshold = float(
            battery_threshold
        )

        interval = int(interval)

        if not 1 <= cpu_threshold <= 100:

            return {

                "success": False,

                "error":
                    "CPU threshold must be between 1 and 100.",
            }

        if not 1 <= ram_threshold <= 100:

            return {

                "success": False,

                "error":
                    "RAM threshold must be between 1 and 100.",
            }

        if not 1 <= disk_threshold <= 100:

            return {

                "success": False,

                "error":
                    "Disk threshold must be between 1 and 100.",
            }

        if not 1 <= battery_threshold <= 100:

            return {

                "success": False,

                "error":
                    "Battery threshold must be between 1 and 100.",
            }

        if interval < 5:

            return {

                "success": False,

                "error":
                    "Monitoring interval must be at least 5 seconds.",
            }

        with _monitor_lock:

            _monitor_settings[
                "cpu_threshold"
            ] = cpu_threshold

            _monitor_settings[
                "ram_threshold"
            ] = ram_threshold

            _monitor_settings[
                "disk_threshold"
            ] = disk_threshold

            _monitor_settings[
                "battery_threshold"
            ] = battery_threshold

            _monitor_settings[
                "interval"
            ] = interval

        return {

            "success": True,

            "message":
                "Monitoring thresholds updated.",

            "settings":
                _monitor_settings.copy(),

        }

    except Exception as e:

        return {

            "success": False,

            "error": str(e),

        }