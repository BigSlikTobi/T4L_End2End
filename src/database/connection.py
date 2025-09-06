from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", "sqlite:///./t4l.db")


def get_engine(echo: bool = False) -> Engine:
    return create_engine(get_database_url(), echo=echo, future=True)


def get_sessionmaker() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, future=True)
