# plan-codex-codex-sprint-r19-deepseek-outcome-copy-drift-guard

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `master` |
| Source Task | `codex-sprint-r19-deepseek-outcome-copy-drift-guard` |
| Status | integrated |
| Created | 2026-07-05 21:20 +1000 |
| Source HEAD | `6ba0805` |

## Plan Summary

Backend/frontend outcome-copy parity guard with documented exception for interpreted_ready

## My Understanding

Map every BernieBookingOutcomeKind (10 values) through bernieReviewTransition() to its transition.state, then verify each transition.state has copy coverage in BERNIE_STATUS_COPY, BERNIE_HEADLINE_COPY, or the hardcoded chains in bernieStatusCopyForPayload/bernieHeadlineCopyForPayload. 1 outcome (interpreted_ready) is transient and has no dedicated copy; all others are covered. Produce a Python test that proves the map and a documented exception.

## Intended Surface / Boundary

app/services/diary/outcomes.py enum, docs/diary/diary.js copy constants and bernieReviewTransition(), tests/test_bernie_booking_outcomes.py

## Out Of Scope

Live AI calls, prompt injection, broad frontend refactors, copy redesign, database migrations, appointment mutation behaviour, GitHub Pages deploy edits, other outcome files (route_outcome_events, session routes, etc.)

## Files I Expect To Edit

tests/test_bernie_outcome_copy_drift_guard.py (new), orchestration/sprint_closeout.md (update)

## Implementation Steps

1. Create Python test file with explicit mapping table. 2. Extract JS constants as test data (mirror of current diary.js values). 3. Define each backend kind plus frontend state plus copy path. 4. Mark interpreted_ready as deliberate transient exception. 5. Run py_compile / pytest. 6. Record in sprint closeout.

## Visual / Behavioural Acceptance Checks

pytest passes proving every BernieBookingOutcomeKind has coverage or a documented exception. No production code touched. No visible UX copy changed.

## Risks / Ambiguities

interpreted_ready is transient and not user-visible for long; its copy is auto-generated. If a future sprint adds a permanent UI path that exposes interpreted_ready, the exception must be revisited.

## Codex Plan Review

- Review result: accepted and integrated with Ariadne improvement to parse `docs/diary/diary.js` copy dictionaries directly rather than mirroring them by hand.
- Required changes before implementation: none beyond the parser improvement applied during integration.
- Approved to proceed: yes
