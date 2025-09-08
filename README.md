# T4L End-to-End

[![CI](https://github.com/BigSlikTobi/T4L_End2End/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/BigSlikTobi/T4L_End2End/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![Coverage](https://img.shields.io/badge/coverage-%E2%89%A580%25-brightgreen.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white)](Dockerfile)

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

Optional data sources:
- nfl_data_py (used for NFL reference data loaders): install optional extra `nfl` (recommended on Python 3.12).

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

Useful pipeline flags:
- `--only-publisher "<Publisher>"` (repeatable) — process sources only from specific publishers
- `--only-source "<Source Name>"` (repeatable) — process specific source names from the config

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

NFL sitemap options:
```
# Frequently updated news sitemap (recommended)
url: https://www.nfl.com/sitemap-fast-changing.xml

# Sitemap index (discover site sitemaps)
url: https://www.nfl.com/sitemap-index.xml

# Monthly HTML articles sitemap (supported; placeholders auto-filled for current UTC year/month)
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

## Configure OpenAI (optional)

The pipeline works without OpenAI; ambiguous items fall back to rule-based decisions. To enable LLM-assisted checks:

1) Set environment variables (in your `.env`):
```
OPENAI_API_KEY=sk-...
# Optional:
OPENAI_MODEL=gpt-5-nano
OPENAI_CACHE=1  # in-memory cache for repeated calls
```

2) Verify:
```
python -m src.cli health
```
Look for `"openai": { "configured": true }`.

Notes:
- We use the OpenAI Python SDK (>=1.40). If the client cannot be created, the code falls back to a lightweight rule-based classification.

## Configure Supabase/Postgres (optional)

You can run locally on SQLite (default) or point the app to a Supabase Postgres database for production.

Option A — SQLite (default):
- Do nothing. `DATABASE_URL` defaults to `sqlite:///./t4l.db` and tables auto-create for local runs.

Option B — Supabase/Postgres (recommended for prod):
1) Install a Postgres driver if not present:
```
pip install "psycopg[binary]"
```
2) Set `DATABASE_URL` to your Supabase connection string (Project Settings → Database → Connection string):
```
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/postgres?sslmode=require
```
3) (Recommended) Run migrations to create/update schema:
```
# Using Alembic config shipped in this repo
python -m src.database.init_db
# or equivalently, if you use Alembic CLI:
# alembic upgrade head
```
4) (Optional) Configure the Supabase client for API usage (if you plan to use it elsewhere):
```
SUPABASE_URL=https://<your-project-ref>.supabase.co
SUPABASE_ANON_KEY=...
```
5) Verify:
```
python -m src.cli health
```
Look for `"database": { "ok": true }` and `"supabase": { "configured": true }`.

## NFL Reference Data (optional)

To enable reference data loaders, install the optional extras (prefer Python 3.12 due to pandas wheels):

```
pip install -e .[nfl]
```

Quick check (non-fatal):
```
make verify-nfl
```

How backend selection works:
- If `DATABASE_URL` starts with `sqlite`, the app uses SQLite and auto-creates tables.
- Otherwise, it uses SQLAlchemy with pooling against the configured DB. For Postgres/Supabase, migrations should be applied first.

## Run the pipeline

Prepare a config (YAML) describing your sources, for example:
```
version: 1
defaults:
  max_parallel_fetches: 5
  timeout: 15
sources:
  - name: ESPN NFL
    type: rss
    url: https://www.espn.com/espn/rss/nfl/news
    publisher: ESPN
    nfl_only: true
    enabled: true
```

Run the pipeline:
```
python -m src.cli pipeline --config config/feeds.yaml
```

Tips:
- For NFL.com, you can use the XML fast-changing sitemap or the monthly HTML articles sitemap.
- Dynamic placeholders `{YYYY}` and `{MM}` are auto-filled using current UTC year/month for monthly HTML URLs.
- Use `python -m src.cli health` to check DB/OpenAI/Supabase readiness before running.
- See `scripts/demo.sh` for a turnkey example that builds a temp config and runs the pipeline.

Run selected sources only:
```
# By publisher
python -m src.cli pipeline --config config/feeds.yaml --only-publisher "NFL.com"

# By source name (repeat flag to include several)
python -m src.cli pipeline --config config/feeds.yaml \
  --only-source "ESPN - NFL News" \
  --only-source "NFL.com - Articles Monthly Sitemap"
```

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
- Postgres driver missing: install `psycopg[binary]` and ensure `DATABASE_URL` uses the `postgresql+psycopg://` scheme

Health output quick guide:
- `database.ok: true` — database reachable (SQLite by default)
- `openai.configured: true` — `OPENAI_API_KEY` set and SDK importable
- `supabase.configured: true` — `SUPABASE_URL` + `SUPABASE_ANON_KEY` set and client importable
