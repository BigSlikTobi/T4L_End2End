# Repository Guidelines

## Project Structure & Module Organization
- Source code lives in `src/` with domains under `cli/`, `database/`, `models/`, `services/`.
- Tests are in `tests/` with `contract/`, `unit/`, and `integration/` subfolders.
- Database migrations live in `migrations/` (Alembic). Specs and plans live under `specs/`.
- Utility scripts in `scripts/`; templates in `templates/`.

## Build, Test, and Development Commands
- Before starting any new feature, ensure dependencies are current:
- `pip install -r requirements.txt` (keeps runtime and dev tools in sync).
- `make install` — Install package in editable mode with dev tools.
- `make lint` — Run black, isort, flake8, mypy checks.
- `make format` — Auto-format with black and isort.
- `make test` — Run pytest (respects `pytest.ini`).
- `make alembic-init` — Create an auto-generated Alembic revision.

Examples:
- `pytest -q` for quick feedback; `pytest --cov=src` for coverage.

## Coding Style & Naming Conventions
- Python 3.10+. Line length 100 (black/isort/flake8 configured in `pyproject.toml`).
- Type hints required for public functions (mypy strict options enabled).
- Commit messages use Conventional Commits: `feat|fix|docs|test|chore|refactor`.
- Reference tasks in commits, e.g., `test(contracts): add FeedIngester tests (T007)`.
- Branch naming for features: `feature/<id>-<slug>` (e.g., `feature/001-core-pipeline`).

## Testing Guidelines
- Framework: pytest. Place tests under `tests/<type>/` and name files `test_*.py`.
- Contract tests should assert interface shape and behavior before implementations.
- Aim for high coverage on core modules; use `pytest --cov` locally.
- Keep tests deterministic; use fixtures and avoid network calls.

## Commit & Pull Request Guidelines
- Small, focused commits that pass `make lint` and `make test`.
- Always create and push a feature branch before starting development; do not commit directly to `main`.
- Example: `git checkout -b feature/001-core-pipeline && git push -u origin feature/001-core-pipeline`.
- PRs must include: concise description, linked task IDs (e.g., T007), affected paths, and any setup notes.
- Open PRs from feature branches; keep scope minimal and aligned with specs in `specs/001-core-pipeline/`.

## Security & Configuration Tips
- Manage secrets via `.env`/`.env.example`; never commit real credentials.
- Prefer dependency pins via `pyproject.toml`; avoid ad-hoc installs in CI.
- Run migrations with Alembic; do not edit generated SQL by hand.
