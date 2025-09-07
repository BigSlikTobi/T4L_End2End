from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

from ..connection import get_sessionmaker
from ...models.database import Base


class SourceWatermarkORM(Base):
    __tablename__ = "source_watermarks"
    __table_args__ = (
        UniqueConstraint("source_key", name="uq_source_watermarks_source_key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_key: Mapped[str] = mapped_column(String(255), nullable=False)
    last_publication_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    last_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)


class WatermarkRepository:
    def __init__(self, factory: Optional[sessionmaker[Session]] = None) -> None:
        self._factory: sessionmaker[Session] = factory or get_sessionmaker()

    def get(self, source_key: str) -> Optional[SourceWatermarkORM]:
        with self._factory() as session:
            return (
                session.query(SourceWatermarkORM)
                .filter(SourceWatermarkORM.source_key == source_key)
                .one_or_none()
            )

    def upsert(self, source_key: str, last_publication_date: Optional[datetime], last_url: Optional[str]) -> SourceWatermarkORM:
        with self._factory() as session:
            row = (
                session.query(SourceWatermarkORM)
                .filter(SourceWatermarkORM.source_key == source_key)
                .one_or_none()
            )
            if row is None:
                row = SourceWatermarkORM(
                    source_key=source_key,
                    last_publication_date=last_publication_date,
                    last_url=last_url,
                )
                session.add(row)
            else:
                row.last_publication_date = last_publication_date or row.last_publication_date
                row.last_url = last_url or row.last_url
            session.commit()
            session.refresh(row)
            return row


__all__ = ["WatermarkRepository", "SourceWatermarkORM"]
