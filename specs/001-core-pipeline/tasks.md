# Tasks: Core Pipeline

**Input**: Design documents from `/specs/001-core-pipeline/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Repository Workflow Rules
- Always develop on a dedicated feature branch in GitHub before starting implementation.
   - Branch name format: `feature/<id>-<slug>` (e.g., `feature/001-core-pipeline`)
   - Create and push the branch, then open a PR when ready to merge.
- Use Conventional Commits for all commits:
   - Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `build`, `ci`.
   - Format: `<type>(<scope>): <summary>` (reference tasks, e.g., `T007`).
   - Example: `feat(ingestion): add RSS parser scaffolding (T019)`

## Execution Flow (main)
```
0. Ensure feature branch exists (feature/<id>-<slug>)
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 3.1: Setup
- [x] T001 Create project structure per implementation plan (`src/`, `tests/`, `migrations/`)
- [x] T002 Initialize Python project with dependencies (`requirements.txt`, `pyproject.toml`)
- [x] T003 [P] Configure linting and formatting tools (black, flake8, mypy)
- [x] T004 [P] Set up development environment (.env, .env.example, .gitignore)
- [x] T005 [P] Initialize Git repository with main branch (Already initialized)
- [x] T006 Configure Alembic for database migrations (`alembic.ini`, `migrations/`)

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

### Contract Tests
- [x] T007 Write contract tests for FeedIngester interface (`tests/contract/test_feed_ingester.py`)
- [x] T008 Write contract tests for RelevanceFilter interface (`tests/contract/test_relevance_filter.py`)

### Data Model Tests
- [x] T009 Write Pydantic model tests for Article (`tests/unit/test_models.py`)
- [x] T010 Write database schema tests (SQLite parity with Supabase)

### Unit Tests - Core Components
- [x] T011 Write unit tests for feed parsing (`tests/unit/test_feed_parser.py`)
- [x] T012 Write unit tests for URL pattern matching (`tests/unit/test_url_filter.py`)
- [x] T013 Write unit tests for team/player name detection (`tests/unit/test_team_detection.py`)
- [x] T014 Write unit tests for LLM client mock (`tests/unit/test_llm_client.py`)
- [x] T015 Write unit tests for database operations (`tests/unit/test_database.py`)
git pull

## Phase 3.3: Core Implementation

### Data Models
- [x] T016 Implement Pydantic models (`src/models/article.py`, `src/models/feed.py`)
- [x] T017 Implement database models (`src/models/database.py`)

### Services - Feed Ingestion
- [x] T018 Implement FeedIngester concrete class (`src/services/feed_ingester.py`)
- [x] T019 Implement RSS feed parser (`src/services/rss_parser.py`)
- [x] T020 Implement sitemap parser (`src/services/sitemap_parser.py`)
 - [x] T020a Implement dynamic sitemap URL templating (NFL monthly sitemap `{YYYY}/{MM}` from current UTC date) (`src/services/sitemap_parser.py`)

### Services - Filtering
- [x] T021 Implement RelevanceFilter concrete class (`src/services/relevance_filter.py`)
- [x] T022 Implement rule-based filtering logic (`src/services/rule_filter.py`)
- [x] T023 Implement LLM classification service (`src/services/llm_classifier.py`)

### Services - Storage
- [x] T024 Implement database connection layer (`src/database/connection.py`)
- [x] T025 Implement article repository (`src/database/repositories/article_repo.py`)
- [x] T026 Implement processing log repository (`src/database/repositories/log_repo.py`)
 - [x] T026a Implement per-source watermark repository (latest publication_date/URL) (`src/database/repositories/watermark_repo.py`)

### CLI Interface
- [x] T027 Implement CLI entry point (`src/cli/__init__.py`)
- [x] T028 Implement ingest command (`src/cli/commands/ingest.py`)
- [x] T029 Implement filter command (`src/cli/commands/filter.py`)
- [x] T030 Implement pipeline command (`src/cli/commands/pipeline.py`)

## Phase 3.4: Integration

### Database Integration
- [ ] T031 Create Alembic migrations for articles table (`migrations/versions/001_articles.py`)
- [ ] T032 Create Alembic migrations for feeds table (`migrations/versions/002_feeds.py`)
- [ ] T033 Create Alembic migrations for processing_log table (`migrations/versions/003_processing_log.py`)
- [ ] T034 Implement database initialization script (`src/database/init_db.py`)

