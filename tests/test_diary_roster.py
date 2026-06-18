"""
GET /api/v1/diary/roster?date=YYYY-MM-DD must be authenticated and return
the practice's room roster for the given date (empty list if not configured).
"""
from datetime import date

from app.models.diary import Room, DiaryRoster
from app.models.tenancy import Practitioner
from tests.conftest import make_token


def test_roster_requires_auth(client):
    resp = client.get("/api/v1/diary/roster?date=2026-06-18")
    assert resp.status_code == 401


def test_roster_empty_when_no_rooms_configured(client, gp_user):
    """A practice with no rooms returns an empty entries list (not a 404)."""
    token = make_token(gp_user)
    resp = client.get("/api/v1/diary/roster?date=2026-06-18",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["date"] == "2026-06-18"
    assert data["entries"] == []


def test_roster_rooms_with_no_entries_return_null_assignment(client, db, gp_user, practice):
    """Rooms with no roster entry for the date return null practitioner/label."""
    db.add(Room(practice_id=practice.id, name="Room 1", display_order=0))
    db.add(Room(practice_id=practice.id, name="Room 2", display_order=1))
    db.flush()

    token = make_token(gp_user)
    resp = client.get("/api/v1/diary/roster?date=2026-06-18",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["date"] == "2026-06-18"
    assert len(data["entries"]) == 2
    for entry in data["entries"]:
        assert entry["practitioner_id"] is None
        assert entry["practitioner_ahpra"] is None
        assert entry["label"] is None


def test_roster_practitioner_assignment(client, db, gp_user, practice, practitioner):
    """A roster entry with a practitioner is returned with AHPRA."""
    room = Room(practice_id=practice.id, name="Room 1", display_order=0)
    db.add(room)
    db.flush()
    db.add(DiaryRoster(
        practice_id=practice.id,
        room_id=room.id,
        roster_date=date(2026, 6, 18),
        practitioner_id=practitioner.id,
        practitioner_ahpra=practitioner.ahpra_number,
    ))
    db.flush()

    token = make_token(gp_user)
    resp = client.get("/api/v1/diary/roster?date=2026-06-18",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    entry = resp.json()["entries"][0]
    assert entry["room_name"] == "Room 1"
    assert entry["practitioner_ahpra"] == "MED0001234567"
    assert entry["label"] is None


def test_roster_label_assignment(client, db, gp_user, practice):
    """A roster entry with a label (no practitioner) returns that label."""
    room = Room(practice_id=practice.id, name="Room 2", display_order=0)
    db.add(room)
    db.flush()
    db.add(DiaryRoster(
        practice_id=practice.id,
        room_id=room.id,
        roster_date=date(2026, 6, 18),
        label="[Available]",
    ))
    db.flush()

    token = make_token(gp_user)
    resp = client.get("/api/v1/diary/roster?date=2026-06-18",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    entry = resp.json()["entries"][0]
    assert entry["label"] == "[Available]"
    assert entry["practitioner_id"] is None


def test_roster_ordered_by_display_order(client, db, gp_user, practice):
    """Rooms are returned in display_order, not insertion order."""
    db.add(Room(practice_id=practice.id, name="Room C", display_order=2))
    db.add(Room(practice_id=practice.id, name="Room A", display_order=0))
    db.add(Room(practice_id=practice.id, name="Room B", display_order=1))
    db.flush()

    token = make_token(gp_user)
    resp = client.get("/api/v1/diary/roster?date=2026-06-18",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    names = [e["room_name"] for e in resp.json()["entries"]]
    assert names == ["Room A", "Room B", "Room C"]


def test_roster_inactive_rooms_excluded(client, db, gp_user, practice):
    """Rooms with is_active=False are excluded from roster results."""
    db.add(Room(practice_id=practice.id, name="Active Room", display_order=0, is_active=True))
    db.add(Room(practice_id=practice.id, name="Inactive Room", display_order=1, is_active=False))
    db.flush()

    token = make_token(gp_user)
    resp = client.get("/api/v1/diary/roster?date=2026-06-18",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    names = [e["room_name"] for e in resp.json()["entries"]]
    assert names == ["Active Room"]


def test_roster_cross_practice_isolation(client, db, gp_user, practice, practice_b):
    """A user from practice A cannot see practice B's rooms or roster."""
    room_b = Room(practice_id=practice_b.id, name="Room B1", display_order=0)
    db.add(room_b)
    db.flush()
    db.add(DiaryRoster(
        practice_id=practice_b.id,
        room_id=room_b.id,
        roster_date=date(2026, 6, 18),
        label="Dr Other",
    ))
    db.flush()

    token = make_token(gp_user)
    resp = client.get("/api/v1/diary/roster?date=2026-06-18",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    # gp_user belongs to practice (no rooms), so empty — not practice_b's rooms
    assert resp.json()["entries"] == []


def test_roster_date_isolation(client, db, gp_user, practice):
    """Roster entries for a different date are not returned."""
    room = Room(practice_id=practice.id, name="Room 1", display_order=0)
    db.add(room)
    db.flush()
    db.add(DiaryRoster(
        practice_id=practice.id,
        room_id=room.id,
        roster_date=date(2026, 6, 19),  # different date
        label="Dr Tomorrow",
    ))
    db.flush()

    token = make_token(gp_user)
    resp = client.get("/api/v1/diary/roster?date=2026-06-18",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    entry = resp.json()["entries"][0]
    assert entry["label"] is None  # no entry for 2026-06-18
