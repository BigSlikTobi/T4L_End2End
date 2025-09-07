from __future__ import annotations

from src.services.error_handler import safe_call
from src.services.log_aggregator import LogAggregator


def test_safe_call_ok_and_error():
    ok, res = safe_call(lambda: 1 + 1)
    assert ok and res == 2
    ok2, err = safe_call(lambda: 1 / 0)
    assert not ok2 and isinstance(err, Exception)


def test_log_aggregator_flush_counts():
    agg = LogAggregator()
    n = agg.flush([
        {"level": "INFO", "message": "a"},
        {"level": "ERROR", "message": "b", "article_url": "u", "metadata": "{}"},
    ])
    assert n == 2
