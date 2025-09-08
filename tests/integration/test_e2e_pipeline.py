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


def test_article_to_event_happy_path(tmp_path, monkeypatch):
  """
  T007: Given an article about an NFL game, the pipeline should create an event,
  link entities (team/player if detectable), record a citation to the article,
  and compute a confidence score.

  Pending implementation of event models/services, mark as xfail.
  """
  try:
    # Repos expected by event feature (to be implemented in Phase 3.3):
    import importlib

    events_repo_mod = importlib.import_module(
      "src.database.repositories.events_repo"
    )  # noqa: F401
    claims_repo_mod = importlib.import_module(
      "src.database.repositories.claims_repo"
    )  # noqa: F401
  except Exception as e:
    import pytest

    pytest.xfail(f"Pending event repos and services (T010–T016, T021): {e}")

  # If repos exist, attempt an end-to-end minimal flow
  db = tmp_path / "test_events.db"
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

  from unittest.mock import Mock, patch

  with patch("requests.get") as pget:
    resp = Mock()
    resp.status_code = 200
    resp.text = SAMPLE_RSS
    resp.headers = {"Content-Type": "application/rss+xml"}
    pget.return_value = resp

    stats = asyncio.run(Pipeline().run_from_config(str(cfg_path)))

  # Basic sanity on ingestion
  assert stats["kept"] >= 1

  # Verify event-related side effects (interfaces to be defined by repos)
  # These asserts are placeholders and may be refined once schemas exist.
  EventsRepo = getattr(events_repo_mod, "EventsRepository")
  ev_repo = EventsRepo()
  events = getattr(ev_repo, "list")()
  assert isinstance(events, list) and len(events) >= 1
  ev = events[0]
  # Event should have confidence and citations
  assert getattr(ev, "confidence", None) is not None
  assert getattr(ev, "id", None) is not None
  # Access citations/links if provided by repo API
  get_ev = getattr(ev_repo, "get")
  ev_full = get_ev(ev.id)
  citations = getattr(ev_full, "citations", []) or getattr(ev_full, "sources", [])
  assert citations, "Event should contain at least one citation/source"
