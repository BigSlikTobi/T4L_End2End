from __future__ import annotations

from src.database.connection import get_database_url


def test_placeholder_database_url_falls_back_to_sqlite(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB")
    url = get_database_url()
    assert url.startswith("sqlite:///")
