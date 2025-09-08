from __future__ import annotations

from typing import Iterable, List

from sqlalchemy.orm import Session

try:
    import nfl_data_py as nfl
except Exception:  # pragma: no cover - optional dependency in some envs
    nfl = None  # type: ignore

from models import PlayerORM, TeamORM


def _upsert_team(session: Session, team: dict) -> None:
    if not team.get("team_id"):
        return
    existing = session.query(TeamORM).filter_by(team_id=team["team_id"]).one_or_none()
    if existing:
        existing.name = team.get("name", existing.name)
        existing.abbreviation = team.get("abbreviation", existing.abbreviation)
        existing.city = team.get("city", existing.city)
        existing.conference = team.get("conference", existing.conference)
        existing.division = team.get("division", existing.division)
    else:
        session.add(
            TeamORM(
                team_id=team.get("team_id"),
                name=team.get("name") or team.get("full_name") or team.get("team_name") or "",
                abbreviation=team.get("abbreviation") or team.get("team_abbr") or "",
                city=team.get("city"),
                conference=team.get("conference"),
                division=team.get("division"),
            )
        )


def _upsert_player(session: Session, player: dict) -> None:
    pid = player.get("player_id") or player.get("gsis_id") or player.get("pfr_id")
    name = player.get("full_name") or player.get("player_name")
    if not pid or not name:
        return
    existing = session.query(PlayerORM).filter_by(player_id=str(pid)).one_or_none()
    if existing:
        existing.full_name = name
        existing.position = player.get("position") or existing.position
    else:
        session.add(PlayerORM(player_id=str(pid), full_name=name, position=player.get("position")))


def load_teams(session: Session) -> int:
    """Load NFL teams into reference table using nfl_data_py or fallback list."""
    teams: Iterable[dict]
    if nfl and hasattr(nfl, "import_team_desc"):
        # nfl.import_team_desc returns a DataFrame with columns like team_abbr, team_name, etc.
        df = nfl.import_team_desc()
        teams = [
            {
                "team_id": str(row.team_abbr),
                "name": str(row.team_name),
                "abbreviation": str(row.team_abbr),
                "city": str(row.team_city) if hasattr(row, "team_city") else None,
                "conference": str(row.team_conf) if hasattr(row, "team_conf") else None,
                "division": str(row.team_division) if hasattr(row, "team_division") else None,
            }
            for _, row in df.iterrows()
        ]
    else:
        # Minimal fallback for offline dev
        teams = [
            {
                "team_id": "KC",
                "name": "Kansas City Chiefs",
                "abbreviation": "KC",
                "city": "Kansas City",
                "conference": "AFC",
                "division": "West",
            }
        ]

    count = 0
    for t in teams:
        _upsert_team(session, t)
        count += 1
    session.commit()
    return count


def load_players(session: Session, season: int | None = None) -> int:
    players: List[dict] = []
    seasons = [season] if season else [2024]

    # Try multiple nfl_data_py sources
    try:
        if nfl is not None:
            df = None
            if hasattr(nfl, "import_rosters"):
                try:
                    df = nfl.import_rosters(seasons)
                except Exception:
                    df = None
            if df is None and hasattr(nfl, "import_players"):
                try:
                    df = nfl.import_players()
                except Exception:
                    df = None
            if df is None and hasattr(nfl, "import_seasonal_player_stats"):
                try:
                    df = nfl.import_seasonal_player_stats(seasons)
                except Exception:
                    df = None

            if df is not None and getattr(df, "empty", True) is False:
                # Normalize column names present in df
                cols = set(df.columns)
                pid_col = (
                    "player_id"
                    if "player_id" in cols
                    else "gsis_id" if "gsis_id" in cols else "pfr_id" if "pfr_id" in cols else None
                )
                name_col = (
                    "full_name"
                    if "full_name" in cols
                    else (
                        "player_display_name"
                        if "player_display_name" in cols
                        else (
                            "display_name"
                            if "display_name" in cols
                            else "player_name" if "player_name" in cols else None
                        )
                    )
                )
                pos_col = "position" if "position" in cols else None
                if pid_col and name_col:
                    for _, row in df.iterrows():
                        pid = (
                            str(getattr(row, pid_col))
                            if hasattr(row, pid_col)
                            else str(row[pid_col])
                        )
                        name = (
                            str(getattr(row, name_col))
                            if hasattr(row, name_col)
                            else str(row[name_col])
                        )
                        position = None
                        if pos_col:
                            position = (
                                str(getattr(row, pos_col))
                                if hasattr(row, pos_col)
                                else str(row[pos_col])
                            )
                        if pid and name:
                            players.append(
                                {"player_id": pid, "full_name": name, "position": position}
                            )
    except Exception:
        # Swallow and use fallback
        players = []

    # Fallback sample if none available (dev convenience)
    if not players:
        players = [
            {"player_id": "00-0031234", "full_name": "Patrick Mahomes", "position": "QB"},
            {"player_id": "00-0031235", "full_name": "Travis Kelce", "position": "TE"},
        ]
        # Print a helpful hint once per call
        print(
            "[ref] Loaded fallback sample players. Install extras to fetch real data: "
            "pip install .[nfl] (ensure pandas is available for your Python version)."
        )

    count = 0
    for p in players:
        _upsert_player(session, p)
        count += 1
        # Avoid huge dev imports on accidental large datasets
        if count % 1000 == 0:
            session.commit()
    session.commit()
    return count


__all__ = ["load_teams", "load_players"]
