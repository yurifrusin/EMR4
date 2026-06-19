# review-claude-claude-booking-patient-flow-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-booking-patient-flow-contract` |
| Status | integrated |

## Review Request

claude-booking-patient-flow-contract ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `app/schemas/appointments.py` — added `model_validator(mode="after")` to `AppointmentUpdate` that rejects partial `appointment_date`/`start_time_local` pairs (one without the other → 422).
  - `app/routers/appointments.py` — cached `practice_id = current_user.practice_id` (and `booked_by = current_user.id`) at the top of all four mutating handlers (`create_appointment`, `update_appointment`, `update_appointment_status`, `cancel_appointment`) before any `db.commit()`, fixing post-commit lazy-load failures (`ObjectDeletedError`) when SQLAlchemy expires ORM objects after flush.
  - `tests/test_booking_patient_flow.py` — new file, 20 tests covering: partial local pair → 422; Cancelled re-open → 200 + visible in list + recoverable in waiting room; Cancelled doesn't block new booking at same slot; DNA/NoShow as non-blocking attendance outcomes (parametrized); DNA/NoShow visible in list but excluded from waiting room; list status filter; appointment_type update via PUT; cross-practice appointment_type → 404; queue_position update via PUT; mixed-status waiting room ordering by queue then time.

- Verification run:
  - `pytest tests/test_booking_patient_flow.py -q` → **20 passed** (45s)
  - `pytest tests/test_booking_create_edit.py tests/test_appointment_conflicts.py tests/test_appointment_status_mutations.py tests/test_waiting_room.py tests/test_slots.py -q` → **85 passed** (3m41s)
  - Combined 6-file run: 10 failed / 46 errors — all are ordering flaps (see Remaining Risks). Each failing test passes in isolation.

- Remaining risks:
  - **Ordering flaps in combined run (known, pre-existing pattern):** When all 6 test files run sequentially in a single pytest session, accumulated SQLAlchemy session state (NullPool + multiple commits per test) causes `db.refresh()` / lazy-load failures in ~15 tests from `test_booking_patient_flow.py`. Every affected test passes cleanly in isolation and in its own file run. This is the same transient ordering sensitivity seen in the prior `test_booking_create_edit.py` submission. Root cause: the test `db` fixture uses a shared NullPool engine with per-test sessions; after many commits across multiple test files the session expiry / connection-return timing becomes sensitive to insertion order. The fix would be a per-test transaction rollback approach, but the previous attempt to add `session.rollback()` to the `db` fixture teardown caused catastrophic "relation 'practices' does not exist" failures (DDL inside an implicit transaction with NullPool in SQLAlchemy 2.x). Documented for Codex to address as a separate test-infrastructure task if desired.
  - **`appointment_type_id` cross-practice guard relies on `_ensure_appointment_type`:** The helper fetches `AppointmentType` filtered by `practice_id`, returning 404 if not found. This correctly rejects cross-practice type IDs. No schema or model change was needed.
  - **No new migrations:** All changes are schema/router/test only; the `Appointment` model and DB tables are unchanged.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-booking-patient-flow-contract.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Integrated into Sprint 9. Focused appointment patient-flow
  contract tests passed as part of the 113-test sequential backend run.
- Follow-up required: Keep test DB runs sequential until the enum/schema reset
  issue is fixed at fixture level.
