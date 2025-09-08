# Tasks: NFL Event Knowledge Graph

**Input**: Design documents from `/specs/002-vision-the-nfl/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
- This file is generated per template and tailored to the feature. Execute tasks top-to-bottom, honoring dependencies and [P] for safe parallelism.

## Phase 3.1: Setup
- [x] T001 Ensure Supabase connection config is present and working (env, URL, key) in `src/database/supabase_client.py`
- [x] T002 [P] Add dependency lock/verify for `nfl_data_py` and ensure availability in runtime env (document in README if needed)
- [x] T003 [P] Add migration stubs for reference tables (teams, players, player_team_history) and KG tables (events, event_entities, claims, claim_sources, event_articles, sources) under `migrations/versions/`

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
- [x] T004 [P] Contract test GET /events in `tests/contract/test_events_list.py` (based on `contracts/openapi.yaml`)
- [x] T005 [P] Contract test GET /events/{event_id} in `tests/contract/test_event_details.py`
- [x] T006 [P] Contract test GET /events/{event_id}/summary in `tests/contract/test_event_summary.py`
- [x] T007 [P] Integration test: article→event happy path in `tests/integration/test_e2e_pipeline.py` asserting event created, entities linked, citation present, confidence computed
- [x] T008 [P] Integration test: dedup clustering within 5 days in `tests/integration/test_incremental_ingestion.py` asserting same event clustered and confidence increases with corroboration
- [x] T009 [P] Integration test: allowlisted claim extraction in `tests/integration/test_filtering_pipeline.py` asserting claim added with provenance and status

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [x] T010 [P] Models: create reference tables mapping in `src/models` for teams, players, player_team_history (SQLAlchemy/Pydantic as used in repo)
- [x] T011 [P] Models: create KG tables mapping in `src/models` for events, event_entities, claims, claim_sources, event_articles, sources
- [x] T012 Service: reference loader using `nfl_data_py` to populate Supabase reference tables in `src/services/nfl_reference_loader.py` with cadence hooks
- [x] T013 Service: event signature and clustering (5-day window) in `src/services/simple_pipeline.py` or `src/services/pipeline.py` respecting idempotence
- [x] T014 Service: confidence computation per spec in `src/services/metrics.py` or a new `src/services/confidence.py`
- [x] T015 Service: claim extraction guardrailed by domain policy in `src/services/relevance_filter.py` or `src/services/rule_filter.py` with provenance recording
- [x] T016 Service: summary generator that cites after every fact in `src/services/log_aggregator.py` or a new `src/services/summary.py`
- [x] T017 API: implement GET /events endpoint in existing CLI/API surface (add a minimal http layer or CLI command) consistent with `contracts/openapi.yaml`
- [x] T018 API: implement GET /events/{event_id}`
- [x] T019 API: implement GET /events/{event_id}/summary`

## Phase 3.4: Integration
- [ ] T020 Wire ingestion to existing RSS/sitemap pipeline (`src/services/feed_ingester.py`, `src/services/rss_parser.py`, `src/services/sitemap_parser.py`) to call article→event path
- [ ] T021 Ensure Supabase repositories exist or add them under `src/database/repositories/` for events, claims, links, and reference tables
- [ ] T022 Logging/audit: log evidence additions, merges/splits, confidence recalculations in `src/services/log_aggregator.py`
- [ ] T023 Observability counters: per-run metrics (events created/updated, claims added, merge/split, latency, LLM hit-rate) in `src/services/metrics.py`

## Phase 3.5: Polish
- [ ] T024 [P] Unit tests for confidence computation edge cases in `tests/unit/test_metrics.py`
- [ ] T025 [P] Unit tests for signature hashing and idempotence in `tests/unit/test_async_utils.py` or new `tests/unit/test_signature.py`
- [ ] T026 [P] Update docs `docs/api.md` to describe the new endpoints and examples
- [ ] T027 [P] Update `specs/002-vision-the-nfl/quickstart.md` with concrete CLI/API calls
- [ ] T028 Performance sanity: run on 1,000 articles; ensure median time-to-event < 20 min; document results in `tests/performance/test_performance_1000.py`

## Dependencies
- T004–T009 before T010–T019 (TDD)
- T010 blocks T012, T021
- T011 blocks T013–T015
- T013 blocks T020
- T014 blocks T023, summaries confidence display
- T017–T019 depend on models/services

## Parallel Execution Examples
```
# Contracts and integration tests in parallel
Task: "Contract test GET /events in tests/contract/test_events_list.py"
Task: "Contract test GET /events/{event_id} in tests/contract/test_event_details.py"
Task: "Contract test GET /events/{event_id}/summary in tests/contract/test_event_summary.py"
Task: "Integration test article→event in tests/integration/test_e2e_pipeline.py"
Task: "Integration test clustering in tests/integration/test_incremental_ingestion.py"
Task: "Integration test allowlisted claims in tests/integration/test_filtering_pipeline.py"

# Model creation in parallel
Task: "Models for reference tables in src/models"
Task: "Models for KG tables in src/models"
```

## Validation Checklist
- [ ] All contracts have corresponding tests (T004–T006)
- [ ] All entities have model tasks (T010–T011)
- [ ] All tests come before implementation
- [ ] Parallel tasks touch different files only
- [ ] Each task lists exact files or directories
- [ ] Observability and audit trails included
