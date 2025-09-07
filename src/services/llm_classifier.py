from __future__ import annotations

from typing import Any, Dict


class LLMClassifier:
    """Simple LLM classification stub.

    Contract test only checks class exists and method presence; no network calls.
    """

    def __init__(self, model: str | None = None) -> None:
        self.model = model or "mock"

    def classify_title_url(self, title: str, url: str) -> Dict[str, Any]:
        # Very naive mock classification; downstream tasks can replace with real API
        title_l = (title or "").lower()
        url_l = (url or "").lower()
        is_nfl = any(k in title_l or k in url_l for k in ("nfl", "chiefs", "patriots"))
        return {"is_relevant": is_nfl, "confidence": 0.7 if is_nfl else 0.2}


__all__ = ["LLMClassifier"]
