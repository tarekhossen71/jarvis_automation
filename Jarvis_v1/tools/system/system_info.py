import os
import platform
import psutil


def get_ram_info():
    """
    Return current RAM usage information.
    """

    memory = psutil.virtual_memory()

    return {
        "usage_percent": round(
            memory.percent,
            1,
        ),
        "total_gb": round(
            memory.total / (1024 ** 3),
            2,
        ),
        "available_gb": round(
            memory.available / (1024 ** 3),
            2,
        ),
        "used_gb": round(
            memory.used / (1024 ** 3),
            2,
        ),
        "free_gb": round(
            memory.free / (1024 ** 3),
            2,
        ),
    }


def get_cpu_info():
    """
    Return current CPU usage information.
    """

    return {
        "usage_percent": round(
            psutil.cpu_percent(
                interval=0.5
            ),
            1,
        ),
        "processor": platform.processor(),
        "logical_cpus": psutil.cpu_count(
            logical=True
        ),
        "physical_cpus": psutil.cpu_count(
            logical=False
        ),
    }


def get_disk_info(drive):
    """
    Return disk usage information for a specific drive.

    Example:
        get_disk_info("C:\\")
        get_disk_info("D:\\")
    """

    if not drive:
        return {
            "error": "Drive is required."
        }

    drive = str(drive).strip()

    # Convert D:/ -> D:\
    drive = drive.replace("/", "\\")

    # Convert D: -> D:\
    if len(drive) == 2 and drive[1] == ":":
        drive += "\\"

    # Normalize drive letter
    if len(drive) >= 2 and drive[1] == ":":
        drive = drive[0].upper() + drive[1:]

    if not os.path.exists(drive):
        return {
            "drive": drive,
            "error": f"Drive '{drive}' does not exist.",
        }

    disk = psutil.disk_usage(drive)

    return {
        "drive": drive,
        "usage_percent": round(
            disk.percent,
            1,
        ),
        "total_gb": round(
            disk.total / (1024 ** 3),
            2,
        ),
        "used_gb": round(
            disk.used / (1024 ** 3),
            2,
        ),
        "free_gb": round(
            disk.free / (1024 ** 3),
            2,
        ),
    }


def get_system_info():
    """
    Return complete system information.
    """

    ram = get_ram_info()
    cpu = get_cpu_info()
    disk = get_disk_info(
        os.path.abspath(os.sep)
    )

    return {
        "machine": platform.node(),
        "operating_system": platform.system(),
        "os_version": platform.version(),

        "cpu": cpu,
        "ram": ram,
        "disk": disk,
    }