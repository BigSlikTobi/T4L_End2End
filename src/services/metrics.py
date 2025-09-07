from __future__ import annotations

import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Dict

_lock = threading.Lock()


@dataclass
class Counter:
    name: str
    value: int = 0

    def inc(self, n: int = 1) -> None:
        with _lock:
            self.value += n


@dataclass
class Histogram:
    name: str
    buckets: Dict[str, int] = field(default_factory=dict)

    def observe(self, duration_sec: float) -> None:
        # Very simple bucketization
        if duration_sec < 0.1:
            k = "lt_100ms"
        elif duration_sec < 0.5:
            k = "lt_500ms"
        elif duration_sec < 1.0:
            k = "lt_1s"
        else:
            k = "gt_1s"
        with _lock:
            self.buckets[k] = self.buckets.get(k, 0) + 1


class Metrics:
    counters: Dict[str, Counter] = {}
    histograms: Dict[str, Histogram] = {}

    @classmethod
    def counter(cls, name: str) -> Counter:
        if name not in cls.counters:
            cls.counters[name] = Counter(name)
        return cls.counters[name]

    @classmethod
    def histogram(cls, name: str) -> Histogram:
        if name not in cls.histograms:
            cls.histograms[name] = Histogram(name)
        return cls.histograms[name]

    @classmethod
    @contextmanager
    def time(cls, name: str):
        start = time.perf_counter()
        try:
            yield
        finally:
            cls.histogram(name).observe(time.perf_counter() - start)

    @classmethod
    def snapshot(cls) -> Dict[str, Dict[str, int]]:
        # Return a serializable snapshot
        with _lock:
            return {
                "counters": {k: v.value for k, v in cls.counters.items()},
                "histograms": {k: dict(v.buckets) for k, v in cls.histograms.items()},
            }


__all__ = ["Metrics"]
