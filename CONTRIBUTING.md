# Contributing Guide

## Branching Strategy
Create a feature branch in GitHub before development.
- Naming: `feature/<id>-<slug>` (e.g., `feature/001-core-pipeline`).
- Open a draft PR early; push small, frequent commits.

## Conventional Commits
- Format: `<type>(<scope>): <summary>`
- Common types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `build`, `ci`.
- Include task IDs where relevant (e.g., `T019`).

Examples:
- `feat(models): add Article and Feed Pydantic models (T016)`
- `test(contracts): add FeedIngester contract tests (T007)`
- `chore(ci): add lint + test workflow`

## PR Guidelines
- Keep PRs focused; link tasks and spec sections.
- Ensure `make lint` and tests pass.
- Squash merge using the Conventional Commit style for the title.