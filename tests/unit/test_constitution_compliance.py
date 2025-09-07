from __future__ import annotations

import inspect

from src.services.feed_ingester import FeedIngester
from src.services.sitemap_parser import fetch_sitemap


def test_no_crawling_affordances():
    # FeedIngester only fetches feeds, not article pages
    # Unbound method includes 'self' plus one argument 'feed_url'
    sig = inspect.signature(FeedIngester.fetch_feed)
    params = list(sig.parameters)
    assert params == ["self", "feed_url"]


def test_transparency_hooks_exist():
    # Logging and metrics modules exist and expose expected functions
    from src.services import logger, metrics

    assert hasattr(logger, "log_json")
    assert hasattr(metrics, "Metrics")


def test_llm_usage_is_optional():
    # OpenAI client must gracefully operate without API key
    from src.services.openai_client import OpenAIClient

    c = OpenAIClient(enable_cache=True)
    out = c.classify_title_url("Test", "https://ex.com")
    assert out["label"] in {"NFL", "NON_NFL", "AMBIGUOUS"}
