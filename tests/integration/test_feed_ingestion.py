import asyncio
from unittest.mock import patch, Mock

from src.services.feed_ingester import FeedIngester


SAMPLE_RSS = """
<rss version="2.0">
<channel>
  <title>Sample NFL Feed</title>
  <item>
    <title>Patriots sign veteran QB</title>
    <link>https://example.com/nfl/patriots-sign-qb</link>
    <description>Move to bolster depth</description>
    <pubDate>Sun, 07 Sep 2025 12:00:00 GMT</pubDate>
  </item>
  <item>
    <title>NBA news not relevant</title>
    <link>https://example.com/nba/news</link>
    <description>Basketball</description>
    <pubDate>Sun, 07 Sep 2025 13:00:00 GMT</pubDate>
  </item>
</channel>
</rss>
"""


async def _run_ingest(url: str):
    fi = FeedIngester()
    feed = await fi.fetch_feed(url)
    raw = await fi.extract_articles(feed)
    norm = [fi.standardize_article(r) for r in raw]
    return norm


def test_feed_ingestion_and_standardization():
    with patch("requests.get") as pget:
        resp = Mock()
        resp.status_code = 200
        resp.text = SAMPLE_RSS
        resp.headers = {"Content-Type": "application/rss+xml"}
        pget.return_value = resp

        url = "https://example.com/rss"
        articles = asyncio.run(_run_ingest(url))

    assert len(articles) == 2
    assert {"url", "title", "publisher", "publication_date", "content_summary"}.issubset(
        set(articles[0].keys())
    )
