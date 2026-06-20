# claude-appointment-patient-link-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | submitted |
| Created | 90a951f |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-appointment-patient-link-contract --commit-message "Add appointment patient-link contract" --message "Appointment patient-link contract ready for Codex review"` |

## Mission

Split patient identity/linkage semantics from appointment attendance status. Add a minimal backend contract so appointments can distinguish linked patient records from provisional free-text names, without treating Confirmed as an attendance state.

## Scope

### In Scope

app/models/appointments.py, app/schemas/appointments.py, app/routers/appointments.py, Alembic migration if needed, focused appointment create/edit/status/waiting-room tests, seed/test helpers only if needed.

### Out of Scope

Diary frontend, taskpane/Command Centre UI, drag/drop/resize, SMS reminder confirmation, billing/completion guards beyond documenting test expectations.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Work only inside the stated scope unless the user or Codex expands it.
5. Do not merge to `master`.
6. Do not move `handoff/current`.
7. Run the verification listed below.
8. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
9. Finish with the submit command above.

## Hard Stop Rules

- Do not push to `master` or `handoff/current`.
- Do not manually work around a failed protocol command (`handin`, `sync`, `submit`,
  `realign`, or related orchestration commands).
- Report every protocol-followed command back to Codex/orchestrator, whether it
  succeeds or fails. For success, include the command, working directory, branch,
  and short success result.
- If any protocol command refuses to run or fails, stop and report the exact command,
  working directory, branch, `git status --short --branch`, and error output to the
  orchestrator. On push failure, `submit` will also try to publish a
  `submit-alert/...` branch for Codex to poll.
- If these instructions conflict with remembered prior protocol, trust the current
  `handin` alerts and this task packet.

## Verification

Run focused appointment create/edit/status/waiting-room/conflict tests plus migration check if a migration is added; run git diff --check. Include exact commands/results in the Codex review packet.

## Merge Criteria

Existing linked-patient booking API remains backward compatible; tests define provisional patient-name behaviour and patient-link/attendance separation; no non-orchestrator merge to master or handoff/current.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

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
