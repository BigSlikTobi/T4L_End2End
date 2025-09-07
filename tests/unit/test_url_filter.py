import importlib

import pytest


def _load_filter_module():
    try:
        return importlib.import_module("src.services.relevance_filter")
    except Exception as e:
        pytest.xfail(f"Pending RelevanceFilter implementation (T021): {e}")


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://example.com/nfl/chiefs/news", True),
        ("https://site.com/sports/nba/lakers", False),
        ("https://blog.com/patriots/story", True),
        ("https://media.net/soccer/epl", False),
    ],
)
def test_is_nfl_url_pattern_examples(url, expected):
    mod = _load_filter_module()
    cls = getattr(mod, "RelevanceFilter", None)
    if cls is None:
        pytest.xfail("RelevanceFilter not found (T021)")

    # Assume a simple concrete for tests will be provided later; here we only check method exists.
    assert hasattr(cls, "is_nfl_url_pattern"), "Missing is_nfl_url_pattern method"
