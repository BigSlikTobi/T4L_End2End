# Data Model (Phase 1)

This model reflects the spec’s pragmatic Postgres approach and constitution constraints.

## Entities

- events
  - event_id (pk)
  - type (transaction|injury|game|discipline|analysis|rumor)
  - subtype (signing|extension|trade|waiver|IR|questionable|out|preview|recap|...)
  - phase (preseason|regular|postseason|offseason|unknown)
  - week (int|null)
  - status (rumor|reported|confirmed|superseded)
  - confidence (int 0-100)
  - first_seen (timestamptz)
  - last_seen (timestamptz)
  - signature_hash (text; unique within 5-day window)

- event_entities
  - event_id (fk→events)
  - entity_type (team|player|game)
  - entity_id (text)
  - role (subject|counterparty|context)

- claims
  - claim_id (pk)
  - event_id (fk→events)
  - kind (contract|injury_status|game_result|...)
  - value_json (jsonb)
  - confidence (int 0-100)
  - status (rumor|reported|confirmed|superseded)

- claim_sources
  - claim_id (fk→claims)
  - article_id (fk→articles)
  - weight (float)

- event_articles
  - event_id (fk→events)
  - article_id (fk→articles)
  - role (primary|secondary|corroboration)
  - source_tier (A|B|C)
  - confidence (int 0-100)

- teams (reference; from nfl_data_py)
  - team_id (slug)
  - names (jsonb aliases)

- players (reference; from nfl_data_py)
  - player_id
  - name
  - aliases (jsonb)
  - position

- player_team_history (optional reference)
  - player_id (fk→players)
  - team_id (fk→teams)
  - start_date
  - end_date

- sources
  - source_id (pk)
  - domain
  - tier (A|B|C)
  - policy_mode (strict|preview|provider-context)

- articles (existing)
  - article_id (pk)
  - url (unique)
  - title
  - publisher
  - published_at

## Indexes (high level)
- events(type, week, first_seen DESC)
- event_entities(event_id), event_entities(entity_type, entity_id)
- claims(event_id), claims using GIN on value_json

## Invariants
- Event signature hashing stable for 5-day window
- Idempotent upserts on URL (articles), signature (events), normalized claim keys
- Every user-facing fact must be backed by at least one citation
