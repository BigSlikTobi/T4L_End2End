"""NFL.com article content extractor."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup


class NFLArticleExtractor:
    """Extract full article content from NFL.com URLs."""

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "T4L-End2End/1.0 (+https://github.com/BigSlikTobi/T4L_End2End)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
            }
        )

    def is_recent(self, url: str, days_back: int = 7) -> bool:
        """Check if URL appears to be from recent articles based on URL pattern."""
        # NFL.com URLs often contain dates like /2025/09/07/
        date_pattern = r"/(\d{4})/(\d{1,2})/(\d{1,2})/"
        match = re.search(date_pattern, url)

        if match:
            try:
                year, month, day = map(int, match.groups())
                article_date = datetime(year, month, day, tzinfo=timezone.utc)
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
                return article_date >= cutoff_date
            except ValueError:
                pass

        # If no date in URL, assume it might be recent
        return True

    def extract_article_content(self, url: str) -> Optional[Dict[str, str]]:
        """Extract article content from NFL.com article URL."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract title - try multiple selectors
            title = None
            title_selectors = [
                'h1[data-testid="headline"]',
                "h1.headline",
                "h1",
                ".article-title",
                '[data-testid="headline"]',
            ]

            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break

            if not title:
                title = soup.title.get_text(strip=True) if soup.title else "NFL Article"

            # Extract content - try multiple selectors
            content = ""
            content_selectors = [
                '[data-testid="article-body"]',
                ".article-body",
                ".story-body",
                ".content-body",
                "article",
                ".article-content",
            ]

            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remove script, style, and nav elements
                    for unwanted in content_elem.find_all(
                        ["script", "style", "nav", "header", "footer", "aside"]
                    ):
                        unwanted.decompose()

                    # Get text content
                    paragraphs = content_elem.find_all(["p", "div"], recursive=True)
                    content_parts = []

                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if text and len(text) > 20:  # Filter out short snippets
                            content_parts.append(text)

                    content = "\n\n".join(content_parts[:10])  # Limit to first 10 paragraphs
                    break

            # Extract author
            author = None
            author_selectors = [
                '[data-testid="author"]',
                ".author",
                ".byline",
                '[data-module="BylineModule"]',
            ]

            for selector in author_selectors:
                author_elem = soup.select_one(selector)
                if author_elem:
                    author = author_elem.get_text(strip=True)
                    break

            # Extract publish date
            publish_date = None
            date_selectors = [
                '[data-testid="publish-date"]',
                ".publish-date",
                ".date",
                "time[datetime]",
            ]

            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    # Try datetime attribute first
                    datetime_attr = date_elem.get("datetime")
                    if datetime_attr:
                        publish_date = datetime_attr
                    else:
                        publish_date = date_elem.get_text(strip=True)
                    break

            # Clean title
            if title:
                title = re.sub(r"\s*\|\s*NFL\.com\s*$", "", title)
                title = title.strip()

            return {
                "title": title or "NFL Article",
                "content": content or "Content not extracted",
                "author": author,
                "publish_date": publish_date,
                "url": url,
            }

        except Exception as e:
            print(f"Failed to extract content from {url}: {e}")
            return None

    def process_sitemap_urls(
        self, sitemap_urls: List[Dict], max_articles: int = 50, days_back: int = 7
    ) -> List[Dict[str, str]]:
        """Process sitemap URLs and extract article content with intelligent filtering."""
        articles = []
        processed = 0

        print(f"Processing up to {max_articles} recent articles (last {days_back} days)...")

        for url_entry in sitemap_urls:
            if processed >= max_articles:
                break

            url = url_entry.get("url", "")
            if not url:
                continue

            # Filter by recency
            if not self.is_recent(url, days_back):
                continue

            # Extract article content
            article_data = self.extract_article_content(url)
            if article_data:
                # Add metadata from sitemap
                article_data["lastmod"] = url_entry.get("lastmod")
                article_data["source"] = "NFL.com"
                article_data["publisher"] = "NFL.com"

                articles.append(article_data)
                processed += 1

                if processed % 5 == 0:
                    print(f"Processed {processed}/{max_articles} articles...")

        print(f"Successfully extracted {len(articles)} articles from NFL.com")
        return articles


def extract_nfl_articles(
    sitemap_urls: List[Dict], max_articles: int = 50, days_back: int = 7
) -> List[Dict[str, str]]:
    """Convenience function to extract NFL articles."""
    extractor = NFLArticleExtractor()
    return extractor.process_sitemap_urls(sitemap_urls, max_articles, days_back)
