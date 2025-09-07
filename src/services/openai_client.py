from __future__ import annotations

import os
from typing import Any, Dict, Optional, Tuple

try:
    # OpenAI >=1.40
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover - optional dependency at dev time
    OpenAI = None  # type: ignore


class OpenAIClient:
    """Thin wrapper around OpenAI APIs with a safe offline fallback.

    Contract:
        - classify_title_url(title, url, model=None) -> Dict with keys label, confidence, reason
    """

    def __init__(self, api_key: Optional[str] = None, enable_cache: bool | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._client = None
        self._cache: Dict[Tuple[str, str], Dict[str, Any]] = {}
        self._enable_cache = (
            bool(int(os.getenv("OPENAI_CACHE", "1"))) if enable_cache is None else enable_cache
        )
        if self.api_key and OpenAI is not None:
            try:
                self._client = OpenAI(api_key=self.api_key)
            except Exception:
                # Fallback to offline if instantiation fails
                self._client = None

    def classify_title_url(
        self, title: str, url: str, model: Optional[str] = None
    ) -> Dict[str, Any]:
        # Cache check
        cache_key = (title.strip(), url.strip())
        if self._enable_cache and cache_key in self._cache:
            return self._cache[cache_key]

        # Offline fallback: quick heuristic to avoid hard dependency in dev
        if not self._client:
            result = self._offline_classify(title, url)
            if self._enable_cache:
                self._cache[cache_key] = result
            return result

        model_name = model or os.getenv("OPENAI_MODEL", "gpt-5-nano")
        prompt = (
            "Classify if the following headline+URL is NFL-related.\n"
            "Return JSON with keys label in {NFL, NON_NFL, AMBIGUOUS}, confidence [0,1], "
            "reason.\n\n"
            f"Title: {title}\nURL: {url}\n"
        )
        try:
            # Prefer Responses API when available
            if hasattr(self._client, "responses"):
                resp = self._client.responses.create(
                    model=model_name,
                    input=prompt,
                    temperature=0.2,
                )
                content = resp.output_text  # type: ignore[attr-defined]
            else:
                # Back-compat: chat.completions
                chat = self._client.chat.completions.create(  # type: ignore[attr-defined]
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                )
                content = chat.choices[0].message.content or ""  # type: ignore[index]

            # Very light parsing: look for label hints
            lowered = content.lower()
            if "nfl" in lowered:
                label = "NFL"
                confidence = 0.8
            elif "non_nfl" in lowered or "not nfl" in lowered or "non-nfl" in lowered:
                label = "NON_NFL"
                confidence = 0.8
            else:
                label = "AMBIGUOUS"
                confidence = 0.5
            result = {"label": label, "confidence": confidence, "reason": content[:500]}
            if self._enable_cache:
                self._cache[cache_key] = result
            return result
        except Exception as e:
            # Fallback gracefully
            result = {"label": "AMBIGUOUS", "confidence": 0.5, "reason": f"offline_fallback: {e}"}
            if self._enable_cache:
                self._cache[cache_key] = result
            return result

    @staticmethod
    def _offline_classify(title: str, url: str) -> Dict[str, Any]:
        try:
            # Local rule-based fallback
            from .rule_filter import score_text_relevance
        except Exception:
            # Minimal heuristic if rule_filter isn't available
            def score_text_relevance(text: str, keywords: Any) -> float:  # type: ignore
                t = text.lower()
                return 1.0 if any(k in t for k in ["nfl", "patriots", "chiefs", "packers"]) else 0.0

        text = f"{title} {url}"
        score = score_text_relevance(
            text,
            [
                "nfl",
                "super bowl",
                "patriots",
                "chiefs",
                "packers",
                "eagles",
                "cowboys",
            ],
        )
        if score >= 0.7:
            return {"label": "NFL", "confidence": min(1.0, score), "reason": "rule-fallback"}
        elif score <= 0.2:
            return {"label": "NON_NFL", "confidence": 1.0 - score, "reason": "rule-fallback"}
        return {"label": "AMBIGUOUS", "confidence": 0.5, "reason": "rule-fallback"}
