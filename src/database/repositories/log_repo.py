from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session, sessionmaker

from database.connection import get_sessionmaker
from models.database import ProcessingLogORM


class ProcessingLogRepository:
    def __init__(self, factory: Optional[sessionmaker[Session]] = None) -> None:
        self._factory: sessionmaker[Session] = factory or get_sessionmaker()

    def add(
        self,
        level: str,
        message: str,
        article_url: Optional[str] = None,
        metadata: Optional[str] = None,
    ) -> ProcessingLogORM:
        with self._factory() as session:
            row = ProcessingLogORM(
                level=level, message=message, article_url=article_url, meta=metadata
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return row


__all__ = ["ProcessingLogRepository"]
