"""
005 Indexes and performance notes

This placeholder migration documents recommended indexes for Postgres. For SQLite
dev/testing, table creation is auto-managed and indexes are minimal.

In a production Postgres/Supabase environment, consider adding indexes:
  - CREATE INDEX IF NOT EXISTS idx_articles_publication_date ON articles (publication_date DESC);
  - CREATE INDEX IF NOT EXISTS idx_processing_log_created_at ON processing_log (created_at DESC);
"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "005_indexes_and_performance_notes"
down_revision = None  # Ensure manual ordering when integrating with existing chain
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name.startswith("postgres"):
        op.execute(
            "CREATE INDEX IF NOT EXISTS idx_articles_publication_date ON articles (publication_date DESC)"
        )
        op.execute(
            "CREATE INDEX IF NOT EXISTS idx_processing_log_created_at ON processing_log (created_at DESC)"
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name.startswith("postgres"):
        op.execute("DROP INDEX IF EXISTS idx_articles_publication_date")
        op.execute("DROP INDEX IF EXISTS idx_processing_log_created_at")
