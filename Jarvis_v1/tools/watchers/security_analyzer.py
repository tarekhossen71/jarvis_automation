import os


class SecurityAnalyzer:

    # =========================================================
    # WINDOWS PATHS
    # =========================================================

    WINDOWS_SYSTEM_ROOT = os.path.normcase(
        os.environ.get(
            "SystemRoot",
            r"C:\Windows",
        )
    )

    SAFE_PROGRAM_FILES = (
        os.path.normcase(
            os.environ.get(
                "ProgramFiles",
                r"C:\Program Files",
            )
        ),
        os.path.normcase(
            os.environ.get(
                "ProgramFiles(x86)",
                r"C:\Program Files (x86)",
            )
        ),
    )

    WINDOWS_APPS_PATH = os.path.normcase(
        os.path.join(
            os.environ.get(
                "ProgramFiles",
                r"C:\Program Files",
            ),
            "WindowsApps",
        )
    )

    SAFE_SYSTEM_EXECUTABLES = {
        "svchost.exe",
        "smartscreen.exe",
        "explorer.exe",
        "notepad.exe",
        "dwm.exe",
        "conhost.exe",
        "csrss.exe",
        "lsass.exe",
        "services.exe",
        "winlogon.exe",
        "taskhostw.exe",
        "runtimebroker.exe",
        "dllhost.exe",
    }

    # =========================================================
    # ANALYZE PROCESS
    # =========================================================

    @classmethod
    def analyze(cls, process):

        name = (process.get("name") or "").strip()
        path = (process.get("path") or "").strip()

        normalized_name = name.lower()

        if not path:
            return {
                "risk": "MEDIUM",
                "reason": "Executable path could not be determined.",
            }

        normalized_path = os.path.normcase(
            os.path.abspath(path)
        )

        # =====================================================
        # WINDOWS SYSTEM DIRECTORY
        # =====================================================

        if normalized_path.startswith(
            cls.WINDOWS_SYSTEM_ROOT
        ):

            if normalized_name in cls.SAFE_SYSTEM_EXECUTABLES:

                return {
                    "risk": "LOW",
                    "reason": "Known Windows system executable.",
                }

            return {
                "risk": "LOW",
                "reason": "Executable is running from the Windows system directory.",
            }

        # =====================================================
        # WINDOWS APPS
        # =====================================================

        if normalized_path.startswith(
            cls.WINDOWS_APPS_PATH
        ):

            return {
                "risk": "LOW",
                "reason": "Executable is running from the official WindowsApps directory.",
            }

        # =====================================================
        # PROGRAM FILES
        # =====================================================

        for program_path in cls.SAFE_PROGRAM_FILES:

            if normalized_path.startswith(program_path):

                return {
                    "risk": "LOW",
                    "reason": "Executable is running from a standard Program Files directory.",
                }

        # =====================================================
        # TEMP DIRECTORY
        # =====================================================

        temp_path = os.path.normcase(
            os.environ.get(
                "TEMP",
                "",
            )
        )

        if (
            temp_path
            and normalized_path.startswith(temp_path)
        ):

            return {
                "risk": "MEDIUM",
                "reason": "Executable is running from a temporary directory.",
            }

        # =====================================================
        # APPDATA
        # =====================================================

        appdata = os.path.normcase(
            os.environ.get(
                "APPDATA",
                "",
            )
        )

        local_appdata = os.path.normcase(
            os.environ.get(
                "LOCALAPPDATA",
                "",
            )
        )

        if (
            (appdata and normalized_path.startswith(appdata))
            or
            (
                local_appdata
                and normalized_path.startswith(local_appdata)
            )
        ):

            return {
                "risk": "MEDIUM",
                "reason": "Executable is running from an AppData directory.",
            }

        # =====================================================
        # UNKNOWN LOCATION
        # =====================================================

        return {
            "risk": "MEDIUM",
            "reason": "Executable location is not recognized as a standard system path.",
        }