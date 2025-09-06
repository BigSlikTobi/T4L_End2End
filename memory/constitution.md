# T4L_End2End Constitution

## What We Are Doing

We are building an end-to-end pipeline that transforms the fragmented stream of NFL news into structured, reliable, and actionable information. The process covers:

### Ingesting NFL News

Sources: official sitemaps, RSS feeds, and team news sites.

Inputs are standardized into articles with core metadata: URL, title, publisher, publication date.

### Filtering for NFL Relevance

Rules and regex filters (team names, URL paths, keyword include/exclude).

Negative filters ensure non-NFL content (NBA, MLB, soccer, etc.) is excluded upfront.

Endpoint-level flags (nfl_only=true) mark trusted NFL-exclusive feeds.

### Semantic & LLM-Based Relevance Checks

A small LLM (e.g., Gemma 3N or GPT-5 nano) classifies ambiguous items.

Only headlines/titles and URLs are analyzed — no full crawling, no long excerpts.

Ensures edge cases like "Hurts runs for 10 TDs" are correctly kept as NFL.

### Database Insertion

Clean, NFL-only news entries are written into a structured Supabase schema.

Metadata includes relevance score, LLM model version, and confidence for auditability.

This database forms the foundation for grouping, clustering, and downstream content creation.

### 🎯 Why We Are Doing It

1. **Clarity from Noise**

NFL news is spread across dozens of outlets and feeds, often duplicated and mixed with non-NFL content. Fans and fantasy players don't want "sports news" — they want NFL-only news.
Our pipeline cuts through the clutter, ensuring only relevant, high-quality signals are captured.

2. **Trust and Legality**

No crawling or scraping: We respect publisher terms by working only with public feeds, metadata, and URL context.

Transparent filtering: Every decision (rule, regex, LLM judgment) is logged with scores.

Auditable storage: Sources, dates, and model outputs are preserved, making the process trustworthy and compliant.

3. **Scalable Foundations**

The pipeline is built for volume: 1,000+ articles/day, across all 32 teams, with minimal cost.
By layering cheap rules before expensive LLM checks, we keep operating costs predictable while staying flexible for future growth.

4. **Future: Enabling the Event Graph** (Not Current Implementation)

The database is not the end — it's the foundation. Once NFL-only items are stored, we can:

Cluster them into events (signings, injuries, recaps).

Track entities (teams, players, weeks).

Generate evidence packs for grounding.

Power owned content creation (articles, YouTube scripts, X threads).

5. **Differentiation**

Unlike aggregators that simply re-list links, our system:

Understands what the news is about (semantics).

Filters it to NFL only.

Structures it for multiple angles (team, player, event type).
This enables us to produce our own content — timely, trustworthy, and multi-format — without relying on reprints or scraping.

### 🚀 Strategic Vision

We are not just aggregating news.
We are building an NFL Intelligence Layer that:

Collects → Filters → Structures → Groups → Powers content.

Allows fans, fantasy players, and media consumers to explore news by team, player, topic, and time.

Serves as the backbone for multi-channel publishing: articles, YouTube videos, X threads, and more.

In short:
We are turning raw feeds into structured knowledge, and structured knowledge into original, ownable content.

## Core Principles

### I. No Scraping or Crawling
Respect publisher terms by working only with public feeds, metadata, and URL context. No full article crawling or scraping to ensure legality and trust.

### II. Transparent and Auditable Filtering
Every decision (rule, regex, LLM judgment) is logged with scores. Sources, dates, and model outputs are preserved for auditability.

### III. LLM-Assisted Relevance Checks
Use small LLMs for classifying ambiguous items. Analyze only headlines/titles and URLs — no long excerpts. Ensures edge cases are correctly handled.

### IV. Scalable and Cost-Effective
Built for volume: 1,000+ articles/day. Layer cheap rules before expensive LLM checks to keep costs predictable.

### V. Structured Data Foundation
Transform fragmented news into structured, reliable information. Enable clustering, entity tracking, and downstream content creation.

## Additional Constraints

### Technology Stack
- Python for scripting and processing
- Supabase (PostgreSQL) for production database
- SQLite for local development/testing and pre-storage
- Small LLMs (e.g., Gemma 3N or GPT-5 nano) for relevance checks
- RSS feeds and sitemaps for data ingestion

### Security and Compliance
- No scraping or crawling to respect publisher terms
- Transparent logging of all decisions
- Auditable metadata storage

### Performance Standards
- Handle 1,000+ articles/day
- Minimal cost through layered filtering (rules before LLM)
- Scalable across all 32 NFL teams

### Storage Strategy
- Use SQLite locally for fast iterations and deterministic tests.
- Mirror schema to Supabase Postgres; keep a single source-of-truth migration set.
- Provide lightweight migration tooling to apply the same schema to both targets.
- Ensure parity in constraints (unique URL, indexes on publication_date, publisher).

## Development Workflow

### Planning
- Use feature specs in `/specs/` directory
- Follow plan-template.md for implementation plans
- Constitution check mandatory before research

### Implementation
- Test-first approach where applicable
- Integration testing for database and LLM components
- Observability through logging

### Review Process
- Code reviews must verify constitution compliance
- Quality gates: tests pass, no violations
- Amendments to constitution require documentation and approval

## Governance

Constitution supersedes all other practices. Amendments require documentation, approval, and migration plan.

All PRs/reviews must verify compliance with core principles. Complexity must be justified. Use constitution_update_checklist.md for guidance on updates.

**Version**: 1.0.0 | **Ratified**: 2025-09-06 | **Last Amended**: 2025-09-06