from __future__ import annotations

from typing import Iterable, Optional

from ..database.repositories.log_repo import ProcessingLogRepository


class LogAggregator:
    """A thin helper to capture and flush structured logs to the database.

    Usage: collect log entries as dicts and flush in batches.
    Each entry should include: level, message, article_url?, metadata?
    """

    def __init__(self, repo: Optional[ProcessingLogRepository] = None) -> None:
        self._repo = repo or ProcessingLogRepository()

    def flush(self, entries: Iterable[dict]) -> int:
        count = 0
        for e in entries:
            try:
                self._repo.add(
                    level=str(e.get("level", "INFO")),
                    message=str(e.get("message", "")),
                    article_url=e.get("article_url"),
                    metadata=e.get("metadata"),
                )
                count += 1
            except Exception:
                # Best-effort; continue on errors
                continue
        return count


__all__ = ["LogAggregator"]
