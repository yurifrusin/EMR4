# review-claude-claude-sprint-d6-patient-advisory-collision-semantics

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-d6-patient-advisory-collision-semantics` |
| Status | queued |

## Review Request

claude-sprint-d6-patient-advisory-collision-semantics ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - NEW tests/test_bernie_d6_patient_advisory_collision.py — 10 focused tests:
    - 6 pure unit tests for has_existing_booking_on_requested_day (no DB, no fixtures):
      true for matching date, false for different date, false for None, false for empty
      future_bookings, false when only recent_bookings match, true for one match among several.
    - 2 interpret-route regression tests: same-day positive (hard assert warning emitted),
      different-day negative (hard assert warning not emitted, patient_booking_context preserved).
    - 2 supervised-booking regression tests: same-day positive, different-day negative, both
      hard asserts with patient_booking_context preservation confirmed.
  - No production code changes. The existing gating in app/routers/appointments.py
    (has_existing_booking_on_requested_day at lines ~3801-3806 for interpret and ~5555-5561
    for supervised booking) was verified to be correct. D6 implements regression-test hardening
    only, per user approval.

- Verification run:
  - py_compile tests/test_bernie_d6_patient_advisory_collision.py app/services/bernie_patient_context.py: OK
  - pytest tests/test_bernie_d6_patient_advisory_collision.py -v: 10 passed in 3.45s
  - pytest tests/test_bernie_patient_context.py tests/test_bernie_d5_route_builder_search_horizon.py tests/test_bernie_interpret_booking_instruction.py -q: all passed (51 tests)
  - Full pytest tests/ -q: in progress (background)
  - git diff --check: clean

- Remaining risks:
  - Cap silent false-negative: has_existing_booking_on_requested_day checks future_bookings
    which is capped at _FUTURE_CAP=3. If the patient has 3+ nearer future bookings before
    the requested date, the requested date's booking falls outside the cap and the warning
    is silently suppressed. Rare in normal practice but possible. Follow-up: consider
    raising the cap, adding an exact-date query, or documenting the limitation explicitly.
  - Self-collision gap: build_patient_booking_context is called after normalization but
    before any write. If a receptionist is rebooking a patient (cancelling old, booking
    new same day), the old appointment still appears in future_bookings at context-build
    time, which may cause a spurious warning. Not a data-correctness issue (no write
    happens), but could confuse reception staff. Follow-up: evaluate at the booking-create
    surface when the cancel+rebook workflow is implemented.
  - Both risks noted per user instruction; no production code change required this sprint.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-sprint-d6-patient-advisory-collision-semantics.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
