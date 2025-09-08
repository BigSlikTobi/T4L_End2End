from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from src.database.repositories.watermark_repo import WatermarkRepository
from src.services.sitemap_parser import apply_dynamic_template


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


def test_dedup_clustering_within_5_days(tmp_path, monkeypatch):
    """
    T008: Two highly similar articles within 5 days should cluster into the same event
    and increase confidence with corroboration.

    Pending implementation of event clustering and confidence computation, mark xfail.
    """
    import pytest

    pytest.xfail("Pending clustering and confidence (T013–T014)")
