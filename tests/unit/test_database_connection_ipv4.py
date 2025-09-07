from __future__ import annotations

from sqlalchemy.engine.url import make_url

from src.database import connection as conn


def test_get_database_url_rewrites_to_ipv4(monkeypatch):
    # Provide a plausible Postgres URL with a DNS host
    pg_url = "postgresql+psycopg://u:p@db.example.com:5432/postgres?sslmode=require"
    monkeypatch.setenv("DATABASE_URL", pg_url)

    # Force DNS resolution to a known IPv4 address
    def fake_getaddrinfo(host, port, family, socktype):
        return [(family, socktype, 6, "", ("203.0.113.10", port))]

    monkeypatch.setattr(conn.socket, "getaddrinfo", fake_getaddrinfo)

    url = conn.get_database_url()
    parsed = make_url(url)
    assert parsed.host == "203.0.113.10"


def test_get_engine_sqlite_calls_create_all(monkeypatch, tmp_path):
    # Use a temp sqlite file to avoid pollution
    db_file = tmp_path / "t4l_test.db"
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")

    called = {"ok": False}

    # Patch Base.metadata.create_all inside the module
    original_meta = conn.Base.metadata

    class FakeMeta:
        def create_all(self, bind=None):
            called["ok"] = True

    try:
        conn.Base.metadata = FakeMeta()  # type: ignore
        engine = conn.get_engine()
        assert engine is not None
        assert called["ok"] is True
    finally:
        conn.Base.metadata = original_meta  # type: ignore
