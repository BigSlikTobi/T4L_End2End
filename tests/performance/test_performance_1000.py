from __future__ import annotations

import asyncio
import time
from types import SimpleNamespace
from typing import Any, Dict, List

from src.services.pipeline import Pipeline


def make_items(n: int) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for i in range(n):
        title = "Patriots win" if i % 2 == 0 else "International soccer news"
        items.append(
            {
                "link": f"https://ex.com/a{i}",
                "title": title,
                "publisher": "Perf",
                "published": "2025-09-07T00:00:00Z",
            }
        )
    return items


def test_pipeline_processes_1000_plus_under_time(monkeypatch):
    p = Pipeline()

    async def fake_fetch_feed(url: str) -> Dict[str, Any]:  # type: ignore[override]
        return {"url": url, "content": ""}

    async def fake_extract_articles(feed: Dict[str, Any]) -> List[Dict[str, Any]]:  # type: ignore[override]
        return make_items(1200)

    # Patch ingester methods
    monkeypatch.setattr(p.ingester, "fetch_feed", fake_fetch_feed)
    monkeypatch.setattr(p.ingester, "extract_articles", fake_extract_articles)

    # Patch repositories to avoid real DB cost
    def fake_upsert(data: Dict[str, Any]):
        return SimpleNamespace(url=data.get("url"), publication_date=None)

    monkeypatch.setattr(p.article_repo, "upsert", fake_upsert)
    monkeypatch.setattr(p.log_repo, "add", lambda *a, **k: None)
    monkeypatch.setattr(p.watermarks, "get", lambda *a, **k: None)
    monkeypatch.setattr(p.watermarks, "upsert", lambda *a, **k: None)

    src = {"name": "perf", "type": "rss", "url": "https://ex.com/rss", "enabled": True}

    t0 = time.time()
    st = asyncio.run(p._process_source(src, {}))
    elapsed = time.time() - t0

    assert st["total"] >= 1200
    assert st["kept"] + st["rejected"] + st["escalated"] == st["total"]
    # Should run well under 15 seconds in CI
    assert elapsed < 15.0
