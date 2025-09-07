"""create processing_log table

Revision ID: 003_processing_log
Revises: 002_feeds
Create Date: 2025-09-07
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "003_processing_log"
down_revision = "002_feeds"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "processing_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("level", sa.String(length=20), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("article_url", sa.String(length=1000), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("processing_log")
