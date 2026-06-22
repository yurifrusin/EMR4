# plan-claude-claude-location-scoped-diary-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-location-scoped-diary-contract` |
| Status | integrated |
| Created | 2026-06-22 18:39 +1000 |
| Source HEAD | `1e9444c` |

## Plan Summary

Add location_id (nullable FK) to Room, WaitingArea, DiaryTemplate; update DiaryTemplate unique constraint; add location filter params to diary endpoints and GET /appointments + GET /appointments/waiting-room; fix checkin-defaults roster disambiguation via appointment.location_id; seed one dev PracticeLocation; write 13 location isolation tests.

## My Understanding

PracticeLocation, Appointment.location_id, _ensure_location(), and the two other location FK columns are already in place. Room, WaitingArea, DiaryTemplate are only practice-scoped. DiaryTemplate has a column-level UNIQUE(practice_id). GET /appointments, GET /appointments/waiting-room, and GET /{id}/checkin-defaults are in app/routers/appointments.py. The checkin-defaults endpoint queries DiaryRoster by (practice_id, practitioner_id, roster_date) and calls .first() — this is ambiguous when the same practitioner appears in roster entries at multiple locations on the same date. The fix is to additionally filter the roster query by Room.location_id == appt.location_id when appt.location_id is set, degrading gracefully to .first() when it is None.

## Intended Surface / Boundary

