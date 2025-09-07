# API and CLI Documentation

This project exposes a CLI with subcommands for ingestion, filtering, the full pipeline, and health checks.

## CLI overview

Run the CLI locally:

```
python -m src.cli --help
```

Available commands:

- `ingest` — Parse a single feed URL (RSS or sitemap) and print item counts.
  - Options:
    - `--url TEXT` (required): Feed URL
    - `--type [rss|sitemap]` (required): Feed type

- `filter` — Run the relevance filter on a single title+URL.
  - Options:
    - `--title TEXT` (required)
    - `--url TEXT` (required)
    - `--use-llm` (flag): Also call the LLM classifier

- `pipeline` — Execute the full pipeline based on a YAML config.
  - Options:
    - `--config PATH` (required): Path to YAML configuration file

- `health` — Health checks: DB connectivity, OpenAI/Supabase configuration presence.

## Pipeline configuration

The pipeline loads a YAML file (see `config/feeds.yaml` example). Minimal schema:

```
version: 1
defaults:
  max_parallel_fetches: 5
  timeout: 15
sources:
  - name: Example Feed
    type: rss            # or sitemap
    url: https://example.com/rss
    publisher: Example
    nfl_only: true
    enabled: true
```

Sitemap sources can use dynamic placeholders for NFL monthly sitemaps:

```
url: https://www.nfl.com/sitemap/html/articles/{YYYY}/{MM}
```

## Environment variables

- `DATABASE_URL` — SQLAlchemy URL. Defaults to `sqlite:///./t4l.db`.
- `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_TIMEOUT` — Connection pool sizing (non-SQLite).
- `OPENAI_API_KEY` — Enables live LLM classification (optional).
- `OPENAI_CACHE` — Enable in-memory LLM cache (1/0, default 1).
- `SUPABASE_URL`, `SUPABASE_ANON_KEY` — Supabase client configuration (optional).
- `LOG_LEVEL` — Log level (default INFO).

## Programmatic usage

You can import services directly, e.g.:

```python
from src.services.pipeline import Pipeline

stats = await Pipeline().run_from_config("config/feeds.yaml")
print(stats)
```
