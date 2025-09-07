from __future__ import annotations

import ipaddress
import os
import socket

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL, make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

# Import ORM base for optional auto-creation in lightweight SQLite setups (tests)
from ..models.database import Base


def _valid_db_url(url: str | None) -> bool:
    if not url:
        return False
    placeholders = ("HOST", "PORT", "USER", "PASSWORD", "DB", "<", ">")
    if any(tok in url for tok in placeholders):
        return False
    try:
        make_url(url)
        return True
    except Exception:
        return False


def get_database_url() -> str:
    """Resolve database URL from env; defaults to local SQLite.

    Supports switching to Supabase/Postgres via DATABASE_URL, e.g.,
    DATABASE_URL=postgresql+psycopg://user:pass@host:5432/db
    """
    env_url = os.getenv("DATABASE_URL")
    url = env_url if _valid_db_url(env_url) else "sqlite:///./t4l.db"
    return _prefer_ipv4(url)


def _prefer_ipv4(url_str: str) -> str:
    """If URL points to Postgres, prefer IPv4 by resolving DNS to an A record.

    Some environments (e.g., GitHub runners) fail IPv6 connections. We rewrite the host
    to the first IPv4 address when the original host is a DNS name.
    """
    try:
        u: URL = make_url(url_str)
        if not u.drivername.startswith("postgresql"):
            return url_str
        host = u.host
        if not host:
            return url_str
        try:
            # If host is already an IP (v4 or v6), keep as-is
            ipaddress.ip_address(host)
            return url_str
        except ValueError:
            pass  # not an IP literal, resolve

        port = u.port or 5432
        infos = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
        if not infos:
            return url_str
        ipv4 = infos[0][4][0]
        # Rebuild URL with IPv4 address
        u2 = u.set(host=ipv4)
        return str(u2)
    except Exception:
        return url_str


def get_engine(echo: bool = False) -> Engine:
    url = get_database_url()
    pool_size = int(os.getenv("DB_POOL_SIZE", "5"))
    max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    pool_kwargs = {}
    # SQLite file DB ignores pool size; still pass reasonable defaults for other backends
    if not url.startswith("sqlite"):
        pool_kwargs.update(
            dict(pool_size=pool_size, max_overflow=max_overflow, pool_timeout=pool_timeout)
        )

    engine = create_engine(url, echo=echo, future=True, **pool_kwargs)
    # In test/integration contexts we often use a throwaway SQLite file DB without
    # running Alembic migrations. Ensure tables exist to avoid 'no such table' errors.
    if url.startswith("sqlite"):
        try:
            Base.metadata.create_all(bind=engine)
        except OperationalError:
            # If the database is temporarily unavailable or locked, ignore here;
            # operations will surface a clearer error later.
            pass
    return engine


def get_sessionmaker() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, future=True)
