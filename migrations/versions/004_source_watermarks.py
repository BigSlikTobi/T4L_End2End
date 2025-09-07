"""create source_watermarks table

Revision ID: 004_source_watermarks
Revises: 003_processing_log
Create Date: 2025-09-07
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "004_source_watermarks"
down_revision = "003_processing_log"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "source_watermarks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source_key", sa.String(length=255), nullable=False),
        sa.Column("last_publication_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_url", sa.String(length=1000), nullable=True),
        sa.UniqueConstraint("source_key", name="uq_source_watermarks_source_key"),
    )


def downgrade() -> None:
    op.drop_table("source_watermarks")
