"""T4L Core Pipeline CLI entrypoints."""

import click

from .commands.filter import filter_cmd
from .commands.ingest import ingest
from .commands.pipeline import pipeline
from .commands.health import health_cmd


@click.group()
def cli() -> None:
    """T4L Core Pipeline CLI."""


def main() -> None:
    cli.add_command(ingest)
    cli.add_command(filter_cmd)
    cli.add_command(pipeline)
    cli.add_command(health_cmd)
    cli()


__all__ = ["cli", "main"]
