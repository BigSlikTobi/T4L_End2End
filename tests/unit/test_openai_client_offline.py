from __future__ import annotations

import os

from src.services.openai_client import OpenAIClient


def test_openai_offline_and_cache():
    os.environ.pop("OPENAI_API_KEY", None)
    c = OpenAIClient(enable_cache=True)
    r1 = c.classify_title_url("Patriots win", "https://example.com/nfl")
    r2 = c.classify_title_url("Patriots win", "https://example.com/nfl")
    assert r1["label"] in {"NFL", "NON_NFL", "AMBIGUOUS"}
    assert r2 == r1  # cache hit returns same dict
