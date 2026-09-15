import html
import re
import requests
from urllib.parse import quote_plus, urlparse, parse_qs


def clean_text(value):
    if not value:
        return ""

    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def extract_google_url(href):
    if not href:
        return None

    href = html.unescape(href)

    # Google redirect URL
    if href.startswith("/url?"):
        try:
            parsed = urlparse(href)
            params = parse_qs(parsed.query)

            real_url = params.get("q", [None])[0]

            if real_url:
                return real_url

        except Exception:
            return None

    # Direct external URL
    if href.startswith("https://"):
        return href

    if href.startswith("http://"):
        return href

    return None


def google_research(query: str, limit: int = 5):

    try:

        query = (query or "").strip()

        if not query:
            return {
                "success": False,
                "error": "Google search query is empty.",
            }

        # -------------------------------------------------
        # LIMIT
        # -------------------------------------------------

        try:
            limit = int(limit)
        except (TypeError, ValueError):
            limit = 5

        limit = max(1, min(limit, 10))

        # -------------------------------------------------
        # GOOGLE URL
        # -------------------------------------------------

        search_url = (
            "https://www.google.com/search"
            "?q="
            + quote_plus(query)
            + "&num="
            + str(limit)
            + "&hl=en"
        )

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/140.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,"
                "application/xhtml+xml,"
                "application/xml;q=0.9,"
                "image/avif,"
                "image/webp,"
                "*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
        }

        # -------------------------------------------------
        # REQUEST
        # -------------------------------------------------

        response = requests.get(
            search_url,
            headers=headers,
            timeout=20,
            allow_redirects=True,
        )

        response.raise_for_status()

        page = response.text

        with open(
            "google_debug.html",
            "w",
            encoding="utf-8",
        ) as f:
            f.write(page)

        print("📝 Saved Google response to google_debug.html")

        print(
            f"🔎 Google response: "
            f"{response.status_code} | "
            f"{len(page)} bytes"
        )

        # -------------------------------------------------
        # DEBUG
        # -------------------------------------------------

        print(
            f"🔎 Google response: "
            f"{response.status_code} | "
            f"{len(page)} bytes"
        )

        # -------------------------------------------------
        # RESULT CONTAINER PATTERNS
        # -------------------------------------------------

        containers = []

        patterns = [

            # Modern Google result blocks
            r'<div[^>]+class="[^"]*\bMjjYud\b[^"]*"[^>]*>'
            r'.*?'
            r'(?=<div[^>]+class="[^"]*\bMjjYud\b|$)',

            # Older result blocks
            r'<div[^>]+class="[^"]*\btF2Cxc\b[^"]*"[^>]*>'
            r'.*?'
            r'(?=<div[^>]+class="[^"]*\btF2Cxc\b|$)',

            # Generic block containing H3
            r'<div[^>]*>'
            r'.*?<h3[^>]*>.*?</h3>'
            r'.*?</div>',
        ]

        for pattern in patterns:

            matches = re.findall(
                pattern,
                page,
                re.DOTALL | re.IGNORECASE,
            )

            if matches:

                containers.extend(matches)

                if len(containers) >= limit:
                    break

        # -------------------------------------------------
        # PARSE RESULTS
        # -------------------------------------------------

        results = []
        seen_urls = set()

        for block in containers:

            if len(results) >= limit:
                break

            # ---------------------------------------------
            # TITLE
            # ---------------------------------------------

            title_match = re.search(
                r"<h3[^>]*>(.*?)</h3>",
                block,
                re.DOTALL | re.IGNORECASE,
            )

            if not title_match:
                continue

            title = clean_text(
                title_match.group(1)
            )

            if not title:
                continue

            # ---------------------------------------------
            # LINKS
            # ---------------------------------------------

            links = re.findall(
                r'<a[^>]+href=["\']([^"\']+)["\']',
                block,
                re.DOTALL | re.IGNORECASE,
            )

            url = None

            for href in links:

                candidate = extract_google_url(
                    href
                )

                if not candidate:
                    continue

                domain = urlparse(
                    candidate
                ).netloc.lower()

                # Ignore Google internal URLs
                if (
                    "google." in domain
                    or "googleusercontent." in domain
                ):
                    continue

                url = candidate
                break

            if not url:
                continue

            if url in seen_urls:
                continue

            seen_urls.add(url)

            # ---------------------------------------------
            # SNIPPET
            # ---------------------------------------------

            snippet = ""

            snippet_patterns = [

                r'class="[^"]*VwiC3b[^"]*"[^>]*>'
                r'(.*?)'
                r'</div>',

                r'class="[^"]*yXK7lf[^"]*"[^>]*>'
                r'(.*?)'
                r'</div>',

                r'class="[^"]*aCOpRe[^"]*"[^>]*>'
                r'(.*?)'
                r'</span>',
            ]

            for snippet_pattern in snippet_patterns:

                snippet_match = re.search(
                    snippet_pattern,
                    block,
                    re.DOTALL | re.IGNORECASE,
                )

                if snippet_match:

                    snippet = clean_text(
                        snippet_match.group(1)
                    )

                    if snippet:
                        break

            # ---------------------------------------------
            # DOMAIN
            # ---------------------------------------------

            try:

                domain = urlparse(
                    url
                ).netloc

                if domain.startswith("www."):
                    domain = domain[4:]

            except Exception:

                domain = ""

            # ---------------------------------------------
            # RESULT
            # ---------------------------------------------

            results.append(
                {
                    "rank": len(results) + 1,
                    "title": title,
                    "url": url,
                    "domain": domain,
                    "snippet": snippet,
                }
            )

        # -------------------------------------------------
        # FALLBACK:
        # Scan ALL H3 tags and nearby links
        # -------------------------------------------------

        if not results:

            print(
                "⚠️ Google primary parser found "
                "no results. Trying fallback parser..."
            )

            h3_matches = list(
                re.finditer(
                    r"<h3[^>]*>(.*?)</h3>",
                    page,
                    re.DOTALL | re.IGNORECASE,
                )
            )

            for match in h3_matches:

                if len(results) >= limit:
                    break

                title = clean_text(
                    match.group(1)
                )

                if not title:
                    continue

                # Search around H3
                start = max(
                    0,
                    match.start() - 3000,
                )

                end = min(
                    len(page),
                    match.end() + 5000,
                )

                nearby = page[
                    start:end
                ]

                links = re.findall(
                    r'<a[^>]+href=["\']([^"\']+)["\']',
                    nearby,
                    re.DOTALL | re.IGNORECASE,
                )

                url = None

                for href in links:

                    candidate = extract_google_url(
                        href
                    )

                    if not candidate:
                        continue

                    domain = urlparse(
                        candidate
                    ).netloc.lower()

                    if (
                        "google." in domain
                        or "googleusercontent." in domain
                    ):
                        continue

                    url = candidate
                    break

                if not url:
                    continue

                if url in seen_urls:
                    continue

                seen_urls.add(url)

                try:

                    domain = urlparse(
                        url
                    ).netloc

                    if domain.startswith("www."):
                        domain = domain[4:]

                except Exception:

                    domain = ""

                results.append(
                    {
                        "rank": len(results) + 1,
                        "title": title,
                        "url": url,
                        "domain": domain,
                        "snippet": "",
                    }
                )

        # -------------------------------------------------
        # FINAL RESULT
        # -------------------------------------------------

        if not results:

            return {
                "success": False,
                "query": query,
                "error": (
                    "Google search completed, "
                    "but no search results could be extracted."
                ),
            }

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
                f"Google request failed: {str(e)}"
            ),
        }

    except Exception as e:

        return {
            "success": False,
            "query": query,
            "error": str(e),
        }