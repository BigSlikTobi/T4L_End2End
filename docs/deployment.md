# Deployment Guide

This guide covers local, Docker, and CI deployment patterns for the T4L End-to-End pipeline.

## Prerequisites
- Python 3.11+
- Optional: Docker Desktop
- Optional: Supabase project (for production DB)

## Environment
Create a `.env` file at the project root with relevant variables:

```
# Database
DATABASE_URL=sqlite:///./t4l.db
# For Postgres/Supabase:
# DATABASE_URL=postgresql+psycopg://user:pass@host:5432/db
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30

# OpenAI (optional)
OPENAI_API_KEY=
OPENAI_CACHE=1

# Supabase (optional)
SUPABASE_URL=
SUPABASE_ANON_KEY=

# Logging
LOG_LEVEL=INFO
```

## Local (virtualenv)

1. Create a virtual environment and install dependencies:
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run tests:
```
pytest -q
```

3. Run the CLI:
```
python -m src.cli --help
python -m src.cli health
python -m src.cli pipeline --config config/feeds.yaml
```

## Docker

Build and run the container:
```
docker build -t t4l-end2end:latest .
docker run --rm --env-file .env t4l-end2end:latest python -m src.cli pipeline --config config/feeds.yaml
```

Or use docker-compose:
```
docker compose up --build
```

## CI/CD

- GitHub Actions workflow `.github/workflows/ci.yml` runs lint and tests on pushes and PRs.
- Extend the workflow to build and publish Docker images if needed.

## Production considerations
- Use Postgres/Supabase for persistent storage. Set `DATABASE_URL` accordingly.
- Monitor logs and consider central log storage.
- Schedule the pipeline (e.g., cron, GitHub Actions workflow on schedule, or a Kubernetes CronJob).
- Scale by splitting sources across runs or increasing concurrency limits.
