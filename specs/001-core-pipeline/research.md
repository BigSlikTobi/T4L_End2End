# Research: Core Pipeline

**Feature**: 001-core-pipeline  
**Date**: 2025-09-06  
**Input**: Technical Context from plan.md

## Research Tasks Completed

### Task: Research RSS feed parsing libraries for Python
**Decision**: Use `feedparser` library  
**Rationale**: Mature, handles multiple RSS formats, simple API, no external dependencies  
**Alternatives considered**: `xml.etree.ElementTree` (too low-level), `requests` + manual parsing (error-prone)

### Task: Research LLM integration for text classification
**Decision**: Use OpenAI API with GPT-4o mini or similar small model  
**Rationale**: Reliable API, good performance for classification tasks, cost-effective for headlines/URLs only  
**Alternatives considered**: Local models (too resource-intensive), other APIs (OpenAI has best Python support)

### Task: Research Supabase Python client
**Decision**: Use `supabase-py` official client  
**Rationale**: Official client, good documentation, handles auth and real-time features  
**Alternatives considered**: Direct PostgreSQL client (would need to handle Supabase-specific features)

### Task: Research SQLite for local testing
**Decision**: Use Python's built-in `sqlite3` module  
**Rationale**: No additional dependencies, same SQL syntax as PostgreSQL, perfect for testing  
**Alternatives considered**: Other embedded DBs (overkill for this use case)

### Task: Research testing frameworks for data pipelines
**Decision**: Use `pytest` with `pytest-asyncio` for async tests  
**Rationale**: Standard Python testing, good fixtures for database setup, async support for I/O operations  
**Alternatives considered**: `unittest` (less flexible), `behave` (overkill for unit tests)

### Task: Research logging and observability
**Decision**: Use Python's `logging` module with structured JSON output  
**Rationale**: Built-in, configurable, can output to files/databases, good for audit trails  
**Alternatives considered**: `loguru` (nice but adds dependency), `structlog` (good but overkill)

### Task: Research data validation and schemas
**Decision**: Use `pydantic` for data models  
**Rationale**: Type validation, JSON serialization, good error messages, integrates well with FastAPI if needed later  
**Alternatives considered**: `dataclasses` (no validation), `marshmallow` (similar but pydantic more popular)

### Task: Research migration tools for dual databases
**Decision**: Use `alembic` for migrations with custom scripts for SQLite/Supabase  
**Rationale**: Industry standard, handles schema changes, can generate migration files  
**Alternatives considered**: Custom SQL scripts (error-prone), Django migrations (framework-specific)

### Task: Research sitemap parsing for news URLs (no crawling)
**Decision**: Use Python's built-in `xml.etree.ElementTree` (or `defusedxml` for safety) to parse XML sitemaps (incl. news sitemaps)  
**Rationale**: Lightweight, sufficient for extracting `<url><loc>`, `<lastmod>`, and news entries without fetching article pages  
**Alternatives considered**: `lxml` (faster but extra dependency), `sitemap-parser` libs (unnecessary abstraction)

## Architecture Decisions

### Decision: CLI-first design
**Rationale**: Pipeline runs as scheduled job, CLI allows easy integration with cron/systemd  
**Implications**: Focus on command-line interface, structured logging to stdout/stderr

### Decision: Layered filtering approach
**Rationale**: Rules first (cheap), then LLM (expensive) to minimize costs  
**Implications**: Need clear thresholds for LLM escalation, good rule coverage for common cases

### Decision: Single migration source
**Rationale**: Ensures schema parity between SQLite and Supabase  
**Implications**: Use environment variables to switch database URLs, test migrations on both

### Decision: Incremental ingestion with per-source watermarks
**Rationale**: Avoid reprocessing and duplicates; scale efficiently  
**Implications**: Track latest processed `publication_date` and/or last seen URL per source; filter feeds by watermark before processing; enforce DB unique(url)

### Decision: Dynamic NFL monthly sitemap construction
**Rationale**: NFL sitemap path includes year and month segments; must adapt each month automatically  
**Implications**: Build sitemap URL at runtime from current UTC date as `https://www.nfl.com/sitemap/html/articles/{YYYY}/{MM}` with zero-padded month; allow overriding via config if needed

## Open Questions Resolved

- **Feed formats**: RSS 2.0, Atom supported by feedparser
- **Sitemaps**: Standard XML sitemaps and Google News sitemaps supported via XML parsing (no article-page crawling)
- **LLM prompt engineering**: Simple classification prompts work well for headlines
- **Database schema**: Articles table with indexes on URL (unique), publication_date, publisher
- **Error handling**: Graceful degradation - log errors but continue processing
- **Performance**: Python async can handle 1000+ articles/day on modest hardware

## Next Steps
- Proceed to Phase 1: Design data models, contracts, and quickstart
- All technical unknowns resolved
- Ready for implementation planning

## Ingestion Sources Configuration

We will maintain feed sources in `config/feeds.yaml` with entries like:
- name, type (rss|sitemap), url, publisher, nfl_only, enabled
- Defaults: user_agent, timeout, max_parallel_fetches

User action requested: Provide known official RSS and sitemap URLs for teams and trusted publishers to populate `config/feeds.yaml`.
