"""create articles table

Revision ID: 001_articles
Revises:
Create Date: 2025-09-07
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "001_articles"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("publisher", sa.String(length=256), nullable=False),
        sa.Column("publication_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("content_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("url", name="uq_articles_url"),
    )


def downgrade() -> None:
    op.drop_table("articles")
