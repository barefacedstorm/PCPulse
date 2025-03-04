import platform
import psutil
import os
import sys

def get_system_info():
    """Get basic system information"""
    info = {
        "os_name": platform.system(),
        "os_version": platform.version(),
        "os_release": platform.release(),
        "computer_name": platform.node(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": sys.version,
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available
    }

    # Add disk information
    info["disks"] = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            info["disks"].append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent
            })
        except PermissionError:
            # This can happen on Windows with some system drives
            pass

    return info
