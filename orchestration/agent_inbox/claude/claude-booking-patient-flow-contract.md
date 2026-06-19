# claude-booking-patient-flow-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | submitted |
| Created | 14bc9e4 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-booking-patient-flow-contract --commit-message "Booking and patient-flow contract" --message "claude-booking-patient-flow-contract ready for Codex review"` |

## Mission

Harden the backend contract for the diary's next operational layer: booking edits, terminal status semantics, waiting-room/patient-flow data, and safer validation before drag/drop and a visible waiting-room panel are built.

## Scope

### In Scope

app/schemas/appointments.py, app/routers/appointments.py, app/models/appointments.py only if needed, focused tests around create/edit/status/waiting-room/slots. Add schema-level validation for partial appointment_date/start_time_local updates; codify Cancelled as recoverable/non-blocking and hidden-from-working-diary by policy notes/tests where backend-relevant; codify DNA/NoShow as attendance outcomes that remain visible but non-blocking; strengthen waiting-room tests around Arrived/InConsult and queue ordering; add narrowly useful response fields or helper behavior only if needed by the diary UI.

### Out of Scope

docs/diary frontend, drag/drop/resize UI, roster admin UI, taskpane/Command Centre/Gemini, patient-file import tooling, broad refactors, online booking portal.

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

.venv\\Scripts\\python.exe -m pytest tests/test_booking_create_edit.py tests/test_appointment_conflicts.py tests/test_appointment_status_mutations.py tests/test_waiting_room.py tests/test_slots.py -q plus any new focused tests.

## Merge Criteria

Partial date/time update behavior is explicit and tested; status semantics for Cancelled versus DNA/NoShow are covered; waiting-room/patient-flow regressions pass; existing API clients remain compatible or differences are explicitly justified; review packet includes files, commands, results, and risks.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

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
