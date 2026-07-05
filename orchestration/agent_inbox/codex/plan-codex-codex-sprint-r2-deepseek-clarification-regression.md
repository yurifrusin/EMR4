# plan-codex-codex-sprint-r2-deepseek-clarification-regression

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/sprint-r2-deepseek-clarification-regression` |
| Source Task | `codex-sprint-r2-deepseek-clarification-regression` |
| Status | pending_plan_review |
| Created | 2026-07-05 14:13 +1000 |
| Source HEAD | `89cb837` |

## Plan Summary

DeepSeek Flash regression lane for R2 clarification merge invariants

## My Understanding

Add independent regression coverage that catches patient/practitioner/date/time field loss across Bernie clarification replies while Claude owns the production merge implementation.

## Intended Surface / Boundary

Tests and fixture validation around tests/bernie_scenarios, tests/test_bernie_scenario_integrity.py, session-route/store tests if useful; no production or UI ownership.

## Out Of Scope

Production implementation, Diary UI, live provider calls, GraphRAG, Codex GUI model switching, global config, and broad corpus authorship.

## Files I Expect To Edit

tests/bernie_scenarios/replay.py; tests/test_bernie_scenario_integrity.py; tests/test_bernie_session_store.py or tests/test_bernie_session_routes.py if a focused regression is warranted; tests/fixtures/bernie_scenarios read-only unless a schema issue is found.

## Implementation Steps

Review current replay/assertion gaps; add preserved-field fixture integrity if schema supports it; add focused store/route regression for clarification_reply preservation; review xfail fixtures; run py_compile/focused pytest/git diff --check where sandbox permits.

## Visual / Behavioural Acceptance Checks

Regression coverage fails if clarification_reply loses previously resolved patient, practitioner, date, or time; fixture checks do not create false positives; no UI or production code changes.

## Risks / Ambiguities

DeepSeek sandbox may block Python/git; harness support for preserved fields may be too broad for this lane; exact conflict-resolution semantics may depend on Claude's implementation.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
