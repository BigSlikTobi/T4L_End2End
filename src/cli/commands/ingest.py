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
            try:
                xml = fetch_sitemap(url)
                items = parse_sitemap(xml)
                click.echo(f"Parsed {len(items)} sitemap URLs from {url}")
            except Exception as e:  # noqa: BLE001 (show helpful hint)
                hint = (
                    "For NFL.com, a working sitemap is the fast-changing feed: "
                    "https://www.nfl.com/sitemap-fast-changing.xml\n"
                    "Or discover sitemaps via the index: https://www.nfl.com/sitemap-index.xml"
                )
                raise click.ClickException(f"Failed to fetch/parse sitemap: {e}\n{hint}")

    asyncio.run(run())


__all__ = ["ingest"]