### External Service Integration
- [ ] T035 Integrate OpenAI API client (`src/services/openai_client.py`)
- [ ] T036 Integrate Supabase client (`src/database/supabase_client.py`)
- [ ] T037 Implement environment-based database switching (SQLite ↔ Supabase)

### Full Pipeline Integration
- [ ] T038 Implement end-to-end pipeline orchestrator (`src/services/pipeline.py`)
- [ ] T039 Implement error handling and recovery (`src/services/error_handler.py`)
- [ ] T040 Implement structured logging (`src/services/logger.py`)
 - [ ] T040a Enforce incremental ingestion using watermarks and URL de-duplication (`src/services/pipeline.py`)

## Phase 3.5: Integration Testing

### Component Integration Tests
- [ ] T041 Write integration tests for feed ingestion + parsing (`tests/integration/test_feed_ingestion.py`)
- [ ] T042 Write integration tests for filtering pipeline (`tests/integration/test_filtering_pipeline.py`)
- [ ] T043 Write integration tests for database operations (`tests/integration/test_database_ops.py`)
 - [ ] T043a Write integration tests for watermark-based incremental ingestion (`tests/integration/test_incremental_ingestion.py`)
 - [ ] T043b Write integration tests for dynamic NFL sitemap URL generation (`tests/integration/test_dynamic_sitemap.py`)

### End-to-End Tests
- [ ] T044 Write E2E test for single feed processing (`tests/integration/test_single_feed_e2e.py`)
- [ ] T045 Write E2E test for full pipeline with mock data (`tests/integration/test_full_pipeline_e2e.py`)
- [ ] T046 Write E2E test with real Supabase connection (`tests/integration/test_supabase_integration.py`)

## Phase 3.6: Polish

### Performance & Optimization
- [ ] T047 Add async processing for concurrent feed fetching (`src/services/async_processor.py`)
- [ ] T048 Implement connection pooling for database (`src/database/pool.py`)
- [ ] T049 Add caching for LLM responses (`src/services/cache.py`)
- [ ] T050 Optimize database queries with proper indexing

### Monitoring & Observability
- [ ] T051 Implement health checks (`src/cli/commands/health.py`)
- [ ] T052 Add performance metrics (`src/services/metrics.py`)
- [ ] T053 Implement log aggregation to database (`src/services/log_aggregator.py`)

### Documentation & Deployment
- [ ] T054 Create API documentation (`docs/api.md`)
- [ ] T055 Create deployment configuration (Dockerfile, docker-compose.yml)
- [ ] T056 Create CI/CD pipeline (GitHub Actions)
- [ ] T057 Write production deployment guide (`docs/deployment.md`)

### Final Validation
- [ ] T058 Run full test suite with >80% coverage
- [ ] T059 Validate constitution compliance
- [ ] T060 Performance test with 1000+ articles
- [ ] T061 Create demo script for stakeholders

## Dependency Graph

```
Setup Tasks (T001-T006) → Contract Tests (T007-T010) → Unit Tests (T011-T015)
                                                            ↓
Data Models (T016-T017) → Services (T018-T030) → Integration (T031-T040)
                                                            ↓
Integration Tests (T041-T046) → Polish (T047-T061)
```

## Parallel Execution Examples

### Development Setup (can run in parallel)
- T003 Configure linting tools
- T004 Set up environment files
- T005 Initialize Git repository

### Core Implementation (parallel by component)
- T018-T020 Feed ingestion services
- T021-T023 Filtering services
- T024-T026 Storage services
- T027-T030 CLI commands

### Testing (parallel by test type)
- T007-T008 Contract tests
- T011-T015 Unit tests
- T041-T046 Integration tests

## Task Validation Checklist
- [ ] All contracts have corresponding tests? (T007-T008)
- [ ] All entities have models? (T016-T017)
- [ ] All services implemented? (T018-T030)
- [ ] Database schema complete? (T031-T033)
- [ ] Integration points tested? (T041-T046)
- [ ] Performance requirements met? (T047-T050)
- [ ] Documentation complete? (T054-T057)
- [ ] Constitution compliance verified? (T059)

**Total Tasks**: 61 | **Estimated Timeline**: 8-12 weeks | **Team Size**: 2-3 developers
