from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session, sessionmaker

from database.connection import get_sessionmaker
from models.database import ArticleORM


def _parse_dt(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        v = value.strip()
        # Support ISO8601 with trailing Z
        if v.endswith("Z"):
            v = v[:-1] + "+00:00"
        try:
            return datetime.fromisoformat(v)
        except Exception:
            return None
    return None


class ArticleRepository:
    """Repository for articles using SQLAlchemy ORM.

    Minimal interface per tests: upsert, get_by_url.
    """

    def __init__(self, factory: Optional[sessionmaker[Session]] = None) -> None:
        self._factory: sessionmaker[Session] = factory or get_sessionmaker()

    def upsert(self, data: Dict[str, Any]) -> ArticleORM:
        """Insert or update by unique URL.

        Expected keys: url, title, publisher, publication_date (str|datetime|None), content_summary.
        """
        with self._factory() as session:
            url = str(data.get("url") or "").strip()
            obj = session.query(ArticleORM).filter(ArticleORM.url == url).one_or_none()
            if obj is None:
                obj = ArticleORM(
                    url=url,
                    title=str(data.get("title") or ""),
                    publisher=str(data.get("publisher") or ""),
                    publication_date=_parse_dt(data.get("publication_date")),
                    content_summary=data.get("content_summary"),
                    created_at=datetime.now(timezone.utc),
                )
                session.add(obj)
            else:
                obj.title = str(data.get("title") or obj.title)
                obj.publisher = str(data.get("publisher") or obj.publisher)
                obj.publication_date = (
                    _parse_dt(data.get("publication_date")) or obj.publication_date
                )
                obj.content_summary = data.get("content_summary", obj.content_summary)
            session.commit()
            session.refresh(obj)
            return obj

    def get_by_url(self, url: str) -> Optional[ArticleORM]:
        with self._factory() as session:
            return session.query(ArticleORM).filter(ArticleORM.url == url).one_or_none()


__all__ = ["ArticleRepository"]
