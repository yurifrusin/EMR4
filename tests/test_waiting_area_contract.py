"""
Waiting Area contract tests.

Covers:
- GET /api/v1/diary/waiting-areas requires auth
- GET /api/v1/diary/waiting-areas returns practice-scoped named areas ordered by display_order
- Cross-practice isolation: Practice B areas not visible to Practice A token
- GET /api/v1/appointments/waiting-room backward compat with no filter
- GET /api/v1/appointments/waiting-room filters by waiting_area_id
- PUT /api/v1/appointments/{id} assigns appointment to a waiting area
- PUT with cross-practice waiting_area_id rejected as 404
- Inactive waiting area excluded from list
"""
from datetime import date, datetime, time, timezone

import pytest

from app.models.appointments import Appointment, AppointmentStatus, BookingChannel
from app.models.diary import WaitingArea
from tests.conftest import make_token

TODAY = date.today()


def _make_appt(db, practice, practitioner, patient, start_h=9, status=AppointmentStatus.Arrived):
    a = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(TODAY, time(start_h, 0), tzinfo=timezone.utc),
        appointment_date=TODAY,
        start_time_local=time(start_h, 0),
        duration_minutes=15,
        status=status,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(a)
    db.flush()
    return a


def _make_area(db, practice, name, order=0):
    area = WaitingArea(
        practice_id=practice.id,
        name=name,
        display_order=order,
        is_active=True,
    )
    db.add(area)
    db.flush()
    return area


# ─── Auth gate ─────────────────────────────────────────────────────────────────

def test_waiting_areas_requires_auth(client):
    r = client.get("/api/v1/diary/waiting-areas")
    assert r.status_code == 401


# ─── List endpoint ─────────────────────────────────────────────────────────────

def test_waiting_areas_returns_practice_scoped_areas(client, db, gp_user, practice):
    _make_area(db, practice, "Main Waiting Room", 0)
    _make_area(db, practice, "Children's Area", 1)
    token = make_token(gp_user)

    r = client.get("/api/v1/diary/waiting-areas", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    names = [a["name"] for a in r.json()]
    assert names == ["Main Waiting Room", "Children's Area"]


def test_waiting_areas_cross_practice_isolation(client, db, gp_user, practice, practice_b, gp_user_b):
    _make_area(db, practice_b, "Practice B Waiting", 0)
    token_a = make_token(gp_user)

    r = client.get("/api/v1/diary/waiting-areas", headers={"Authorization": f"Bearer {token_a}"})
    assert r.status_code == 200
    assert r.json() == []


def test_waiting_areas_inactive_excluded(client, db, gp_user, practice):
    active = _make_area(db, practice, "Active Room", 0)
    inactive = WaitingArea(
        practice_id=practice.id,
        name="Inactive Room",
        display_order=1,
        is_active=False,
    )
    db.add(inactive)
    db.flush()
    token = make_token(gp_user)

    r = client.get("/api/v1/diary/waiting-areas", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    names = [a["name"] for a in r.json()]
    assert names == ["Active Room"]
    assert "Inactive Room" not in names


# ─── Waiting-room endpoint ─────────────────────────────────────────────────────

def test_waiting_room_backward_compat_no_filter(
        client, db, gp_user, practice, practitioner, patient, schedule):
    _make_appt(db, practice, practitioner, patient, start_h=9)
    token = make_token(gp_user)

    r = client.get("/api/v1/appointments/waiting-room",
                   headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_waiting_room_filter_by_waiting_area_id(
        client, db, gp_user, practice, practitioner, patient, schedule):
    area_a = _make_area(db, practice, "Area A", 0)
    area_b = _make_area(db, practice, "Area B", 1)

    appt_a = _make_appt(db, practice, practitioner, patient, start_h=9)
    appt_a.waiting_area_id = area_a.id

    appt_b = _make_appt(db, practice, practitioner, patient, start_h=10)
    appt_b.waiting_area_id = area_b.id
    db.flush()

    token = make_token(gp_user)
    r = client.get(
        f"/api/v1/appointments/waiting-room?waiting_area_id={area_a.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["id"] == str(appt_a.id)


def test_waiting_room_filter_excludes_unassigned(
        client, db, gp_user, practice, practitioner, patient, schedule):
    area = _make_area(db, practice, "Area A", 0)
    # Create appointment with no waiting_area_id
    _make_appt(db, practice, practitioner, patient, start_h=9)
    token = make_token(gp_user)

    r = client.get(
        f"/api/v1/appointments/waiting-room?waiting_area_id={area.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json() == []


# ─── PUT assignment ────────────────────────────────────────────────────────────

def test_assign_appointment_to_waiting_area_via_put(
        client, db, gp_user, practice, practitioner, patient, schedule):
    area = _make_area(db, practice, "Main Waiting Room", 0)
    appt = _make_appt(db, practice, practitioner, patient, start_h=9)
    token = make_token(gp_user)

    r = client.put(
        f"/api/v1/appointments/{appt.id}",
        json={
            "patient_id": str(patient.id),
            "practitioner_id": str(practitioner.id),
            "appointment_date": str(TODAY),
            "start_time_local": "09:00:00",
            "waiting_area_id": str(area.id),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["waiting_area_id"] == str(area.id)


def test_cross_practice_waiting_area_rejected(
        client, db, gp_user, practice, practitioner, patient, schedule, practice_b, gp_user_b):
    area_b = _make_area(db, practice_b, "Practice B Area", 0)
    appt = _make_appt(db, practice, practitioner, patient, start_h=9)
    token_a = make_token(gp_user)

    r = client.put(
        f"/api/v1/appointments/{appt.id}",
        json={
            "patient_id": str(patient.id),
            "practitioner_id": str(practitioner.id),
            "appointment_date": str(TODAY),
            "start_time_local": "09:00:00",
            "waiting_area_id": str(area_b.id),
        },
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert r.status_code == 404
