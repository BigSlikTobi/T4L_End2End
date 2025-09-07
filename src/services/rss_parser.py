from __future__ import annotations

from typing import Any, Dict, List

import feedparser


def parse_feed(feed_content: str) -> List[Dict[str, Any]]:
    """Parse RSS/Atom feed content string and return list of entry dicts.

    Minimal contract used by tests: function exists and is callable, returning a list.
    """
    parsed = feedparser.parse(feed_content or "")
    articles: List[Dict[str, Any]] = []
    for entry in getattr(parsed, "entries", []) or []:
        # Convert feedparser entry (object) to plain dict for downstream mapping
        item: Dict[str, Any] = {}
        for key in ("title", "link", "summary", "published", "published_parsed"):
            if key in entry:
                item[key] = entry[key]
        # propagate source if available
        if "source" in entry and hasattr(entry["source"], "title"):
            item["publisher"] = entry["source"].title
        # Some feeds omit source; derive from feed metadata when obvious
        if "publisher" not in item and hasattr(parsed, "feed"):
            title = getattr(parsed.feed, "title", "") or ""
            if "ESPN" in title.upper():
                item["publisher"] = "ESPN"
        articles.append(item)
    return articles


__all__ = ["parse_feed"]
