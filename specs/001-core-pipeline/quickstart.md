# Quickstart: Core Pipeline

**Feature**: 001-core-pipeline  
**Date**: 2025-09-06  
**Target**: New developers joining the project

## Prerequisites

- Python 3.11+
- Git
- Supabase account (for production database)
- OpenAI API key (for LLM classification)

## Local Development Setup

### 1. Clone and Setup
```bash
git clone <repository-url>
cd T4L_End2End
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Create .env file
cp .env.example .env

# Edit .env with your values
DATABASE_URL=sqlite:///local.db  # For local development
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
OPENAI_API_KEY=your-openai-key
```

### 3. Initialize Database
```bash
# Run migrations for local SQLite
alembic upgrade head

# Or create tables manually
python -c "from src.database import init_db; init_db()"
```

### 4. Run the Pipeline
```bash
# Process a single feed
python -m src.cli ingest --feed-url "https://example.com/rss"

# Run full pipeline
python -m src.cli pipeline --all-feeds

# View processed articles
python -m src.cli list-articles --limit 10
```

## Project Structure

```
src/
├── cli/           # Command-line interface
├── models/        # Pydantic data models
├── services/      # Business logic
│   ├── ingester.py    # Feed ingestion
│   ├── filter.py      # Relevance filtering
│   ├── llm.py         # LLM classification
│   └── storage.py     # Database operations
├── database/      # DB connection and migrations
└── config/        # Configuration management

tests/
├── unit/          # Unit tests
├── integration/   # Integration tests
└── fixtures/      # Test data
```

## Key Components

### Feed Ingester
- Uses `feedparser` for RSS/Atom feeds
- Handles multiple feed formats
- Extracts standardized article metadata

### Relevance Filter
- Rule-based filtering (fast, cheap)
- LLM classification for ambiguous cases
- Configurable thresholds

### Database Layer
- SQLite for local development/testing
- Supabase PostgreSQL for production
- Single migration source for both

## Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Write Tests First
```bash
# Run tests
pytest tests/unit/test_filter.py

# Run with coverage
pytest --cov=src tests/
```

### 3. Implement Code
- Follow contracts defined in `/specs/001-core-pipeline/contracts/`
- Use data models from `data-model.md`
- Ensure constitution compliance

### 4. Test Integration
```bash
# Test with real feeds
python -m src.cli test-integration

# Test database operations
python -m src.cli test-db
```

### 5. Submit PR
- All tests pass
- Code review completed
- Constitution check passed

## Common Issues

### Database Connection
- Ensure DATABASE_URL is set correctly
- For Supabase: Check API keys and URL format
- For SQLite: File permissions on db file

### LLM API
- Check OpenAI API key validity
- Monitor rate limits and costs
- Handle API errors gracefully

### Feed Processing
- Some feeds may be slow or unresponsive
- Handle malformed XML gracefully
- Log errors but continue processing

## Performance Tuning

- Use async operations for I/O bound tasks
- Batch database operations
- Cache LLM results for repeated articles
- Monitor memory usage with large feeds

## Next Steps

1. Complete Phase 2: Task generation (`/tasks` command)
2. Implement core components following contracts
3. Add comprehensive test coverage
4. Set up CI/CD pipeline
5. Deploy to production environment
