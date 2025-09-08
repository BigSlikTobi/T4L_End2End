from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class EventORM(Base):
    __tablename__ = "events"
    __table_args__ = (UniqueConstraint("signature", name="uq_events_signature"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    signature: Mapped[str] = mapped_column(String(256), nullable=False)
    event_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    event_type: Mapped[str | None] = mapped_column(String(64))
    title: Mapped[str | None] = mapped_column(String(512))
    summary: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class EntityORM(Base):
    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(64))
    display_name: Mapped[str] = mapped_column(String(256), nullable=False)

    __table_args__ = (Index("ix_entities_type", "entity_type"),)


class EventEntityORM(Base):
    __tablename__ = "event_entities"
    __table_args__ = (
        UniqueConstraint("event_id", "entity_id", "role", name="uq_event_entity_role"),
        Index("ix_event_entities_event", "event_id"),
        Index("ix_event_entities_entity", "entity_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False
    )
    entity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("entities.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str | None] = mapped_column(String(32))


class SourceORM(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    publisher: Mapped[str | None] = mapped_column(String(256))
    url: Mapped[str | None] = mapped_column(String(1000))


class ClaimORM(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False
    )
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str | None] = mapped_column(String(32))
    confidence: Mapped[float | None] = mapped_column(Float)

    __table_args__ = (Index("ix_claims_event", "event_id"),)


class ClaimSourceORM(Base):
    __tablename__ = "claim_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    claim_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("claims.id", ondelete="CASCADE"), nullable=False
    )
    source_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False
    )
    url: Mapped[str | None] = mapped_column(String(1000))
    citation: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (Index("ix_claim_sources_claim", "claim_id"),)


class EventArticleORM(Base):
    __tablename__ = "event_articles"
    __table_args__ = (
        UniqueConstraint("event_id", "article_id", name="uq_event_article"),
        Index("ix_event_articles_event", "event_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False
    )
    article_id: Mapped[int] = mapped_column(Integer, nullable=False)
    relation: Mapped[str | None] = mapped_column(String(32))


__all__ = [
    "EventORM",
    "EntityORM",
    "EventEntityORM",
    "SourceORM",
    "ClaimORM",
    "ClaimSourceORM",
    "EventArticleORM",
]
