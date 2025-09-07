# T4L End-to-End

This repository contains an end-to-end pipeline that ingests NFL-related news from RSS feeds and sitemaps, filters for relevance using rule-based logic and optional LLM checks, and stores clean, deduplicated articles in a database.

## Why

- Reduce noise from sports news sources by automatically selecting NFL-relevant items
- Ensure transparency and auditability: every decision can be traced
- Scale to 1,000+ articles/day with concurrency and efficient storage

## What

- Ingestion from RSS and sitemaps (including dynamic monthly NFL sitemap templates)
- Relevance filtering: rules first, optional LLM for ambiguous cases
- Incremental ingestion: per-source watermarks and URL de-duplication
- Storage: SQLite for local dev/tests; Postgres/Supabase for production
- Observability: health checks, lightweight metrics, structured logs

## How (Quickstart)

### 1) Prerequisites
- Python 3.11+
- Optional: Docker
- Optional: Supabase project (for production)

### 2) Clone and set up environment
```
git clone https://github.com/BigSlikTobi/T4L_End2End.git
cd T4L_End2End
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file (optional but recommended):
```
DATABASE_URL=sqlite:///./t4l.db
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30

# Optional integrations
OPENAI_API_KEY=
OPENAI_CACHE=1
SUPABASE_URL=
SUPABASE_ANON_KEY=

LOG_LEVEL=INFO
```

### 3) Run tests
```
pytest -q
```

### 4) Explore the CLI
```
python -m src.cli --help
python -m src.cli health
python -m src.cli pipeline --config config/feeds.yaml
```

CLI commands:
- `ingest`: Parse one feed (RSS or sitemap) and print counts
- `filter`: Run rule-based filter (and optional LLM) on title+URL
- `pipeline`: Full E2E run from YAML config
- `health`: DB/OpenAI/Supabase basic checks

### 5) Configuration

Example `config/feeds.yaml` entry:
```
version: 1
defaults:
  max_parallel_fetches: 5
  timeout: 15
sources:
  - name: Example Feed
    type: rss
    url: https://example.com/rss
    publisher: Example
    nfl_only: true
    enabled: true
```

NFL monthly sitemap templating:
```
url: https://www.nfl.com/sitemap/html/articles/{YYYY}/{MM}
```

### 6) Docker (optional)
```
docker build -t t4l-end2end:latest .
docker run --rm --env-file .env t4l-end2end:latest python -m src.cli pipeline --config config/feeds.yaml
```
Or with Compose:
```
docker compose up --build
```

### 7) CI/CD
GitHub Actions workflow `.github/workflows/ci.yml` runs linting and tests on pushes/PRs.

## Developer Notes

- Code lives in `src/`; tests in `tests/`
- Database migrations live under `migrations/` (Alembic)
- Docs: `docs/api.md` (CLI/API), `docs/deployment.md` (deployment)
- Concurrency utilities: `src/services/async_processor.py`
- Observability: `src/cli/commands/health.py`, `src/services/metrics.py`, `src/services/log_aggregator.py`

## Troubleshooting

- “no such table” in SQLite during tests/runs: SQLite tables auto-create in local runs; ensure `DATABASE_URL` points to a writable file path
- LLM not configured: the pipeline uses rule-based decisions and degrades gracefully without OpenAI
- Supabase not configured: local runs default to SQLite; set `SUPABASE_URL` and `SUPABASE_ANON_KEY` when needed
