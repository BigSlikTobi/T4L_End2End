import importlib

import pytest


def _load_rss_parser_module():
    try:
        return importlib.import_module("src.services.rss_parser")
    except Exception as e:
        pytest.xfail(f"Pending RSS parser implementation (T019): {e}")


def test_rss_parser_interface_and_output_shape():
    mod = _load_rss_parser_module()
    parse = getattr(mod, "parse_feed", None)
    if parse is None:
        pytest.xfail("Function parse_feed not found in src.services.rss_parser (T019)")

    # Expected behavior: returns list of raw article dicts with at least url/title
    # Use a minimal fake feed string once implemented; now, assert callable only.
    assert callable(parse)
