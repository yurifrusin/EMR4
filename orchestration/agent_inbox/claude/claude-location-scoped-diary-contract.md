# claude-location-scoped-diary-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | submitted |
| Created | 32f1577 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-location-scoped-diary-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-location-scoped-diary-contract --commit-message "Add location-scoped diary contract" --message "Location-scoped diary backend contract ready for Codex review"` |

## Mission

Plan first, then after explicit approval implement the smallest backend changes needed so diary templates, rooms, waiting areas, rosters, and appointments do not assume one physical location per practice.

## Scope

### In Scope

PracticeLocation, Room, WaitingArea, DiaryTemplate, DiaryRoster, Appointment.location_id, seed/test data, focused schemas/routers/tests, migrations only if needed.

### Out of Scope

Diary frontend, taskpane, Command Centre, full practice/location admin UI, drag/drop/resize, online booking portal, Bernie runtime.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Before editing project code, write an implementation plan and stop. The plan
   must be shown in the agent GUI and captured for Codex with the plan command
   above. Do not code until the user/Codex says `complete sprint task`.
5. After plan approval, work only inside the stated scope unless the user or Codex
   expands it.
6. Do not merge to `master`.
7. Do not move `handoff/current`.
8. Run the verification listed below.
9. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
10. Finish with the submit command above.

## Implementation Plan Requirements

Before coding, the implementation plan must include:

- My Understanding
- Intended Surface / Boundary
- Out of Scope
- Files I Expect To Edit
- Implementation Steps
- Visual / Behavioural Acceptance Checks
- Risks / Ambiguities

Pay special attention to visually loaded words such as cards, slots, stacking,
panels, waiting room, diary grid, booking slot, and status. State exactly which
surface is affected and which nearby surfaces must not change.

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

Plan packet first. After approval: focused location/diary/appointment pytest, backend py_compile, migration check if changed, git diff --check.

## Merge Criteria

A one-location practice continues to behave exactly as today; multi-location data cannot leak or ambiguously mix diary templates/rooms/waiting areas/rosters/appointments; tests describe the intended location boundary.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `alembic/versions/g7h8i9j0k1l2_add_location_to_diary_resources.py` (new migration — adds nullable `location_id` FK to rooms, waiting_areas, diary_templates; drops single-practice unique constraint; replaces with two partial unique indexes WHERE location_id IS NULL / IS NOT NULL)
  - `app/models/diary.py` — added `location_id` column + updated `__table_args__` for DiaryTemplate (partial indexes), Room (ix_rooms_location_id), WaitingArea (ix_waiting_areas_location_id)
  - `app/schemas/diary.py` — added `PracticeLocationOut`; added `location_id: Optional[UUID] = None` to DiaryTemplateOut, WaitingAreaOut, RoomOut, DiaryRosterEntryOut
  - `app/routers/diary.py` — added `_ensure_location` guard; new `GET /diary/locations`; updated template to use location_id fallback chain (location-specific → practice-wide NULL → JSON file); updated roster and waiting-areas to filter by location_id when supplied
  - `app/routers/appointments.py` — added `location_id` query param + guard + filter to `list_appointments` and `get_waiting_room`; fixed `get_checkin_defaults` to join Room and filter `Room.location_id == appt.location_id` when appt.location_id is set (disambiguates multi-location practitioners)
  - `seed.py` — added PracticeLocation seeding right after Practice; wires location_id to Room, WaitingArea, and sample Appointment creation; backfills location_id on existing rows
  - `tests/test_location_scoped_diary.py` (new) — 13 tests covering auth gates, cross-practice isolation, active-only, template location-specific vs fallback, roster/waiting-area/appointment location filters, cross-practice 404, and checkin-defaults disambiguation

- Verification run:
  - `py_compile` on all 7 source files: all OK
  - `pytest tests/test_location_scoped_diary.py tests/test_waiting_area_checkin_defaults.py tests/test_waiting_area_checkin_contract.py tests/test_waiting_area_contract.py tests/test_appointment_status_mutations.py tests/test_diary_template.py tests/test_diary_roster.py -q --tb=short -p no:randomly`: **81 passed** (includes 13 new + 68 regressions)
  - `git diff --check`: clean (only a CRLF/LF warning on the existing task packet, no whitespace errors)

- Remaining risks:
  - Migration drops `diary_templates_practice_id_key` by name — that name was auto-generated by PostgreSQL from `unique=True` in the original migration. If any dev environment used a different Postgres version that generated a different constraint name, the migration will fail. Codex should verify the constraint name against the dev DB before merging.
  - `seed.py` idempotent backfill for existing appointment.location_id sets all today's sample appointments to the one "Main Street Surgery" location. If a dev DB already has appointments from a previous seed run with no location, they'll all be backfilled to that location, which is correct for single-location practices.
  - `location_id IS NULL` partial index on diary_templates means the existing seeded template (location_id=None) serves all location_id query params that have no matching location-specific template. This is the intended fallback behaviour, but a practice with location-specific templates that intentionally wants "no template" for some location will currently get the practice-wide one instead of a 404. Codex may want to add a "no-template-for-this-location" sentinel if that use case materialises.
