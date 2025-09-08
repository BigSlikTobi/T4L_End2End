from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import List, Optional

from .relevance_filter import FilterDecision, RelevanceFilter


@dataclass
class ClaimCandidate:
    text: str
    status: str = "reported"  # reported|confirmed|retracted (simple taxonomy)
    citation: Optional[str] = None  # short snippet from title/content


@lru_cache(maxsize=1)
def _load_allowlist_patterns() -> List[str]:
    import os

    import yaml

    path = os.getenv(
        "T4L_ALLOWLIST_PATH",
        os.path.join(os.getcwd(), "config", "extraction", "allowlist.yaml"),
    )
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}
            pats = data.get("patterns") or []
            # Validate a bit and return
            return [str(p) for p in pats if p]
    except Exception:
        # Fallback to built-in defaults
        return [
            r"\b(signs?|re-signs?|agrees? to)\b",
            r"\b(traded?|trade[s]? for|acquires?|acquired)\b",
            r"\b(placed? on (ir|injured reserve)|suffers?|tear|fracture|sprain|strain|injury)\b",
            r"\b(waived|released|cut)\b",
            r"\b(activated|designated to return)\b",
            r"\b(suspended|suspension)\b",
        ]


def _allowlist_regex() -> re.Pattern[str]:
    pats = _load_allowlist_patterns()
    try:
        return re.compile("|".join(pats), re.IGNORECASE)
    except Exception:
        # If any pattern is invalid, fallback to simple-safe union
        safe = [p for p in pats if isinstance(p, str)]
        return re.compile("|".join(safe), re.IGNORECASE)


def extract_allowlisted_claims(title: str | None, content: str | None) -> List[ClaimCandidate]:
    """Extract simple claims from title/content using allowlisted patterns.

    Guardrails: Only emit when RelevanceFilter keeps the article AND a pattern matches.
    """
    title = title or ""
    content = content or ""

    filt = RelevanceFilter()
    decision, score = filt.filter_article(
        {
            "title": title,
            "url": "",
            "content_summary": content,
        }
    )
    if decision == FilterDecision.REJECT:
        return []

    text_for_patterns = f"{title}. {content}"
    if not _allowlist_regex().search(text_for_patterns):
        return []

    # For now, use the title as the canonical claim text to avoid noisy content.
    snippet = title.strip() or (content[:140] + ("…" if len(content) > 140 else ""))
    if not snippet:
        return []

    return [ClaimCandidate(text=snippet, status="reported", citation=snippet)]


__all__ = ["ClaimCandidate", "extract_allowlisted_claims"]
