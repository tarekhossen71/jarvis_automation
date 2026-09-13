import platform
import psutil


def get_system_info():
    """
    Get basic computer system information.
    """

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "computer": platform.node(),
        "processor": platform.processor(),
        "cpu_usage": f"{psutil.cpu_percent(interval=1)}%",
        "ram_usage": f"{memory.percent}%",
        "ram_total_gb": round(memory.total / (1024 ** 3), 2),
        "ram_available_gb": round(memory.available / (1024 ** 3), 2),
        "disk_usage": f"{disk.percent}%",
        "disk_total_gb": round(disk.total / (1024 ** 3), 2),
        "disk_free_gb": round(disk.free / (1024 ** 3), 2),
    }