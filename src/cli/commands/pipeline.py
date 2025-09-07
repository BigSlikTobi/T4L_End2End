import asyncio

import click

from ...services.pipeline import Pipeline


@click.command()
@click.option("--config", "config_path", required=True, help="Path to feeds.yaml config")
@click.option(
    "--only-publisher",
    "only_publishers",
    multiple=True,
    help="Only process sources with this publisher (repeatable)",
)
@click.option(
    "--only-source",
    "only_sources",
    multiple=True,
    help="Only process sources with this source name (repeatable)",
)
def pipeline(
    config_path: str, only_publishers: tuple[str, ...], only_sources: tuple[str, ...]
) -> None:
    """Run the full pipeline from a config file."""

    async def run() -> None:
        p = Pipeline()
        stats = await p.run_from_config(
            config_path,
            only_publishers=list(only_publishers) or None,
            only_sources=list(only_sources) or None,
        )
        click.echo(stats)

    asyncio.run(run())


__all__ = ["pipeline"]
