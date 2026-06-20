# review-claude-claude-appointment-patient-link-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-appointment-patient-link-contract` |
| Status | queued |

## Review Request

Appointment patient-link contract ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `app/models/appointments.py` — `patient_id` changed to `nullable=True`; `patient_name_provisional` column added (`String(200), nullable=True`)
  - `alembic/versions/e5f6a7b8c9d0_add_provisional_patient_to_appointments.py` — new migration: `alter_column patient_id nullable=True` + `add_column patient_name_provisional`
  - `app/schemas/appointments.py` — `AppointmentCreate`: `patient_id` now Optional, added `patient_name_provisional`, combined validator requires at least one; `AppointmentUpdate`: added `patient_id` and `patient_name_provisional` fields; `AppointmentOut`: `patient_id` Optional, `patient` Optional[PatientBrief], added `patient_name_provisional`
  - `app/routers/appointments.py` — `create_appointment`: `_ensure_patient` skipped when `patient_id is None`; `update_appointment`: calls `_ensure_patient` when `patient_id` present in update values and non-None
  - `tests/test_appointment_patient_link.py` — 8 new tests covering provisional create, 422 on missing identity, full-patient backward compat, both fields accepted, GET provisional, PUT to link patient, cross-practice 404, status patch on provisional
- Verification run:
  - `alembic -x sqlalchemy.url=<test_db> upgrade head` → `d4e5f6a7b8c9 -> e5f6a7b8c9d0` applied
  - `pytest tests/test_appointment_patient_link.py -v` → 8/8 passed
  - `pytest tests/test_appointment_patient_link.py tests/test_booking_patient_flow.py tests/test_nurse_practitioner.py tests/test_appointment_conflicts.py tests/test_appointment_status_mutations.py tests/test_slots.py -q` → 70/70 passed in 174s
  - `py_compile app/routers/appointments.py app/schemas/appointments.py app/models/appointments.py` → OK
  - `git diff --check` → OK
- Remaining risks:
  - Combined-run ordering flaps (pre-existing): when all 15 test files run together, NullPool session state can deadlock. Each file passes in per-file runs; separate infrastructure task.
  - Diary frontend: `AppointmentOut.patient` is now Optional. Provisional bookings return `patient: null`. The diary JS render path should guard `.patient?.first_name` before provisional appointments appear in the grid. Low risk now (diary maps by `a.practitioner.ahpra_number`), but Codex should audit before provisional bookings land in the grid.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-appointment-patient-link-contract.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
