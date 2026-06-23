# plan-claude-claude-diary-resource-admin-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `master` |
| Source Task | `claude-diary-resource-admin-contract` |
| Status | pending_plan_review |
| Created | 2026-06-23 15:22 +1000 |
| Source HEAD | `3ec4604` |

## Plan Summary

Add GET /rooms + Admin CRUD for Room and WaitingArea; no migration needed; ~15 focused tests

## My Understanding

Sprint 19 Workstream A: add the missing write contract for Room and WaitingArea resources so practice admins can maintain diary resources through the API. Room and WaitingArea tables already exist in the DB (from Sprint 13/15). The gaps are: no GET /api/v1/diary/rooms list endpoint; no write schemas (RoomCreate/Update, WaitingAreaCreate/Update); no Admin/PracticeOwner-gated create/update/archive endpoints; no test file for resource admin. No migration is needed.

## Intended Surface / Boundary

Backend only: app/schemas/diary.py (new write schemas + extend RoomOut), app/routers/diary.py (new endpoints), tests/test_diary_resource_admin.py (new test file). No frontend (diary.html/js/css), no taskpane, no Command Centre, no appointment mutation, no roster writes, no diary template editing.

## Out Of Scope

Diary frontend (diary.html/js/css), taskpane, Command Centre, appointment mutations, roster writes, diary template editing, migrations (tables already exist), full practice-admin UI, patient merge/delete, Bernie runtime, audit-log platform, non-person bookable resource schema.

## Files I Expect To Edit

app/schemas/diary.py -- add RoomCreate, RoomUpdate, WaitingAreaCreate, WaitingAreaUpdate; extend RoomOut with default_waiting_area_id | app/routers/diary.py -- add GET /rooms, POST /rooms, PATCH /rooms/{id}, POST /waiting-areas, PATCH /waiting-areas/{id} | tests/test_diary_resource_admin.py -- new: ~15 focused tests for auth, RBAC, CRUD, isolation, archive semantics, default_waiting_area_id validation

## Implementation Steps

1. Extend app/schemas/diary.py: add RoomCreate(name, display_order, location_id?, default_waiting_area_id?), RoomUpdate(name?, display_order?, default_waiting_area_id?, is_active?), WaitingAreaCreate(name, display_order, location_id?), WaitingAreaUpdate(name?, display_order?, is_active?); extend RoomOut with default_waiting_area_id:Optional[UUID]. 2. Add helper _ensure_waiting_area() to diary.py router that validates a waiting_area_id is active, same-practice, and same-location (or null-location area for location-scoped rooms). 3. Add GET /api/v1/diary/rooms: all authenticated users; returns active rooms by default; optional ?location_id and ?include_inactive=false query params; ordered by display_order. 4. Add POST /api/v1/diary/rooms: Admin/PracticeOwner only; validates location_id if given (via _ensure_location); validates default_waiting_area_id if given (via _ensure_waiting_area); sets practice_id from current_user. 5. Add PATCH /api/v1/diary/rooms/{room_id}: Admin/PracticeOwner only; practice-scope check (404 if not found in practice); apply partial updates; validate default_waiting_area_id if changed; is_active=False archives (soft-delete). 6. Add POST /api/v1/diary/waiting-areas: Admin/PracticeOwner only; validates location_id if given; sets practice_id from current_user. 7. Add PATCH /api/v1/diary/waiting-areas/{area_id}: Admin/PracticeOwner only; practice-scope check; apply partial updates including is_active=False for archiving. 8. Write tests/test_diary_resource_admin.py: define admin_user/practice_owner_user fixtures locally; test auth gates (401), role gates (403 for GP/Receptionist on mutate), practice isolation, Room CRUD, WaitingArea CRUD, archive semantics (archived excluded from list, roster reads unaffected), cross-practice default_waiting_area_id rejected.

## Visual / Behavioural Acceptance Checks

GET /api/v1/diary/rooms 401 without auth; 200 with empty list when no rooms; 200 with active rooms only by default. POST /api/v1/diary/rooms 403 for GP/Receptionist; 201 for Admin with correct practice_id; 404 for cross-practice location_id; 400/404 for invalid default_waiting_area_id. PATCH /rooms/{id} 404 for cross-practice room_id; 200 applying partial updates; 400 if default_waiting_area_id points at inactive or cross-practice area. Archive (is_active=False): room excluded from active list; existing DiaryRoster entries for that room still readable via /roster. WaitingArea analogous: POST 403/201, PATCH 200/archive; archived area excluded from /waiting-areas; archived area rejected as default_waiting_area_id. Existing GET /template, GET /roster, GET /waiting-areas, GET /locations contracts unchanged.

## Risks / Ambiguities

1. RoomOut currently lacks default_waiting_area_id; adding it is non-breaking (new field, nullable). The existing roster endpoint reads Room objects and returns DiaryRosterEntryOut which does not include default_waiting_area_id -- that is fine. 2. Archiving a room whose default_waiting_area_id is still referenced is safe since we are only setting is_active=False on the Room, not deleting the WaitingArea. 3. Cross-location validation for default_waiting_area_id: if room.location_id is set, the area must be at that location OR have null location_id (practice-wide). If room has null location_id, any practice-scoped area is valid. This is a guard at write time only; existing data is not retroactively validated. 4. display_order uniqueness: the DB has a partial unique index on (practice_id, display_order) for rooms. If admin sends a duplicate order, the DB will raise an IntegrityError. I will catch this and return 409 Conflict. 5. No admin_user fixture in conftest.py -- I will define one locally in the test file to avoid touching conftest.

## Codex Plan Review

- Review result: Approved. The plan is inside the backend-only Sprint 19 boundary and preserves the room/waiting-area/location vocabulary split.
- Required changes before implementation: Keep `/waiting-areas` read compatibility unchanged; catch duplicate `display_order` integrity failures with rollback and 409; treat client-visible archive as `is_active=False` soft archive only; run the focused resource-admin tests plus adjacent diary/location/waiting-area tests named in the packet.
- Approved to proceed: yes
