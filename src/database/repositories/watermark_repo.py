from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session, sessionmaker

from database.connection import get_sessionmaker
from models.database import SourceWatermarkORM


class WatermarkRepository:
    def __init__(self, factory: Optional[sessionmaker[Session]] = None) -> None:
        self._factory: sessionmaker[Session] = factory or get_sessionmaker()

    def get(self, source_key: str) -> Optional[SourceWatermarkORM]:
        with self._factory() as session:
            row = (
                session.query(SourceWatermarkORM)
                .filter(SourceWatermarkORM.source_key == source_key)
                .one_or_none()
            )
            # SQLite may round-trip timezone-aware datetimes as naive; coerce to UTC-aware.
            if row and row.last_publication_date and row.last_publication_date.tzinfo is None:
                row.last_publication_date = row.last_publication_date.replace(tzinfo=timezone.utc)
            return row

    def upsert(
        self, source_key: str, last_publication_date: Optional[datetime], last_url: Optional[str]
    ) -> SourceWatermarkORM:
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
            if row.last_publication_date and row.last_publication_date.tzinfo is None:
                row.last_publication_date = row.last_publication_date.replace(tzinfo=timezone.utc)
            return row


__all__ = ["WatermarkRepository", "SourceWatermarkORM"]
