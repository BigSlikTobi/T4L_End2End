# Data Model: Core Pipeline

**Feature**: 001-core-pipeline  
**Date**: 2025-09-06  
**Input**: Research findings and constitution requirements

## Database Schema

### Articles Table
```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    url VARCHAR(2048) UNIQUE NOT NULL,
    title VARCHAR(512) NOT NULL,
    publisher VARCHAR(255) NOT NULL,
    publication_date TIMESTAMP NOT NULL,
    content_summary TEXT,
    relevance_score DECIMAL(3,2), -- 0.00 to 1.00
    llm_model VARCHAR(100),
    llm_confidence DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_articles_publication_date ON articles(publication_date DESC);
CREATE INDEX idx_articles_publisher ON articles(publisher);
CREATE INDEX idx_articles_relevance_score ON articles(relevance_score DESC);
```

### Feeds Table
```sql
CREATE TABLE feeds (
    id SERIAL PRIMARY KEY,
    url VARCHAR(2048) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    feed_type VARCHAR(50) NOT NULL, -- 'rss' or 'sitemap'
    nfl_only BOOLEAN DEFAULT FALSE,
    last_fetched TIMESTAMP,
    last_processed_publication TIMESTAMP, -- watermark for incremental ingestion
    last_processed_url VARCHAR(2048),     -- optional fallback watermark
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Processing_Log Table (for auditability)
```sql
CREATE TABLE processing_log (
    id SERIAL PRIMARY KEY,
    article_url VARCHAR(2048) NOT NULL,
    step VARCHAR(100) NOT NULL, -- 'ingest', 'filter', 'llm_check', 'store'
    decision VARCHAR(50) NOT NULL, -- 'keep', 'reject', 'escalate'
    score DECIMAL(3,2),
    llm_model VARCHAR(100),
    confidence DECIMAL(3,2),
    error_message TEXT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_processing_log_article_url ON processing_log(article_url);
CREATE INDEX idx_processing_log_processed_at ON processing_log(processed_at DESC);
```

## Deduplication & Watermarks

- Enforce `UNIQUE(url)` at the database layer to prevent duplicate articles.
- Track per-source watermarks in `feeds` table: `last_processed_publication` and `last_processed_url`.
- In ingestion, filter out entries older than the watermark; on equal or missing timestamps, rely on URL de-duplication.

## Python Data Models (Pydantic)

### Article Model
```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Article(BaseModel):
    url: str
    title: str
    publisher: str
    publication_date: datetime
    content_summary: Optional[str] = None
    relevance_score: Optional[float] = None
    llm_model: Optional[str] = None
    llm_confidence: Optional[float] = None

class ArticleInDB(Article):
    id: int
    created_at: datetime
    updated_at: datetime
```

### Feed Model
```python
class Feed(BaseModel):
    url: str
    name: str
    feed_type: str  # 'rss' or 'sitemap'
    nfl_only: bool = False
    last_fetched: Optional[datetime] = None

class FeedInDB(Feed):
    id: int
    created_at: datetime
```

### Processing Log Model
```python
class ProcessingLog(BaseModel):
    article_url: str
    step: str
    decision: str
    score: Optional[float] = None
    llm_model: Optional[str] = None
    confidence: Optional[float] = None
    error_message: Optional[str] = None
    processed_at: datetime
```

## Migration Strategy

### Single Source Migrations
- Use Alembic for migration management
- Store migrations in `/migrations` directory
- Apply same migrations to both SQLite (local) and Supabase (production)
- Environment variable `DATABASE_URL` controls target database

### Schema Parity Checks
- Unique constraints on `articles.url`
- Indexes on frequently queried fields
- Foreign key relationships where applicable
- Data type consistency between SQLite and PostgreSQL

## Data Flow

1. **Ingestion**: Raw article data from feeds → Article model
2. **Filtering**: Article → ProcessingLog entries for each decision step
3. **Storage**: Validated Article → articles table
4. **Audit**: All decisions logged to processing_log table

## Validation Rules

- URL: Must be valid HTTP/HTTPS, max 2048 chars
- Title: Required, max 512 chars
- Publisher: Required, max 255 chars
- Publication Date: Valid datetime, not in future
- Relevance Score: 0.00 to 1.00 if present
- LLM Confidence: 0.00 to 1.00 if present

## Performance Considerations

- Indexes on publication_date for time-based queries
- Unique index on URL prevents duplicates
- Processing log partitioned by date if volume grows
- Connection pooling for Supabase in production
