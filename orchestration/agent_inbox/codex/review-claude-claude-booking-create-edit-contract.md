# review-claude-claude-booking-create-edit-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-booking-create-edit-contract` |
| Status | queued |

## Review Request

claude-booking-create-edit-contract ready for Codex review

## Worker Completion Notes

- **Files changed:** `tests/test_booking_create_edit.py` (new, 31 tests). No production code changed — endpoints are correct as-is.

- **What is tested:**
  - Auth gate (401 without token) for both create and update
  - Unknown-role token → 401/403
  - Create with `appointment_date + start_time_local` (canonical local pair) → 201
  - Create with UTC `start_time` → 201, `appointment_date`/`start_time_local` computed correctly
  - Response embeds patient, practitioner (AHPRA), appointment_type, `end_time`
  - `end_time` = `start_time` + `duration_minutes` (verified to the second)
  - Missing time fields → 422 (schema `model_validator`)
  - Partial local pair (date-only, time-only) → 422
  - `duration_minutes` = 0 → 422; `duration_minutes` = 481 → 422
  - Unknown `patient_id` → 404; unknown `practitioner_id` → 404
  - Cross-practice patient → 404; cross-practice practitioner → 404
  - Conflict on create → 409 with `conflicting_appointment_id` in detail
  - Non-blocking statuses (Cancelled/NoShow/DNA, parametrized) do not block new booking at same slot → 201
  - Adjacent bookings (09:00–09:15, 09:15–09:30) do NOT conflict → 201
  - Update non-existent → 404
  - Update cross-practice → 404
  - Reschedule to new time → 200, `start_time_local` updated
  - Reschedule into conflict → 409
  - Partial update (reason only) → 200, self-conflict not triggered
  - Duration update → 200, `end_time` recalculated
  - Duration extension self-exclude (no self-conflict) → 200
  - Change practitioner → 200, `practitioner.id` updated in response
  - Change to cross-practice practitioner → 404
  - New practitioner already has conflicting booking → 409

- **Verification run:**
  ```
  python -m pytest tests/test_booking_create_edit.py -v        → 31 passed in 56.21s
  python -m pytest tests/test_appointment_conflicts.py tests/test_appointment_status_mutations.py tests/test_waiting_room.py tests/test_slots.py -q  → 54 passed in 169.79s
  ```

- **Remaining risks:**
  - `AppointmentUpdate` has no schema-level `model_validator` ensuring that `appointment_date` and `start_time_local` are supplied together on update (only the router-level branching logic handles this). If a caller sends only `appointment_date` without `start_time_local`, the router falls through to use the existing `appt.start_time_local`, which is silently tolerant but may be surprising. Not a safety issue today; worth a schema validator when the update form is built.
  - No `appointment_type_id` update path in `AppointmentUpdate` (the field is absent from the schema). The router tries `values.get("appointment_type_id", appt.appointment_type_id)` but can never actually update it through this endpoint. Low risk — add to `AppointmentUpdate` if the diary type-change UI needs it.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-booking-create-edit-contract.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
