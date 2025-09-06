import inspect
import importlib
import pytest
from typing import Dict, Any, List


def _load_feed_ingester_module():
    try:
        return importlib.import_module("src.services.feed_ingester")
    except Exception as e:
        pytest.xfail(f"Pending implementation of feed ingester (T018): {e}")


def test_feed_ingester_class_and_methods_exist():
    mod = _load_feed_ingester_module()

    feed_ingester = getattr(mod, "FeedIngester", None)
    if feed_ingester is None:
        pytest.xfail("Class FeedIngester not found in src.services.feed_ingester (T018)")

    # Methods required by the contract
    for method_name in ("fetch_feed", "extract_articles", "standardize_article"):
        assert hasattr(
            feed_ingester, method_name
        ), f"Missing method {method_name} on FeedIngester (contract)"


def test_feed_ingester_method_signatures_and_types():
    mod = _load_feed_ingester_module()

    feed_ingester = getattr(mod, "FeedIngester", None)
    if feed_ingester is None:
        pytest.xfail("Class FeedIngester not found in src.services.feed_ingester (T018)")

    # fetch_feed must be async and accept (self, feed_url: str) -> Dict[str, Any]
    assert inspect.iscoroutinefunction(
        getattr(feed_ingester, "fetch_feed")
    ), "fetch_feed must be async"
    sig = inspect.signature(getattr(feed_ingester, "fetch_feed"))
    params = list(sig.parameters.values())
    assert len(params) == 2, "fetch_feed(self, feed_url: str) expected"
    # type hints (best-effort):
    hints = getattr(feed_ingester.fetch_feed, "__annotations__", {})
    assert (
        hints.get("feed_url") == str
    ), "fetch_feed should annotate feed_url: str per contract"
    assert (
        hints.get("return") in (Dict[str, Any], dict)
    ), "fetch_feed should return Dict[str, Any] per contract"

    # extract_articles must be async and accept (self, feed_data: Dict[str, Any]) -> List[Dict[str, Any]]
    assert inspect.iscoroutinefunction(
        getattr(feed_ingester, "extract_articles")
    ), "extract_articles must be async"
    sig = inspect.signature(getattr(feed_ingester, "extract_articles"))
    params = list(sig.parameters.values())
    assert len(params) == 2, "extract_articles(self, feed_data: Dict[str, Any]) expected"
    hints = getattr(feed_ingester.extract_articles, "__annotations__", {})
    assert (
        hints.get("feed_data") in (Dict[str, Any], dict)
    ), "extract_articles should annotate feed_data: Dict[str, Any] per contract"
    # Allow List[...] or list for flexibility
    ret_ann = hints.get("return")
    assert ret_ann in (List[Dict[str, Any]], list), (
        "extract_articles should return List[Dict[str, Any]] per contract"
    )

    # standardize_article must be sync and accept (self, raw_article: Dict[str, Any]) -> Dict[str, Any]
    assert not inspect.iscoroutinefunction(
        getattr(feed_ingester, "standardize_article")
    ), "standardize_article must be sync"
    sig = inspect.signature(getattr(feed_ingester, "standardize_article"))
    params = list(sig.parameters.values())
    assert len(params) == 2, "standardize_article(self, raw_article: Dict[str, Any]) expected"
    hints = getattr(feed_ingester.standardize_article, "__annotations__", {})
    assert (
        hints.get("raw_article") in (Dict[str, Any], dict)
    ), "standardize_article should annotate raw_article: Dict[str, Any] per contract"
    assert (
        hints.get("return") in (Dict[str, Any], dict)
    ), "standardize_article should return Dict[str, Any] per contract"

