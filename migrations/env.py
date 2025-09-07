from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add src to sys.path so we can import project packages like `models`, `database`, etc.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Wire SQLAlchemy metadata for autogenerate and explicit migrations
from models.database import Base  # type: ignore

# Ensure all ORM models that inherit from Base are imported so they register with metadata
try:
    from database.repositories.log_repo import ProcessingLogORM  # noqa: F401
    from database.repositories.watermark_repo import SourceWatermarkORM  # noqa: F401
    from models.database import ArticleORM, FeedORM  # noqa: F401
except Exception:
    # During certain operations, these imports may fail; metadata for Base is still valid
    pass

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
