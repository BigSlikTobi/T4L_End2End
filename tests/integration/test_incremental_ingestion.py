from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from src.services.sitemap_parser import apply_dynamic_template, current_utc_year_month
from src.database.repositories.watermark_repo import WatermarkRepository


def test_dynamic_sitemap_template_current_month(monkeypatch):
    # Freeze to a known date
    def fake_now():
        return (2025, 9)

    with patch("src.services.sitemap_parser.current_utc_year_month", return_value=fake_now()):
        url = apply_dynamic_template("https://www.nfl.com/sitemap/html/articles/{YYYY}/{MM}")
        assert url.endswith("/2025/09")


def test_watermark_increments(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db}")

    repo = WatermarkRepository()
    key = "Test Source"
    t1 = datetime(2025, 9, 7, 12, 0, 0, tzinfo=timezone.utc)
    t2 = t1 + timedelta(hours=1)

    repo.upsert(key, t1, "https://example.com/a")
    row = repo.get(key)
    assert row and row.last_publication_date == t1

    repo.upsert(key, t2, "https://example.com/b")
    row2 = repo.get(key)
    assert row2 and row2.last_publication_date == t2 and row2.last_url == "https://example.com/b"
