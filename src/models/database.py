from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ArticleORM(Base):
    __tablename__ = "articles"
    __table_args__ = (UniqueConstraint("url", name="uq_articles_url"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    publisher: Mapped[str] = mapped_column(String(256), nullable=False)
    publication_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    content_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class FeedORM(Base):
    __tablename__ = "feeds"
    __table_args__ = (UniqueConstraint("url", name="uq_feeds_url"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    publisher: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


__all__ = ["Base", "ArticleORM", "FeedORM"]
