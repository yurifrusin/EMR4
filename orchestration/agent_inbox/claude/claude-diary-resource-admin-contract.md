# claude-diary-resource-admin-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | d78659a |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-diary-resource-admin-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-diary-resource-admin-contract --commit-message "Diary resource admin contract" --message "claude-diary-resource-admin-contract ready for Codex review"` |

## Mission

Plan, then after explicit approval implement the smallest backend admin contract for physical rooms and waiting areas so practice admins can maintain Phase 2 diary resources safely.

## Scope

### In Scope

app/schemas/diary.py, app/routers/diary.py, focused tests/test_diary_resource_admin.py; GET /api/v1/diary/rooms; create/update/archive for Room and WaitingArea; Admin/PracticeOwner RBAC; practice/location scoping; active/archive semantics; Room.default_waiting_area_id validation against active same-practice/same-location waiting areas where location is known.

### Out of Scope

Diary frontend, roster writes, diary template editing, appointment mutation semantics, migrations unless your plan proves one is necessary, full practice admin UI, patient merge/delete, taskpane, Command Centre, Bernie runtime, broad audit-log platform, non-person bookable resource schema.

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

Plan packet first. After approval: backend py_compile for touched router/schema/test files; focused pytest tests/test_diary_resource_admin.py plus adjacent tests/test_location_scoped_diary.py tests/test_diary_roster.py tests/test_waiting_area_contract.py as needed; git diff --check.

## Merge Criteria

Admin writes are role-gated to Admin/PracticeOwner, practice-scoped, and location-safe; inactive/archive preserves historical references; room defaults cannot point at invalid cross-practice/cross-location waiting areas; existing diary read endpoints keep their contracts.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `app/schemas/diary.py` — added `WaitingAreaCreate`, `WaitingAreaUpdate`, `RoomCreate`, `RoomUpdate`; extended `RoomOut` with `default_waiting_area_id: Optional[UUID]` (non-breaking, new nullable field)
  - `app/routers/diary.py` — added `_ensure_waiting_area()` helper; added `POST /waiting-areas`, `PATCH /waiting-areas/{area_id}`, `GET /rooms`, `POST /rooms`, `PATCH /rooms/{room_id}`; added `require_role` and `IntegrityError` imports
  - `tests/test_diary_resource_admin.py` (new) — 25 tests covering auth gates, role gates, practice isolation, Room CRUD, WaitingArea CRUD, archive semantics, `default_waiting_area_id` validation, duplicate display_order 409, roster preservation after archive

- Verification run:
  - `py_compile app/schemas/diary.py app/routers/diary.py tests/test_diary_resource_admin.py` → passed
  - `pytest tests/test_diary_resource_admin.py -v --tb=short -p no:randomly` → **25 passed**
  - `pytest tests/test_location_scoped_diary.py tests/test_diary_roster.py tests/test_diary_template.py tests/test_waiting_area_contract.py -q --tb=short -p no:randomly` → **46 passed** (no regressions)
  - `git diff --check -- app/schemas/diary.py app/routers/diary.py tests/test_diary_resource_admin.py` → clean (pre-existing whitespace issues in docs/diary/ are Antigravity's, not mine)

- Remaining risks:
  - `PATCH /rooms/{id}` clears `default_waiting_area_id` only when the field is explicitly included in the JSON body as `null`. Omitting the field leaves it unchanged (uses `model_fields_set`). Codex should confirm this matches the intended API contract.
  - `display_order` uniqueness 409 is tested for the no-location_id case; the location-scoped partial index path is not separately covered — low risk since the index logic is DB-side.
  - Pre-existing whitespace issues in `docs/diary/` (Antigravity's files) cause `git diff --check` to exit non-zero at the repo level; my three files are individually clean.
  - No migration needed: Room and WaitingArea tables already exist.