Backend only. Models/schemas/routers: app/models/diary.py, app/schemas/diary.py, app/routers/diary.py, app/routers/appointments.py. Data: seed.py. Schema: new Alembic migration. Tests: tests/test_location_scoped_diary.py (new file). No diary frontend (docs/diary/*), no taskpane, no admin UI, no Bernie runtime.

## Out Of Scope

docs/diary/*, EMR4 Sidebar/*, full practice/location admin CRUD UI, drag/drop/resize, online booking portal, Bernie runtime. _get_break_overlaps() multi-location disambiguation is a known future limitation (flagged as risk, not in scope this sprint).

## Files I Expect To Edit

app/models/diary.py (add location_id FK to Room, WaitingArea, DiaryTemplate; update DiaryTemplate __table_args__ for partial unique indexes), app/schemas/diary.py (add PracticeLocationOut; optional location_id to RoomOut/WaitingAreaOut/DiaryTemplateOut), app/routers/diary.py (GET /diary/locations; ?location_id on /template, /roster, /waiting-areas; cross-practice guard), app/routers/appointments.py (optional location_id query param on GET /appointments with _ensure_location guard; optional location_id on GET /waiting-room with guard; Room join in checkin-defaults when appt.location_id is set), seed.py (idempotent PracticeLocation for dev practice; link seeded rooms + waiting_area to it), alembic/versions/g7h8i9j0k1l2_add_location_to_diary_resources.py (new migration).

## Implementation Steps

1. Write Alembic migration: add nullable location_id UUID FK to rooms (-> practice_locations.id), waiting_areas (-> practice_locations.id), diary_templates (-> practice_locations.id). Drop the column-level unique constraint on diary_templates.practice_id (named diary_templates_practice_id_key in PostgreSQL). Add two partial unique indexes: UNIQUE (practice_id) WHERE location_id IS NULL and UNIQUE (practice_id, location_id) WHERE location_id IS NOT NULL. 2. Update app/models/diary.py: add location_id column + index to Room, WaitingArea; add location_id column to DiaryTemplate and update __table_args__ to remove unique=True from practice_id and add two partial SQLAlchemy Index objects with postgresql_where=text(...). 3. Update app/schemas/diary.py: add PracticeLocationOut(id: UUID, name: str, is_active: bool); add optional location_id to RoomOut, WaitingAreaOut, DiaryTemplateOut. 4. Update app/routers/diary.py: import PracticeLocation + PracticeLocationOut; add _ensure_location_for_diary() helper (same guard as appointments); add GET /diary/locations returning active PracticeLocations for the practice; add optional location_id query param to GET /diary/template (guard + filter: try location-specific first, fall back to NULL, then JSON fallback); add optional location_id query param to GET /diary/roster (filter rooms by room.location_id == location_id if provided); add optional location_id query param to GET /diary/waiting-areas (filter by waiting_area.location_id == location_id if provided). 5. Update app/routers/appointments.py: (a) add optional location_id: Optional[uuid.UUID] = Query(None) to list_appointments(); call _ensure_location(location_id, practice_id, db) if set; add q = q.filter(Appointment.location_id == location_id) if set; (b) add same optional location_id param to get_waiting_room(); same guard + filter; (c) in get_checkin_defaults(): after existing roster_q filter on (practice_id, practitioner_id, roster_date), add a conditional join: if appt.location_id is not None, join Room and filter Room.location_id == appt.location_id. Call .first() on the narrowed query. No other appointment route changes. 6. Update seed.py: idempotently create one PracticeLocation (name='Main Street Surgery') for the dev practice; update the seeded Room rows to set location_id = that location.id; update the seeded WaitingArea to set location_id = that location.id. 7. Write tests/test_location_scoped_diary.py with 13 tests: (i) GET /diary/locations auth gate; (ii) GET /diary/locations cross-practice isolation; (iii) GET /diary/locations returns active locations only; (iv) GET /diary/template?location_id=X location-specific template; (v) GET /diary/template fallback to practice-wide when no location-specific template; (vi) GET /diary/template cross-practice location_id -> 404; (vii) GET /diary/roster?date&location_id=X returns only rooms for that location; (viii) GET /diary/waiting-areas?location_id=X returns only areas for that location; (ix) GET /appointments?location_id=X returns only that location's appointments; (x) GET /appointments cross-practice location_id -> 404; (xi) GET /appointments/waiting-room?location_id=X returns only that location; (xii) GET /appointments/{id}/checkin-defaults: practitioner with two location roster entries returns the correct room for the appointment location; (xiii) GET /appointments/{id}/checkin-defaults: appt with no location_id returns .first() result unchanged.

## Visual / Behavioural Acceptance Checks

1. alembic upgrade head applies cleanly. 2. GET /diary/locations: 401 without auth; returns practice locations; excludes other practice. 3. GET /diary/template?location_id=X returns location template or falls back gracefully. 4. GET /diary/roster/waiting-areas with location_id filters correctly; without location_id behavior is unchanged. 5. GET /appointments?location_id=X returns only that location's appointments; cross-practice -> 404. 6. GET /appointments/waiting-room?location_id=X filters to location. 7. checkin-defaults with appt.location_id set picks the room at that location, not a different location's room. 8. All 13 new tests pass. 9. Full focused suite (prior waiting-area + checkin tests) still passes. 10. py_compile on all 5 touched source files -> OK. 11. git diff --check -> OK.

## Risks / Ambiguities

1. DiaryTemplate constraint name: PostgreSQL auto-names column-level unique as diary_templates_practice_id_key. Will confirm or use op.execute(SELECT constraint_name ...) inspection before dropping. 2. Partial unique indexes are PostgreSQL-only — not a risk since EMR4 is Postgres-only. 3. Existing rows (rooms, waiting_areas, diary_templates) will have location_id=NULL after migration — queries without ?location_id return them unchanged. Single-location practices continue to work exactly as today. 4. _get_break_overlaps() queries DiaryTemplate by (practice_id, practitioner_id) without location scoping. In a multi-location practice with per-location templates, this may return breaks from both locations. Left as a known limitation to fix in a future sprint — it is a soft-block indicator, not a booking gate, so the impact is low. 5. checkin-defaults disambiguation requires the appointment to have location_id set AND the rooms to have location_id set. A practitioner appearing in rosters at two locations with neither appointments nor rooms carrying location_id will still get .first() — acceptable for single-location practices. 6. test_waiting_room.py session-ordering fragility is pre-existing; excluded from sprint verification as before.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
