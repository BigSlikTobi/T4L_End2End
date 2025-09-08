from __future__ import annotations

from typing import Any, Dict, List

from click.testing import CliRunner

from cli.commands.ingest import ingest as ingest_cmd


def test_ingest_rss_path(monkeypatch):
    # Stub FeedIngester methods inside the command module
    class FakeFI:
        async def fetch_feed(self, feed_url: str) -> Dict[str, Any]:
            return {"url": feed_url, "status": 200, "content": "<rss></rss>", "headers": {}}

        async def extract_articles(self, feed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
            return [
                {"title": "t1", "link": "http://a"},
                {"title": "t2", "link": "http://b"},
            ]

    # Patch constructor in module scope
    monkeypatch.setattr("cli.commands.ingest.FeedIngester", lambda: FakeFI())

    runner = CliRunner()
    result = runner.invoke(ingest_cmd, ["--url", "http://example.com/rss", "--type", "rss"])
    assert result.exit_code == 0
    assert "Parsed 2 RSS entries" in result.output


def test_ingest_sitemap_path(monkeypatch):
    # Patch the imported functions in the command module
    def fake_fetch(url: str) -> str:  # xml content is opaque to the parser here
        return "<xml>ok</xml>"

    def fake_parse(xml: str):
        return [
            {"url": "http://x/1", "lastmod": "2025-09-07T00:00:00Z"},
            {"url": "http://x/2", "lastmod": "2025-09-07T01:00:00Z"},
            {"url": "http://x/3", "lastmod": "2025-09-07T02:00:00Z"},
        ]

    monkeypatch.setattr("cli.commands.ingest.fetch_sitemap", fake_fetch)
    monkeypatch.setattr("cli.commands.ingest.parse_sitemap", fake_parse)

    runner = CliRunner()
    result = runner.invoke(ingest_cmd, ["--url", "http://example.com/sm.xml", "--type", "sitemap"])
    assert result.exit_code == 0
    assert "Parsed 3 sitemap URLs" in result.output
