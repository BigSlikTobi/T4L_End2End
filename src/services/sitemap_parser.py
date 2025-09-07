from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List
from urllib.parse import urljoin

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
    """Parse an NFL sitemap into a list of URL dicts with optional lastmod.

    Supports both XML urlset sitemaps and the HTML monthly articles sitemap.

    Returns a list of dicts: {"url": str, "lastmod": str | None}
    """
    # Try XML first
    soup_xml = BeautifulSoup(xml_text or "", "xml")
    out: List[Dict[str, Any]] = []
    for url_tag in soup_xml.find_all("url"):
        loc = url_tag.find("loc")
        lastmod = url_tag.find("lastmod")
        if not loc or not loc.text:
            continue
        out.append(
            {"url": loc.text.strip(), "lastmod": (lastmod.text.strip() if lastmod else None)}
        )
    if out:
        return out

    # Fallback: HTML monthly articles sitemap (e.g., /sitemap/html/articles/{YYYY}/{MM})
    return parse_html_article_sitemap(xml_text)


def parse_html_article_sitemap(html_text: str) -> List[Dict[str, Any]]:
    """Parse NFL HTML articles sitemap page and extract article URLs with dates if present.

    Heuristic parser: finds anchor tags in table rows; attempts to pair with YYYY-MM-DD
    in the same row.
    """
    soup = BeautifulSoup(html_text or "", "html.parser")
    results: List[Dict[str, Any]] = []
    seen: set[str] = set()

    # Prefer anchors inside table rows
    rows = soup.find_all("tr")
    date_re = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
    for tr in rows:
        a = tr.find("a", href=True)
        if not a:
            continue
        href = a.get("href", "").strip()
        if not href:
            continue
        url = urljoin("https://www.nfl.com", href)
        # Filter to news/articles paths to avoid non-content links
        if not ("/news/" in url or "/stories/" in url or "/videos/" in url):
            continue
        lastmod = None
        text = tr.get_text(" ", strip=True)
        m = date_re.search(text or "")
        if m:
            lastmod = m.group(0)
        if url not in seen:
            seen.add(url)
            results.append({"url": url, "lastmod": lastmod})

    # Fallback: any anchors on the page if table parse finds nothing
    if not results:
        for a in soup.find_all("a", href=True):
            href = a.get("href", "").strip()
            if not href:
                continue
            url = urljoin("https://www.nfl.com", href)
            if "/news/" in url and url not in seen:
                seen.add(url)
                results.append({"url": url, "lastmod": None})

    return results


__all__ = [
    "SitemapURL",
    "current_utc_year_month",
    "apply_dynamic_template",
    "fetch_sitemap",
    "parse_sitemap",
    "parse_html_article_sitemap",
]
