from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class TeamORM(Base):
    __tablename__ = "teams"
    __table_args__ = (
        UniqueConstraint("team_id", name="uq_teams_team_id"),
        UniqueConstraint("abbreviation", name="uq_teams_abbreviation"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    team_id: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    abbreviation: Mapped[str] = mapped_column(String(8), nullable=False)
    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    conference: Mapped[str | None] = mapped_column(String(32), nullable=True)
    division: Mapped[str | None] = mapped_column(String(32), nullable=True)


class PlayerORM(Base):
    __tablename__ = "players"
    __table_args__ = (UniqueConstraint("player_id", name="uq_players_player_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[str] = mapped_column(String(64), nullable=False)
    full_name: Mapped[str] = mapped_column(String(256), nullable=False)
    position: Mapped[str | None] = mapped_column(String(16), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)


class PlayerTeamHistoryORM(Base):
    __tablename__ = "player_team_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False
    )
    team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)


__all__ = ["TeamORM", "PlayerORM", "PlayerTeamHistoryORM"]
