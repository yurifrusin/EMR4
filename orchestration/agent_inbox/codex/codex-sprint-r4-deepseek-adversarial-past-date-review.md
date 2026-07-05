# Plan: R4 Adversarial Past-Date Review Lane

## Summary
Adversarial review and test-design lane exposing bypasses where absolute past dates, backdated reference_dates, or stale session reference dates can flow through normalize → slot search → proposal → confirm without temporal rejection.

## Understanding
The normalizer (bernie_slot_normalizer.py) is a pure format parser — it accepts any valid ISO date, including past dates. evaluate_same_day_window in diary/temporal.py only checks same-day time windows. Outside the same day, there is no past-date block at any pipeline stage:

1. Normalizer accepts past date_from (e.g. "2026-06-30" when today is 2026-07-05).
2. Slot search (_build_slot_search_proposal) generates candidate slots against practitioner schedule for past dates — no temporal check.
3. Create proposal (_build_create_appointment_proposal) validates patient/practitioner/location existence and conflicts — no past-date check.
4. Interpret booking instruction temporal axis only blocks same-day past windows; absolute past ISO dates pass as band=assume.
5. Supervised booking only triggers clinic_day_exhausted for same-day (date_from == clinic_today).
6. reference_date is client-supplied: a backdated reference_date resolves "today" to a past date. ContextFreshness.stale is informational only.
7. Session reference_date is immutable once set, permitting stale sessions.
8. Confirm-create staleness gate checks freshness IDs (session-coordination proof), not temporal validity.
9. AppointmentCreate / AppointmentCreateCommand schemas have no model_validator for past dates.
10. Raw compat endpoints bypass session overlay entirely.

D8 patient collision semantics and existing same-day window clamp/block behavior must be preserved.

## Surface
- app/services/bernie_slot_normalizer.py
- app/services/bernie/__init__.py (resolve_booking_date_transition)
- app/services/diary/temporal.py (evaluate_same_day_window)
- app/routers/appointments.py (propose_bernie_supervised_booking, interpret_booking_instruction, _build_create_appointment_proposal, _build_slot_search_proposal, confirm_bernie_create_proposal, create_appointment)
- app/schemas/appointments.py (SlotSearchProposalIn, AppointmentCreate, AppointmentCreateCommand, SlotSearchCommandIn)
- app/services/bernie_patient_context.py (build_patient_booking_context)
- app/services/bernie/evidence.py, session.py, session_store.py (staleness/session binding)
- tests/test_bernie_slot_normalizer.py
- tests/test_bernie_confidence_policy.py
- tests/test_bernie_supervised_booking_wrapper.py
- tests/test_bernie_confirm_create_proposal.py
- tests/test_bernie_d8_collision_source_hardening.py
- tests/test_bernie_d8_patient_collision_source_hardening.py
- tests/test_bernie_booking_outcomes.py
- tests/test_bernie_interpret_booking_instruction.py

## Out of Scope
- UI/frontend changes
- Office.js add-in changes
- Live Gemini/LLM integration
- Patient data or schema migrations
- Production code changes in this plan phase (plan gate only)
- D4/D5/D6 domain frames unless directly affecting past-date gate logic

## Steps
1. Probe normalizer past-date acceptance — pure-unit tests proving normalizer accepts past date_from with no past-date block.
2. Probe backdated reference_date — show past reference_date resolves "today" to past date unblocked.
3. Probe past absolute date through interpret — route-level: past ISO date passes as band=assume unblocked.
4. Probe past absolute date through supervised-booking — route-level: past date_from proceeds past normalization and same-day check with no past-date block.
5. Probe past-date slot candidates returned — show slot search returns candidates for a past schedule (or no_slot rather than past-date block).
6. Probe past-date confirm-create proposal — route-level: confirm a past-date proposal passes staleness gate when freshness ids match.
7. Probe past-date appointment creation — route-level: create proposal for past date with valid evidence confirms without past-date block.
8. Probe session stale reference_date persistence — show session with past reference persists through turns.
9. Probe raw compat endpoint bypass — demonstrate raw POST /api/v1/appointments/ accepts past appointment_date with no temporal check.
10. Probe no regression on D8 collision — verify cap-overflow and source-appointment self-exclusion still correct.
11. Probe existing same-day window preserved — confirm evaluate_same_day_window still blocks/clamps same-day past windows and clinic_day_exhausted fires.
12. Synthesize findings — classify each probe as attack surface, acceptable, or false alarm; recommend changes with severity.
13. Write adversarial test file tests/test_bernie_r4_past_date_adversarial.py.

## Acceptance Criteria
- All 11 probes produce clear pass/fail with documented expectations.
- D8 collision tests still pass.
- Existing same-day window block and clinic_day_exhausted behavior unchanged.
- Every bypass surface precisely identified with code references.
- Adversarial test file self-contained and ready for review.
- No production code modified during plan phase.

## Risks
- Past-date slot search returns confusing "no slot" instead of blocking clear — pipeline fails open.
- Staleness gate is session-coordination proof not temporal check — single-session backdated booking bypasses.
- Raw compat endpoints may accept past appointments with zero validation — may be intentionally permissive.
- Past-date block risks false positives for history/retrospective entries — must be surgically applied to booking-new path only.
