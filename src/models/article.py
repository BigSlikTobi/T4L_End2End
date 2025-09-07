from __future__ import annotations

from urllib.parse import urlparse

from pydantic import BaseModel, field_validator


class Article(BaseModel):
    """Pydantic model representing a parsed news article.

    Minimal fields are based on tests and specs. Validation ensures URL is HTTP(S).
    """

    url: str
    title: str
    publisher: str
    publication_date: str  # ISO 8601 string (e.g., 2025-09-06T10:00:00Z)
    content_summary: str | None = None

    @field_validator("url")
    @classmethod
    def _validate_http_url(cls, v: str) -> str:
        parsed = urlparse(v)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("url must be a valid HTTP(S) URL")
        return v


__all__ = ["Article"]
