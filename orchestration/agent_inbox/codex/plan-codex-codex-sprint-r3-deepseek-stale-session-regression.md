# plan-codex-codex-sprint-r3-deepseek-stale-session-regression

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/sprint-r3-deepseek-stale-session-regression` |
| Source Task | `codex-sprint-r3-deepseek-stale-session-regression` |
| Status | pending_plan_review |
| Created | 2026-07-05 14:56 +1000 |
| Source HEAD | `f8bc6c8` |

## Plan Summary

DeepSeek Flash regression lane will add focused stale-session/stale-revision tests only, no production ownership.

## My Understanding

R3 hardens stale Bernie session revision/context handling after R2 clarification merge. Existing R2 coverage proves baseline stale revision, route 409s, clarification merge, stale evidence frames, and scenario integrity; the gap is combined stale revision plus context frames, diary navigation, intent switches, server outcomes, and no stale mutation.

## Intended Surface / Boundary

Test-only regression lane around app/services/bernie/session_store.py, app/routers/appointments.py session routes, Bernie context frames, and optional scenario fixture loading. No visible UI surface should change.

## Out Of Scope

Production implementation, Diary UI, taskpane/Word, live Gemini/Vertex calls, GraphRAG/MCP/indexer automation, global config/model switching, broad unrelated test rewrites.

## Files I Expect To Edit

Expected new test: tests/test_deepseek_sprint_r3_stale_session_regression.py. Optional fixture: tests/fixtures/bernie_scenarios/stale_session_revision_clarification.yaml. Existing R2 tests should not be edited unless a tiny adjacent assertion is unavoidable.

## Implementation Steps

1. Add stale revision plus context frame rejection tests. 2. Add stale diary_navigated revision-order tests. 3. Add stale and fresh intent-switch tests. 4. Add server outcome stale revision fail-closed tests. 5. Add active session replacement edge tests. 6. Attempt a slim route-level stale confirm/session-coordinate test only if not over-complex. 7. Add optional YAML scenario if loader support is straightforward.

## Visual / Behavioural Acceptance Checks

Every stale test asserts rejection and unchanged revision/events/state; fresh R2 clarification behavior still passes; no appointment/audit mutation from stale replies; focused pytest and git diff checks pass when run by Ariadne.

## Risks / Ambiguities

Some R2 tests already cover baseline staleness, so this lane must add combinational value. Confirm-route stale coordinate tests may be too mock-heavy and can be left as Ariadne residual review. DeepSeek sandbox cannot reliably run Python/git submit, so Ariadne may verify and submit.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
