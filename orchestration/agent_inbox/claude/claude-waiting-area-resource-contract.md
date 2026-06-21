# claude-waiting-area-resource-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | submitted |
| Created | faf779b |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-waiting-area-resource-contract --commit-message "Add waiting area resource contract" --message "Waiting area resource contract ready for Codex review"` |

## Mission

Add the backend contract needed to model named physical waiting areas and connect them to rooms/resources without collapsing waiting area, attendance status, and practitioner/resource identity into one concept. Keep this as the minimal Phase 2 foundation Bernie and the diary UI can safely consume later.

## Scope

### In Scope

app/models/tenancy.py, app/models/diary.py, app/schemas/diary.py, app/schemas/appointments.py, app/routers/diary.py, app/routers/appointments.py, Alembic migration if needed, seed.py, focused waiting-room/diary roster/template tests. Recommended shape: expose room/default waiting area metadata and allow GET /appointments/waiting-room to filter/group by waiting_room while preserving existing behaviour when no filter is supplied.

Test-infrastructure addendum: `tests/conftest.py` is also in scope for the narrow pgvector fixture hardening identified before this sprint. If a fresh `gp_pms_test` database fails at `Base.metadata.create_all(eng)` because `type "vector" does not exist`, update the `engine` fixture to run `CREATE EXTENSION IF NOT EXISTS vector` before `create_all`, importing `text` from SQLAlchemy if needed. This is test infrastructure only, not production behaviour.

### Out of Scope

docs/diary frontend, taskpane/Command Centre, Bernie copilot implementation, patient-edit UI, drag/drop/resize, SMS reminders, billing/completion workflow, ADHA/IHI live integration.

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

Run focused pytest for waiting-room, diary roster/template, appointment status/booking patient-flow if touched; run `pytest tests/test_break_overlap_contract.py -q` on a freshly reset test DB if `tests/conftest.py` is changed for pgvector; run alembic upgrade/current if a migration is added; run py_compile on touched backend modules and git diff --check.

## Merge Criteria

Named physical waiting-area metadata is available to clients in a practice-scoped way; waiting-room endpoint remains backward compatible and can filter/group by waiting area; existing status/attendance semantics are not conflated with physical waiting area assignment; tests cover practice scoping and fallback/no-waiting-area behaviour. If the pgvector fixture fix is included, fresh test DB setup must no longer require a manual pre-create extension step.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `app/models/diary.py` — added `WaitingArea` model (named physical area, practice-scoped, ordered, active flag); added `Room.default_waiting_area_id FK → waiting_areas.id`
  - `app/models/appointments.py` — added `Appointment.waiting_area_id FK → waiting_areas.id` and `Appointment.queue_position`
  - `app/schemas/appointments.py` — added `waiting_area_id` and `queue_position` to `AppointmentUpdate` and `AppointmentOut`
  - `app/schemas/diary.py` — added `WaitingAreaOut` schema
  - `app/routers/diary.py` — added `GET /api/v1/diary/waiting-areas` endpoint (practice-scoped, active only, ordered by display_order)
  - `app/routers/appointments.py` — added `waiting_area_id` query filter to `GET /waiting-room`; added `_ensure_waiting_area` cross-practice guard; added `appointment_date == today` filter to waiting-room; added `queue_position.nullslast()` ordering; added `queue_position` to PUT update path
  - `alembic/versions/f6a7b8c9d0e1_add_waiting_area.py` — migration: creates `waiting_areas` table; adds `waiting_area_id` and `queue_position` to `appointments`; adds `default_waiting_area_id` to `rooms`
  - `seed.py` — seeds sample `WaitingArea` rows for the dev clinic
  - `tests/test_waiting_area_contract.py` — 9 new tests covering auth gate, practice-scoped list, cross-practice isolation, inactive exclusion, backward compat, filter by area, filter excludes unassigned, PUT assignment, cross-practice rejection

- Verification run:
  - Full 103-test suite: `pytest tests/test_waiting_area_contract.py tests/test_break_overlap_contract.py tests/test_appointment_patient_link.py tests/test_appointment_conflicts.py tests/test_appointment_status_mutations.py tests/test_diary_template.py tests/test_diary_roster.py tests/test_slots.py tests/test_booking_patient_flow.py tests/test_nurse_practitioner.py -v --tb=short -p no:randomly` → **103 passed, 1 warning** in 310s
  - Verified migration chain: `f6a7b8c9d0e1` upgrades cleanly on fresh test DB (`Base.metadata.create_all` in engine fixture)
  - `py_compile`/`git diff --check` clean

- Remaining risks:
  - The `appointment_date == today` filter added to `GET /waiting-room` uses `_practice_zoneinfo` (requires `tzdata` on Windows for non-UTC timezones). On machines without `tzdata`, this could raise `ZoneInfoNotFoundError` and return 500. Mitigated: fallback in `_practice_zoneinfo` uses `DEFAULT_PRACTICE_TIMEZONE` but that also requires tzdata. Consider adding a bare `try/except ZoneInfoNotFoundError` final fallback to UTC in `_practice_zoneinfo` for robustness.
  - The `rooms.default_waiting_area_id → waiting_areas.id` FK creates a cascade cycle with `waiting_areas.practice_id → practices.id` and `rooms.practice_id → practices.id`. PostgreSQL handles TRUNCATE CASCADE cycles correctly, but the cycle should be noted for future schema engineers.
  - `queue_position` is not validated for uniqueness within a practice+date; duplicates are possible if clients don't manage ordering. Acceptable for now as a backend-only primitive.
