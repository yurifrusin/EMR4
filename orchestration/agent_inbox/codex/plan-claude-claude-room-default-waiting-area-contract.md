# plan-claude-claude-room-default-waiting-area-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-room-default-waiting-area-contract` |
| Status | integrated |
| Created | 2026-06-24 18:56 +1000 |
| Source HEAD | `79f2b32` |

## Plan Summary

Add _resolve_default_waiting_area helper; auto-assign on room create; reassign rooms on waiting-area archive; enforce fallback on update_room for active rooms. No schema change.

## My Understanding

Room.default_waiting_area_id is already nullable FK (migration f6a7b8c9d0e1). Three code paths currently leave active rooms without a valid active default:

(1) create_room: no default supplied → stays null even if active areas exist.
(2) update_waiting_area archive: rooms pointing to archived area become stale (FK still set, area inactive); checkin-defaults handles this gracefully at runtime but the admin surface should repair it proactively.
(3) update_room PATCH: explicit null clears the default with no fallback; field omitted on a room that already has null default does nothing. Both leave an active room with no default when a compatible area is available.

Seed.py correctly sets default_waiting_area_id on all 3 seeded rooms, so dev data is consistent. Invariant gaps are create/archive/PATCH code paths only. No schema or migration change is needed.

## Intended Surface / Boundary

Backend only: app/routers/diary.py (create_room, update_room, update_waiting_area, new helper); tests/test_diary_resource_admin.py (7 original + 5 new update_room tests = 12 new tests total). No schema change. No migration. No diary JS, taskpane, Command Centre, appointments UI, or checkin-defaults endpoint changed.

## Out Of Scope

- Diary frontend (docs/diary/), taskpane, Command Centre, appointments UI
- Appointment booking/status semantics (checkin-defaults endpoint unchanged)
- Broad roster redesign or DiaryRoster changes
- Schema/migration changes (none required)
- Production data migration (no production rows affected; dev seed already correct)
- Validation that an existing non-null default is still active on update_room (stale FK is handled by the archive path of update_waiting_area, not by update_room read-time checks)

## Files I Expect To Edit

- app/routers/diary.py: add _resolve_default_waiting_area helper; modify create_room (auto-assign when default not supplied); modify update_waiting_area (reassign active rooms when archiving); modify update_room (resolve fallback for active rooms when explicit null or existing null)
- tests/test_diary_resource_admin.py: 12 new tests (7 from original plan + 5 update_room tests)
- No schema, no migration, no seed change

## Implementation Steps

1. Add _resolve_default_waiting_area(practice_id, room_location_id, db, exclude_id=None) to app/routers/diary.py:
   - Queries WaitingArea where practice_id matches, is_active=True, optionally excludes one id
   - Location filter: if room_location_id is set, filter to areas where location_id == room_location_id OR location_id IS NULL (matches _ensure_waiting_area compatibility); if room_location_id is None, any practice area is compatible
   - Orders by display_order ASC, name ASC, id ASC (deterministic; display_order 0 always wins)
   - Returns areas[0].id if any, else None

2. Modify create_room in app/routers/diary.py:
   - After _ensure_waiting_area validates any explicit default, check: if body.default_waiting_area_id is None, call _resolve_default_waiting_area(practice_id, body.location_id, db)
   - Pass resolved id (not body value) to Room constructor

3. Modify update_waiting_area in app/routers/diary.py:
   - Before applying field updates, detect archive path: was_active = area.is_active
   - If body.is_active is False and was_active is True:
     a. Find all active rooms in practice with default_waiting_area_id == area.id
     b. For each, call _resolve_default_waiting_area(..., exclude_id=area.id) and update room.default_waiting_area_id
     c. db.flush() before continuing
   - Then apply name/is_active updates and normalize as before

4. Modify update_room in app/routers/diary.py:
   - Apply body.is_active (if supplied) first, so room.is_active reflects the final state
   - Apply body.name (if supplied) as before
   - For default_waiting_area_id, use this decision tree (checked AFTER final is_active is known):
     a. If room.is_active is True (active room invariant applies):
        - If default_waiting_area_id in body.model_fields_set AND body value is not None:
            _ensure_waiting_area validates it; accept explicit valid UUID (existing behaviour)
        - If default_waiting_area_id in body.model_fields_set AND body value is None:
            call _resolve_default_waiting_area (explicit null becomes auto-resolved fallback, not clear)
        - If default_waiting_area_id NOT in body.model_fields_set AND room.default_waiting_area_id is None:
            call _resolve_default_waiting_area (fill a missing default opportunistically)
        - If default_waiting_area_id NOT in body.model_fields_set AND existing non-null:
            leave unchanged (no action)
     b. If room.is_active is False (inactive room, invariant does not apply):
        - If default_waiting_area_id in body.model_fields_set:
            validate non-null via _ensure_waiting_area if not None; accept null as clear
        - Otherwise leave unchanged
   - Continue with _normalize_resource_order as before

