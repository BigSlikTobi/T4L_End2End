import importlib
import inspect
from typing import Any, Dict

import pytest


def _load_relevance_filter_module():
    try:
        return importlib.import_module("src.services.relevance_filter")
    except Exception as e:
        pytest.xfail(f"Pending implementation of relevance filter (T021): {e}")


def test_filterdecision_enum_exists():
    mod = _load_relevance_filter_module()

    enum_cls = getattr(mod, "FilterDecision", None)
    if enum_cls is None:
        pytest.xfail("FilterDecision enum not found in src.services.relevance_filter (T021)")

    # Verify expected enum members per contract
    assert hasattr(enum_cls, "KEEP"), "FilterDecision should define KEEP"
    assert hasattr(enum_cls, "REJECT"), "FilterDecision should define REJECT"
    assert hasattr(enum_cls, "ESCALATE"), "FilterDecision should define ESCALATE"


def test_relevance_filter_class_and_methods_exist():
    mod = _load_relevance_filter_module()

    relevance_filter = getattr(mod, "RelevanceFilter", None)
    if relevance_filter is None:
        pytest.xfail("Class RelevanceFilter not found in src.services.relevance_filter (T021)")

    for method_name in ("filter_article", "is_nfl_team_mention", "is_nfl_url_pattern"):
        assert hasattr(
            relevance_filter, method_name
        ), f"Missing method {method_name} on RelevanceFilter (contract)"


def test_relevance_filter_method_signatures_and_types():
    mod = _load_relevance_filter_module()

    relevance_filter = getattr(mod, "RelevanceFilter", None)
    if relevance_filter is None:
        pytest.xfail("Class RelevanceFilter not found in src.services.relevance_filter (T021)")

    filter_article = getattr(relevance_filter, "filter_article")
    sig = inspect.signature(filter_article)
    params = list(sig.parameters.values())
    assert len(params) == 2, "filter_article(self, article: Dict[str, Any]) expected"
    hints = getattr(filter_article, "__annotations__", {})
    assert hints.get("article") in (
        Dict[str, Any],
        dict,
    ), "filter_article should annotate article: Dict[str, Any] per contract"
    ret = hints.get("return")
    # Tuple[FilterDecision, float] is expected; accept generic Tuple for forward-compat
    assert ret is not None, "filter_article should annotate return type per contract"

    # Helper methods
    is_team = getattr(relevance_filter, "is_nfl_team_mention")
    sig = inspect.signature(is_team)
    params = list(sig.parameters.values())
    assert len(params) == 2, "is_nfl_team_mention(self, text: str) expected"
    hints = getattr(is_team, "__annotations__", {})
    assert hints.get("text") == str, "is_nfl_team_mention should annotate text: str per contract"
    assert hints.get("return") in (
        bool,
        type(True),
    ), "is_nfl_team_mention should return bool per contract"

    is_url = getattr(relevance_filter, "is_nfl_url_pattern")
    sig = inspect.signature(is_url)
    params = list(sig.parameters.values())
    assert len(params) == 2, "is_nfl_url_pattern(self, url: str) expected"
    hints = getattr(is_url, "__annotations__", {})
    assert hints.get("url") == str, "is_nfl_url_pattern should annotate url: str per contract"
    assert hints.get("return") in (
        bool,
        type(True),
    ), "is_nfl_url_pattern should return bool per contract"
