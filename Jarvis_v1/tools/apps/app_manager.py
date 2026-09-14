import os
import subprocess
import psutil
import shutil


# =========================================================
# COMMON WINDOWS APPLICATIONS
# =========================================================

APP_ALIASES = {

    # =========================================================
    # GOOGLE CHROME
    # =========================================================

    "chrome": {
        "command": "chrome.exe",
        "process": "chrome.exe",
    },

    "google chrome": {
        "command": "chrome.exe",
        "process": "chrome.exe",
    },

    # =========================================================
    # MICROSOFT EDGE
    # =========================================================

    "msedge": {
        "command": "msedge.exe",
        "process": "msedge.exe",
    },

    "edge": {
        "command": "msedge.exe",
        "process": "msedge.exe",
    },

    "microsoft edge": {
        "command": "msedge.exe",
        "process": "msedge.exe",
    },

    # =========================================================
    # FIREFOX
    # =========================================================

    "firefox": {
        "command": "firefox.exe",
        "process": "firefox.exe",
    },

    # =========================================================
    # VS CODE
    # =========================================================

    "code": {
        "command": "code.exe",
        "process": "Code.exe",
    },

    "vs code": {
        "command": "code.exe",
        "process": "Code.exe",
    },

    "visual studio code": {
        "command": "code.exe",
        "process": "Code.exe",
    },

    "vscode": {
        "command": "code.exe",
        "process": "Code.exe",
    },

    # =========================================================
    # NOTEPAD
    # =========================================================

    "notepad": {
        "command": "notepad.exe",
        "process": "notepad.exe",
    },

    # =========================================================
    # CALCULATOR
    # =========================================================

    "calculator": {
        "command": "calc.exe",
        "process": "CalculatorApp.exe",
    },

    "calc": {
        "command": "calc.exe",
        "process": "CalculatorApp.exe",
    },

    # =========================================================
    # PAINT
    # =========================================================

    "paint": {
        "command": "mspaint.exe",
        "process": "mspaint.exe",
    },

    # =========================================================
    # WORDPAD
    # =========================================================

    "wordpad": {
        "command": "write.exe",
        "process": "wordpad.exe",
    },

    # =========================================================
    # FILE EXPLORER
    # =========================================================

    "file explorer": {
        "command": "explorer.exe",
        "process": "explorer.exe",
    },

    "explorer": {
        "command": "explorer.exe",
        "process": "explorer.exe",
    },

    # =========================================================
    # COMMAND PROMPT
    # =========================================================

    "command prompt": {
        "command": "cmd.exe",
        "process": "cmd.exe",
    },

    "cmd": {
        "command": "cmd.exe",
        "process": "cmd.exe",
    },

    # =========================================================
    # POWERSHELL
    # =========================================================

    "powershell": {
        "command": "powershell.exe",
        "process": "powershell.exe",
    },
}

# =========================================================
# HELPER
# =========================================================

def normalize_app_name(app_name: str):
    """
    Normalize common application names.
    """

    name = (app_name or "").strip().lower()

    aliases = {
        "chrome": "chrome",
        "google chrome": "chrome",

        "edge": "msedge",
        "microsoft edge": "msedge",

        "firefox": "firefox",

        "vs code": "code",
        "visual studio code": "code",
        "vscode": "code",

        "notepad": "notepad",
        "calculator": "calculator",
        "calc": "calculator",

        "paint": "paint",

        "file explorer": "file explorer",
        "explorer": "explorer",

        "command prompt": "command prompt",
        "cmd": "cmd",

        "powershell": "powershell",
    }

    return aliases.get(name, name)


# =========================================================
# FIND APPLICATION COMMAND
# =========================================================

def find_application_command(app_name: str):

    normalized = normalize_app_name(app_name)

    # =========================================================
    # KNOWN APPLICATION
    # =========================================================

    if normalized in APP_ALIASES:

        command = APP_ALIASES[normalized]["command"]
        process = APP_ALIASES[normalized]["process"]

        # Try PATH first
        found = shutil.which(command)

        if found:
            return found, process

        # =====================================================
        # CHROME
        # =====================================================

        if normalized == "chrome":

            chrome_paths = [
                os.path.expandvars(
                    r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"
                ),
                os.path.expandvars(
                    r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
                ),
                os.path.expandvars(
                    r"%LocalAppData%\Google\Chrome\Application\chrome.exe"
                ),
            ]

            for path in chrome_paths:

                if os.path.isfile(path):
                    return path, process

        # =====================================================
        # EDGE
        # =====================================================

        if normalized == "msedge":

            edge_paths = [
                os.path.expandvars(
                    r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
                ),
                os.path.expandvars(
                    r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
                ),
            ]

            for path in edge_paths:

                if os.path.isfile(path):
                    return path, process

        # =====================================================
        # FIREFOX
        # =====================================================

        if normalized == "firefox":

            firefox_paths = [
                os.path.expandvars(
                    r"%ProgramFiles%\Mozilla Firefox\firefox.exe"
                ),
                os.path.expandvars(
                    r"%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe"
                ),
            ]

            for path in firefox_paths:

                if os.path.isfile(path):
                    return path, process

        # Known application but executable not found
        return None, None

    # =========================================================
    # UNKNOWN APPLICATION
    # =========================================================

    executable = normalized

    if not executable.endswith(".exe"):
        executable += ".exe"

    found = shutil.which(executable)

    if found:
        return found, executable

    return None, None


# =========================================================
# OPEN APPLICATION
# =========================================================

