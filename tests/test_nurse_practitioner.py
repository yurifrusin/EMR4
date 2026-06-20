"""
Nurse as a real Practitioner resource.

Room 2 in the diary template and roster is assigned to a nurse Practitioner
record so it is genuinely bookable — the appointment contract requires
practitioner_id, so label-only columns cannot accept bookings.

Verified here:
- Template column for Room 2 carries the nurse's practitioner_id / AHPRA
- Roster entry for Room 2 carries the nurse's AHPRA
- POST /appointments with nurse practitioner_id creates a booking (201)
- GET /slots/{nurse_id} returns available slots when the nurse has a schedule
- A nurse booking blocks that nurse slot without affecting the GP's slots
- A nurse booking does not interfere with a GP booking at the same wall-clock time
"""
from datetime import date, datetime, time

import pytest

from app.models.appointments import (
    Appointment,
    AppointmentStatus,
    BookingChannel,
    PractitionerSchedule,
)
from app.models.diary import DiaryColumn, DiaryRoster, DiaryTemplate, Room
from app.models.tenancy import Practitioner
from tests.conftest import make_token

MONDAY = date(2026, 6, 22)  # a Monday; slot tests use a fixed date


# ─── Local fixture: nurse practitioner ────────────────────────────────────────

@pytest.fixture()
def nurse(db, practice):
    n = Practitioner(
        practice_id=practice.id,
        first_name="Sarah",
        last_name="Chen",
        ahpra_number="NMW0001234567",
        specialty="Nursing",
        is_active=True,
    )
    db.add(n)
    db.flush()
    return n


@pytest.fixture()
def nurse_schedule(db, nurse):
    """Mon–Fri 09:00–17:00, 15-min slots for the nurse."""
    for dow in range(5):
        db.add(PractitionerSchedule(
            practitioner_id=nurse.id,
            day_of_week=dow,
            start_time=time(9, 0),
            end_time=time(17, 0),
            slot_duration_minutes=15,
        ))
    db.flush()


# ─── Template column ──────────────────────────────────────────────────────────

def test_template_room2_column_wired_to_nurse(client, db, gp_user, practice, nurse):
    """DiaryTemplate Room 2 column returns nurse practitioner_id and AHPRA."""
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
        room_label="Room 1",
        assignment="Dr Alex Shera",
    ))
    db.add(DiaryColumn(
        template_id=tmpl.id,
        practice_id=practice.id,
        display_order=1,
        room_label="Room 2",
        assignment=f"Nurse {nurse.first_name} {nurse.last_name}",
        practitioner_id=nurse.id,
        practitioner_ahpra=nurse.ahpra_number,
        tint_hex="FFFF99",
    ))
    db.flush()

    token = make_token(gp_user)
    resp = client.get("/api/v1/diary/template", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    cols = resp.json()["columns"]
    room2 = next(c for c in cols if c["room_label"] == "Room 2")
    assert room2["practitioner_id"] == str(nurse.id)
    assert room2["practitioner_ahpra"] == "NMW0001234567"


# ─── Roster entry ─────────────────────────────────────────────────────────────

def test_roster_room2_wired_to_nurse(client, db, gp_user, practice, nurse):
    """DiaryRoster Room 2 entry returns nurse AHPRA (not a plain label)."""
    room2 = Room(practice_id=practice.id, name="Room 2", display_order=1)
    db.add(room2)
    db.flush()
    db.add(DiaryRoster(
        practice_id=practice.id,
        room_id=room2.id,
        roster_date=MONDAY,
        practitioner_id=nurse.id,
        practitioner_ahpra=nurse.ahpra_number,
        label=None,
    ))
    db.flush()

    token = make_token(gp_user)
    resp = client.get(
        f"/api/v1/diary/roster?date={MONDAY.isoformat()}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    entries = resp.json()["entries"]
    room2_entry = next(e for e in entries if e["room_name"] == "Room 2")
    assert room2_entry["practitioner_ahpra"] == "NMW0001234567"
    assert room2_entry["practitioner_id"] == str(nurse.id)
    assert room2_entry["label"] is None


# ─── Appointment creation ─────────────────────────────────────────────────────

def test_nurse_appointment_can_be_created(
        client, db, gp_user, practice, nurse, patient, nurse_schedule):
    """POST /appointments with nurse practitioner_id creates a 201 booking."""
    token = make_token(gp_user)
    start = datetime(MONDAY.year, MONDAY.month, MONDAY.day, 9, 0)  # naive = local time
    resp = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": str(patient.id),
            "practitioner_id": str(nurse.id),
            "start_time": start.isoformat(),
            "duration_minutes": 15,
            "reason": "Wound dressing",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["practitioner"]["ahpra_number"] == "NMW0001234567"
    assert data["duration_minutes"] == 15


def test_nurse_appointment_blocked_by_conflict(
        client, db, gp_user, practice, nurse, patient, nurse_schedule):
    """A second nurse booking at the same slot returns 409 Conflict."""
    token = make_token(gp_user)
    start = datetime(MONDAY.year, MONDAY.month, MONDAY.day, 10, 0)  # naive = local time

    resp1 = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": str(patient.id),
            "practitioner_id": str(nurse.id),
            "start_time": start.isoformat(),
            "duration_minutes": 15,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp1.status_code == 201

    resp2 = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": str(patient.id),
            "practitioner_id": str(nurse.id),
            "start_time": start.isoformat(),
            "duration_minutes": 15,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp2.status_code == 409


# ─── Slots ────────────────────────────────────────────────────────────────────

def test_nurse_slots_available_when_schedule_exists(
        client, gp_user, nurse, nurse_schedule):
    """GET /slots/{nurse_id} returns available slots when nurse has a schedule."""
    token = make_token(gp_user)
    resp = client.get(
        f"/api/v1/appointments/slots/{nurse.id}",
        params={"date": MONDAY.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    slots = resp.json()
    assert len(slots) > 0
    assert all(s["available"] for s in slots)


def test_nurse_booking_blocks_nurse_slot_only(
        client, db, gp_user, practice, practitioner, nurse, patient,
        schedule, nurse_schedule):
    """A nurse booking marks that nurse slot unavailable but leaves GP's slot open."""
    token = make_token(gp_user)
    start = datetime(MONDAY.year, MONDAY.month, MONDAY.day, 9, 0)  # naive = local time

    resp = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": str(patient.id),
            "practitioner_id": str(nurse.id),
            "start_time": start.isoformat(),
            "duration_minutes": 15,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201

    nurse_slots = {
        s["start_time"][:16]: s["available"]
        for s in client.get(
            f"/api/v1/appointments/slots/{nurse.id}",
            params={"date": MONDAY.isoformat()},
            headers={"Authorization": f"Bearer {token}"},
        ).json()
    }
    gp_slots = {
        s["start_time"][:16]: s["available"]
        for s in client.get(
            f"/api/v1/appointments/slots/{practitioner.id}",
            params={"date": MONDAY.isoformat()},
            headers={"Authorization": f"Bearer {token}"},
        ).json()
    }

    nine_am = f"{MONDAY.isoformat()}T09:00"
    assert nurse_slots[nine_am] is False   # nurse slot blocked
    assert gp_slots[nine_am] is True       # GP slot unaffected
