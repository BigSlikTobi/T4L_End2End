import asyncio
import click

from ...services.feed_ingester import FeedIngester
from ...services.relevance_filter import RelevanceFilter, FilterDecision
from ...services.rss_parser import parse_feed


@click.command()
@click.option("--rss", "rss_url", required=True, help="RSS feed URL")
def pipeline(rss_url: str) -> None:
    """Simple pipeline dry-run: fetch RSS, parse, filter, summarize counts."""

    async def run() -> None:
        fi = FeedIngester()
        feed = await fi.fetch_feed(rss_url)
        raw = await fi.extract_articles(feed)
        rf = RelevanceFilter()
        keep = 0
        for item in raw:
            art = fi.standardize_article(item)
            decision, _ = rf.filter_article(art)
            if decision is FilterDecision.KEEP:
                keep += 1
        click.echo({"total": len(raw), "keep": keep})

    asyncio.run(run())


__all__ = ["pipeline"]
