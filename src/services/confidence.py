from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List, Mapping


@dataclass(frozen=True)
class Evidence:
    source_tier: str  # "A"|"B"|"C"
    published_at: datetime | None = None


_TIER_WEIGHT = {"A": 1.0, "B": 0.7, "C": 0.4}


def _tier_weight(tier: str | None) -> float:
    return _TIER_WEIGHT.get((tier or "").upper(), 0.3)


def compute_event_confidence(evidence: Iterable[Mapping]) -> float:
    """Compute event confidence in [0, 100].

    Heuristic:
    - Base = max tier weight * 60
    - Corroboration bonus: +15 for second distinct source (A/B/C), then +5 each capped
    - Recency decay: -d where d ~ days since most recent evidence (max 20)
    """

    items: List[Evidence] = []
    for e in evidence:
        items.append(
            Evidence(
                source_tier=str(e.get("source_tier") or e.get("tier") or "C"),
                published_at=e.get("published_at"),
            )
        )

    if not items:
        return 0.0

    max_w = max(_tier_weight(i.source_tier) for i in items)
    base = max_w * 60.0

    # Corroboration: count distinct source tiers as a proxy
    tiers = {i.source_tier.upper() for i in items}
    corroboration_count = max(0, len(tiers) - 1)
    bonus = 15.0 if corroboration_count >= 1 else 0.0
    if corroboration_count > 1:
        bonus += min(25.0, (corroboration_count - 1) * 5.0)

    # Recency decay
    now = datetime.now(timezone.utc)
    recency_days = 0.0
    dates = [i.published_at for i in items if isinstance(i.published_at, datetime)]
    if dates:
        most_recent = max(dates)
        recency_days = (now - most_recent).total_seconds() / 86400.0
    decay = min(20.0, max(0.0, recency_days))

    score = max(0.0, min(100.0, base + bonus - decay))
    return round(score, 2)


def compute_claim_confidence(sources: Iterable[Mapping]) -> float:
    """Compute claim confidence similarly but slightly stricter baseline."""
    items: List[Evidence] = []
    for s in sources:
        items.append(
            Evidence(
                source_tier=str(s.get("source_tier") or s.get("tier") or "C"),
                published_at=s.get("published_at"),
            )
        )

    if not items:
        return 0.0

    max_w = max(_tier_weight(i.source_tier) for i in items)
    base = max_w * 50.0

    tiers = {i.source_tier.upper() for i in items}
    corroboration_count = max(0, len(tiers) - 1)
    bonus = 10.0 if corroboration_count >= 1 else 0.0
    if corroboration_count > 1:
        bonus += min(20.0, (corroboration_count - 1) * 5.0)

    now = datetime.now(timezone.utc)
    recency_days = 0.0
    dates = [i.published_at for i in items if isinstance(i.published_at, datetime)]
    if dates:
        most_recent = max(dates)
        recency_days = (now - most_recent).total_seconds() / 86400.0
    decay = min(25.0, max(0.0, recency_days))

    score = max(0.0, min(100.0, base + bonus - decay))
    return round(score, 2)


__all__ = ["compute_event_confidence", "compute_claim_confidence"]
