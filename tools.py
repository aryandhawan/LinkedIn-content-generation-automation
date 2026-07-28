"""
The agent's two callable tools: Hacker News and Reddit fetchers.
Both fail gracefully — on any error, they return an empty list instead of
raising, so the agent's reasoning loop can continue with whatever source
did succeed, rather than crashing the whole run.
"""

import requests
import xml.etree.ElementTree as ET


def fetch_hackernews(limit: int = 10) -> list[dict]:
    """
    Fetches current Hacker News front-page posts via Algolia's HN Search API.
    Returns a list of dicts: {title, url, points, num_comments, source}
    On failure, returns an empty list.
    """
    try:
        response = requests.get(
            "https://hn.algolia.com/api/v1/search",
            params={"tags": "front_page"},
            timeout=10
        )
        response.raise_for_status()  # raises HTTPError on any non-200 status
        data = response.json()

        results = []
        for hit in data.get("hits", [])[:limit]:
            results.append({
                "title": hit.get("title"),
                "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                "points": hit.get("points"),
                "num_comments": hit.get("num_comments"),
                "source": "Hacker News"
            })
        return results

    except requests.exceptions.RequestException as e:
        # Covers HTTPError (from raise_for_status), timeouts, connection errors, etc.
        print(f"[tools] Hacker News fetch failed: {e}")
        return []


def fetch_reddit(subreddit: str = "artificial", limit: int = 10) -> list[dict]:
    """
    Fetches today's top posts from a subreddit via Reddit's public RSS feed.
    Returns a list of dicts: {title, url, source}
    On failure, returns an empty list.
    """
    try:
        rss_url = f"https://www.reddit.com/r/{subreddit}/top/.rss?t=day"
        headers = {"User-Agent": "LinkedInAgentBot/1.0 (personal project)"}

        response = requests.get(rss_url, headers=headers, timeout=10)
        response.raise_for_status()

        namespace = {"atom": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(response.content)

        results = []
        for entry in root.findall("atom:entry", namespace)[:limit]:
            title = entry.find("atom:title", namespace)
            link = entry.find("atom:link", namespace)
            results.append({
                "title": title.text if title is not None else None,
                "url": link.get("href") if link is not None else None,
                "source": f"Reddit (r/{subreddit})"
            })
        return results

    except requests.exceptions.RequestException as e:
        print(f"[tools] Reddit fetch failed: {e}")
        return []
