from __future__ import annotations

from urllib.parse import urlparse

from pydantic import BaseModel, field_validator


class Feed(BaseModel):
    """Pydantic model describing a content feed source (RSS, sitemap, etc.)."""

    name: str
    url: str
    type: str | None = None  # e.g., "rss", "sitemap"
    publisher: str | None = None
    active: bool = True

    @field_validator("url")
    @classmethod
    def _validate_http_url(cls, v: str) -> str:
        parsed = urlparse(v)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("url must be a valid HTTP(S) URL")
        return v


__all__ = ["Feed"]
