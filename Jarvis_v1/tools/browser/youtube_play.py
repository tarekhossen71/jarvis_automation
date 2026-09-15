
import re
import requests

from tools.browser.browser import open_url


def play_youtube(query: str, browser: str = None):
    try:
        query = (query or "").strip()

        if not query:
            return {
                "success": False,
                "error": "YouTube search query is empty.",
            }

        search_url = (
            "https://www.youtube.com/results"
            "?search_query="
            + requests.utils.quote(query)
        )

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/140.0 Safari/537.36"
            )
        }

        response = requests.get(
            search_url,
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()

        html = response.text

        video_ids = re.findall(
            r'"videoId":"([a-zA-Z0-9_-]{11})"',
            html,
        )

        unique_video_ids = []

        for video_id in video_ids:
            if video_id not in unique_video_ids:
                unique_video_ids.append(video_id)

        if not unique_video_ids:
            return {
                "success": False,
                "error": "No YouTube video found.",
            }

        video_id = unique_video_ids[0]

        video_url = (
            "https://www.youtube.com/watch?v="
            + video_id
        )

        # Explicit browser দিলে সেটাই ব্যবহার হবে।
        # Browser না দিলে browser.py-এর default browser ব্যবহার হবে।
        if browser:
            result = open_url(
                video_url,
                browser=browser,
            )
        else:
            result = open_url(video_url)

        if not result.get("success"):
            return result

        used_browser = result.get(
            "browser",
            browser or "default browser",
        )

        return {
            "success": True,
            "query": query,
            "video_id": video_id,
            "url": video_url,
            "browser": used_browser,
            "message": (
                f"Opened the first YouTube video "
                f"for '{query}' in {used_browser}."
            ),
        }

    except requests.RequestException as e:
        return {
            "success": False,
            "error": f"YouTube request failed: {str(e)}",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