def open_application(app_name: str, arguments: str = ""):
    """
    Open a Windows application.

    Examples:
    - open_application("notepad")
    - open_application("calculator")
    - open_application("chrome")
    """

    try:
        app_name = (app_name or "").strip()

        if not app_name:
            return {
                "success": False,
                "error": "Application name cannot be empty.",
            }

        command, process_name = find_application_command(
            app_name
        )

        if not command:
            return {
                "success": False,
                "error": (
                    f"Could not find application: {app_name}. "
                    "Please provide the executable name or "
                    "full path."
                ),
            }

        command_parts = [command]

        if arguments:
            command_parts.extend(
                arguments.strip().split()
            )

        subprocess.Popen(
            command_parts,
            shell=False
        )

        return {
            "success": True,
            "application": app_name,
            "command": command,
            "message": f"Opened {app_name}.",
        }

    except FileNotFoundError:
        return {
            "success": False,
            "error": (
                f"Application executable was not found: "
                f"{app_name}"
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# CHECK IF APPLICATION IS RUNNING
# =========================================================

def is_application_running(app_name: str):
    """
    Check whether an application is currently running.
    """

    try:
        app_name = (app_name or "").strip()

        if not app_name:
            return {
                "success": False,
                "error": "Application name cannot be empty.",
            }

        normalized = normalize_app_name(app_name)

        if normalized in APP_ALIASES:
            process_name = APP_ALIASES[
                normalized
            ]["process"]

        else:
            process_name = normalized

            if not process_name.endswith(".exe"):
                process_name += ".exe"

        process_name = process_name.lower()

        for process in psutil.process_iter(
            ["pid", "name"]
        ):
            try:
                name = process.info["name"]

                if name and name.lower() == process_name:
                    return {
                        "success": True,
                        "running": True,
                        "application": app_name,
                        "process": name,
                        "pid": process.info["pid"],
                    }

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
            ):
                continue

        return {
            "success": True,
            "running": False,
            "application": app_name,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# LIST RUNNING APPLICATIONS
# =========================================================

def get_running_applications():
    """
    Return currently running user applications.
    """

    try:
        applications = []
        seen = set()

        system_processes = {
            "system",
            "system idle process",
            "registry",
            "smss.exe",
            "csrss.exe",
            "wininit.exe",
            "services.exe",
            "lsass.exe",
            "svchost.exe",
            "fontdrvhost.exe",
            "dwm.exe",
            "winlogon.exe",
            "explorer.exe",
            "searchhost.exe",
            "sihost.exe",
            "runtimebroker.exe",
        }

        for process in psutil.process_iter(
            ["pid", "name", "username"]
        ):
            try:
                name = process.info["name"]

                if not name:
                    continue

                lower_name = name.lower()

                if lower_name in system_processes:
                    continue

                if lower_name in seen:
                    continue

                seen.add(lower_name)

                applications.append(
                    {
                        "name": name,
                        "pid": process.info["pid"],
                    }
                )

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
            ):
                continue

        applications.sort(
            key=lambda item: item["name"].lower()
        )

        return {
            "success": True,
            "count": len(applications),
            "applications": applications[:100],
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# CLOSE APPLICATION REQUEST
# =========================================================

def close_application(app_name: str):
    """
    Request closing an application.

    This function does NOT force-kill the process.
    It creates a pending close request.
    """

    try:
        app_name = (app_name or "").strip()

        if not app_name:
            return {
                "success": False,
                "error": "Application name cannot be empty.",
            }

        normalized = normalize_app_name(app_name)

        if normalized in APP_ALIASES:
            process_name = APP_ALIASES[
                normalized
            ]["process"]

        else:
            process_name = normalized

            if not process_name.endswith(".exe"):
                process_name += ".exe"

        process_name = process_name.lower()

        matching_processes = []

        for process in psutil.process_iter(
            ["pid", "name"]
        ):
            try:
                name = process.info["name"]

                if (
                    name
                    and name.lower() == process_name
                ):
                    matching_processes.append(
                        {
                            "pid": process.info["pid"],
                            "name": name,
                        }
                    )

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
            ):
                continue

        if not matching_processes:
            return {
                "success": False,
                "running": False,
                "application": app_name,
                "message": (
                    f"{app_name} is not currently running."
                ),
            }

        return {
            "success": True,
            "requires_confirmation": True,
            "application": app_name,
            "process": process_name,
            "processes": matching_processes,
            "message": (
                f"{app_name} is running. "
                "Confirmation is required before closing it."
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# FORCE CLOSE
# =========================================================

def force_close_application(app_name: str):
    """
    Force close an application after user confirmation.

    WARNING:
    Unsaved work may be lost.
    """

    try:
        app_name = (app_name or "").strip()

        if not app_name:
            return {
                "success": False,
                "error": "Application name cannot be empty.",
            }

        normalized = normalize_app_name(app_name)

        if normalized in APP_ALIASES:
            process_name = APP_ALIASES[
                normalized
            ]["process"]

        else:
            process_name = normalized

            if not process_name.endswith(".exe"):
                process_name += ".exe"

        process_name = process_name.lower()

        closed = []
        failed = []

        for process in psutil.process_iter(
            ["pid", "name"]
        ):
            try:
                name = process.info["name"]

                if (
                    name
                    and name.lower() == process_name
                ):
                    pid = process.info["pid"]

                    try:
                        process.terminate()
                        closed.append(pid)

                    except Exception as e:
                        failed.append(
                            {
                                "pid": pid,
                                "error": str(e),
                            }
                        )

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
            ):
                continue

        if not closed and not failed:
            return {
                "success": False,
                "running": False,
                "application": app_name,
                "message": (
                    f"{app_name} is no longer running."
                ),
            }

        return {
            "success": len(failed) == 0,
            "application": app_name,
            "closed_pids": closed,
            "failed": failed,
            "message": (
                f"Closed {app_name}."
                if not failed
                else f"{app_name} could not be fully closed."
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }