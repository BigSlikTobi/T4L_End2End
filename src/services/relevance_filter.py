from enum import Enum
from typing import Any, Dict, List, Tuple

from .rule_filter import decide, score_text_relevance


class FilterDecision(Enum):
    KEEP = "KEEP"
    REJECT = "REJECT"
    ESCALATE = "ESCALATE"


class RelevanceFilter:
    """Rule-based relevance filter for NFL content.

    Contract-only implementation: minimal but typed methods per tests.
    """

    def __init__(self, keywords: List[str] | None = None) -> None:
        self.keywords = keywords or [
            # Common league/team tokens (sample)
            "nfl",
            "chiefs",
            "patriots",
            "packers",
            "cowboys",
            "49ers",
            "eagles",
            "giants",
            "jets",
            "ravens",
            "steelers",
            "bears",
        ]

    def filter_article(self, article: Dict[str, Any]) -> Tuple[FilterDecision, float]:
        title = str(article.get("title") or "")
        url = str(article.get("url") or "")
        summary = str(article.get("content_summary") or "")

        url_hit = self.is_nfl_url_pattern(url)
        text_score = max(
            score_text_relevance(title, self.keywords),
            score_text_relevance(summary, self.keywords),
        )

        score = max(text_score, 0.9 if url_hit else 0.0)
        decision = decide(score, keep_threshold=0.5, escalate_threshold=0.3)
        return decision, float(score)

    def is_nfl_team_mention(self, text: str) -> bool:
        text_l = (text or "").lower()
        return any(k in text_l for k in self.keywords)

    def is_nfl_url_pattern(self, url: str) -> bool:
        url_l = (url or "").lower()
        return "nfl" in url_l or any(k in url_l for k in self.keywords)


__all__ = ["FilterDecision", "RelevanceFilter"]
