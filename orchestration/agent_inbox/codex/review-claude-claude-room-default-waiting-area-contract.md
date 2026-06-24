# review-claude-claude-room-default-waiting-area-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-room-default-waiting-area-contract` |
| Status | integrated |

## Review Request

Room default waiting-area backend contract ready for Codex review

## Worker Completion Notes

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

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-room-default-waiting-area-contract.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Accepted and integrated. Focused resource-admin and waiting-room tests passed after merge; broad full-suite retry timed out without a failure report.
- Follow-up required: Investigate broad-suite runtime separately; live Pages v84 admin smoke remains useful after deployment.
