import json
import html
import re
import requests
from urllib.parse import quote_plus


# =========================================================
# YOUTUBE RESEARCH
# =========================================================

def youtube_research(
    query: str,
    limit: int = 5,
):
    """
    Search YouTube and return actual video information.

    This function fetches YouTube search results directly
    and extracts structured video information.
    """

    try:

        query = (query or "").strip()

        if not query:
            return {
                "success": False,
                "error": "YouTube search query is empty.",
            }

        # -------------------------------------------------
        # Normalize limit
        # -------------------------------------------------

        try:
            limit = int(limit)
        except (TypeError, ValueError):
            limit = 5

        limit = max(1, min(limit, 10))

        # -------------------------------------------------
        # Build YouTube search URL
        # -------------------------------------------------

        search_url = (
            "https://www.youtube.com/results"
            "?search_query="
            + quote_plus(query)
        )

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/140.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }

        # -------------------------------------------------
        # Request YouTube
        # -------------------------------------------------

        response = requests.get(
            search_url,
            headers=headers,
            timeout=15,
        )

        response.raise_for_status()

        page = response.text

        # -------------------------------------------------
        # Extract ytInitialData
        # -------------------------------------------------

        match = re.search(
            r"var ytInitialData = (.*?);</script>",
            page,
            re.DOTALL,
        )

        if not match:

            # Newer YouTube pages may use:
            # ytInitialData = {...};

            match = re.search(
                r"ytInitialData\s*=\s*(\{.*?\});",
                page,
                re.DOTALL,
            )

        if not match:

            return {
                "success": False,
                "query": query,
                "error": (
                    "YouTube returned a page, but "
                    "search data could not be extracted."
                ),
            }

        raw_data = match.group(1)

        # -------------------------------------------------
        # Parse JSON
        # -------------------------------------------------

        try:

            data = json.loads(raw_data)

        except json.JSONDecodeError:

            return {
                "success": False,
                "query": query,
                "error": (
                    "YouTube search data was found, "
                    "but it could not be parsed."
                ),
            }

        # -------------------------------------------------
        # Find videoRenderer objects recursively
        # -------------------------------------------------

        video_renderers = []

        def walk(value):

            if len(video_renderers) >= limit:
                return

            if isinstance(value, dict):

                if "videoRenderer" in value:

                    renderer = value["videoRenderer"]

                    if isinstance(renderer, dict):
                        video_renderers.append(renderer)

                for child in value.values():

                    if len(video_renderers) >= limit:
                        break

                    walk(child)

            elif isinstance(value, list):

                for child in value:

                    if len(video_renderers) >= limit:
                        break

                    walk(child)

        walk(data)

        # -------------------------------------------------
        # Extract results
        # -------------------------------------------------

        results = []
        seen_ids = set()

        for renderer in video_renderers:

            video_id = renderer.get("videoId")

            if not video_id:
                continue

            if video_id in seen_ids:
                continue

            seen_ids.add(video_id)

            # ---------------------------------------------
            # Title
            # ---------------------------------------------

            title = "Unknown title"

            title_data = renderer.get("title", {})

            if isinstance(title_data, dict):

                runs = title_data.get("runs")

                if runs and isinstance(runs, list):

                    title_parts = []

                    for run in runs:

                        if isinstance(run, dict):

                            text = run.get("text")

                            if text:
                                title_parts.append(text)

                    if title_parts:
                        title = "".join(title_parts)

                elif title_data.get("simpleText"):

                    title = title_data["simpleText"]

            # ---------------------------------------------
            # Channel
            # ---------------------------------------------

            channel = "Unknown channel"

            owner_text = renderer.get(
                "ownerText",
                {},
            )

            if isinstance(owner_text, dict):

                runs = owner_text.get("runs")

                if runs and isinstance(runs, list):

                    channel_parts = []

                    for run in runs:

                        if isinstance(run, dict):

                            text = run.get("text")

                            if text:
                                channel_parts.append(text)

                    if channel_parts:
                        channel = "".join(channel_parts)

            # ---------------------------------------------
            # Published time
            # ---------------------------------------------

            published = "Unknown"

            published_data = renderer.get(
                "publishedTimeText",
                {},
            )

            if isinstance(published_data, dict):

                published = (
                    published_data.get(
                        "simpleText"
                    )
                    or "Unknown"
                )

            # ---------------------------------------------
            # Duration
            # ---------------------------------------------

            duration = "Unknown"

            duration_data = renderer.get(
                "lengthText",
                {},
            )

            if isinstance(duration_data, dict):

                duration = (
                    duration_data.get(
                        "simpleText"
                    )
                    or "Unknown"
                )

            # ---------------------------------------------
            # Views
            # ---------------------------------------------

            views = "Unknown"

            views_data = renderer.get(
                "viewCountText",
                {},
            )

            if isinstance(views_data, dict):

                views = (
                    views_data.get(
                        "simpleText"
                    )
                    or "Unknown"
                )

            # ---------------------------------------------
            # Description
            # ---------------------------------------------

            description = ""

            description_data = renderer.get(
                "detailedMetadataSnippets",
                [],
            )

            if isinstance(
                description_data,
                list,
            ):

                description_parts = []

                for item in description_data:

                    if not isinstance(item, dict):
                        continue

                    snippet_text = item.get(
                        "snippetText",
                        {},
                    )

                    if not isinstance(
                        snippet_text,
                        dict,
                    ):
                        continue

                    runs = snippet_text.get(
                        "runs",
                        [],
                    )

                    for run in runs:

                        if isinstance(run, dict):

                            text = run.get("text")

                            if text:
                                description_parts.append(
                                    text
                                )

                description = "".join(
                    description_parts
                )

            # ---------------------------------------------
            # URL
            # ---------------------------------------------

            video_url = (
                "https://www.youtube.com/watch?v="
                + video_id
            )

            # ---------------------------------------------
            # Clean text
            # ---------------------------------------------

            title = html.unescape(
                str(title)
            ).strip()

            channel = html.unescape(
                str(channel)
            ).strip()

            published = html.unescape(
                str(published)
            ).strip()

            duration = html.unescape(
                str(duration)
            ).strip()

            views = html.unescape(
                str(views)
            ).strip()

            description = html.unescape(
                str(description)
            ).strip()

            # ---------------------------------------------
            # Add result
            # ---------------------------------------------

            results.append(
                {
                    "rank": len(results) + 1,
                    "title": title,
                    "channel": channel,
                    "published": published,
                    "duration": duration,
                    "views": views,
                    "description": description,
                    "video_id": video_id,
                    "url": video_url,
                }
            )

            if len(results) >= limit:
                break

        # -------------------------------------------------
        # No results
        # -------------------------------------------------

        if not results:

            return {
                "success": False,
                "query": query,
                "error": (
                    "YouTube search completed, "
                    "but no video results were found."
                ),
            }

        # -------------------------------------------------
        # Return structured research result
        # -------------------------------------------------

        return {
            "success": True,
            "query": query,
            "result_count": len(results),
            "results": results,
        }

    except requests.RequestException as e:

        return {
            "success": False,
            "query": query,
            "error": (
                f"YouTube request failed: {str(e)}"
            ),
        }

    except Exception as e:

        return {
            "success": False,
            "query": query,
            "error": str(e),
        }