5. Write 7 tests in tests/test_diary_resource_admin.py (original plan, add after existing tests):
   a. test_rooms_create_no_default_auto_assigns_lowest_display_order_area
   b. test_rooms_create_no_default_stays_null_when_no_active_area
   c. test_rooms_create_auto_assigns_display_order_0_among_multiple_areas
   d. test_waiting_area_archive_reassigns_room_default_to_next_active_area
   e. test_waiting_area_archive_clears_room_default_when_no_alternative
   f. test_waiting_area_archive_only_affects_active_rooms
   g. test_waiting_area_archive_location_scoped_does_not_affect_incompatible_rooms

6. Write 5 additional update_room tests in tests/test_diary_resource_admin.py:
   h. test_rooms_update_explicit_null_resolves_to_fallback: active room, explicit {default_waiting_area_id: null} PATCH, active area exists -> area auto-resolved, not cleared
   i. test_rooms_update_omitted_field_resolves_null_default: active room with null default, PATCH with {name: X} only -> null default filled by fallback area
   j. test_rooms_update_explicit_valid_uuid_preserved: active room, PATCH with valid UUID -> that UUID used, _resolve not called
   k. test_rooms_update_archive_does_not_auto_resolve: PATCH is_active=False -> room inactive, null default stays null
   l. test_rooms_update_reactivate_null_default_resolves: inactive room with null default, PATCH is_active=True, active area exists -> default auto-resolved on reactivation

## Visual / Behavioural Acceptance Checks

- POST /api/v1/diary/rooms with no default_waiting_area_id: returns room with display_order=0 active area as default (if one exists)
- POST /api/v1/diary/rooms with no default_waiting_area_id and no active areas: default_waiting_area_id is null
- PATCH /api/v1/diary/rooms/{id} with {default_waiting_area_id: null} on active room with active area: default resolved, not cleared
- PATCH /api/v1/diary/rooms/{id} with only name/is_active fields on active room with null default: default filled by fallback
- PATCH /api/v1/diary/rooms/{id} with valid explicit UUID: that UUID used (explicit wins)
- PATCH /api/v1/diary/rooms/{id} with {is_active: false}: room archived, null default not forced to fill
- PATCH /api/v1/diary/rooms/{id} with {is_active: true} on room with null default: default auto-resolved
- PATCH /api/v1/diary/waiting-areas/{id} with is_active=false: active rooms that used it get new compatible default or null
- PATCH /api/v1/diary/waiting-areas/{id} with is_active=false: inactive rooms unaffected
- Cross-practice isolation preserved throughout
- Location compatibility: room at location X not assigned area from location Y
- python -m pytest tests/test_diary_resource_admin.py passes (existing + 12 new)
- python -m bandit -r app/ -ll -ii -c pyproject.toml exits 0
- git diff --check exits 0

## Risks / Ambiguities

- Auto-resolve on update_room changes visible PATCH behavior: callers that PATCH with explicit null expecting to clear the default will instead receive a fallback UUID. The intent is the invariant. Callers wanting to clear must do so only when no active area exists (null is then the correct result anyway).
- Field-omitted auto-fill: PATCHes that do not touch default_waiting_area_id may now silently fill a null default. Callers that check for null after a name-only PATCH could observe a UUID they did not request. This is intentional but warrants documentation in the endpoint docstring.
- Decision tree for is_active+default changes in same request: is_active is applied first to determine the final active state. If the same PATCH archives a room (is_active=False) and sends default_waiting_area_id=null, the room is inactive so the invariant does not apply; null is accepted as a clear. This ordering must be implemented exactly.
- No migration needed. Existing dev DB rows with null defaults on old rooms are fixed by re-running seed.py or by the next PATCH to that room. No production impact.
- Reassignment during archive is O(n) in active rooms per practice. At GP-practice scale (3-20 rooms) this is safe.
- _resolve_default_waiting_area for practice-wide rooms (location_id=None) may pick a location-specific area (matching existing _ensure_waiting_area permissiveness). If stricter scoping is needed later, it can be added to the helper without changing the tests.

## Codex Plan Review

- Review result: Accepted and integrated in Sprint 23.
- Required changes before implementation: None.
- Approved to proceed: yes; implementation completed and merged.
