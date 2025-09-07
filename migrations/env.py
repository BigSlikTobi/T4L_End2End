from __future__ import annotations

import ipaddress
import os
import socket
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine.url import make_url

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


def _valid_db_url(url: str | None) -> bool:
    if not url:
        return False
    # Quick guard against placeholder values often used in examples
    placeholders = ("HOST", "PORT", "USER", "PASSWORD", "DB", "<", ">")
    if any(tok in url for tok in placeholders):
        return False


def _prefer_ipv4_url(url: str) -> str:
    """Rewrite Postgres URL host to IPv4 address if DNS resolves to IPv6 first.

    GitHub runners often cannot reach IPv6. Resolve host to AF_INET and rebuild URL.
    """
    try:
        u = make_url(url)
        if not u.drivername.startswith("postgresql"):
            return url
        host = u.host
        if not host:
            return url
        try:
            ipaddress.ip_address(host)
            return url  # already an IP literal
        except ValueError:
            pass
        port = u.port or 5432
        infos = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
        if not infos:
            return url
        ipv4 = infos[0][4][0]
        u2 = u.set(host=ipv4)
        return str(u2)
    except Exception:
        return url
    try:
        make_url(url)  # parse to validate
        return True
    except Exception:
        return False


def run_migrations_offline() -> None:
    env_url = os.getenv("DATABASE_URL")
    url = env_url if _valid_db_url(env_url) else config.get_main_option("sqlalchemy.url")
    url = _prefer_ipv4_url(url)
    if env_url and not _valid_db_url(env_url):
        print("[alembic-env] Ignoring invalid DATABASE_URL; falling back to default sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    section = config.get_section(config.config_ini_section) or {}
    # Override URL from env if provided and valid; otherwise keep default
    env_url = os.getenv("DATABASE_URL")
    if env_url and _valid_db_url(env_url):
        section["sqlalchemy.url"] = _prefer_ipv4_url(env_url)
    elif env_url and not _valid_db_url(env_url):
        print("[alembic-env] Ignoring invalid DATABASE_URL; using default from alembic.ini")

    try:
        connectable = engine_from_config(
            section,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
    except Exception as exc:  # final fallback to default config
        print(f"[alembic-env] Failed to create engine from env URL ({exc}); retrying with default")
        fallback = config.get_section(config.config_ini_section) or {}
        connectable = engine_from_config(
            fallback,
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
