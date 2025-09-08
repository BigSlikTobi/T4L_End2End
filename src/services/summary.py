from __future__ import annotations

from typing import List

from sqlalchemy.orm import Session

from models import (
    ClaimORM,
    ClaimSourceORM,
    EntityORM,
    EventArticleORM,
    EventEntityORM,
    EventORM,
)


def generate_event_summary(event_id: int, session: Session) -> str:
    ev: EventORM | None = session.get(EventORM, event_id)
    if not ev:
        return "Event not found"

    # Entities
    ents = (
        session.query(EntityORM)
        .join(EventEntityORM, EventEntityORM.entity_id == EntityORM.id)
        .filter(EventEntityORM.event_id == event_id)
        .all()
    )
    entities_txt = ", ".join(e.display_name for e in ents) if ents else ""

    # Claims and sources
    claims: List[ClaimORM] = session.query(ClaimORM).filter(ClaimORM.event_id == event_id).all()
    sources: List[tuple[int, str]] = []  # (idx, url)
    url_index: dict[str, int] = {}
    pieces: List[str] = []

    for cl in claims:
        # Find first source URL for claim (if any)
        cs_list: List[ClaimSourceORM] = (
            session.query(ClaimSourceORM).filter(ClaimSourceORM.claim_id == cl.id).all()
        )
        cite_idxs: List[int] = []
        for cs in cs_list:
            url = cs.url or ""
            if not url:
                continue
            if url not in url_index:
                url_index[url] = len(sources) + 1
                sources.append((url_index[url], url))
            cite_idxs.append(url_index[url])
        cites_txt = " ".join(f"[{i}]" for i in cite_idxs) if cite_idxs else ""
        pieces.append(f"{cl.claim_text}{(' ' + cites_txt) if cites_txt else ''}")

    # Fallback to event_articles if no claim sources
    if not sources:
        eas: List[EventArticleORM] = (
            session.query(EventArticleORM).filter(EventArticleORM.event_id == event_id).all()
        )
        for ea in eas:
            # We don't have the Article table ORM id→url here; cite generically
            url = f"article:{ea.article_id}"
            if url not in url_index:
                url_index[url] = len(sources) + 1
                sources.append((url_index[url], url))

    header = ev.title or ev.summary or "NFL Event"
    ent_part = f" involving {entities_txt}" if entities_txt else ""
    body = " ".join(pieces) if pieces else (ev.summary or "No detailed claims available.")
    cites_list = " ".join(f"[{i}] {url}" for i, url in sources)

    return f"{header}{ent_part}. {body}\n\nSources: {cites_list}".strip()


__all__ = ["generate_event_summary"]
