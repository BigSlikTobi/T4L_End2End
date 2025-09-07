import asyncio
import click

from ...services.pipeline import Pipeline


@click.command()
@click.option("--config", "config_path", required=True, help="Path to feeds.yaml config")
def pipeline(config_path: str) -> None:
    """Run the full pipeline from a config file."""

    async def run() -> None:
        p = Pipeline()
        stats = await p.run_from_config(config_path)
        click.echo(stats)

    asyncio.run(run())


__all__ = ["pipeline"]
