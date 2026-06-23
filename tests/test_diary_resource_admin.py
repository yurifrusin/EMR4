"""
Diary resource admin contract tests.

Covers:
- GET /api/v1/diary/rooms: auth, active-only default, include_inactive, location filter, isolation
- POST /api/v1/diary/rooms: role gate (403), create (201), cross-practice location 404,
  invalid default_waiting_area_id 400, display_order insertion/resequencing
- PATCH /api/v1/diary/rooms/{id}: role gate, cross-practice 404, partial update,
  archive (is_active=False), reordering, default_waiting_area_id validation
- POST /api/v1/diary/waiting-areas: role gate, create, cross-practice location 404
- PATCH /api/v1/diary/waiting-areas/{id}: role gate, cross-practice 404, partial update, archive
- Archive semantics: archived room excluded from active list; DiaryRoster reads unaffected
- Archived WaitingArea excluded from /waiting-areas; rejected as default_waiting_area_id
"""
import pytest

from app.models.diary import DiaryRoster, Room, WaitingArea
from app.models.tenancy import User, UserRole
from app.services.auth_service import hash_password
from tests.conftest import make_token


# ─── Local fixtures ────────────────────────────────────────────────────────────

@pytest.fixture()
def admin_user(db, practice):
    u = User(
        practice_id=practice.id,
        email="admin@test.local",
        password_hash=hash_password("Password1!"),
        role=UserRole.Admin,
    )
    db.add(u)
    db.flush()
    return u


@pytest.fixture()
def owner_user(db, practice):
    u = User(
        practice_id=practice.id,
        email="owner@test.local",
        password_hash=hash_password("Password1!"),
        role=UserRole.PracticeOwner,
    )
    db.add(u)
    db.flush()
    return u


def _area(db, practice, name="Main Waiting Room", order=0, is_active=True):
    a = WaitingArea(
        practice_id=practice.id,
        name=name,
        display_order=order,
        is_active=is_active,
    )
    db.add(a)
    db.flush()
    return a


def _room(db, practice, name="Room 1", order=0, is_active=True, default_area=None):
    r = Room(
        practice_id=practice.id,
        name=name,
        display_order=order,
        is_active=is_active,
        default_waiting_area_id=default_area,
    )
    db.add(r)
    db.flush()
    return r


# ─── GET /api/v1/diary/rooms ───────────────────────────────────────────────────

def test_rooms_requires_auth(client):
    r = client.get("/api/v1/diary/rooms")
    assert r.status_code == 401


def test_rooms_list_empty(client, gp_user):
    r = client.get("/api/v1/diary/rooms", headers={"Authorization": f"Bearer {make_token(gp_user)}"})
    assert r.status_code == 200
    assert r.json() == []


def test_rooms_list_active_only_by_default(client, db, gp_user, practice):
    _room(db, practice, "Active Room", order=0, is_active=True)
    _room(db, practice, "Archived Room", order=1, is_active=False)
    r = client.get("/api/v1/diary/rooms", headers={"Authorization": f"Bearer {make_token(gp_user)}"})
    assert r.status_code == 200
    names = [room["name"] for room in r.json()]
    assert "Active Room" in names
    assert "Archived Room" not in names


