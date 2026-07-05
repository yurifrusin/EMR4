# Plan: Sprint R5 Adversarial Scenario Review

## My Understanding

The EMR4 repo has 18 YAML scenario fixtures under tests/fixtures/bernie_scenarios/. Only 2 (the harness_demo_*.yaml ones) are executable by the replay harness — they contain \ction:\ fields (normalize/search/select/confirm) that map to deterministic HTTP endpoints. The remaining 16 are natural-language "corpus memory" fixtures with \user:\ text fields and \expect.outcome:\ — these test Bernie's NLU/intent layer, which the replay harness cannot exercise.

Sprint R5's product goal is to "promote the best R3/R4 receptionist-domain corpus memory into executable Bernie replay coverage where the current harness can express it cleanly." This adversarial review lane must independently evaluate which R3/R4 fixtures are promotable, which must remain corpus memory, and why.

## Intended Surface / Boundary

- **Surface analysed**: tests/fixtures/bernie_scenarios/*.yaml (all 18 files), tests/bernie_scenarios/loader.py, replay.py, test_scenario_replay.py, test_bernie_scenario_integrity.py
- **Surface affected by recommendations**: none directly — this is a review artifact with no production code changes
- **Nearby surfaces NOT affected**: app/ backend code, diary UI, taskpane, docs, orchestration/* (except this plan file)

## Out of Scope

- No edits to app/ backend code, no diary UI, no taskpane/Word assets
- No edits to the replay harness (loader.py, replay.py, test_scenario_replay.py) — the implementation lane owns those
- No edits to corpus YAML fixtures — the implementation lane owns fixture promotion
- No raw appointment mutation endpoint policy changes
- No live Gemini/Vertex calls, no session-store redesign

## Classification: Which R3/R4 Fixtures Can Become Executable

### R4 Fixtures

| Fixture | Promotable? | Rationale |
|---|---|---|
| absolute_past_date_blocked.yaml | **YES — one candidate** | The normalizer (test_bernie_slot_normalizer.py) already blocks absolute past dates with \equested_date_in_past\. An executable replay scenario would add end-to-end HTTP coverage: normalize with a past date_from → expect safe:false. LIMITATION: the harness's \_get_nested\ helper uses simple dotted-path traversal and does NOT support array indexing (e.g., \locks[0].code\), so block-code assertion is blocked without harness enhancement. Minimal assertion: \safe: false\ only. |
| same_day_past_window_clarify.yaml | **No** | Tests NLU behaviour: "Book today at 10 AM" when clinic time is 15:00 — needs conversational context and intent parsing, not the deterministic pipeline. |
| stale_reference_date_confirmation_blocked.yaml | **No** | Already tagged xfail with explicit "natural-language corpus memory only" reason. Session-freshness guard not modeled by the pipeline. |

### R3 Fixtures

| Fixture | Promotable? | Rationale |
|---|---|---|
| stale_session_concurrency_conflict.yaml | **No** | Tests extension endpoint + revision conflict. The replay harness covers only normalize→search→select→confirm. Extension/update flows use different endpoints not in the harness. |
| stale_session_reload_blocking.yaml | **No** | Tests browser-reload UI behaviour and session-freshness invariant. Non-deterministic, UI-level. |
| stale_session_correction_and_pivot.yaml | **No** | Tests NLU correction semantics: overwriting resolved fields mid-clarification, intent pivot from booking→extension. Requires NLU layer. |
| refresh_does_not_resurrect_stale_latest_message.yaml | **No** | Tests stale reference-date session guard. Session-level invariant, not pipeline-modelable. |
| booking_to_extension_switch_during_clarification.yaml | **No** | Tests NLU category pivot from booking to extension during a clarification turn. Requires NLU + extension endpoints. |

### Other Non-R3/R4 Corpus Fixtures

| Fixture | Promotable? | Rationale |
|---|---|---|
| booking_clarify_long_duration_preserves_practitioner.yaml | No | xfail; NLU clarification merge |
| booking_clarify_long_duration_preserves_patient_date_time.yaml | No | NLU clarification merge |
| booking_no_matching_times_only_after_slot_search_empty.yaml | No | NLU outcome routing |
| booking_roster_unavailable_distinct_from_no_slots.yaml | No | NLU outcome routing |
| booking_tomorrow_not_blocked_by_patient_booking_today.yaml | No | NLU collision advisory |
| clarification_reply_merges_missing_field_only.yaml | No | xfail; NLU clarification merge |
| confirm_required_before_create_or_update.yaml | No | NLU confirmation gate |
| extend_by_15_minutes_distinct_from_make_30_total.yaml | No | NLU extension semantics |

## Harness Constraint Findings

### Limitation 1: \_get_nested\ lacks array/block-code access
The replay harness's \_get_nested\ helper splits a dotted path by "." and traverses dict keys. It does not support bracket indexing like \locks[0].code\. This means:
- The normalize endpoint's block array (e.g., \{"blocks": [{"code": "requested_date_in_past"}]}\) cannot be asserted via \expect.fields\
- Only top-level scalar fields like \safe: bool\ are assertable
- **For the implementation lane**: Either enhance \_get_nested\ to support array-index access, or use the \safe: false\ assertion as a loose proxy

### Limitation 2: No NLU/LLM assertion path
The harness deliberately forbids AI provider calls (monkeypatch guard). This is correct for a deterministic pipeline test but means no corpus fixture with \user:\ turns can ever be promoted without a fundamentally different test path (e.g., a separate NLU assertion harness not in scope for this sprint).

### Limitation 3: Only 4 endpoints covered
The replay harness hardcodes exactly 4 URLs:
- normalize → /slot-search/normalize
- search → /slot-search/normalized
- select → /slot-search/selection
- confirm → /create/confirm-bernie
Extension, update, correction, stale-session, and direct-mutation endpoints are not covered. Any fixture exercising those flows is non-promotable until the harness is extended.

## Recommendation

**Promote exactly 1 fixture: \bsolute_past_date_blocked.yaml\**, with the caveat that block-code assertions require either harness enhancement or accepting a weaker \safe: false\ assertion.

For the implementation lane:
1. Create \	ests/fixtures/bernie_scenarios/absolute_past_date_blocked_executable.yaml\ with \ction: normalize\ turns
2. Assert \safe: false\ via \expect.fields\
3. Add \orbidden_outcomes: [provider_called, appointment_written, audit_written]\
4. Document that block-code (requested_date_in_past) assertion is blocked by harness \_get_nested\ limitation
5. All other R3/R4 fixtures remain valid corpus memory with no xfail change needed
6. Do not modify the existing \bsolute_past_date_blocked.yaml\ — keep it as natural-language corpus memory

### What remains corpus memory (intentionally)

The other R3/R4 fixtures describe valuable domain knowledge about:
- Concurrency conflict semantics (extension + revision)
- Browser-reload staleness
- NLU correction merge and intent pivot
- Same-day past-window NLU clarification

These are not gaps in coverage — they are legitimately outside the current harness's scope. Product decision: accept them as NLU-level acceptance criteria that current pytest replay cannot test, and defer to a later NLU-specific harness or the existing manual/visual review path.

## Steps

1. [in_progress] Read all 18 YAML fixtures and classify promotability
2. [pending] Write adversarial review artifact documenting classification and findings
3. [pending] Write plan packet for submission
4. [pending] Submit plan to Codex orchestrator via plan/submit protocol (or manual equivalent)
5. [pending] Stop — do not implement until 'complete sprint task' approval

## Acceptance

- Plan shows clear classification of every R3/R4 fixture as promotable or non-promotable
- Plan identifies harness constraints that limit promotion scope
- Plan states minimal viable executable promotion for the implementation lane
- Plan does not overlap the implementation lane's file ownership

## Risks / Ambiguities

- **Harness enhancement boundary**: If the orchestrator decides that \_get_nested\ enhancement is needed for proper past-date assertion, this may blur the boundary between review and implementation. The review lane should flag the limitation, not fix it.
- **Sprint scope creep**: Only 1 of 18 fixtures is promotable and even that has a harness limitation. If promotion is the sprint's hard requirement, the implementation lane may need to accept the weaker assertion or negotiate scope expansion.
- **Existing unit coverage overlap**: The past-date guard is already tested at unit level (test_bernie_slot_normalizer.py, test_bernie_supervised_booking_wrapper.py, test_bernie_confidence_policy.py). The value of end-to-end HTTP replay is genuine but not critical — unit tests cover the function-level semantics.
- **Future fixture drift**: If the implementation lane adds endpoints or harness actions, the promotability classification changes. This review is current as of Sprint R5 baseline (fd0e647).