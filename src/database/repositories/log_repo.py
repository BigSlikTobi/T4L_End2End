from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from ..connection import get_sessionmaker
from ...models.database import Base


class ProcessingLogORM(Base):
    __tablename__ = "processing_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    level: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    article_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    # 'metadata' is reserved on Declarative models; use attribute 'meta' and column name 'metadata'
    meta: Mapped[Optional[str]] = mapped_column("metadata", Text, nullable=True)


class ProcessingLogRepository:
    def __init__(self, factory: Optional[sessionmaker[Session]] = None) -> None:
        self._factory: sessionmaker[Session] = factory or get_sessionmaker()

    def add(self, level: str, message: str, article_url: Optional[str] = None, metadata: Optional[str] = None) -> ProcessingLogORM:
        with self._factory() as session:
            row = ProcessingLogORM(level=level, message=message, article_url=article_url, meta=metadata)
            session.add(row)
            session.commit()
            session.refresh(row)
            return row


__all__ = ["ProcessingLogRepository", "ProcessingLogORM", "Base"]
