from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class SitemapURL:
    url: str


def current_utc_year_month() -> tuple[int, int]:
    now = datetime.now(timezone.utc)
    return now.year, now.month


def apply_dynamic_template(url: str) -> str:
    """Apply dynamic placeholders for NFL monthly sitemap: {YYYY}/{MM}.

    Example template: https://www.nfl.com/sitemaps/news/{YYYY}/{MM}/sitemap.xml
    """
    if "{YYYY}" in url or "{MM}" in url:
        y, m = current_utc_year_month()
        return url.replace("{YYYY}", f"{y:04d}").replace("{MM}", f"{m:02d}")
    return url


def fetch_sitemap(url: str, timeout: int = 20) -> str:
    real_url = apply_dynamic_template(url)
    resp = requests.get(real_url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def parse_sitemap(xml_text: str) -> List[Dict[str, Any]]:
    """Parse a sitemap XML into a list of URL dicts with optional lastmod.

    Returns a list of dicts: {"url": str, "lastmod": str | None}
    """
    soup = BeautifulSoup(xml_text or "", "xml")
    out: List[Dict[str, Any]] = []
    for url_tag in soup.find_all("url"):
        loc = url_tag.find("loc")
        lastmod = url_tag.find("lastmod")
        if not loc or not loc.text:
            continue
        out.append(
            {"url": loc.text.strip(), "lastmod": (lastmod.text.strip() if lastmod else None)}
        )
    return out


__all__ = [
    "SitemapURL",
    "current_utc_year_month",
    "apply_dynamic_template",
    "fetch_sitemap",
    "parse_sitemap",
]
