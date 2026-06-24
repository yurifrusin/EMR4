# plan-claude-claude-room-default-waiting-area-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-room-default-waiting-area-contract` |
| Status | pending_plan_review |
| Created | 2026-06-24 18:50 +1000 |
| Source HEAD | `761e39d` |

## Plan Summary

Add _resolve_default_waiting_area helper; auto-assign on room create; reassign rooms on waiting-area archive. No schema change needed.

## My Understanding

Room.default_waiting_area_id is already nullable FK on the rooms table (migration f6a7b8c9d0e1). create_room and update_room both call _ensure_waiting_area to validate explicit assignments, but neither auto-assigns when none is supplied. update_waiting_area archives a waiting area with no reassignment of rooms that use it as default — leaving them silently stale. The checkin-defaults endpoint already handles the stale case gracefully (returns null suggestion when area is inactive), so the runtime is safe, but the admin surface should prevent the stale state proactively.

Seed.py correctly sets default_waiting_area_id on all 3 seeded rooms, so dev data is already consistent. The invariant gap is in the create/archive code paths only.

## Intended Surface / Boundary

Backend only: app/routers/diary.py (create_room, update_waiting_area, new helper function); tests/test_diary_resource_admin.py (7 new tests). No schema change (column already exists). No migration. No diary JS, taskpane, command centre, appointment booking, or waiting-room UI changed.

## Out Of Scope

- Diary frontend (docs/diary/), taskpane, Command Centre, appointments UI
- Appointment booking/status semantics (checkin-defaults endpoint unchanged)
- Broad roster redesign or DiaryRoster changes
- Schema/migration changes (none required)
- Production data migration (no production rows affected; dev seed already correct)
- update_room reassignment (admin can manually clear/set via PATCH, no auto-reassign on room edit)

## Files I Expect To Edit

- app/routers/diary.py: add _resolve_default_waiting_area helper; modify create_room (auto-assign when default not supplied); modify update_waiting_area (reassign active rooms when archiving)
- tests/test_diary_resource_admin.py: 7 new tests (see Steps)
- No schema, no migration, no seed change

## Implementation Steps

1. Add _resolve_default_waiting_area(practice_id, room_location_id, db, exclude_id=None) to app/routers/diary.py:
   - Queries WaitingArea where practice_id matches, is_active=True, optionally excludes one id
   - Location filter: if room_location_id is set, filter to areas where location_id == room_location_id OR location_id IS NULL (matches _ensure_waiting_area compatibility rules); if room_location_id is None, return any practice area
   - Orders by display_order ASC, name ASC, id ASC (deterministic; display_order 0 always wins)
   - Returns areas[0].id if any, else None

2. Modify create_room in app/routers/diary.py:
   - After _ensure_waiting_area validates any explicit default_waiting_area_id, check: if body.default_waiting_area_id is None, call _resolve_default_waiting_area(practice_id, body.location_id, db) and use the result as default_area_id
   - Pass default_area_id (not body.default_waiting_area_id) to Room constructor

3. Modify update_waiting_area in app/routers/diary.py:
   - Before applying field updates, detect archive path: was_active = area.is_active
   - If body.is_active is False and was_active is True:
     a. Find all active rooms in practice with default_waiting_area_id == area.id
     b. For each, call _resolve_default_waiting_area(..., exclude_id=area.id) and update room.default_waiting_area_id
     c. db.flush() to persist room updates before continuing
   - Then apply name/is_active updates and normalize as before

4. Write 7 new tests in tests/test_diary_resource_admin.py (add after existing tests):
   a. test_rooms_create_no_default_auto_assigns_lowest_display_order_area: create area (order=0), create room without default -> room.default_waiting_area_id == area.id
   b. test_rooms_create_no_default_stays_null_when_no_active_area: no areas in practice -> room.default_waiting_area_id is None
   c. test_rooms_create_auto_assigns_display_order_0_among_multiple_areas: create areas at order=0 and order=1, create room without default -> gets order=0 area
   d. test_waiting_area_archive_reassigns_room_default_to_next_active_area: room with area A as default; archive A; room now has area B as default
   e. test_waiting_area_archive_clears_room_default_when_no_alternative: room with area A as only active area; archive A; room.default_waiting_area_id is None
   f. test_waiting_area_archive_only_affects_active_rooms: archived room with area A; archive A; archived room unchanged (or null, but no error)
   g. test_waiting_area_archive_location_scoped_does_not_affect_incompatible_rooms: area at location_id=None (practice-wide); room at different scope is not incorrectly reassigned

## Visual / Behavioural Acceptance Checks

- POST /api/v1/diary/rooms with no default_waiting_area_id returns a room with default_waiting_area_id set to the display_order=0 active area (if one exists)
- POST /api/v1/diary/rooms with no default_waiting_area_id and no active areas returns default_waiting_area_id=null
- PATCH /api/v1/diary/waiting-areas/{id} with is_active=false: all active rooms in the practice that had that area as default now have a different active area (or null if none available)
- PATCH /api/v1/diary/waiting-areas/{id} with is_active=false: inactive rooms are not affected
- Cross-practice isolation: only rooms in the same practice are reassigned
- Location compatibility: a room at location X is only auto-assigned areas at location X or practice-wide; it is not auto-assigned an area at location Y
- Existing create_room with explicit valid default_waiting_area_id still works unchanged
- Existing _ensure_waiting_area validation still rejects cross-practice and inactive areas
- python -m pytest tests/test_diary_resource_admin.py passes (existing + 7 new)
- python -m bandit -r app/ -ll -ii -c pyproject.toml exits 0
- git diff --check exits 0

## Risks / Ambiguities

- Auto-assignment on room create changes visible API behavior: callers that POST without default_waiting_area_id and expect null will now receive a UUID. This is intentional (the invariant) but callers should handle non-null defaults. Current tests/clients are compatible since they assert specific values, not null-by-default.
- Reassignment during archive runs multiple room UPDATEs in the same transaction. This is safe for the small room counts in a practice (typically 3-20 rooms), but is O(n) in active rooms. Not a concern at this scale.
- The _resolve_default_waiting_area location filter matches _ensure_waiting_area behavior for practice-wide rooms (location_id=None): any active area in the practice passes. This may auto-assign a location-specific area to a practice-wide room. This matches existing _ensure_waiting_area semantics and is acceptable for now; a stricter rule can be added later if needed.
- No migration needed but existing dev DB rows may have null defaults on old rooms. The seed already handles the 3 seeded rooms; a dev can re-run seed.py to backfill. No production impact.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
