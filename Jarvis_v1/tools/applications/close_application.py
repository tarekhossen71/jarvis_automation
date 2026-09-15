
import os
import subprocess
import psutil
import shutil
import win32com.client


# =========================================================
# COMMON WINDOWS APPLICATIONS
# =========================================================

APP_ALIASES = {

    # =====================================================
    # GOOGLE CHROME
    # =====================================================

    "chrome": {
        "command": "chrome.exe",
    },

    "google chrome": {
        "command": "chrome.exe",
    },

    # =====================================================
    # MICROSOFT EDGE
    # =====================================================

    "msedge": {
        "command": "msedge.exe",
    },

    "edge": {
        "command": "msedge.exe",
    },

    "microsoft edge": {
        "command": "msedge.exe",
    },

    # =====================================================
    # FIREFOX
    # =====================================================

    "firefox": {
        "command": "firefox.exe",
    },

    # =====================================================
    # VS CODE
    # =====================================================

    "code": {
        "command": "code.exe",
    },

    "vs code": {
        "command": "code.exe",
    },

    "visual studio code": {
        "command": "code.exe",
    },

    "vscode": {
        "command": "code.exe",
    },

    # =====================================================
    # NOTEPAD
    # =====================================================

    "notepad": {
        "command": "notepad.exe",
    },

    # =====================================================
    # CALCULATOR
    # =====================================================

    "calculator": {
        "command": "calc.exe",
    },

    "calc": {
        "command": "calc.exe",
    },

    # =====================================================
    # PAINT
    # =====================================================

    "paint": {
        "command": "mspaint.exe",
    },

    # =====================================================
    # WORDPAD
    # =====================================================

    "wordpad": {
        "command": "write.exe",
    },

    # =====================================================
    # FILE EXPLORER
    # =====================================================

    "file explorer": {
        "command": "explorer.exe",
    },

    "explorer": {
        "command": "explorer.exe",
    },

    # =====================================================
    # COMMAND PROMPT
    # =====================================================

    "command prompt": {
        "command": "cmd.exe",
    },

    "cmd": {
        "command": "cmd.exe",
    },

    # =====================================================
    # POWERSHELL
    # =====================================================

    "powershell": {
        "command": "powershell.exe",
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
# DYNAMIC NAME NORMALIZATION
# =========================================================

def clean_process_name(name: str):
    """
    Convert a Windows process name into a comparable form.

    Example:

        WhatsApp.Root.exe
        -> whatsapproot

        WhatsApp.exe
        -> whatsapp

        Code.exe
        -> code
    """

    if not name:
        return ""

    value = str(name).strip().lower()

    if value.endswith(".exe"):
        value = value[:-4]

    # Remove separators commonly used in executable names.
    for char in (
        ".",
        "_",
        "-",
        " ",
    ):
        value = value.replace(char, "")

    return value


# =========================================================
# DYNAMIC APPLICATION MATCHING
# =========================================================

def application_name_matches(
    requested_name: str,
    process_name: str,
):
    """
    Dynamically determine whether a process belongs
    to the requested application.

    No hardcoded process name is required.
    """

    requested = normalize_app_name(
        requested_name
    )

    process = clean_process_name(
        process_name
    )

    if not requested or not process:
        return False

    requested_clean = clean_process_name(
        requested
    )

    # -----------------------------------------------------
    # Exact match
    # -----------------------------------------------------

    if process == requested_clean:
        return True

    # -----------------------------------------------------
    # Common Windows executable pattern
    #
    # Example:
    #
    # requested: whatsapp
    # process:   whatsapproot
    #
    # requested: code
    # process:   code
    # -----------------------------------------------------

    if process.startswith(
        requested_clean
    ):
        return True

    if requested_clean.startswith(
        process
    ):
        return True

    # -----------------------------------------------------
    # Known application executable aliases
    #
    # These are executable names, not process mappings.
    # They help dynamic matching without requiring
    # a fixed process name.
    # -----------------------------------------------------

    dynamic_aliases = {
        "chrome": {
            "chrome",
        },

        "msedge": {
            "msedge",
            "edge",
        },

        "firefox": {
            "firefox",
        },

        "code": {
            "code",
            "visualstudiocode",
        },

        "calculator": {
            "calculatorapp",
            "calculator",
            "calc",
        },

        "file explorer": {
            "explorer",
        },

        "command prompt": {
            "cmd",
            "commandprompt",
        },

        "powershell": {
            "powershell",
            "pwsh",
        },
    }

    aliases = dynamic_aliases.get(
        requested,
        set(),
    )

    if process in aliases:
        return True

    return False


# =========================================================
# FIND RUNNING APPLICATION DYNAMICALLY
# =========================================================

def find_running_application(
    app_name: str,
):
    """
    Dynamically search currently running processes
    for the requested application.

    Returns matching process information.
    """

    matches = []

    requested = normalize_app_name(
        app_name
    )

    if not requested:
        return matches

    for process in psutil.process_iter(
        [
            "pid",
            "name",
            "exe",
            "username",
        ]
    ):
        try:

            name = process.info.get(
                "name"
            )

            if not name:
                continue

            if application_name_matches(
                requested,
                name,
            ):

                matches.append(
                    {
                        "pid": process.info.get(
                            "pid"
                        ),
                        "name": name,
                        "exe": process.info.get(
                            "exe"
                        ),
                    }
                )

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
        ):
            continue

    return matches


# =========================================================
# OPEN APPLICATION
# =========================================================

def open_application(
    app_name: str,
    arguments: str = "",
):
    """
    Open a Windows application.

    Known applications use their known executable.
    Unknown applications are searched dynamically.
    """

    try:

        app_name = (
            app_name or ""
        ).strip()

        if not app_name:
            return {
                "success": False,
                "error": (
                    "Application name cannot be empty."
                ),
            }

        command, process_name = (
            find_application_command(
                app_name
            )
        )

        if not command:
            return {
                "success": False,
                "error": (
                    f"Could not find application: "
                    f"{app_name}."
                ),
            }

        command_parts = [
            command
        ]

        if arguments:
            command_parts.extend(
                arguments.strip().split()
            )

        subprocess.Popen(
            command_parts,
            shell=False,
        )

        return {
            "success": True,
            "application": app_name,
            "command": command,
            "process": process_name,
            "message": (
                f"Opened {app_name}."
            ),
        }

    except FileNotFoundError:

        return {
            "success": False,
            "error": (
                "Application executable was "
                f"not found: {app_name}"
            ),
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# FIND APPLICATION COMMAND
# =========================================================

def find_application_command(
    app_name: str,
):

    normalized = normalize_app_name(
        app_name
    )

    # =====================================================
    # KNOWN APPLICATION
    # =====================================================

    if normalized in APP_ALIASES:

        command = APP_ALIASES[
            normalized
        ]["command"]

        # -------------------------------------------------
        # PATH
        # -------------------------------------------------

        found = shutil.which(
            command
        )

        if found:
            return (
                found,
                os.path.basename(found),
            )

        # -------------------------------------------------
        # CHROME
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
                    return (
                        path,
                        os.path.basename(path),
                    )

        # -------------------------------------------------
        # EDGE
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
                    return (
                        path,
                        os.path.basename(path),
                    )

        # -------------------------------------------------
        # FIREFOX
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
                    return (
                        path,
                        os.path.basename(path),
                    )

        # -------------------------------------------------
        # AUTOMATIC SEARCH
        # -------------------------------------------------

        automatic_result = (
            search_windows_application(
                normalized
            )
        )

        if automatic_result:

            return (
                automatic_result,
                os.path.basename(
                    automatic_result
                ),
            )

        return None, None

    # =====================================================
    # UNKNOWN APPLICATION
    # =====================================================

    executable = normalized

    if not executable.endswith(
        ".exe"
    ):
        executable += ".exe"

    # -----------------------------------------------------
    # PATH
    # -----------------------------------------------------

    found = shutil.which(
        executable
    )

    if found:

        return (
            found,
            os.path.basename(found),
        )

    # -----------------------------------------------------
    # AUTOMATIC WINDOWS SEARCH
    # -----------------------------------------------------

    automatic_result = (
        search_windows_application(
            normalized
        )
    )

    if automatic_result:

        return (
            automatic_result,
            os.path.basename(
                automatic_result
            ),
        )

    return None, None


# =========================================================
# CHECK IF APPLICATION IS RUNNING
# =========================================================

def is_application_running(
    app_name: str,
):
    """
    Dynamically check whether an application
    is currently running.
    """

    try:

        app_name = (
            app_name or ""
        ).strip()

        if not app_name:
            return {
                "success": False,
                "error": (
                    "Application name cannot be empty."
                ),
            }

        matches = find_running_application(
            app_name
        )

        if not matches:

            return {
                "success": True,
                "running": False,
                "application": app_name,
            }

        first = matches[0]

        return {
            "success": True,
            "running": True,
            "application": app_name,
            "process": first.get(
                "name"
            ),
            "pid": first.get(
                "pid"
            ),
            "processes": matches,
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
            [
                "pid",
                "name",
                "username",
            ]
        ):

            try:

                name = process.info[
                    "name"
                ]

                if not name:
                    continue

                lower_name = (
                    name.lower()
                )

                if (
                    lower_name
                    in system_processes
                ):
                    continue

                if (
                    lower_name
                    in seen
                ):
                    continue

                seen.add(
                    lower_name
                )

                applications.append(
                    {
                        "name": name,
                        "pid": process.info[
                            "pid"
                        ],
                    }
                )

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
            ):
                continue

        applications.sort(
            key=lambda item:
                item["name"].lower()
        )

        return {
            "success": True,
            "count": len(
                applications
            ),
            "applications":
                applications[:100],
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# CLOSE APPLICATION REQUEST
# =========================================================

def close_application(
    app_name: str,
):
    """
    Dynamically find a running application.

    This function does NOT close it immediately.
    It returns the exact process information so
    the confirmation system can approve the close.
    """

    try:

        app_name = (
            app_name or ""
        ).strip()

        if not app_name:

            return {
                "success": False,
                "error": (
                    "Application name cannot be empty."
                ),
            }

        matching_processes = (
            find_running_application(
                app_name
            )
        )

        # -------------------------------------------------
        # APPLICATION NOT RUNNING
        # -------------------------------------------------

        if not matching_processes:

            return {
                "success": False,
                "running": False,
                "application": app_name,
                "message": (
                    f"{app_name} is not "
                    "currently running."
                ),
            }

        # -------------------------------------------------
        # APPLICATION FOUND
        # -------------------------------------------------

        return {
            "success": True,
            "requires_confirmation": True,
            "application": app_name,
            "processes": matching_processes,
            "message": (
                f"{app_name} is currently running. "
                "Confirmation is required before "
                "closing it."
            ),
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# FORCE CLOSE APPLICATION
# =========================================================

def force_close_application(
    app_name: str,
):
    """
    Force close the requested application.

    File Explorer is handled specially:
    it closes the Explorer window instead of
    terminating explorer.exe, so the Windows
    desktop/taskbar remains untouched.
    """

    try:

        app_name = (
            app_name or ""
        ).strip()

        if not app_name:

            return {
                "success": False,
                "error": (
                    "Application name cannot be empty."
                ),
            }

        # =================================================
        # SPECIAL CASE: FILE EXPLORER
        # =================================================

        normalized = normalize_app_name(
            app_name
        )

        if normalized in {
            "explorer",
            "file explorer",
        }:

            try:

                shell = (
                    win32com.client.Dispatch(
                        "Shell.Application"
                    )
                )

                windows = list(
                    shell.Windows()
                )

                closed_windows = 0

                for window in windows:

                    try:

                        # ---------------------------------
                        # Close ONLY the Explorer window.
                        #
                        # Do NOT terminate explorer.exe.
                        # ---------------------------------

                        window.Quit()

                        closed_windows += 1

                    except Exception:
                        continue

                if closed_windows == 0:

                    return {
                        "success": False,
                        "running": False,
                        "application": app_name,
                        "message": (
                            "No File Explorer window "
                            "is currently open."
                        ),
                    }

                return {
                    "success": True,
                    "application": app_name,
                    "closed_windows": closed_windows,
                    "message": (
                        "File Explorer window(s) "
                        "closed successfully."
                    ),
                }

            except Exception as e:

                return {
                    "success": False,
                    "application": app_name,
                    "error": str(e),
                }

        # =================================================
        # NORMAL APPLICATION HANDLING
        # =================================================

        matching_processes = (
            find_running_application(
                app_name
            )
        )

        # -------------------------------------------------
        # NOTHING TO CLOSE
        # -------------------------------------------------

        if not matching_processes:

            return {
                "success": False,
                "running": False,
                "application": app_name,
                "message": (
                    f"{app_name} is no longer running."
                ),
            }

        closed = []
        failed = []

        # -------------------------------------------------
        # CLOSE EXACT MATCHED PIDS
        # -------------------------------------------------

        for item in matching_processes:

            pid = item.get(
                "pid"
            )

            if not pid:
                continue

            try:

                process = psutil.Process(
                    pid
                )

                process.terminate()

                closed.append(
                    {
                        "pid": pid,
                        "name": item.get(
                            "name"
                        ),
                    }
                )

            except psutil.NoSuchProcess:
                pass

            except psutil.AccessDenied as e:

                failed.append(
                    {
                        "pid": pid,
                        "name": item.get(
                            "name"
                        ),
                        "error": str(e),
                    }
                )

            except Exception as e:

                failed.append(
                    {
                        "pid": pid,
                        "name": item.get(
                            "name"
                        ),
                        "error": str(e),
                    }
                )

        # -------------------------------------------------
        # RESULT
        # -------------------------------------------------

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
            "closed_processes": closed,
            "failed": failed,
            "message": (
                f"Closed {app_name}."
                if not failed
                else (
                    f"{app_name} could not be "
                    "fully closed."
                )
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

def search_windows_application(
    app_name: str,
):
    """
    Automatically search for a Windows application.

    Searches:

    - PATH
    - Start Menu
    - Desktop
    - Common installation folders
    """

    name = (
        app_name or ""
    ).strip().lower()

    if not name:
        return None

    # -----------------------------------------------------
    # Remove .exe
    # -----------------------------------------------------

    if name.endswith(
        ".exe"
    ):
        name = name[:-4]

    # -----------------------------------------------------
    # Possible executable names
    # -----------------------------------------------------

    possible_names = {
        name,
        name.replace(
            " ",
            "",
        ),
        name.replace(
            " ",
            "_",
        ),
        name.replace(
            " ",
            "-",
        ),
    }

    # -----------------------------------------------------
    # PATH
    # -----------------------------------------------------

    for executable_name in possible_names:

        if not executable_name.endswith(
            ".exe"
        ):
            executable_name += ".exe"

        found = shutil.which(
            executable_name
        )

        if found:
            return found

    # -----------------------------------------------------
    # START MENU + DESKTOP
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

        if not os.path.isdir(
            location
        ):
            continue

        for root, dirs, files in os.walk(
            location
        ):

            for file in files:

                lower_file = (
                    file.lower()
                )

                if not lower_file.endswith(
                    ".lnk"
                ):
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

                        shell = (
                            win32com.client.Dispatch(
                                "WScript.Shell"
                            )
                        )

                        shortcut = (
                            shell.CreateShortCut(
                                os.path.join(
                                    root,
                                    file,
                                )
                            )
                        )

                        target = (
                            shortcut.Targetpath
                        )

                        if (
                            target
                            and os.path.isfile(
                                target
                            )
                        ):
                            return target

                    except Exception:
                        pass

    # -----------------------------------------------------
    # COMMON INSTALLATION FOLDERS
    # -----------------------------------------------------

    common_locations = [

        os.environ.get(
            "ProgramFiles"
        ),

        os.environ.get(
            "ProgramFiles(x86)"
        ),

        os.environ.get(
            "LOCALAPPDATA"
        ),

        os.environ.get(
            "APPDATA"
        ),

        os.environ.get(
            "USERPROFILE"
        ),

        os.path.join(
            os.environ.get(
                "USERPROFILE",
                "",
            ),
            "AppData",
            "Local",
        ),

        os.path.join(
            os.environ.get(
                "USERPROFILE",
                "",
            ),
            "AppData",
            "Roaming",
        ),
    ]

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    for base_path in common_locations:

        if (
            not base_path
            or not os.path.isdir(
                base_path
            )
        ):
            continue

        try:

            for root, dirs, files in os.walk(
                base_path
            ):

                dirs[:] = [
                    d
                    for d in dirs
                    if d.lower()
                    not in {
                        "node_modules",
                        "__pycache__",
                        ".git",
                        "cache",
                        "caches",
                    }
                ]

                for file in files:

                    if not file.lower().endswith(
                        ".exe"
                    ):
                        continue

                    exe_name = os.path.splitext(
                        file.lower()
                    )[0]

                    if (
                        exe_name == name
                        or
                        exe_name.replace(
                            " ",
                            "",
                        )
                        ==
                        name.replace(
                            " ",
                            "",
                        )
                    ):

                        return os.path.join(
                            root,
                            file,
                        )

        except (
            PermissionError,
            OSError,
        ):
            continue

    return None
