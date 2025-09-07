from __future__ import annotations

from typing import Iterable


def score_text_relevance(text: str, keywords: Iterable[str]) -> float:
    t = (text or "").lower()
    if not t:
        return 0.0
    hits = sum(1 for k in keywords if k and k.lower() in t)
    # Simple bounded score: 0..1
    return min(1.0, hits / 3.0)


def decide(score: float, keep_threshold: float = 0.5, escalate_threshold: float = 0.3):
    from .relevance_filter import FilterDecision

    if score >= keep_threshold:
        return FilterDecision.KEEP
    if score >= escalate_threshold:
        return FilterDecision.ESCALATE
    return FilterDecision.REJECT


__all__ = ["score_text_relevance", "decide"]
