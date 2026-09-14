import ctypes
import os
import subprocess


# =========================================================
# LOCK PC
# =========================================================

def lock_pc():
    """
    Lock the Windows computer immediately.
    """

    try:
        ctypes.windll.user32.LockWorkStation()

        return {
            "success": True,
            "message": "The PC has been locked.",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# SLEEP PC
# =========================================================

def sleep_pc():
    """
    Put the Windows computer into sleep mode.
    """

    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Add-Type -AssemblyName System.Windows.Forms; "
                "[System.Windows.Forms.Application]::SetSuspendState("
                "'Suspend', $false, $false)"
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return {
                "success": False,
                "error": result.stderr.strip()
                or "Could not put the PC to sleep.",
            }

        return {
            "success": True,
            "message": "The PC is going to sleep.",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# RESTART PC
# =========================================================

def restart_pc(confirmed: bool = False):
    """
    Restart the Windows computer.

    Restart is only executed when confirmed=True.
    """

    if not confirmed:
        return {
            "success": False,
            "confirmation_required": True,
            "message": (
                "Restarting the PC requires explicit confirmation."
            ),
        }

    try:
        os.system("shutdown /r /t 0")

        return {
            "success": True,
            "message": "The PC is restarting.",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# SHUTDOWN PC
# =========================================================

def shutdown_pc(confirmed: bool = False):
    """
    Shut down the Windows computer.

    Shutdown is only executed when confirmed=True.
    """

    if not confirmed:
        return {
            "success": False,
            "confirmation_required": True,
            "message": (
                "Shutting down the PC requires explicit confirmation."
            ),
        }

    try:
        os.system("shutdown /s /t 0")

        return {
            "success": True,
            "message": "The PC is shutting down.",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }