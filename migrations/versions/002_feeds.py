"""create feeds table

Revision ID: 002_feeds
Revises: 001_articles
Create Date: 2025-09-07
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "002_feeds"
down_revision = "001_articles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "feeds",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=True),
        sa.Column("publisher", sa.String(length=256), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.UniqueConstraint("url", name="uq_feeds_url"),
    )


def downgrade() -> None:
    op.drop_table("feeds")
