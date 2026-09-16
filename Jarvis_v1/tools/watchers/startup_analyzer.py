import os


class StartupAnalyzer:

    SAFE_STARTUP_EXTENSIONS = {
        ".lnk",
        ".url",
    }

    SCRIPT_EXTENSIONS = {
        ".bat",
        ".cmd",
        ".ps1",
        ".vbs",
        ".vbe",
        ".js",
        ".jse",
        ".wsf",
        ".wsh",
    }

    EXECUTABLE_EXTENSIONS = {
        ".exe",
        ".com",
        ".scr",
    }

    @classmethod
    def analyze(cls, item):

        location = (
            item.get("location") or ""
        ).strip()

        name = (
            item.get("name") or ""
        ).strip()

        value = (
            item.get("value") or ""
        ).strip()

        if not value:
            return {
                "risk": "MEDIUM",
                "reason": "Startup item path or command could not be determined.",
            }

        normalized_value = os.path.normcase(value)

        extension = os.path.splitext(
            normalized_value
        )[1]

        # -------------------------------------------------
        # Standard Windows startup shortcut
        # -------------------------------------------------

        if extension in cls.SAFE_STARTUP_EXTENSIONS:

            return {
                "risk": "LOW",
                "reason": "Startup item uses a standard Windows shortcut or URL format.",
            }

        # -------------------------------------------------
        # Script-based startup item
        # -------------------------------------------------

        if extension in cls.SCRIPT_EXTENSIONS:

            return {
                "risk": "MEDIUM",
                "reason": "Startup item uses a script-based file type.",
            }

        # -------------------------------------------------
        # Executable startup item
        # -------------------------------------------------

        if extension in cls.EXECUTABLE_EXTENSIONS:

            return {
                "risk": "MEDIUM",
                "reason": "Startup item launches an executable directly.",
            }

        # -------------------------------------------------
        # Registry startup command
        # -------------------------------------------------

        if location in (
            "HKCU_RUN",
            "HKLM_RUN",
            "HKCU_RUNONCE",
            "HKLM_RUNONCE",
        ):

            return {
                "risk": "MEDIUM",
                "reason": "Startup item is registered through a Windows Run or RunOnce registry key.",
            }

        # -------------------------------------------------
        # Unknown startup type
        # -------------------------------------------------

        return {
            "risk": "MEDIUM",
            "reason": "Startup item type is not recognized.",
        }