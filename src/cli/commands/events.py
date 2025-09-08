from __future__ import annotations

import json
from typing import Optional

import click
from sqlalchemy import and_

from database.connection import get_sessionmaker
from models import (
    ClaimORM,
    ClaimSourceORM,
    EntityORM,
    EventArticleORM,
    EventEntityORM,
    EventORM,
)
from services.summary import generate_event_summary


@click.group(name="events")
def events_group() -> None:
    """Event browsing commands (contract-equivalent to /events endpoints)."""


@events_group.command(name="list")
@click.option("team_id", "--team-id", type=str, required=False)
@click.option("player_id", "--player-id", type=str, required=False)
@click.option("etype", "--type", type=str, required=False)
@click.option("min_conf", "--min-confidence", type=int, required=False, default=0)
def list_events(
    team_id: Optional[str], player_id: Optional[str], etype: Optional[str], min_conf: int
) -> None:
    sm = get_sessionmaker()
    with sm() as session:  # session: Session
        q = session.query(EventORM)

        # Filter by type
        if etype:
            q = q.filter(EventORM.event_type == etype)

        # Filter by min confidence
        if min_conf:
            q = q.filter(EventORM.confidence >= float(min_conf))

        # Filter by entity constraints via join
        if team_id or player_id:
            q = q.join(EventEntityORM, EventEntityORM.event_id == EventORM.id).join(
                EntityORM, EntityORM.id == EventEntityORM.entity_id
            )
            conds = []
            if team_id:
                conds.append(
                    and_(EntityORM.entity_type == "team", EntityORM.external_id == team_id)
                )
            if player_id:
                conds.append(
                    and_(EntityORM.entity_type == "player", EntityORM.external_id == player_id)
                )
            if conds:
                q = q.filter(and_(*conds))

        rows = q.order_by(EventORM.event_date.desc().nullslast()).limit(100).all()
        out = [
            {
                "id": r.id,
                "title": r.title,
                "summary": r.summary,
                "confidence": r.confidence,
                "event_date": r.event_date.isoformat() if r.event_date else None,
            }
            for r in rows
        ]
        print(json.dumps(out, indent=2))


@events_group.command(name="show")
@click.argument("event_id", type=int, required=True)
def show_event(event_id: int) -> None:
    sm = get_sessionmaker()
    with sm() as session:  # session: Session
        ev = session.get(EventORM, event_id)
        if not ev:
            click.echo("{}")
            return
        ents = (
            session.query(EntityORM)
            .join(EventEntityORM, EventEntityORM.entity_id == EntityORM.id)
            .filter(EventEntityORM.event_id == event_id)
            .all()
        )
        claims = session.query(ClaimORM).filter(ClaimORM.event_id == event_id).all()
        claim_sources = {
            c.id: session.query(ClaimSourceORM).filter(ClaimSourceORM.claim_id == c.id).all()
            for c in claims
        }
        arts = session.query(EventArticleORM).filter(EventArticleORM.event_id == event_id).all()
        out = {
            "id": ev.id,
            "title": ev.title,
            "summary": ev.summary,
            "event_date": ev.event_date.isoformat() if ev.event_date else None,
            "confidence": ev.confidence,
            "entities": [
                {
                    "id": e.id,
                    "type": e.entity_type,
                    "external_id": e.external_id,
                    "name": e.display_name,
                }
                for e in ents
            ],
            "claims": [
                {
                    "id": c.id,
                    "text": c.claim_text,
                    "status": c.status,
                    "confidence": c.confidence,
                    "sources": [
                        {"id": cs.id, "url": cs.url, "citation": cs.citation}
                        for cs in claim_sources.get(c.id, [])
                    ],
                }
                for c in claims
            ],
            "articles": [{"article_id": a.article_id, "relation": a.relation} for a in arts],
        }
        print(json.dumps(out, indent=2))


@events_group.command(name="summary")
@click.argument("event_id", type=int, required=True)
def summary_event(event_id: int) -> None:
    sm = get_sessionmaker()
    with sm() as session:  # session: Session
        txt = generate_event_summary(event_id, session)
        click.echo(txt)


__all__ = ["events_group"]
