# plan-claude-claude-sprint-r7-raw-temporal-guard-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-r7-raw-temporal-guard-contract` |
| Status | pending_plan_review |
| Created | 2026-07-05 17:12 +1000 |
| Source HEAD | `e7e891f` |

## Plan Summary

Add explicit past-date and fully-elapsed same-day temporal guardrails to the raw appointment create/update endpoints and the create/update proposal builders, using a small pure helper in diary/temporal.py, plus focused clock-injected regression tests.

## My Understanding

Raw POST /appointments (_create_appointment_from_body) and PUT /appointments/{id} (_apply_appointment_update) currently resolve a canonical appointment_date/start_time_local and check entity existence + conflicts + breaks, but never verify the resolved slot is not in the past. A raw call can therefore silently create or move a booking to yesterday, or to a same-day window that has already fully elapsed. The compatibility proposal builders (_build_create_appointment_proposal L1011, propose_update_appointment L1296) similarly accumulate blocks (conflict, terminal_status, patient_identity) but have no temporal block. R6 deliberately excluded raw-mutation date policy; R7 closes that gap. temporal.py already owns pure clock-injected policy (evaluate_same_day_window) and _clinic_local_now(practice_tz) is the monkeypatchable clock. Merge criteria: past absolute dates and fully-elapsed same-day raw windows cannot silently create/move; compat/proposal paths keep existing signed-confirm/evidence boundaries; valid future and same-day-open requests still pass.

## Intended Surface / Boundary

Backend only: app/routers/appointments.py raw create/update service functions and the create/update proposal builders; a small pure predicate helper in app/services/diary/temporal.py; new focused pytest module(s). NO diary grid, taskpane/Word, GitHub Pages, migrations, or live-provider changes. Visually loaded terms (cards, slots, stacking, panels, waiting room, diary grid, booking slot, status) are untouched — no UI/status-lifecycle surface changes; status mutation, waiting-area, and signed-confirm endpoints are unchanged.

## Out Of Scope

Diary/taskpane/Word UI, GitHub Pages assets, migrations, live provider calls, broad route rewrites, signed-confirm authority redesign, Bernie interpret/slot-search temporal policy (R6 territory), status/waiting-area mutation policy, receptionist scenario corpus changes beyond a focused regression.

## Files I Expect To Edit

app/services/diary/temporal.py (new tiny pure helper evaluate_raw_mutation_temporal_guard + Literal kind + __all__); app/routers/appointments.py (temporal guard in _create_appointment_from_body and _apply_appointment_update raising HTTP 422; temporal block appended in _build_create_appointment_proposal and propose_update_appointment); tests/test_appointment_raw_temporal_guard.py (new); tests/conftest.py (add an autouse clock-freeze fixture pinning appointments._clinic_local_now to an early clinic-local morning so existing same-day fixed-time bookings stay future/open deterministically; new tests override it).

## Implementation Steps

1) Add pure helper evaluate_raw_mutation_temporal_guard(appointment_date, start_time_local, duration_minutes, clinic_now) -> 'ok'|'past_date'|'window_fully_past' in temporal.py: reject when appointment_date < clinic_now.date(); for same-day reject only when start+duration has fully elapsed (window_end <= now), building start_dt tz-aware from clinic_now.tzinfo to avoid naive/aware comparison errors; export it. 2) In _create_appointment_from_body, after canonicalizing values, call the helper with _clinic_local_now(practice_tz) and raise HTTPException 422 with a stable code (appointment_in_past / same_day_window_elapsed) before DB insert. 3) In _apply_appointment_update, apply the same guard only when a date/time/duration change is in values (mirroring the existing conflict-check gate) so non-temporal edits like reason are unaffected. 4) In _build_create_appointment_proposal and propose_update_appointment, append a blocked AppointmentProposalIssue when the guard fails; safe=not blocks already flips autonomy_tier to blocked and skips signed-confirm minting, preserving evidence boundaries. 5) Add tests/conftest.py autouse clock-freeze. 6) Add tests: past-date raw create 422; fully-elapsed same-day raw create 422; valid future + same-day-open raw create 201; raw update reschedule into past 422 vs future 200; non-temporal update (reason only) unaffected; proposal builders emit temporal block + safe=false + no signed_confirmation_evidence for past, and remain safe for future.

## Visual / Behavioural Acceptance Checks

Behavioural (no visual surface): raw create/update reject past-date and fully-elapsed same-day slots with 422 and a stable error code; valid future and same-day-open requests still return 201/200; create/update proposals for past slots return safe=false, autonomy_tier=blocked, a temporal block code, and NO signed_confirmation_evidence, while future slots keep prior signed-confirm/evidence shape; existing raw_compat evidence tags and Deprecation-header behaviour unchanged; py_compile clean; focused pytest for new guard + test_appointment_raw_compat.py + test_appointment_proposals.py + test_appointment_update_proposal.py + test_appointment_conflicts.py green; git diff --check clean.

## Risks / Ambiguities

1) Same-day guard blast radius: several suites POST same-day fixed-time appointments; without a deterministic clock they could flake after that wall-clock time. Mitigation: autouse clock-freeze in conftest + narrow 'fully elapsed' (start+duration<=now) predicate. Need Codex view on whether a global conftest clock fixture is acceptable vs per-test freezing. 2) tz-aware vs naive datetime comparison must be handled in the helper. 3) Error code naming/response shape for raw 422 — confirm no client depends on raw create/update never returning 422 for temporal reasons. 4) Whether 'compatibility proposal paths' means the proposal builders (assumed) or something narrower; will confirm with Codex if ambiguous. 5) Update guard should not fire on pure metadata edits (reason/notes) — gated on date/time/duration keys.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
