
import os
import subprocess
from urllib.parse import quote_plus


# =========================================================
# BROWSER PATHS
# =========================================================

BROWSER_PATHS = {
    "chrome": [
        os.path.expandvars(
            r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"
        ),
        os.path.expandvars(
            r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
        ),
        os.path.expandvars(
            r"%LocalAppData%\Google\Chrome\Application\chrome.exe"
        ),
    ],

    "firefox": [
        os.path.expandvars(
            r"%ProgramFiles%\Mozilla Firefox\firefox.exe"
        ),
        os.path.expandvars(
            r"%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe"
        ),
        os.path.expandvars(
            r"%LocalAppData%\Mozilla Firefox\firefox.exe"
        ),
    ],

    "edge": [
        os.path.expandvars(
            r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
        ),
        os.path.expandvars(
            r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
        ),
    ],

    "brave": [
        os.path.expandvars(
            r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe"
        ),
        os.path.expandvars(
            r"%ProgramFiles(x86)%\BraveSoftware\Brave-Browser\Application\brave.exe"
        ),
        os.path.expandvars(
            r"%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe"
        ),
    ],
}


# =========================================================
# DEFAULT BROWSER
# =========================================================

DEFAULT_BROWSER = "firefox"


# =========================================================
# NORMALIZE BROWSER NAME
# =========================================================

def normalize_browser_name(browser):

    browser = (browser or "").strip().lower()

    aliases = {
        "google chrome": "chrome",
        "chrome browser": "chrome",

        "mozilla firefox": "firefox",
        "firefox browser": "firefox",

        "microsoft edge": "edge",
        "edge browser": "edge",
        "msedge": "edge",

        "brave browser": "brave",
        "brave-browser": "brave",
    }

    return aliases.get(browser, browser)


# =========================================================
# FIND BROWSER
# =========================================================

def find_browser(browser=DEFAULT_BROWSER):

    browser = normalize_browser_name(
        browser or DEFAULT_BROWSER
    )

    if browser not in BROWSER_PATHS:
        return None

    for path in BROWSER_PATHS[browser]:

        if os.path.isfile(path):
            return path

    return None


# =========================================================
# CHECK BROWSER RUNNING
# =========================================================

def is_browser_running(browser):

    browser = normalize_browser_name(browser)

    process_names = {
        "chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "edge": "msedge.exe",
        "brave": "brave.exe",
    }

    process_name = process_names.get(browser)

    if not process_name:
        return False

    try:

        result = subprocess.run(
            [
                "tasklist",
                "/FI",
                f"IMAGENAME eq {process_name}",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )

        return process_name.lower() in (
            result.stdout or ""
        ).lower()

    except Exception:
        return False


# =========================================================
# OPEN BROWSER
# =========================================================

def open_browser(browser=DEFAULT_BROWSER):

    browser = normalize_browser_name(
        browser or DEFAULT_BROWSER
    )

    browser_path = find_browser(browser)

    if not browser_path:

        return {
            "success": False,
            "error": (
                f"Could not find {browser} browser."
            ),
        }

    if is_browser_running(browser):

        return {
            "success": True,
            "browser": browser,
            "already_running": True,
            "message": (
                f"{browser.title()} "
                "is already running."
            ),
        }

    try:

        subprocess.Popen(
            [browser_path],
            shell=False,
        )

        return {
            "success": True,
            "browser": browser,
            "already_running": False,
            "message": (
                f"Opened {browser.title()}."
            ),
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }

# =========================================================
# INTERNAL: OPEN URL
# =========================================================

def _open_url(
    url: str,
    browser=DEFAULT_BROWSER,
):

    try:

        url = (url or "").strip()

        if not url:

            return {
                "success": False,
                "error": "URL cannot be empty.",
            }

        browser = normalize_browser_name(
            browser or DEFAULT_BROWSER
        )

        if browser not in BROWSER_PATHS:

            return {
                "success": False,
                "error": (
                    f"Unsupported browser: {browser}. "
                    "Supported browsers: "
                    "chrome, firefox, edge, brave."
                ),
            }

        if not url.startswith(
            ("http://", "https://")
        ):

            url = "https://" + url

        browser_path = find_browser(browser)

        if not browser_path:

            return {
                "success": False,
                "error": (
                    f"Could not find {browser} browser."
                ),
            }

        already_running = is_browser_running(
            browser
        )

        # =================================================
        # BROWSER ALREADY RUNNING
        # =================================================

        if already_running:

            try:

                subprocess.Popen(
                    [
                        browser_path,
                        url,
                    ],
                    shell=False,
                )

                return {
                    "success": True,
                    "browser": browser,
                    "url": url,
                    "already_running": True,
                    "message": (
                        f"Opened the URL in the "
                        f"existing {browser.title()} browser."
                    ),
                }

            except Exception as e:

                return {
                    "success": False,
                    "error": str(e),
                }

        # =================================================
        # BROWSER NOT RUNNING
        # =================================================

        try:

            subprocess.Popen(
                [
                    browser_path,
                    url,
                ],
                shell=False,
            )

            return {
                "success": True,
                "browser": browser,
                "url": url,
                "already_running": False,
                "message": (
                    f"Opened {url} in "
                    f"{browser.title()}."
                ),
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e),
            }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }

# =========================================================
# PUBLIC: OPEN URL
# =========================================================

def open_url(
    url: str,
    browser=DEFAULT_BROWSER,
):

    return _open_url(
        url,
        browser=browser,
    )


# =========================================================
# PUBLIC: OPEN WEBSITE
# =========================================================

def open_website(
    website: str,
    browser=DEFAULT_BROWSER,
):

    try:

        website = (website or "").strip()

        if not website:

            return {
                "success": False,
                "error": "Website cannot be empty.",
            }

        shortcuts = {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "facebook": "https://www.facebook.com",
            "github": "https://github.com",
            "gmail": "https://mail.google.com",
            "chatgpt": "https://chatgpt.com",
            "linkedin": "https://www.linkedin.com",
        }

        key = website.lower()

        if key in shortcuts:

            url = shortcuts[key]

        elif website.startswith(
            ("http://", "https://")
        ):

            url = website

        else:

            url = "https://" + website

        return _open_url(
            url,
            browser=browser,
        )

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# GOOGLE SEARCH
# =========================================================

def google_search(
    query: str,
    browser=DEFAULT_BROWSER,
):

    try:

        query = (query or "").strip()

        if not query:

            return {
                "success": False,
                "error": "Search query is empty.",
            }

        encoded_query = quote_plus(query)

        url = (
            "https://www.google.com/search?q="
            + encoded_query
        )

        return _open_url(
            url,
            browser=browser,
        )

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# YOUTUBE SEARCH
# =========================================================

def youtube_search(
    query: str,
    browser=DEFAULT_BROWSER,
):

    try:

        query = (query or "").strip()

        if not query:

            return {
                "success": False,
                "error": (
                    "YouTube search query is empty."
                ),
            }

        encoded_query = quote_plus(query)

        url = (
            "https://www.youtube.com/results"
            "?search_query="
            + encoded_query
        )

        return _open_url(
            url,
            browser=browser,
        )

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }
