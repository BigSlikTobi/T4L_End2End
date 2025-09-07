"""CLI package placeholder. Commands will be added in later tasks (T027-T030)."""


def main() -> None:
    """Temporary CLI entry point for packaging sanity check."""
    print("t4l CLI is installed.")
import click


@click.group()
def cli() -> None:
    """T4L Core Pipeline CLI"""


def main() -> None:
    from .commands.ingest import ingest
    from .commands.filter import filter_cmd
    from .commands.pipeline import pipeline

    cli.add_command(ingest)
    cli.add_command(filter_cmd)
    cli.add_command(pipeline)
    cli()


__all__ = ["cli", "main"]
