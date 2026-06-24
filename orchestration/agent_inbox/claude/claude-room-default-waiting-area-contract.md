# claude-room-default-waiting-area-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | 3665aef |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-room-default-waiting-area-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-room-default-waiting-area-contract --commit-message "Dispatch Sprint 23 backend default waiting-area contract" --message "Room default waiting-area backend contract ready for Codex review"` |

## Mission

Plan, then after approval enforce a safe backend invariant that every active room has a valid active default waiting area for its practice/location, defaulting to the active waiting area with display_order 0 when no explicit default is supplied.

## Scope

### In Scope

Backend Room/WaitingArea models, schemas, resource-admin routes/services, seed/dev-data repair path, migrations only if required, and focused pytest coverage for create/edit/archive/default fallback behavior.

### Out of Scope

Diary frontend UI, taskpane/Command Centre, appointment booking/status semantics beyond preserving existing consumers, broad roster redesign, production data migration outside a minimal invariant-preserving migration if required.

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

Plan packet first; after approval run focused diary resource-admin/default-waiting-area pytest coverage, backend Tier-1 check, full pytest if invariant touches shared fixtures, and git diff --check.

## Merge Criteria

Active rooms cannot persist with no valid active default waiting area when an active waiting area exists; default fallback is deterministic by display_order then stable id/name; archiving a default area safely reassigns affected rooms or blocks with a clear contract; cross-practice/location defaults remain impossible.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `app/routers/diary.py` — four changes:
    1. Added `from sqlalchemy import or_` import.
    2. Added `_resolve_default_waiting_area(practice_id, room_location_id, db, exclude_id=None)` helper after `_ensure_waiting_area`. Queries active `WaitingArea` rows compatible with the room's location (mirrors `_ensure_waiting_area` location rules: room at location X → areas at X or practice-wide; practice-wide room → any area), ordered `display_order ASC, name ASC, id ASC` for deterministic fallback.
    3. Modified `create_room`: after `_ensure_waiting_area` validates any explicit default, if `body.default_waiting_area_id is None`, calls `_resolve_default_waiting_area` and passes resolved id to the `Room` constructor instead of null.
    4. Modified `update_waiting_area`: detects the archive transition (`body.is_active is False and area.is_active`), queries all active rooms pointing to the being-archived area, calls `_resolve_default_waiting_area(..., exclude_id=area_id)` for each, flushes — before applying the `is_active=False` update so the archived area is excluded from candidates via `exclude_id`.
    5. Modified `update_room`: applies `body.is_active` first (so final active state is known), then enforces the active-room invariant for `default_waiting_area_id` via a four-branch decision tree: explicit valid UUID → validate and accept; explicit null on active room → resolve fallback instead of clearing; field omitted on active room with null default → opportunistically fill; inactive room → honour explicit field changes only, no auto-resolve.
  - `tests/test_diary_resource_admin.py` — 12 new tests added and 1 existing test updated:
    - Updated: `test_rooms_clear_default_waiting_area` → renamed `test_rooms_clear_default_waiting_area_resolves_to_fallback_when_area_exists`; assertion changed from `None` to `str(area.id)` to match new invariant.
    - New (create_room): `test_rooms_create_no_default_auto_assigns_lowest_display_order_area`, `test_rooms_create_no_default_stays_null_when_no_active_area`, `test_rooms_create_auto_assigns_display_order_0_among_multiple_areas`.
    - New (archive invariant): `test_waiting_area_archive_reassigns_room_default_to_next_active_area`, `test_waiting_area_archive_clears_room_default_when_no_alternative`, `test_waiting_area_archive_only_affects_active_rooms`, `test_waiting_area_archive_location_scoped_does_not_affect_incompatible_rooms`.
    - New (update_room): `test_rooms_update_explicit_null_resolves_to_fallback`, `test_rooms_update_omitted_field_resolves_null_default`, `test_rooms_update_explicit_valid_uuid_preserved`, `test_rooms_update_archive_does_not_auto_resolve`, `test_rooms_update_reactivate_null_default_resolves`.
    - New (companion): `test_rooms_clear_default_waiting_area_stays_null_when_no_active_area`.

- Verification run:
  - Tier-1 (`scripts/check_backend.ps1` equivalent):
    - `python -m compileall app/ scripts/ -q` → exit 0, no errors.
    - `python -m bandit -r app/ -ll -ii -c pyproject.toml` → exit 0, no medium/high issues.
    - `git diff --check` → exit 0, no trailing-whitespace issues.
  - Targeted: `python -m pytest tests/test_diary_resource_admin.py -q --tb=short -p no:randomly` → **43 passed** (31 original + 12 new).
  - Regression: `python -m pytest tests/test_waiting_room.py -q --tb=short -p no:randomly` → **18 passed** (pre-existing errors from prior full-suite run were transient DB-state artefacts; isolated run is clean).
  - Full suite: `python -m pytest tests/ -q --tb=short -p no:randomly` → **exit 0, all tests passed**, no failures or errors.

- Remaining risks:
  - The `_resolve_default_waiting_area` call in `update_room` fires on every PATCH to an active room that currently has a null default (even name-only PATCHes). Callers that check for null after such a PATCH may observe a UUID they did not request — this is intentional (invariant enforcement) but is a visible behaviour change for any consumer that relies on null persisting. Documented in the plan.
  - Auto-resolve during `create_room` and `update_room` can select a practice-wide waiting area for a location-scoped room (matching existing `_ensure_waiting_area` permissiveness). If stricter location scoping is needed, the helper can be tightened later without test changes.
  - No migration was needed; existing dev DB rows with null defaults are repaired on their next PATCH. No production impact (no production rows exist yet).
