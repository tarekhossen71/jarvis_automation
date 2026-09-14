import os
import subprocess
from urllib.parse import quote_plus


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
    ],
    "edge": [
        os.path.expandvars(
            r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
        ),
        os.path.expandvars(
            r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
        ),
    ],
}


DEFAULT_BROWSER = "firefox"


def find_browser(browser=DEFAULT_BROWSER):
    browser = (browser or DEFAULT_BROWSER).strip().lower()

    if browser not in BROWSER_PATHS:
        return None

    for path in BROWSER_PATHS[browser]:
        if os.path.isfile(path):
            return path

    return None


def _open_url(url: str, browser=DEFAULT_BROWSER):
    try:
        url = (url or "").strip()

        if not url:
            return {
                "success": False,
                "error": "URL cannot be empty.",
            }

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        browser_path = find_browser(browser)

        if not browser_path:
            return {
                "success": False,
                "error": f"Could not find {browser} browser.",
            }

        subprocess.Popen(
            [browser_path, url],
            shell=False,
        )

        return {
            "success": True,
            "browser": browser,
            "url": url,
            "message": f"Opened {url} in {browser}.",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def open_url(url: str):
    """
    Public JARVIS tool.

    Always opens URLs in Chrome.
    """

    return _open_url(
        url,
        browser=DEFAULT_BROWSER,
    )


def open_website(website: str):
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
            browser=DEFAULT_BROWSER,
        )

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def google_search(query: str):
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
            browser=DEFAULT_BROWSER,
        )

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def youtube_search(query: str):
    try:
        query = (query or "").strip()

        if not query:
            return {
                "success": False,
                "error": "YouTube search query is empty.",
            }

        encoded_query = quote_plus(query)

        url = (
            "https://www.youtube.com/results"
            "?search_query="
            + encoded_query
        )

        return _open_url(
            url,
            browser=DEFAULT_BROWSER,
        )

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }