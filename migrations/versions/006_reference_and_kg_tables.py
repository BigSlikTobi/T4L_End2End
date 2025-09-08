"""create reference and knowledge graph tables

Revision ID: 006_reference_and_kg_tables
Revises: 005_indexes_and_performance_notes
Create Date: 2025-09-08
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "006_reference_and_kg_tables"
down_revision = "005_indexes_and_performance_notes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Reference tables
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("team_id", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("abbreviation", sa.String(length=8), nullable=False),
        sa.Column("city", sa.String(length=128), nullable=True),
        sa.Column("conference", sa.String(length=32), nullable=True),
        sa.Column("division", sa.String(length=32), nullable=True),
        sa.UniqueConstraint("team_id", name="uq_teams_team_id"),
        sa.UniqueConstraint("abbreviation", name="uq_teams_abbreviation"),
    )

    op.create_table(
        "players",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("player_id", sa.String(length=64), nullable=False),
        sa.Column("full_name", sa.String(length=256), nullable=False),
        sa.Column("position", sa.String(length=16), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.UniqueConstraint("player_id", name="uq_players_player_id"),
    )

    op.create_table(
        "player_team_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "player_id",
            sa.Integer(),
            sa.ForeignKey("players.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "team_id", sa.Integer(), sa.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Index("ix_pth_player_team", "player_id", "team_id"),
    )

    # Knowledge Graph tables
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("signature", sa.String(length=256), nullable=False),
        sa.Column("event_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=True),
        sa.Column("title", sa.String(length=512), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("signature", name="uq_events_signature"),
    )

    op.create_table(
        "entities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("entity_type", sa.String(length=32), nullable=False),
        sa.Column("external_id", sa.String(length=64), nullable=True),
        sa.Column("display_name", sa.String(length=256), nullable=False),
        sa.Index("ix_entities_type", "entity_type"),
    )

    op.create_table(
        "event_entities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "event_id", sa.Integer(), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "entity_id",
            sa.Integer(),
            sa.ForeignKey("entities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(length=32), nullable=True),
        sa.Index("ix_event_entities_event", "event_id"),
        sa.Index("ix_event_entities_entity", "entity_id"),
        sa.UniqueConstraint("event_id", "entity_id", "role", name="uq_event_entity_role"),
    )

    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("publisher", sa.String(length=256), nullable=True),
        sa.Column("url", sa.String(length=1000), nullable=True),
    )

    op.create_table(
        "claims",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "event_id", sa.Integer(), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("claim_text", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Index("ix_claims_event", "event_id"),
    )

    op.create_table(
        "claim_sources",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "claim_id", sa.Integer(), sa.ForeignKey("claims.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "source_id",
            sa.Integer(),
            sa.ForeignKey("sources.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("url", sa.String(length=1000), nullable=True),
        sa.Column("citation", sa.Text(), nullable=True),
        sa.Index("ix_claim_sources_claim", "claim_id"),
    )

    op.create_table(
        "event_articles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "event_id", sa.Integer(), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("article_id", sa.Integer(), nullable=False),  # references articles.id in app DB
        sa.Column("relation", sa.String(length=32), nullable=True),
        sa.Index("ix_event_articles_event", "event_id"),
        sa.UniqueConstraint("event_id", "article_id", name="uq_event_article"),
    )


def downgrade() -> None:
    for table in [
        "event_articles",
        "claim_sources",
        "claims",
        "sources",
        "event_entities",
        "entities",
        "events",
        "player_team_history",
        "players",
        "teams",
    ]:
        op.drop_table(table)
