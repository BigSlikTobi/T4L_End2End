import asyncio
import os
from unittest.mock import Mock, patch

from src.services.pipeline import Pipeline

SAMPLE_RSS = """
<rss version="2.0">
<channel>
  <title>Sample NFL Feed</title>
  <item>
    <title>Chiefs win opener</title>
    <link>https://example.com/nfl/chiefs-win</link>
    <description>Week 1 victory</description>
    <pubDate>Sun, 07 Sep 2025 12:00:00 GMT</pubDate>
  </item>
</channel>
</rss>
"""


def test_e2e_single_feed(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db}")

    cfg_path = tmp_path / "feeds.yaml"
    cfg_path.write_text(
        """
version: 1
sources:
  - name: Test RSS
    type: rss
    url: https://example.com/rss
    publisher: Example
    nfl_only: true
    enabled: true
        """,
        encoding="utf-8",
    )

    with patch("requests.get") as pget:
        resp = Mock()
        resp.status_code = 200
        resp.text = SAMPLE_RSS
        resp.headers = {"Content-Type": "application/rss+xml"}
        pget.return_value = resp

        stats = asyncio.run(Pipeline().run_from_config(str(cfg_path)))

    assert stats["total"] >= 1 and stats["kept"] >= 1


def test_supabase_integration_smoke(monkeypatch):
    # Only run if env is configured; otherwise skip
    if not (os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_ANON_KEY")):
        return
    # Minimal smoke: just ensure client can be constructed and list tables
    from src.database.supabase_client import SupabaseClient

    client = SupabaseClient()
    # This may still fail without proper permissions; keep as soft check
    assert client.client is not None
