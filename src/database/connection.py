from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

# Import ORM base for optional auto-creation in lightweight SQLite setups (tests)
from ..models.database import Base


def get_database_url() -> str:
    """Resolve database URL from env; defaults to local SQLite.

    Supports switching to Supabase/Postgres via DATABASE_URL, e.g.,
    DATABASE_URL=postgresql+psycopg://user:pass@host:5432/db
    """
    return os.getenv("DATABASE_URL", "sqlite:///./t4l.db")


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
