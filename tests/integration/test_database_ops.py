from datetime import datetime, timezone

from src.database.repositories.article_repo import ArticleRepository
from src.database.repositories.watermark_repo import WatermarkRepository


def test_article_upsert_and_get(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db}")

    ar = ArticleRepository()

    data = {
        "url": "https://example.com/nfl/patriots-sign-qb",
        "title": "Patriots sign QB",
        "publisher": "Example",
        "publication_date": "2025-09-07T12:00:00Z",
        "content_summary": "Move to bolster depth",
    }
    obj = ar.upsert(data)
    assert obj.url == data["url"]

    # Update title only
    obj2 = ar.upsert({"url": data["url"], "title": "Updated"})
    assert obj2.title == "Updated"


def test_watermark_upsert_and_get(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db}")

    wm = WatermarkRepository()
    k = "ESPN - NFL News"
    now = datetime.now(timezone.utc)
    row = wm.upsert(k, now, "https://example.com/a")
    assert row.source_key == k

    got = wm.get(k)
    assert got is not None and got.last_url == "https://example.com/a"
