# Phase 0 Research: NFL Event Knowledge Graph

## Decisions
- Source integration: Use existing rss/sitemap ingestion services; no new crawlers.
- Entity lexicons: Source Teams/Players from nfl_data_py; store in Supabase reference tables; daily in-season, weekly off-season, on-demand refresh.
- Event clustering window: 5 days (rolling from first_seen).
- Confidence: Normative formula with E, Cb, K, O, Rm; hysteresis at 65/85 promote and 55/75 demote.
- DB: Supabase Postgres is authoritative; SQLite mirrors for local tests.
- LLM usage: Small models for ambiguity classification, claim extraction (allowlisted), and summaries with mandatory citations.

## Rationale
- Aligns with constitution (no scraping; metadata-only) and cost goals (rules before LLM).
- 5-day window captures multi-day storylines while limiting over-merge.
- nfl_data_py provides stable canonical entities; Supabase keeps centralized source of truth.

## Alternatives Considered
- Neo4j/graph store first: deferred; start with Postgres tables per spec.
- Full-page scraping for claims: rejected due to compliance.
- Longer window (7-10 days): increases accidental merges.

## Open Points Resolved
- Alerts & RBAC: out of scope for this feature; to be handled in later specs.
