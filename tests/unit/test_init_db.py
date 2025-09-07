from __future__ import annotations

from src.database import init_db


def test_upgrade_to_head_invokes_alembic(monkeypatch, tmp_path):
    called = {}

    class FakeCfg:
        def __init__(self, path: str) -> None:
            called["cfg_path"] = path

    def fake_upgrade(cfg, rev):
        called["rev"] = rev

    monkeypatch.setattr(init_db, "Config", FakeCfg)
    monkeypatch.setattr(init_db, "command", type("C", (), {"upgrade": staticmethod(fake_upgrade)}))

    # Provide a custom path so we don't inspect real filesystem
    ini = tmp_path / "alembic.ini"
    ini.write_text("[alembic]\n", encoding="utf-8")
    init_db.upgrade_to_head(str(ini))

    assert called.get("cfg_path") == str(ini)
    assert called.get("rev") == "head"
