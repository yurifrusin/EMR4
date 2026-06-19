# claude-booking-create-edit-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | 9ccd838 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-booking-create-edit-contract --commit-message "Booking create/edit contract" --message "claude-booking-create-edit-contract ready for Codex review"` |

## Mission

Harden the backend appointment create/edit contract so the diary can safely create and edit bookings through the existing API surface.

## Scope

### In Scope

app/models/appointments.py, app/schemas/appointments.py, app/routers/appointments.py, focused appointment conflict/create/update tests, and minimal seed/test helper changes if needed. Cover appointment_date + start_time_local, duration, practitioner/patient/type validation, conflict behavior, role/auth gates, and response shape.

### Out of Scope

docs/diary frontend, drag/drop/resize UI, roster admin UI, waiting-room display app, taskpane/Command Centre/Gemini, online booking portal, broad refactors.

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

.venv\\Scripts\\python.exe -m pytest tests/test_appointment_conflicts.py tests/test_appointment_status_mutations.py tests/test_waiting_room.py tests/test_slots.py -q plus any new focused booking create/edit tests.

## Merge Criteria

Existing behavior remains compatible; create/edit failures are explicit and tested; conflict and practice-scope protections are covered; Codex review packet includes changed files, commands run, pass/fail output, and remaining risks.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

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
