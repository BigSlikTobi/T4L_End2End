# CLAUDE.md: Core Pipeline Development Guide

**Feature**: 001-core-pipeline  
**Date**: 2025-09-06  
**Purpose**: AI assistant guidelines for implementing the NFL news pipeline

## Context
You are implementing a data pipeline that processes NFL news from RSS feeds and sitemaps, filters for relevance, and stores clean data in Supabase. The system must respect publisher terms (no scraping), be transparent/auditable, and cost-effective.

## Key Principles (from Constitution)
- **No Scraping**: Only use public feeds, metadata, URL context
- **Transparent**: Log all decisions with scores
- **LLM-Assisted**: Use small LLMs for ambiguous classification
- **Scalable**: Handle 1000+ articles/day
- **Structured**: Transform to clean, queryable data

## Implementation Guidelines

### Code Style
- Use type hints throughout
- Follow PEP 8
- Use pydantic for data validation
- Async/await for I/O operations
- Structured logging with context

### Architecture
- CLI-first design (`src/cli/`)
- Service layer pattern (`src/services/`)
- Repository pattern for data access
- Dependency injection for testability

### Testing
- Write tests before implementation (TDD)
- Unit tests for pure functions
- Integration tests for I/O operations
- Contract tests for interfaces
- Use pytest fixtures for setup

### Database
- Single migration source (Alembic)
- Schema parity between SQLite and Supabase
- Connection pooling in production
- Indexes on frequently queried fields

## Common Patterns

### Error Handling
```python
try:
    result = await process_feed(feed_url)
except FeedError as e:
    logger.error("Feed processing failed", extra={
        "feed_url": feed_url,
        "error": str(e),
        "step": "ingestion"
    })
    # Continue with next feed
```

### Logging Decisions
```python
logger.info("Article filtered", extra={
    "article_url": article.url,
    "decision": "keep",
    "score": 0.95,
    "filter_type": "rule_based",
    "step": "filtering"
})
```

### Data Validation
```python
class Article(BaseModel):
    url: HttpUrl
    title: str = Field(..., max_length=512)
    publisher: str = Field(..., max_length=255)
    publication_date: datetime
```

## Development Workflow

### When Implementing a Component
1. Check contracts in `/specs/001-core-pipeline/contracts/`
2. Write tests first
3. Implement following interface contracts
4. Ensure constitution compliance
5. Add integration tests
6. Update documentation

### When Modifying Schema
1. Create Alembic migration
2. Test on SQLite first
3. Apply to Supabase test environment
4. Verify data integrity
5. Update data models

### When Adding Dependencies
1. Check if already in requirements.txt
2. Prefer lightweight, well-maintained packages
3. Consider security implications
4. Update both requirements.txt and pyproject.toml

## Quality Gates

### Code Review Checklist
- [ ] Type hints on all functions
- [ ] Docstrings with examples
- [ ] Unit test coverage >80%
- [ ] Integration tests for I/O
- [ ] Constitution compliance verified
- [ ] Performance tested with realistic data
- [ ] Error handling comprehensive
- [ ] Logging adequate for debugging

### Constitution Compliance
- [ ] No scraping/crawling code
- [ ] All decisions logged with scores
- [ ] LLM used only for ambiguous cases
- [ ] Cost-effective filtering (rules before LLM)
- [ ] Data structured for downstream use

## Performance Targets
- Feed fetch: <30s timeout
- Article processing: <100ms per article
- Database insert: <10ms per article
- Memory usage: <200MB for 1000 articles
- LLM calls: <10% of articles (rule filtering first)

## Deployment
- Docker container for consistent environment
- Environment variables for configuration
- Health checks for monitoring
- Graceful shutdown handling
- Log aggregation to Supabase

## Troubleshooting
- Check logs first (structured with context)
- Use debug mode for detailed traces
- Test with minimal data sets
- Verify network connectivity for feeds/APIs
- Check database connections and permissions

Remember: This is a data pipeline, not a web app. Focus on reliability, observability, and efficiency. Every decision should be logged for auditability.
