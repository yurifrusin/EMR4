"""
GET /api/v1/diary/template must be authenticated and return the practice's
diary template (from DB or diary_template.json fallback).
"""
from datetime import time

from app.models.diary import DiaryBreak, DiaryColumn, DiaryTemplate
from tests.conftest import make_token


def test_template_requires_auth(client):
    resp = client.get("/api/v1/diary/template")
    assert resp.status_code == 401


def test_template_returns_db_record(client, db, gp_user, practice):
    """When a DiaryTemplate row exists for the practice, the endpoint returns it."""
    tmpl = DiaryTemplate(
        practice_id=practice.id,
        practice_name="Test Clinic",
        slot_start=time(9, 0),
        slot_end=time(17, 0),
        slot_interval_minutes=15,
        footer=["Messages:"],
    )
    db.add(tmpl)
    db.flush()

    col = DiaryColumn(
        template_id=tmpl.id,
        practice_id=practice.id,
        display_order=0,
        room_label="Room 1",
        assignment="Dr Alex Shera",
        practitioner_ahpra="MED0001234567",
    )
    db.add(col)
    db.flush()

    db.add(DiaryBreak(
        column_id=col.id,
        display_order=0,
        label="LUNCH",
        from_time=time(13, 0),
        to_time=time(14, 0),
    ))
    db.flush()

    token = make_token(gp_user)
    resp = client.get("/api/v1/diary/template", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()

    assert data["slot_interval_minutes"] == 15
    assert data["slot_start"] == "09:00:00"
    assert data["slot_end"] == "17:00:00"
    assert data["footer"] == ["Messages:"]
    assert len(data["columns"]) == 1
    col_out = data["columns"][0]
    assert col_out["room_label"] == "Room 1"
    assert col_out["practitioner_ahpra"] == "MED0001234567"
    assert len(col_out["breaks"]) == 1
    assert col_out["breaks"][0]["label"] == "LUNCH"
    assert col_out["breaks"][0]["from_time"] == "13:00:00"


def test_template_fallback_to_json(client, gp_user):
    """A practice with no DiaryTemplate row falls back to diary_template.json."""
    token = make_token(gp_user)
    resp = client.get("/api/v1/diary/template", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert "slot_start" in data
    assert "slot_end" in data
    assert "columns" in data
    assert len(data["columns"]) >= 1


def test_column_without_slot_interval_returns_null(client, db, gp_user, practice):
    """A column with no per-column interval returns slot_interval_minutes=null."""
    tmpl = DiaryTemplate(
        practice_id=practice.id,
        slot_start=time(9, 0),
        slot_end=time(17, 0),
        slot_interval_minutes=15,
        footer=[],
    )
    db.add(tmpl)
    db.flush()
    db.add(DiaryColumn(
        template_id=tmpl.id,
        practice_id=practice.id,
        display_order=0,
        room_label="Room A",
    ))
    db.flush()

    token = make_token(gp_user)
    resp = client.get("/api/v1/diary/template", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    col = resp.json()["columns"][0]
    assert col["slot_interval_minutes"] is None


def test_column_with_valid_slot_interval_returned(client, db, gp_user, practice):
    """A column with a valid per-column interval (10 min) returns that value."""
    tmpl = DiaryTemplate(
        practice_id=practice.id,
        slot_start=time(9, 0),
        slot_end=time(17, 0),
        slot_interval_minutes=15,
        footer=[],
    )
    db.add(tmpl)
    db.flush()
    db.add(DiaryColumn(
        template_id=tmpl.id,
        practice_id=practice.id,
        display_order=0,
        room_label="Nurse Room",
        slot_interval_minutes=10,
    ))
    db.flush()

    token = make_token(gp_user)
    resp = client.get("/api/v1/diary/template", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    col = resp.json()["columns"][0]
    assert col["slot_interval_minutes"] == 10


def test_practice_wide_interval_unaffected_by_column_override(client, db, gp_user, practice):
    """Practice-wide slot_interval_minutes is still returned correctly when a column overrides it."""
    tmpl = DiaryTemplate(
        practice_id=practice.id,
        slot_start=time(9, 0),
        slot_end=time(17, 0),
        slot_interval_minutes=15,
        footer=[],
    )
    db.add(tmpl)
    db.flush()
    db.add(DiaryColumn(
        template_id=tmpl.id,
        practice_id=practice.id,
        display_order=0,
        room_label="Room GP",
        slot_interval_minutes=None,
    ))
    db.add(DiaryColumn(
        template_id=tmpl.id,
        practice_id=practice.id,
        display_order=1,
        room_label="Room Nurse",
        slot_interval_minutes=10,
    ))
    db.flush()

    token = make_token(gp_user)
    resp = client.get("/api/v1/diary/template", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["slot_interval_minutes"] == 15
    assert data["columns"][0]["slot_interval_minutes"] is None
    assert data["columns"][1]["slot_interval_minutes"] == 10


def test_template_cross_practice_isolation(client, db, gp_user, practice_b):
    """A GP from practice A cannot see practice B's template."""
    tmpl_b = DiaryTemplate(
        practice_id=practice_b.id,
        practice_name="Other Clinic",
        slot_start=time(8, 0),
        slot_end=time(16, 0),
        slot_interval_minutes=20,
        footer=[],
    )
    db.add(tmpl_b)
    db.flush()

    token = make_token(gp_user)
    resp = client.get("/api/v1/diary/template", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    # gp_user belongs to practice (no template), so fallback fires — not practice_b's 20-min slots
    assert data.get("slot_interval_minutes") != 20
