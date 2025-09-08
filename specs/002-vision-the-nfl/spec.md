# Feature Specification: NFL Event Knowledge Graph

**Feature Branch**: `[002-vision-the-nfl]`  
**Created**: 2025-09-08  
**Status**: Draft  
**Input**: Vision to build a live, provenance-aware knowledge graph that turns raw NFL news articles into Events, Entities, and Claims with timestamps, confidence, and citations; supports deduped timelines, auditing, summaries with citations, and downstream content generation.

## Execution Flow (main)
```
1. Parse user description from Input
   → If empty: ERROR "No feature description provided"
2. Extract key concepts from description
   → Identify: actors, actions, data, constraints
3. For each unclear aspect:
   → Mark with [NEEDS CLARIFICATION: specific question]
4. Fill User Scenarios & Testing section
   → If no clear user flow: ERROR "Cannot determine user scenarios"
5. Generate Functional Requirements
   → Each requirement must be testable
   → Mark ambiguous requirements
6. Identify Key Entities (if data involved)
7. Run Review Checklist
   → If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
   → If implementation details found: ERROR "Remove tech details"
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
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
   - Security/compliance needs

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
As a football fan or content editor, I want timely, trustworthy event records (signings, injuries, trades, game recaps) consolidated from multiple sources with clear confidence and citations, so I can understand what happened, who’s involved, and create content that is consistent and auditable.

### Acceptance Scenarios
1. Given a new reputable article about a player signing, when the system processes the item, then a single Event is present with type "transaction/signing," the involved Team and Player attached, first_seen set, confidence calculated, and at least one citation to the source article.
2. Given two differently worded articles about the same event within a short window, when both are processed, then they are clustered into the same Event, citations include both, and confidence increases due to corroboration.
3. Given an allowlisted source that includes clear factual details (e.g., contract years and amount), when processed, then a structured Claim is added to the Event with provenance and a confidence appropriate to source policy.
4. Given conflicting details from lower-tier sources, when processed, then the system records evidence but keeps Event confidence conservative and marks discrepancy until high-tier corroboration arrives.
5. Given a later correction or update, when processed, then the Event and/or Claims are updated, last_seen is revised, and the summary reflects the change with updated citations.

### Edge Cases
- Ambiguous or pun-heavy headlines with missing entities → system defers to low-confidence hints and awaits corroboration.
- Multiple similar events (e.g., two extensions on the same team the same day) → ensure signature prevents cross-association.
- Rumor-only items → recorded with low confidence and status "rumor," excluded from high-confidence feeds unless promoted.
- Corrections that invalidate earlier claims → prior claims marked superseded; summaries update accordingly.
- Out-of-season or off-calendar events → still captured; temporal context marked as preseason/offseason.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST classify incoming article items as in-scope NFL event news or out-of-scope, using title, URL, and publisher metadata.
- **FR-002**: For in-scope items, System MUST extract an Event type and subtype (e.g., transaction/signing, injury/out, game/recap).
- **FR-003**: System MUST identify and normalize referenced Teams and Players to canonical identities.
- **FR-004**: System MUST capture temporal context when present (phase and/or week) or mark it unknown when not derivable.
- **FR-005**: System MUST construct an Event signature from type plus key entities and a 5-day time window (120 hours, rolling from first_seen), and use it to attach evidence to an existing Event or create a new one.
- **FR-006**: System MUST deduplicate near-duplicate reports about the same real-world event and cluster them under a single Event.
- **FR-007**: System MUST record first_seen when an Event is created and update last_seen as new evidence arrives.
- **FR-008**: System MUST associate source Articles to Events with role, source tier, and per-article confidence.
- **FR-009**: System MUST support structured Claims for Events (e.g., contract terms, injury status) when extractable from permitted metadata, including kind, values, confidence, and status.
- **FR-010**: System MUST record provenance for each Claim, linking to contributing Articles and weighting when applicable.
- **FR-011**: System MUST compute an Event-level confidence based on source mix, corroboration count, and cross-source consistency, and update it as evidence changes.
- **FR-012**: System MUST enforce per-domain policy modes (e.g., strict, preview, provider-context) that govern what metadata can be used for claims and summaries.
- **FR-013**: System MUST behave idempotently by upserting Articles by URL, Events by signature within the defined time window, and Claims by normalized key.
- **FR-014**: System MUST maintain an audit trail of changes to Events and Claims with timestamps and reasons (e.g., new evidence, correction, merge/split).
- **FR-015**: System MUST provide controlled operations to merge duplicate Events and to split conflated Events, preserving provenance.
- **FR-016**: System MUST provide an Event-level human-readable summary: one-line overview plus bullet points, each with citations after every fact.
- **FR-017**: Users MUST be able to browse and filter Events by team, player, type/subtype, temporal context, and confidence threshold.
- **FR-018**: Users MUST be able to subscribe to alerts for specific teams, players, or event types and receive notifications for new or updated high-confidence Events.
- **FR-019**: System MUST report run-level metrics including counts of created/updated Events and Claims, merges/splits, average processing latency, and model usage rate.
- **FR-020**: System MUST present unknown values explicitly as "unknown" rather than inferring or fabricating data in summaries or claims.
- **FR-021**: System MUST support event and claim status states (e.g., rumor, reported, confirmed, superseded) with clear promotion rules.
- **FR-022**: System MUST ensure every fact presented in user-facing summaries has at least one citation.
- **FR-023**: System MUST support partner-facing health metrics (coverage by team, time-to-event, corroboration rate) accessible for review.

- **FR-024**: System MUST compute the Event confidence score S and assign status per the "Confidence Computation and Status Thresholds" rules below.
- **FR-025**: System MUST apply hysteresis to avoid oscillation: promote at S ≥ 65 (Reported) and S ≥ 85 (Confirmed); demote at S < 55 and S < 75 respectively, and on explicit retraction by an official source.
- **FR-026**: System MUST deduplicate evidence by domain for corroboration and cap the number of counted sources so that no single domain overwhelms the score.

- **FR-027**: System MUST source canonical Team and Player lexicons from the NFL_DATA_PY data feed and persist them as separate reference tables in the operational database (Supabase/Postgres), not intermixed with event/claim tables.
- **FR-028**: System MUST maintain these reference tables with a defined cadence: daily in-season, weekly off-season, and support on-demand manual refresh for breaking changes.
- **FR-029**: System MUST provide stable identifiers and disambiguation: team_id (slug), player_id, names/aliases, position, and player_team_history, enabling reliable entity linking from headlines.

- **FR-030**: Supabase (Postgres) MUST be the authoritative operational database for Events, Claims, evidence links, Entities, and reference lexicons; no alternative primary datastore may be used for this feature.
- **FR-031**: All data access and integrations for this feature MUST use the project’s provided Python packages/libraries (approved internal packages) for Supabase and data handling to ensure consistency and observability.

#### Confidence Computation and Status Thresholds (normative)

Definitions
- Unique source: a distinct publishing domain or official team/NFL property. Multiple articles from the same domain count once for corroboration.
- Source tiers (policy-controlled):
   - Tier A (Official): team sites, NFL.com, formal league statements → weight w=0.60
   - Tier B (Major): nationally reputable outlets/beat reporters → weight w=0.35
   - Tier C (Other): all others → weight w=0.20
   - Use at most the top 4 unique sources by tier for scoring.
- Consistency scope: values for key attributes within an Event (e.g., contract years/total, injury status). Contradictions are measured per attribute.

Components (each in [0,1])
- Evidence strength E: E = 1 − Π_i (1 − w_i), over the selected unique sources i. (Diminishing returns for additional sources.)
- Corroboration Cb: Let u = number of unique sources (deduped by domain). Cb = min(1, (u − 1) / 3). (1 source→0.0; 2→0.33; 4+→1.0)
- Consistency K: If any contradictions on key attributes exist, K = consistent_count / (consistent_count + contradictory_count); else K = 1. For Event-only items without claims, K = 1 unless explicit contradictions are detected across headlines.
- Official boost O: O = 1 if any Tier A official source is present; else 0.
- Rumor flag Rm: Rm = 1 if sources are labeled rumor-only or speculative; else 0.

Score and clamping
- Raw score: S_raw = 100 × (0.55·E + 0.25·Cb + 0.20·K) + 5·O − 10·Rm
- Final score: S = clamp(S_raw, 0, 100)

Status mapping (with hysteresis)
- Rumor: S < 40 OR (no Tier A/B sources AND unique_source_count < 2)
- Reported (promotion): S ≥ 65 OR (unique_source_count ≥ 2 AND K ≥ 0.60 and no explicit contradictions)
- Confirmed (promotion): S ≥ 85 AND (Tier A present OR (unique_source_count ≥ 3 AND includes ≥1 Tier B))
- Demotion: From Confirmed→Reported if S < 75 or an official retraction occurs. From Reported→Rumor if S < 55 or K < 0.40 due to contradictions.

Additional rules
- Per-domain cap: multiple articles from the same domain do not increase u and contribute only once to E (the highest-tier instance).
- Supersession: when a later correction changes a key attribute, mark prior claim as superseded; recompute K and S immediately.
- Unknowns: absence of claim values does not reduce K; only contradictions do. Unknowns must be stated as "unknown" in summaries.

#### Reference Data Policy (normative)
- Canonical sources: NFL_DATA_PY is the authoritative feed for Teams and Players.
- Storage: keep Teams and Players in separate reference tables within Supabase/Postgres; do not duplicate into event/claim tables.
- Minimum fields: teams(team_id/slug, names/aliases); players(player_id, name, aliases, position, optional player_team_history with date ranges).
- Freshness: refresh on the stated cadence; provide an admin-triggered refresh. Late or missing items must not break ingestion; unknown entities remain unlinked until the next refresh.

### Key Entities *(include if feature involves data)*
- **Event**: A single real-world occurrence (e.g., signing, injury, game recap). Attributes: type, subtype, temporal context, first_seen/last_seen, confidence, status. Relationships: involves Teams/Players; relates to Games; has Claims; has Articles as evidence; may supersede/ be superseded by other Events.
- **Team**: A canonical NFL team identity. Attributes: name/slug and aliases. Relationships: participates in Events; may be related to Players and Games.
- **Player**: A canonical NFL player identity. Attributes: name, aliases, position. Relationships: participates in Events; may have current/prior team memberships.
- **Game**: A specific NFL game instance. Attributes: season/week/phase and opponent context. Relationships: Events may relate to a Game (preview/recap/injury context).
- **Claim**: A structured fact associated with an Event (e.g., contract terms, injury designation). Attributes: kind, values, confidence, status. Relationships: evidenced by Articles.
- **Source**: A publisher/domain identity with a policy mode and tier. Relationships: publishes Articles.
- **Article**: An ingested news item. Attributes: URL, title, publisher. Relationships: published by a Source; cited as evidence for Events and Claims.

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [ ] No implementation details (languages, frameworks, APIs)
- [ ] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [ ] All mandatory sections completed

### Requirement Completeness
- [ ] No [NEEDS CLARIFICATION] markers remain
- [ ] Requirements are testable and unambiguous  
- [ ] Success criteria are measurable
- [ ] Scope is clearly bounded
- [ ] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [ ] User description parsed
- [ ] Key concepts extracted
- [ ] Ambiguities marked
- [ ] User scenarios defined
- [ ] Requirements generated
- [ ] Entities identified
- [ ] Review checklist passed

---