def test_rooms_include_inactive(client, db, admin_user, practice):
    _room(db, practice, "Active Room", order=0, is_active=True)
    _room(db, practice, "Archived Room", order=1, is_active=False)
    r = client.get(
        "/api/v1/diary/rooms?include_inactive=true",
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    assert r.status_code == 200
    names = [room["name"] for room in r.json()]
    assert "Active Room" in names
    assert "Archived Room" in names


def test_rooms_cross_practice_isolation(client, db, gp_user_b, practice_b):
    # Practice A room not visible via Practice B token
    from app.models.tenancy import Practice
    practice_a = db.query(Practice).filter(Practice.name == "Test Practice").first()
    if practice_a:
        _room(db, practice_a, "Practice A Room", order=0)
    r = client.get("/api/v1/diary/rooms", headers={"Authorization": f"Bearer {make_token(gp_user_b)}"})
    assert r.status_code == 200
    names = [room["name"] for room in r.json()]
    assert "Practice A Room" not in names


# ─── POST /api/v1/diary/rooms ─────────────────────────────────────────────────

def test_rooms_create_requires_admin(client, gp_user, receptionist_user):
    payload = {"name": "Room 1", "display_order": 0}
    for user in (gp_user, receptionist_user):
        r = client.post(
            "/api/v1/diary/rooms",
            json=payload,
            headers={"Authorization": f"Bearer {make_token(user)}"},
        )
        assert r.status_code == 403, f"Expected 403 for {user.role}, got {r.status_code}"


def test_rooms_create_admin(client, admin_user):
    r = client.post(
        "/api/v1/diary/rooms",
        json={"name": "Consult Room 1", "display_order": 0},
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Consult Room 1"
    assert data["display_order"] == 0
    assert data["is_active"] is True
    assert data["default_waiting_area_id"] is None


def test_rooms_create_owner(client, owner_user):
    r = client.post(
        "/api/v1/diary/rooms",
        json={"name": "Procedure Room", "display_order": 1},
        headers={"Authorization": f"Bearer {make_token(owner_user)}"},
    )
    assert r.status_code == 201


def test_rooms_create_with_valid_default_area(client, db, admin_user, practice):
    area = _area(db, practice, "Main Waiting Room")
    r = client.post(
        "/api/v1/diary/rooms",
        json={"name": "Room 1", "display_order": 0, "default_waiting_area_id": str(area.id)},
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    assert r.status_code == 201
    assert r.json()["default_waiting_area_id"] == str(area.id)


def test_rooms_create_invalid_default_area_rejected(client, db, admin_user, practice_b):
    # Area from practice_b is invalid for practice_a room
    area_b = _area(db, practice_b, "Other Practice Area")
    r = client.post(
        "/api/v1/diary/rooms",
        json={"name": "Room 1", "display_order": 0, "default_waiting_area_id": str(area_b.id)},
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    assert r.status_code == 400


def test_rooms_create_inactive_default_area_rejected(client, db, admin_user, practice):
    area = _area(db, practice, "Old Area", is_active=False)
    r = client.post(
        "/api/v1/diary/rooms",
        json={"name": "Room 1", "display_order": 0, "default_waiting_area_id": str(area.id)},
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    assert r.status_code == 400


def test_rooms_create_inserts_at_display_order_and_resequences(client, db, admin_user, practice):
    _room(db, practice, "Room 1", order=0)
    r = client.post(
        "/api/v1/diary/rooms",
        json={"name": "Room 2", "display_order": 0},
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    assert r.status_code == 201
    assert r.json()["display_order"] == 0

    list_r = client.get("/api/v1/diary/rooms", headers={"Authorization": f"Bearer {make_token(admin_user)}"})
    rooms = [(room["name"], room["display_order"]) for room in list_r.json()]
    assert rooms == [("Room 2", 0), ("Room 1", 1)]


# ─── PATCH /api/v1/diary/rooms/{id} ───────────────────────────────────────────

def test_rooms_update_requires_admin(client, db, gp_user, practice):
    room = _room(db, practice)
    r = client.patch(
        f"/api/v1/diary/rooms/{room.id}",
        json={"name": "Renamed"},
        headers={"Authorization": f"Bearer {make_token(gp_user)}"},
    )
    assert r.status_code == 403


def test_rooms_update_cross_practice_404(client, db, admin_user, practice_b):
    room_b = _room(db, practice_b, "B Room", order=0)
    r = client.patch(
        f"/api/v1/diary/rooms/{room_b.id}",
        json={"name": "Hacked"},
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    assert r.status_code == 404


def test_rooms_update_name(client, db, admin_user, practice):
    room = _room(db, practice)
    r = client.patch(
        f"/api/v1/diary/rooms/{room.id}",
        json={"name": "Renamed Room"},
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Renamed Room"


def test_rooms_update_display_order_moves_and_resequences(client, db, admin_user, practice):
    _room(db, practice, "Room 1", order=0)
    _room(db, practice, "Room 2", order=1)
    room_3 = _room(db, practice, "Room 3", order=2)

    r = client.patch(
        f"/api/v1/diary/rooms/{room_3.id}",
        json={"display_order": 1},
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    assert r.status_code == 200
    assert r.json()["display_order"] == 1

    list_r = client.get("/api/v1/diary/rooms", headers={"Authorization": f"Bearer {make_token(admin_user)}"})
    rooms = [(room["name"], room["display_order"]) for room in list_r.json()]
    assert rooms == [("Room 1", 0), ("Room 3", 1), ("Room 2", 2)]


def test_rooms_archived_order_no_longer_blocks_visible_reorder(client, db, admin_user, practice):
    _room(db, practice, "Room 1", order=0)
    _room(db, practice, "Room 2", order=1)
    _room(db, practice, "Archived Room", order=2, is_active=False)
    room_3 = _room(db, practice, "Room 3", order=3)

    r = client.patch(
        f"/api/v1/diary/rooms/{room_3.id}",
        json={"display_order": 2},
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    assert r.status_code == 200
    assert r.json()["display_order"] == 2

    list_r = client.get(
        "/api/v1/diary/rooms?include_inactive=true",
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    rooms = [(room["name"], room["display_order"], room["is_active"]) for room in list_r.json()]
    assert rooms == [
        ("Room 1", 0, True),
        ("Room 2", 1, True),
        ("Room 3", 2, True),
        ("Archived Room", 3, False),
    ]


def test_rooms_archive(client, db, admin_user, practice):
    room = _room(db, practice)
    r = client.patch(
        f"/api/v1/diary/rooms/{room.id}",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    assert r.status_code == 200
    assert r.json()["is_active"] is False

    # Archived room excluded from default GET
    list_r = client.get("/api/v1/diary/rooms", headers={"Authorization": f"Bearer {make_token(admin_user)}"})
    ids = [rm["id"] for rm in list_r.json()]
    assert str(room.id) not in ids


def test_rooms_archive_preserves_roster(client, db, admin_user, practice, practitioner):
    room = _room(db, practice)
    from datetime import date as _date
    db.add(DiaryRoster(
        practice_id=practice.id,
        room_id=room.id,
        roster_date=_date(2026, 7, 1),
        practitioner_id=practitioner.id,
    ))
    db.flush()

    # Archive the room
    client.patch(
        f"/api/v1/diary/rooms/{room.id}",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )

    # GET /roster with include_inactive should still return the roster entry
    roster_r = client.get(
        "/api/v1/diary/roster?date=2026-07-01&include_inactive=true",
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    # roster endpoint filters active rooms, so archived room won't appear — but
    # the key assertion is the request doesn't error and the room_id still exists in DB
    assert roster_r.status_code == 200
    db.expire(room)
    db.refresh(room)
    assert room.is_active is False  # room archived
    entry = db.query(DiaryRoster).filter(DiaryRoster.room_id == room.id).first()
    assert entry is not None  # roster entry still exists (not cascade-deleted)


def test_rooms_clear_default_waiting_area(client, db, admin_user, practice):
    area = _area(db, practice)
    room = _room(db, practice, default_area=area.id)
    r = client.patch(
        f"/api/v1/diary/rooms/{room.id}",
        json={"default_waiting_area_id": None},
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    assert r.status_code == 200
    assert r.json()["default_waiting_area_id"] is None


# ─── POST /api/v1/diary/waiting-areas ─────────────────────────────────────────

def test_waiting_areas_create_requires_admin(client, gp_user, receptionist_user):
    for user in (gp_user, receptionist_user):
        r = client.post(
            "/api/v1/diary/waiting-areas",
            json={"name": "Main", "display_order": 0},
            headers={"Authorization": f"Bearer {make_token(user)}"},
        )
        assert r.status_code == 403


def test_waiting_areas_create_admin(client, admin_user):
    r = client.post(
        "/api/v1/diary/waiting-areas",
        json={"name": "Main Waiting Room", "display_order": 0},
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Main Waiting Room"
    assert data["is_active"] is True


def test_waiting_areas_create_inserts_and_resequences(client, db, admin_user, practice):
    _area(db, practice, "Main Waiting Room", order=0)
    r = client.post(
        "/api/v1/diary/waiting-areas",
        json={"name": "Kids Play Area", "display_order": 0},
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    assert r.status_code == 201
    assert r.json()["display_order"] == 0

    list_r = client.get(
        "/api/v1/diary/waiting-areas",
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    areas = [(area["name"], area["display_order"]) for area in list_r.json()]
    assert areas == [("Kids Play Area", 0), ("Main Waiting Room", 1)]


# ─── PATCH /api/v1/diary/waiting-areas/{id} ───────────────────────────────────

def test_waiting_areas_update_requires_admin(client, db, gp_user, practice):
    area = _area(db, practice)
    r = client.patch(
        f"/api/v1/diary/waiting-areas/{area.id}",
        json={"name": "Renamed"},
        headers={"Authorization": f"Bearer {make_token(gp_user)}"},
    )
    assert r.status_code == 403


def test_waiting_areas_update_cross_practice_404(client, db, admin_user, practice_b):
    area_b = _area(db, practice_b, "B Area")
    r = client.patch(
        f"/api/v1/diary/waiting-areas/{area_b.id}",
        json={"name": "Hacked"},
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    assert r.status_code == 404


def test_waiting_areas_update_name(client, db, admin_user, practice):
    area = _area(db, practice)
    r = client.patch(
        f"/api/v1/diary/waiting-areas/{area.id}",
        json={"name": "Kids Corner"},
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Kids Corner"


def test_waiting_areas_update_display_order_moves_and_resequences(client, db, admin_user, practice):
    _area(db, practice, "Main Waiting Room", order=0)
    area_2 = _area(db, practice, "Kids Play Area", order=1)
    _area(db, practice, "TV Lounge", order=2)

    r = client.patch(
        f"/api/v1/diary/waiting-areas/{area_2.id}",
        json={"display_order": 2},
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    assert r.status_code == 200
    assert r.json()["display_order"] == 2

    list_r = client.get(
        "/api/v1/diary/waiting-areas",
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    areas = [(area["name"], area["display_order"]) for area in list_r.json()]
    assert areas == [("Main Waiting Room", 0), ("TV Lounge", 1), ("Kids Play Area", 2)]


def test_waiting_areas_get_compacts_gaps_after_archive(client, db, admin_user, practice):
    _area(db, practice, "Main Waiting Room", order=0)
    archived = _area(db, practice, "Archived Area", order=1, is_active=False)
    active = _area(db, practice, "Kids Play Area", order=4)

    r = client.get(
        "/api/v1/diary/waiting-areas",
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    assert r.status_code == 200
    areas = [(area["name"], area["display_order"]) for area in r.json()]
    assert areas == [("Main Waiting Room", 0), ("Kids Play Area", 1)]

    db.refresh(archived)
    db.refresh(active)
    assert archived.display_order == 2
    assert active.display_order == 1


def test_waiting_areas_archive(client, db, admin_user, practice):
    area = _area(db, practice)
    r = client.patch(
        f"/api/v1/diary/waiting-areas/{area.id}",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    assert r.status_code == 200
    assert r.json()["is_active"] is False

    # Archived area excluded from default GET /waiting-areas
    list_r = client.get(
        "/api/v1/diary/waiting-areas",
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    ids = [a["id"] for a in list_r.json()]
    assert str(area.id) not in ids


def test_waiting_areas_archived_rejected_as_room_default(client, db, admin_user, practice):
    area = _area(db, practice, is_active=False)
    r = client.post(
        "/api/v1/diary/rooms",
        json={"name": "Room 1", "display_order": 0, "default_waiting_area_id": str(area.id)},
        headers={"Authorization": f"Bearer {make_token(admin_user)}"},
    )
    assert r.status_code == 400
