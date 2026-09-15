import os
import subprocess
import psutil
import shutil
import win32com.client

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

    # =========================================================
    # WHATSAPP
    # =========================================================

    "whatsapp": {
        "command": "WhatsApp.exe",
        "process": "WhatsApp.Root.exe",
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
# OPEN APPLICATION
# =========================================================

def open_application(app_name: str, arguments: str = ""):
    """
    Open a Windows application.

    JARVIS first checks known applications,
    then automatically searches Windows
    for unknown applications.
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
                    f"Could not find application: {app_name}."
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
            "process": process_name,
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

def find_application_command(app_name: str):

    normalized = normalize_app_name(app_name)

    # =====================================================
    # KNOWN APPLICATION
    # =====================================================

    if normalized in APP_ALIASES:

        command = APP_ALIASES[normalized]["command"]
        process = APP_ALIASES[normalized]["process"]

        # -------------------------------------------------
        # PATH
        # -------------------------------------------------

        found = shutil.which(command)

        if found:
            return found, process

        # -------------------------------------------------
        # Chrome
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Edge
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Firefox
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Automatic search
        # -------------------------------------------------

        automatic_result = search_windows_application(
            normalized
        )

        if automatic_result:

            return automatic_result, process

        return None, None

    # =====================================================
    # UNKNOWN APPLICATION
    # =====================================================

    executable = normalized

    if not executable.endswith(".exe"):
        executable += ".exe"

    # -----------------------------------------------------
    # PATH
    # -----------------------------------------------------

    found = shutil.which(executable)

    if found:
        return found, executable

    # -----------------------------------------------------
    # Automatic Windows search
    # -----------------------------------------------------

    automatic_result = search_windows_application(
        normalized
    )

    if automatic_result:

        return automatic_result, executable

    return None, None

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

# =========================================================
# AUTOMATIC WINDOWS APPLICATION SEARCH
# =========================================================

def search_windows_application(app_name: str):
    """
    Automatically search for a Windows application.

    Searches:
    - PATH
    - Start Menu
    - Desktop
    - Common installation folders
    """

    name = (app_name or "").strip().lower()

    if not name:
        return None

    # Remove .exe if user provided it
    if name.endswith(".exe"):
        name = name[:-4]

    # -----------------------------------------------------
    # Possible executable names
    # -----------------------------------------------------

    possible_names = {
        name,
        name.replace(" ", ""),
        name.replace(" ", "_"),
        name.replace(" ", "-"),
    }

    # -----------------------------------------------------
    # 1. Search PATH
    # -----------------------------------------------------

    for executable_name in possible_names:

        if not executable_name.endswith(".exe"):
            executable_name += ".exe"

        found = shutil.which(executable_name)

        if found:
            return found

    # -----------------------------------------------------
    # 2. Search Start Menu + Desktop shortcuts
    # -----------------------------------------------------

    shortcut_locations = [
        os.path.expandvars(
            r"%ProgramData%\Microsoft\Windows\Start Menu\Programs"
        ),
        os.path.expandvars(
            r"%AppData%\Microsoft\Windows\Start Menu\Programs"
        ),
        os.path.expandvars(
            r"%USERPROFILE%\Desktop"
        ),
        os.path.expandvars(
            r"%PUBLIC%\Desktop"
        ),
    ]

    for location in shortcut_locations:

        if not os.path.isdir(location):
            continue

        for root, dirs, files in os.walk(location):

            for file in files:

                lower_file = file.lower()

                if not lower_file.endswith(".lnk"):
                    continue

                shortcut_name = os.path.splitext(
                    lower_file
                )[0]

                if (
                    name == shortcut_name
                    or name in shortcut_name
                    or shortcut_name in name
                ):
                    try:
                        import win32com.client

                        shell = win32com.client.Dispatch(
                            "WScript.Shell"
                        )

                        shortcut = shell.CreateShortCut(
                            os.path.join(root, file)
                        )

                        target = shortcut.Targetpath

                        if target and os.path.isfile(target):
                            return target

                    except Exception:
                        pass

    # -----------------------------------------------------
    # 3. Common installation folders
    # -----------------------------------------------------

    common_locations = [
        os.environ.get("ProgramFiles"),
        os.environ.get("ProgramFiles(x86)"),
        os.environ.get("LOCALAPPDATA"),
        os.environ.get("APPDATA"),
        os.environ.get("USERPROFILE"),
        os.path.join(
            os.environ.get("USERPROFILE", ""),
            "AppData",
            "Local",
        ),
        os.path.join(
            os.environ.get("USERPROFILE", ""),
            "AppData",
            "Roaming",
        ),
    ]

    # -----------------------------------------------------
    # Search common folders
    # -----------------------------------------------------

    for base_path in common_locations:

        if not base_path or not os.path.isdir(base_path):
            continue

        try:

            for root, dirs, files in os.walk(base_path):

                # Avoid unnecessary huge folders
                dirs[:] = [
                    d for d in dirs
                    if d.lower() not in {
                        "node_modules",
                        "__pycache__",
                        ".git",
                        "cache",
                        "caches",
                    }
                ]

                for file in files:

                    if not file.lower().endswith(".exe"):
                        continue

                    exe_name = os.path.splitext(
                        file.lower()
                    )[0]

                    if (
                        exe_name == name
                        or exe_name.replace(" ", "") == name.replace(" ", "")
                    ):
                        return os.path.join(
                            root,
                            file
                        )

        except (PermissionError, OSError):
            continue

    return None