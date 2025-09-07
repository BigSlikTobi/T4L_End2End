import asyncio

import click

from ...services.feed_ingester import FeedIngester
from ...services.sitemap_parser import fetch_sitemap, parse_sitemap


@click.command()
@click.option("--url", "url", required=True, help="Feed URL (RSS or sitemap)")
@click.option("--type", "type_", type=click.Choice(["rss", "sitemap"]), required=True)
def ingest(url: str, type_: str) -> None:
    """Ingest a single feed URL and print counts."""

    async def run() -> None:
        fi = FeedIngester()
        if type_ == "rss":
            feed = await fi.fetch_feed(url)
            raw = await fi.extract_articles(feed)
            click.echo(f"Parsed {len(raw)} RSS entries from {url}")
        else:
            xml = fetch_sitemap(url)
            items = parse_sitemap(xml)
            click.echo(f"Parsed {len(items)} sitemap URLs from {url}")

    asyncio.run(run())


__all__ = ["ingest"]
