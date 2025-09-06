# Implementation Plan: Core Pipeline

**Branch**: `001-core-pipeline` | **Date**: 2025-09-06 | **Spec**: /specs/001-core-pipeline/spec.md
**Input**: Feature specification from `/specs/001-core-pipeline/spec.md`

## Branching & Commits
- Create a feature branch in GitHub before development: `feature/001-core-pipeline`.
- Open a draft PR early and keep it updated.
- Use Conventional Commits for every commit (e.g., `feat(models): add Article schema (T016)`).

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
4. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, or `GEMINI.md` for Gemini CLI).
   ✅ COMPLETED: All Phase 1 deliverables created
6. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
7. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
   - Analyze contracts and data models for implementation tasks
   - Identify parallel vs sequential task dependencies
   - Plan testing strategy (TDD: tests before implementation)
   - Estimate task complexity and time
8. STOP - Ready for /tasks command

**Phase 2 Planning Notes**:
- Break down by component: ingester, filter, LLM, storage, CLI
- Use contracts as task boundaries
- Ensure test-first approach (RED-GREEN-Refactor)
- Plan for integration testing between components
- Consider database migration tasks
- Include setup tasks (dependencies, environment, CI/CD)
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Build the core NFL news processing pipeline that ingests from RSS feeds and sitemaps, filters for NFL relevance using rules and LLM checks, and stores clean data in Supabase with strict de-duplication and incremental ingestion via per-source watermarks. Technical approach: Python-based data pipeline with SQLite for local testing and Supabase for production storage.

### Ingestion Integration (RSS + Sitemaps)
- Configuration-driven sources in `config/feeds.yaml` (type: rss|sitemap, url, publisher, nfl_only, enabled)
- RSS: Fetch via HTTP, parse with `feedparser`, normalize entries → standardized Article
- Sitemaps: Fetch XML, parse URLs + lastmod with `xml` parser; if sitemap points to article pages with sufficient metadata in URL/title, standardize as Article; no crawling of article pages
- Concurrency: Up to `max_parallel_fetches` from config; per-source timeout and retries
- Dedupe by normalized URL before downstream filtering
 - Incremental ingestion: Maintain per-source watermark (latest publication_date or last seen URL) to skip already-processed items; database unique(url) as final guard
 - Dynamic sitemap templating: For NFL monthly sitemap, construct URL at runtime as `https://www.nfl.com/sitemap/html/articles/{YYYY}/{MM}` using current UTC year and zero-padded month (e.g., 2025/09)

## Technical Context
**Language/Version**: Python 3.11  
**Primary Dependencies**: feedparser, requests, supabase-py, openai, pydantic  
**Storage**: SQLite (local/testing) → Supabase Postgres (production)  
**Testing**: pytest with contract/integration tests  
**Target Platform**: Linux server (CLI-based pipeline)  
**Project Type**: single (data processing pipeline)  
**Performance Goals**: Process 1000+ articles/day, <5min end-to-end  
**Constraints**: No scraping/crawling, respect publisher terms, transparent logging  
**Scale/Scope**: 32 NFL teams, 1000+ articles/day, single pipeline instance  

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**No Scraping or Crawling**:
- Using only public feeds, metadata, URL context? (no full crawling)
- Respecting publisher terms?

**Transparent and Auditable Filtering**:
- Logging all decisions with scores?
- Preserving sources, dates, model outputs?

**LLM-Assisted Relevance Checks**:
- Using small LLMs for ambiguous items?
- Analyzing only headlines/titles/URLs (no long excerpts)?

**Scalable and Cost-Effective**:
- Handling 1,000+ articles/day?
- Layering cheap rules before LLM checks?

**Structured Data Foundation**:
- Transforming to structured information?
- Enabling clustering and entity tracking?

**Storage Parity & Migrations**:
- Single migration source applied to SQLite and Supabase?
- Schema parity verified (indexes, unique URL, FKs)?
- Local tests run against SQLite and a Supabase test schema?

## Project Structure

### Documentation (this feature)
```
specs/001-core-pipeline/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure]
```

**Structure Decision**: Option 1 (single project) - data processing pipeline with CLI interface

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved
