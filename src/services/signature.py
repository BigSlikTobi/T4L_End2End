from __future__ import annotations

import hashlib
import re
from datetime import datetime
from typing import Optional


def normalize_title(title: str) -> str:
    t = (title or "").lower().strip()
    # Remove punctuation and collapse whitespace
    t = re.sub(r"[^a-z0-9\s]", "", t)
    t = re.sub(r"\s+", " ", t)
    return t[:200]


def event_signature(title: str, date: Optional[datetime]) -> str:
    date_str = date.date().isoformat() if isinstance(date, datetime) else "na"
    key = f"{normalize_title(title)}|{date_str}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:40]


__all__ = ["normalize_title", "event_signature"]
