from __future__ import annotations

from src.services.logger import get_logger, log_json
from src.services.metrics import Metrics


def test_logger_and_log_json():
    logger = get_logger()
    logger.info("hello")
    # Ensure log_json does not raise and accepts fields
    log_json("INFO", "msg", a=1, b="x")


def test_metrics_counters_and_timer():
    c = Metrics.counter("unit.test.counter")
    c.inc(2)
    assert Metrics.snapshot()["counters"]["unit.test.counter"] >= 2

    with Metrics.time("unit.test.timer"):
        pass
    snap = Metrics.snapshot()
    assert "unit.test.timer" in snap["histograms"]
