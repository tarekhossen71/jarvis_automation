import psutil


def get_battery():
    """
    Get current battery information.
    """

    battery = psutil.sensors_battery()

    if battery is None:
        return {
            "available": False,
            "device_type": "desktop_pc",
            "message": (
                "No battery detected. The computer appears "
                "to be a desktop PC."
            ),
        }

    return {
        "available": True,
        "battery_percent": f"{battery.percent}%",
        "plugged_in": battery.power_plugged,
        "status": (
            "Charging"
            if battery.power_plugged
            else "Discharging"
        ),
        "seconds_left": battery.secsleft,
    }