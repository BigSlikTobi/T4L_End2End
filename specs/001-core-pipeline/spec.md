# Feature Specification: Core Pipeline

**Feature Branch**: `001-core-pipeline`  
**Created**: 2025-09-06  
**Status**: Draft  
**Input**: Constitution document: `/memory/constitution.md`

## Workflow Policy
- All development work must occur on a dedicated GitHub feature branch created before coding starts.
- Branch naming: `feature/<id>-<slug>` (e.g., `feature/001-core-pipeline`).
- Commits must follow Conventional Commits (e.g., `feat(services): add pipeline orchestrator (T038)`).

## Execution Flow (main)
```
1. Parse constitution document from Input
   → If not found: ERROR "No constitution at {path}"
2. Extract core requirements from "What We Are Doing" section
   → Identify: ingestion, filtering, LLM checks, storage
3. For each unclear aspect:
   → Mark with [NEEDS CLARIFICATION: specific question]
4. Fill User Scenarios & Testing section
   → If no clear pipeline flow: ERROR "Cannot determine core functionality"
5. Generate Functional Requirements
   → Each requirement must be testable
   → Mark ambiguous requirements
6. Identify Key Entities (articles, feeds, filters)
7. Run Review Checklist
   → If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
   → If implementation details found: ERROR "Remove tech details"
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT the pipeline does and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

### Section Requirements
- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation
When creating this spec from a user prompt:
1. **Mark all ambiguities**: Use [NEEDS CLARIFICATION: specific question] for any assumption you'd need to make
2. **Don't guess**: If the prompt doesn't specify something (e.g., "login system" without auth method), mark it
3. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
4. **Common underspecified areas**:
   - User types and permissions
   - Data retention/deletion policies  
   - Performance targets and scale
   - Error handling behaviors
   - Integration requirements

## User Scenarios
### Primary User Flow
1. **News Ingestion**: System automatically fetches articles from RSS feeds and sitemaps
2. **Relevance Filtering**: Articles are filtered for NFL content using rules and LLM analysis
3. **Data Storage**: Clean NFL articles are stored with metadata for auditability
4. **Pipeline Monitoring**: System provides transparent logging of all decisions

### Edge Cases
- Ambiguous headlines (e.g., "Hurts runs for 10 TDs") correctly identified as NFL
- Non-NFL content (NBA, MLB, soccer) excluded upfront
- Duplicate articles from multiple sources handled gracefully
- Feed failures don't stop the entire pipeline

## Functional Requirements

### FR-001: News Ingestion
- System shall ingest articles from RSS feeds and sitemaps
- System shall standardize article metadata (URL, title, publisher, publication date)
- System shall handle multiple feed formats and sources
 - System shall support dynamic sitemap URL construction for sources whose sitemap path depends on current date (e.g., NFL monthly sitemap `.../articles/{YYYY}/{MM}` using current UTC year and zero-padded month)

### FR-002: NFL Relevance Filtering
- System shall apply rule-based filters (team names, URL paths, keywords)
- System shall use negative filters to exclude non-NFL content
- System shall support endpoint-level NFL-only flags

### FR-003: LLM-Based Classification
- System shall use small LLMs for ambiguous item classification
- System shall analyze only headlines/titles and URLs (no full content)
- System shall log LLM decisions with scores and confidence

### FR-004: Database Storage
- System shall store clean NFL articles in structured schema
- System shall include audit metadata (relevance score, LLM version, confidence)
- System shall ensure data integrity and uniqueness

### FR-005: Transparency and Auditability
- System shall log all filtering decisions with scores
- System shall preserve source information and timestamps
- System shall provide pipeline monitoring and error reporting

### FR-006: Incremental Ingestion & De-duplication
- System shall maintain a per-source watermark (latest processed publication date and/or URL) and only process items newer than the watermark
- System shall deduplicate by URL across all sources and runs
- On equal timestamps or missing dates, system shall fall back to URL-based de-duplication
- The database shall enforce uniqueness on article URL and skip/ignore duplicates gracefully

## Key Entities
- **Article**: Core data with URL, title, publisher, publication_date, content_summary
- **Feed**: Source configuration with URL, type (RSS/sitemap), nfl_only flag
- **Filter**: Rule definition with pattern, type (include/exclude), priority
- **Decision**: Audit log with article_id, filter_id, score, llm_model, confidence

## Non-Functional Requirements
- **Performance**: Process 1000+ articles per day
- **Reliability**: Handle feed failures gracefully
- **Scalability**: Support all 32 NFL teams
- **Cost**: Minimize LLM usage through layered filtering
- **Compliance**: No scraping/crawling, respect publisher terms

## Testing Requirements
- **Unit Tests**: Individual components (parsers, filters, LLM client)
- **Integration Tests**: End-to-end pipeline with mock feeds
- **Contract Tests**: Database schema and API compatibility
- **Performance Tests**: 1000+ articles/day throughput
- **Edge Case Tests**: Ambiguous content classification accuracy

## Review Checklist
- [ ] All requirements are testable and unambiguous
- [ ] No implementation details specified
- [ ] Edge cases identified and covered
- [ ] Performance and scalability requirements defined
- [ ] Compliance and legal requirements addressed
- [ ] Auditability and transparency requirements included
