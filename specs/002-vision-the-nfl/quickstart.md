# Quickstart (Phase 1)

This validates the end-to-end flow using existing RSS/sitemap ingestion.

## Prereqs
- Supabase credentials configured (as per project README)
- Migrations applied; reference tables populated from nfl_data_py

## Steps
1. Start ingestion of RSS/sitemaps (existing command/cron) to populate articles.
2. Run the article→event pipeline:
   - Classify relevance (rules → small LLM for edge cases)
   - Extract type/subtype, entities, temporal hints
   - Upsert Event with 5-day signature window
   - Attach Articles; compute confidence; optionally extract structured Claims (allowlisted)
3. Inspect results:
   - Query Events by team/player; verify citations and confidence
   - Check summaries show citations and "unknown" where applicable

## Expected Outcome
- New or updated Events with citations and computed confidence
- Deduped clustering for near-duplicate reports
- Structured Claims for allowlisted sources when present
