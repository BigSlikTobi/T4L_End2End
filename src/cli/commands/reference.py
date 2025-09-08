from __future__ import annotations

import click

from database.connection import get_sessionmaker
from services.nfl_reference_loader import load_players, load_teams


@click.group(name="ref")
def reference_group() -> None:
    """Reference data commands (teams, players)."""


@reference_group.command(name="load-teams")
def cmd_load_teams() -> None:
    sm = get_sessionmaker()
    with sm() as session:
        n = load_teams(session)
        click.echo(f"Loaded/updated {n} teams")


@reference_group.command(name="load-players")
@click.option("--season", type=int, default=None)
def cmd_load_players(season: int | None) -> None:
    sm = get_sessionmaker()
    with sm() as session:
        n = load_players(session, season=season)
        click.echo(f"Loaded/updated {n} players")


__all__ = ["reference_group"]
