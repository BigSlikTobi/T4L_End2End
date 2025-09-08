"""T4L Core Pipeline CLI entrypoints."""

import click

from .commands.events import events_group
from .commands.filter import filter_cmd
from .commands.health import health_cmd
from .commands.ingest import ingest
from .commands.pipeline import pipeline
from .commands.reference import reference_group
from .commands.simple import simple_pipeline


@click.group()
def cli() -> None:
    """T4L Core Pipeline CLI."""


def main() -> None:
    cli.add_command(ingest)
    cli.add_command(filter_cmd)
    cli.add_command(pipeline)
    cli.add_command(simple_pipeline)
    cli.add_command(health_cmd)
    cli.add_command(events_group)
    cli.add_command(reference_group)
    cli()


__all__ = ["cli", "main"]
