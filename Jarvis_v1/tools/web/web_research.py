import requests

from config import TAVILY_API_KEY


# =========================================================
# WEB RESEARCH
# =========================================================

def web_research(
    query: str,
    max_results: int = 5,
    time_range: str = None,
):
    """
    Search the live web and return structured research results.

    This tool is designed for natural-language research requests,
    latest news, current information, comparisons, and fact finding.
    """

    try:

        query = (query or "").strip()

        if not query:

            return {
                "success": False,
                "error": "Research query cannot be empty.",
            }

        if not TAVILY_API_KEY:

            return {
                "success": False,
                "error": (
                    "TAVILY_API_KEY is missing from .env."
                ),
            }

        # -------------------------------------------------
        # LIMIT RESULTS
        # -------------------------------------------------

        try:
            max_results = int(max_results)
        except (TypeError, ValueError):
            max_results = 5

        max_results = max(
            1,
            min(max_results, 10),
        )

        # -------------------------------------------------
        # REQUEST DATA
        # -------------------------------------------------

        payload = {
            "query": query,
            "topic": "general",
            "search_depth": "basic",
            "max_results": max_results,
            "include_answer": False,
            "include_raw_content": False,
        }

        if time_range in {
            "day",
            "week",
            "month",
            "year",
        }:

            payload["time_range"] = time_range

        # -------------------------------------------------
        # API REQUEST
        # -------------------------------------------------

        response = requests.post(
            "https://api.tavily.com/search",
            headers={
                "Authorization": (
                    f"Bearer {TAVILY_API_KEY}"
                ),
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=20,
        )

        response.raise_for_status()

        data = response.json()

        # -------------------------------------------------
        # RESULTS
        # -------------------------------------------------

        raw_results = data.get(
            "results",
            [],
        )

        results = []

        for index, item in enumerate(
            raw_results,
            start=1,
        ):

            if not isinstance(
                item,
                dict,
            ):
                continue

            results.append(
                {
                    "rank": index,
                    "title": item.get(
                        "title",
                        "",
                    ),
                    "url": item.get(
                        "url",
                        "",
                    ),
                    "content": item.get(
                        "content",
                        "",
                    ),
                    "score": item.get(
                        "score",
                    ),
                }
            )

        # -------------------------------------------------
        # NO RESULTS
        # -------------------------------------------------

        if not results:

            return {
                "success": False,
                "query": query,
                "error": (
                    "Web search completed, "
                    "but no results were found."
                ),
            }

        # -------------------------------------------------
        # SUCCESS
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
                f"Web research request failed: {str(e)}"
            ),
        }

    except Exception as e:

        return {
            "success": False,
            "query": query,
            "error": str(e),
        }