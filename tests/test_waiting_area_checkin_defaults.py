"""
Waiting Area check-in defaults contract.

Covers:
- GET /api/v1/appointments/{id}/checkin-defaults
    - auth gate
    - cross-practice isolation
    - no DiaryRoster entry → nulls
    - DiaryRoster + active Room default → UUID + room name
    - DiaryRoster + inactive area → nulls
- PATCH /api/v1/appointments/{id}/status terminal auto-clear
    - Completed auto-clears waiting_area_id when field absent
    - Cancelled auto-clears waiting_area_id when field absent
    - Active-status transition does NOT auto-clear
    - Explicit UUID on terminal PATCH wins over auto-clear

TUESDAY = 2026-06-23 (a real Tuesday; fits the Mon-Fri schedule fixture).
"""
from datetime import date, datetime, time, timezone

import pytest

from app.models.appointments import Appointment, AppointmentStatus, BookingChannel
from app.models.diary import DiaryRoster, Room, WaitingArea
from tests.conftest import make_token

TUESDAY = date(2026, 6, 23)


def _make_appt(db, practice, practitioner, patient, start_h=9,
               status=AppointmentStatus.Booked, waiting_area_id=None):
    a = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(TUESDAY, time(start_h, 0), tzinfo=timezone.utc),
        appointment_date=TUESDAY,
        start_time_local=time(start_h, 0),
        duration_minutes=15,
        status=status,
        booked_via=BookingChannel.Receptionist,
        waiting_area_id=waiting_area_id,
    )
    db.add(a)
    db.flush()
    return a


def _make_area(db, practice, name="Main Waiting", order=0, is_active=True):
    area = WaitingArea(
        practice_id=practice.id,
        name=name,
        display_order=order,
        is_active=is_active,
    )
    db.add(area)
    db.flush()
    return area


def _make_room(db, practice, name="Room 1", order=0, default_waiting_area_id=None):
    room = Room(
        practice_id=practice.id,
        name=name,
        display_order=order,
        is_active=True,
        default_waiting_area_id=default_waiting_area_id,
    )
    db.add(room)
    db.flush()
    return room


def _make_roster(db, practice, room, practitioner, roster_date=TUESDAY):
    entry = DiaryRoster(
        practice_id=practice.id,
        room_id=room.id,
        roster_date=roster_date,
        practitioner_id=practitioner.id,
    )
    db.add(entry)
    db.flush()
    return entry


# ─── GET /checkin-defaults ─────────────────────────────────────────────────────

def test_checkin_defaults_requires_auth(client, db, practice, practitioner, patient):
    """GET without token → 401."""
    appt = _make_appt(db, practice, practitioner, patient)
    resp = client.get(f"/api/v1/appointments/{appt.id}/checkin-defaults")
    assert resp.status_code == 401


def test_checkin_defaults_cross_practice_returns_404(
        client, db, gp_user, practice_b, patient_b):
    """GET with an appointment from another practice → 404."""
    from app.models.tenancy import Practitioner
    prac_b = Practitioner(
        practice_id=practice_b.id,
        first_name="Other", last_name="Doctor",
        ahpra_number="MED0009999999",
    )
    db.add(prac_b)
    db.flush()
    appt_b = _make_appt(db, practice_b, prac_b, patient_b)

    token = make_token(gp_user)
    resp = client.get(
        f"/api/v1/appointments/{appt_b.id}/checkin-defaults",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


def test_checkin_defaults_no_roster_returns_nulls(
        client, db, gp_user, practice, practitioner, patient):
    """GET with no DiaryRoster entry → both fields null."""
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    resp = client.get(
        f"/api/v1/appointments/{appt.id}/checkin-defaults",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["suggested_waiting_area_id"] is None
    assert data["room_name"] is None


def test_checkin_defaults_with_active_default_returns_suggestion(
        client, db, gp_user, practice, practitioner, patient):
    """GET with DiaryRoster + Room.default_waiting_area_id + active area → suggestion."""
    area = _make_area(db, practice, name="Main Waiting")
    room = _make_room(db, practice, name="Room 1", default_waiting_area_id=area.id)
    _make_roster(db, practice, room, practitioner)

    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    resp = client.get(
        f"/api/v1/appointments/{appt.id}/checkin-defaults",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["suggested_waiting_area_id"] == str(area.id)
    assert data["room_name"] == "Room 1"


def test_checkin_defaults_inactive_area_returns_nulls(
        client, db, gp_user, practice, practitioner, patient):
    """GET with DiaryRoster + Room default pointing to an inactive area → nulls."""
    area = _make_area(db, practice, name="Closed Wing", is_active=False)
    room = _make_room(db, practice, name="Room 2", default_waiting_area_id=area.id)
    _make_roster(db, practice, room, practitioner)

    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    resp = client.get(
        f"/api/v1/appointments/{appt.id}/checkin-defaults",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["suggested_waiting_area_id"] is None
    assert data["room_name"] == "Room 2"


# ─── Terminal status auto-clear ────────────────────────────────────────────────

def test_patch_to_completed_auto_clears_area(
        client, db, gp_user, practice, practitioner, patient):
    """PATCH to Completed with no waiting_area_id field → area auto-cleared."""
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient,
                      status=AppointmentStatus.InConsult,
                      waiting_area_id=area.id)
    token = make_token(gp_user)

    resp = client.patch(
        f"/api/v1/appointments/{appt.id}/status",
        json={"status": "Completed"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["waiting_area_id"] is None


def test_patch_to_cancelled_auto_clears_area(
        client, db, gp_user, practice, practitioner, patient):
    """PATCH to Cancelled with no waiting_area_id field → area auto-cleared."""
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient,
                      status=AppointmentStatus.Arrived,
                      waiting_area_id=area.id)
    token = make_token(gp_user)

    resp = client.patch(
        f"/api/v1/appointments/{appt.id}/status",
        json={"status": "Cancelled"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["waiting_area_id"] is None


def test_patch_to_active_status_does_not_auto_clear(
        client, db, gp_user, practice, practitioner, patient):
    """PATCH to InConsult (active) with no waiting_area_id field → area preserved."""
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient,
                      status=AppointmentStatus.Arrived,
                      waiting_area_id=area.id)
    token = make_token(gp_user)

    resp = client.patch(
        f"/api/v1/appointments/{appt.id}/status",
        json={"status": "InConsult"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["waiting_area_id"] == str(area.id)


def test_explicit_uuid_on_terminal_patch_wins_over_auto_clear(
        client, db, gp_user, practice, practitioner, patient):
    """Explicit waiting_area_id on a terminal PATCH wins; area is assigned, not cleared."""
    area1 = _make_area(db, practice, name="Area 1", order=0)
    area2 = _make_area(db, practice, name="Area 2", order=1)
    appt = _make_appt(db, practice, practitioner, patient,
                      status=AppointmentStatus.InConsult,
                      waiting_area_id=area1.id)
    token = make_token(gp_user)

    resp = client.patch(
        f"/api/v1/appointments/{appt.id}/status",
        json={"status": "Completed", "waiting_area_id": str(area2.id)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["waiting_area_id"] == str(area2.id)
