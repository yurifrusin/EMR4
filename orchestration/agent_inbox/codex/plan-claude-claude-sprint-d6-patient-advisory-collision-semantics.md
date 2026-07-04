# plan-claude-claude-sprint-d6-patient-advisory-collision-semantics

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-d6-patient-advisory-collision-semantics` |
| Status | integrated |
| Created | 2026-07-04 16:32 +1000 |
| Source HEAD | `c4e793f` |

## Plan Summary

Lock Bernie existing_future_follow_up warning to day-level date-collision semantics with focused regression tests at the helper, interpret, and supervised routes; flag the date-range window gap for Codex. Investigation shows the warning gating already routes through has_existing_booking_on_requested_day, so the deliverable is regression-test hardening, not a semantics change.

## My Understanding

The existing_future_follow_up warning must fire only when a recognized patient's compact context shows a future booking on the requested booking day, not merely any future booking. The context FIELD existing_future_follow_up stays advisory (has any future booking) and must be preserved. Current master (HEAD c4e793f): both warning-emission paths in app/routers/appointments.py already route through has_existing_booking_on_requested_day (interpret enrichment ~line 3801, supervised booking ~line 5555), landed in hotfix 50b28c8. constraint.date_from is a typed date (schema line 505, parsed by the slot normalizer), so the day-level == comparison against entry.appointment_date is sound. The interpret route already has a negative different-day test (line 750) and a tomorrow-vs-today test (785), but its positive test (709) is vacuously conditional; the supervised route (test 440) only asserts the context field, never collision-vs-non-collision warning behaviour; and there are no direct unit tests for the helper. So semantics are already correct at code level; remaining D6 work is regression-test hardening that locks the contract.

## Intended Surface / Boundary

Backend domain plus pytest only. Affected: existing_future_follow_up advisory warning-emission semantics in app/routers/appointments.py (interpret enrichment and supervised booking) and the helper in app/services/bernie_patient_context.py, exercised via tests. NO UI surface changes: diary grid, booking-slot cards, status pills / lifecycle colours, waiting-room feed, command centre, and taskpane panels are all untouched. No frontend copy. This is server-side warning logic and its tests, not any visual panel or stacking behaviour.

## Out Of Scope

No frontend/UI copy. No GraphRAG. No persisted sessions or migrations. No broad API review. Do not suppress or alter patient_booking_context output. Do NOT change the context field existing_future_follow_up (stays advisory any-future-booking; interpret test 774 relies on it staying True for a different-day booking). No confirmation / write / booking-mutation semantics change. Do NOT expand BernieBookingContextEntry with start_time or add time-of-day window collision (schema change, out of scope).

## Files I Expect To Edit

tests/test_bernie_patient_context.py (add direct unit tests for has_existing_booking_on_requested_day). tests/test_bernie_interpret_booking_instruction.py (strengthen the vacuous positive collision test near line 709 into a deterministic same-day collision). tests/test_bernie_supervised_booking_wrapper.py (add same-day-collision-fires and different-day-no-warning tests). Expected production code changes: NONE by default (gating already correct). Only if Codex green-lights the range/window enhancement (see risks) would app/services/bernie_patient_context.py plus the two call sites in app/routers/appointments.py change.

## Implementation Steps

1. tests/test_bernie_patient_context.py: add unit tests for has_existing_booking_on_requested_day - requested_date None -> False; requested_date equal to a future_bookings entry date -> True; requested_date not among future_bookings -> False; empty future_bookings -> False. 2. tests/test_bernie_interpret_booking_instruction.py: replace the conditional positive test (709) with a deterministic one - recognized patient booked on exactly the requested day (pin a concrete date so normalization.constraint.date_from equals the booking date) and assert unconditionally that the existing_future_follow_up warning code AND an advisory_warning frame with source=patient_context are present and reception_policy.advisory_warnings_only is True. 3. tests/test_bernie_supervised_booking_wrapper.py: add (a) positive - recognized patient with a future booking ON the requested day -> existing_future_follow_up warning present and advisory_warning frame source=patient_context; (b) negative - recognized patient with a future booking on a DIFFERENT day -> patient_booking_context present with existing_future_follow_up True but NO existing_future_follow_up warning and no advisory_warning frame. 4. Verify: py_compile touched modules, focused pytest for the four Bernie test files (patient_context, interpret, supervised wrapper, context-frames/outcomes), git diff --check. 5. Fill Completion Notes and submit.

## Visual / Behavioural Acceptance Checks

Visual: NO UI change anywhere - diary grid, booking-slot cards, status pills, waiting room, and side panels are unchanged (backend + tests only). Behavioural: existing_future_follow_up warning appears ONLY when a recognized patient has a future booking on the requested day, at BOTH the interpret and supervised routes. Same-day/today or other-day future bookings remain in patient_booking_context (context field existing_future_follow_up still True) but do NOT emit the warning or the advisory_warning frame for a different requested day. All new and existing Bernie tests green; no confirmation/write semantics change.

## Risks / Ambiguities

1. KEY FINDING: both warning paths already route through has_existing_booking_on_requested_day (hotfix 50b28c8) and constraint.date_from is a typed date, so no production semantics change appears necessary - this sprint lands as regression-test hardening. If Codex intended an actual code fix, please confirm; the merge criteria (warning is date-collision based, context preserved, no write change) already hold at code level. 2. DAY vs WINDOW ambiguity: mission says requested booking day/window but both call sites pass only constraint.date_from, ignoring constraint.date_to. A range request (e.g. next week spanning date_from..date_to) with a booking mid-window currently produces NO warning. Making collision range-aware over [date_from,date_to] would be more faithful to window and stays consistent with existing negatives (tests 750, 785 are outside-window), but it changes the helper signature and conflicts with use-existing-helper + narrow-fix + preserve-output. Default: keep day-level; flag as optional follow-up for Codex to green-light rather than assume. 3. Context field existing_future_follow_up stays advisory (any future booking); interpret test 774 depends on this - not changed. 4. Positive tests must pin a concrete requested day; next-week normalization can resolve date_from to a range start not equal to the booking date, which is exactly why the current 709 test passes vacuously.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no


## Codex Integration Notes

Integrated in Sprint D6 closeout. Ariadne accepted the broad-context/narrow-warning semantics, kept the dedicated D6 regression module as canonical, and recorded follow-ups for frontend copy, capped-context collision lookup, and source appointment exclusion.
