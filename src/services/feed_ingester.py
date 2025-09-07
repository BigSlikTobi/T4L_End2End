import asyncio
import os
from typing import Any, Dict, List

import requests

from . import rss_parser
from .logger import log_json


class FeedIngester:
    """Concrete Feed Ingester.

    Contract (per tests):
      - async fetch_feed(self, feed_url: str) -> Dict[str, Any]
      - async extract_articles(self, feed_data: Dict[str, Any]) -> List[Dict[str, Any]]
      - standardize_article(self, raw_article: Dict[str, Any]) -> Dict[str, Any]
    """

    async def fetch_feed(self, feed_url: str) -> Dict[str, Any]:
        def _get() -> Dict[str, Any]:
            headers = {
                "User-Agent": os.getenv(
                    "T4L_USER_AGENT",
                    "T4L-End2End/1.0 (+https://github.com/BigSlikTobi/T4L_End2End)",
                ),
                "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
            }
            resp = requests.get(feed_url, timeout=15, headers=headers)
            if resp.status_code != 200:
                try:
                    log_json(
                        "WARNING",
                        "feed_fetch_non_200",
                        url=feed_url,
                        status=resp.status_code,
                        content_type=resp.headers.get("Content-Type"),
                    )
                except Exception:
                    pass
            text = resp.text
            if not text and resp.content:
                try:
                    text = resp.content.decode(resp.encoding or "utf-8", errors="ignore")
                except Exception:
                    text = resp.text
            return {
                "url": feed_url,
                "status": resp.status_code,
                "content": text,
                "headers": dict(resp.headers),
            }

        return await asyncio.to_thread(_get)

    async def extract_articles(self, feed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        content = feed_data.get("content", "")
        try:
            return rss_parser.parse_feed(content)
        except Exception:
            # Keep contract simple; callers can handle/log specifics.
            return []

    def standardize_article(self, raw_article: Dict[str, Any]) -> Dict[str, Any]:
        """Map a raw RSS entry dict into a normalized article dict.

        Keys standardized: url, title, publisher, publication_date, content_summary.
        """
        url = raw_article.get("link") or raw_article.get("url") or ""
        title = raw_article.get("title") or ""
        publisher = raw_article.get("publisher") or raw_article.get("source") or ""
        publication_date = (
            raw_article.get("published")
            or raw_article.get("published_parsed")  # may be struct_time
            or raw_article.get("publication_date")
        )
        # Convert struct_time to ISO8601 if present
        if hasattr(publication_date, "tm_year"):
            try:
                import datetime as _dt

                publication_date = _dt.datetime(*publication_date[:6]).isoformat() + "Z"
            except Exception:
                publication_date = None

        content_summary = (
            raw_article.get("summary")
            or raw_article.get("description")
            or raw_article.get("content_summary")
        )

        return {
            "url": url,
            "title": title,
            "publisher": publisher,
            "publication_date": publication_date if publication_date is not None else None,
            "content_summary": content_summary,
        }


__all__ = ["FeedIngester"]
