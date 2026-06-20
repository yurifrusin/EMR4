"""
Break-overlap warning contract for appointments.

Appointments that overlap a diary break are PERMITTED (soft block, not hard block).
The create/update response includes a breaks_overlap list so callers can surface a
warning to reception staff. An empty list means no break conflict.

THURSDAY = 2026-06-25 (a real Thursday; fits Mon-Fri schedule fixture).
"""
from datetime import date, datetime, time

import pytest

from tests.conftest import make_token

THURSDAY = date(2026, 6, 25)


def _start(hour: int, minute: int = 0) -> str:
    return datetime(THURSDAY.year, THURSDAY.month, THURSDAY.day, hour, minute).isoformat()


@pytest.fixture()
def diary_with_break(db, practice, practitioner):
    """DiaryTemplate with one column for the test practitioner with MORNING TEA 10:45–11:00."""
    from app.models.diary import DiaryTemplate, DiaryColumn, DiaryBreak

    tmpl = DiaryTemplate(
        practice_id=practice.id,
        slot_start=time(9, 0),
        slot_end=time(17, 0),
        slot_interval_minutes=15,
        footer=[],
    )
    db.add(tmpl)
    db.flush()
    col = DiaryColumn(
        template_id=tmpl.id,
        practice_id=practice.id,
        display_order=0,
        room_label="Room 1",
        assignment=f"Dr {practitioner.last_name}",
        practitioner_id=practitioner.id,
        practitioner_ahpra=practitioner.ahpra_number,
    )
    db.add(col)
    db.flush()
    db.add(DiaryBreak(
        column_id=col.id,
        display_order=0,
        label="MORNING TEA",
        from_time=time(10, 45),
        to_time=time(11, 0),
    ))
    db.flush()


# ─── Create routes ────────────────────────────────────────────────────────────

def test_appointment_overlapping_break_returns_201_with_warning(
        client, gp_user, practitioner, patient, schedule, diary_with_break):
    """Booking during a break succeeds (201) and populates breaks_overlap."""
    token = make_token(gp_user)
    resp = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": str(patient.id),
            "practitioner_id": str(practitioner.id),
            "start_time": _start(10, 45),  # exactly at MORNING TEA
            "duration_minutes": 15,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert "MORNING TEA" in data["breaks_overlap"]


def test_appointment_outside_break_has_empty_breaks_overlap(
        client, gp_user, practitioner, patient, schedule, diary_with_break):
    """Booking outside a break → 201 with empty breaks_overlap."""
    token = make_token(gp_user)
    resp = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": str(patient.id),
            "practitioner_id": str(practitioner.id),
            "start_time": _start(10),  # ends 10:15, before MORNING TEA at 10:45
            "duration_minutes": 15,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["breaks_overlap"] == []


def test_update_into_break_populates_breaks_overlap(
        client, gp_user, practitioner, patient, schedule, diary_with_break):
    """Rescheduling into a break via PUT also populates breaks_overlap."""
    token = make_token(gp_user)
    create = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": str(patient.id),
            "practitioner_id": str(practitioner.id),
            "start_time": _start(10),
            "duration_minutes": 15,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create.status_code == 201
    appt_id = create.json()["id"]

    resp = client.put(
        f"/api/v1/appointments/{appt_id}",
        json={
            "appointment_date": THURSDAY.isoformat(),
            "start_time_local": "10:45:00",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "MORNING TEA" in data["breaks_overlap"]


def test_appointment_without_diary_template_has_empty_breaks_overlap(
        client, gp_user, practitioner, patient, schedule):
    """Practice with no diary template → breaks_overlap is empty (no error)."""
    token = make_token(gp_user)
    resp = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": str(patient.id),
            "practitioner_id": str(practitioner.id),
            "start_time": _start(10, 45),
            "duration_minutes": 15,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["breaks_overlap"] == []
