"""
GET /api/v1/appointments/slots/{practitioner_id} must use duration-aware
overlap logic: a 30-minute booking at 09:00 must mark BOTH the 09:00 and
09:15 slots as unavailable, not just 09:00.

This tests the fix for the double-booking bug where the old implementation
used exact start-time equality and therefore left overlapping slots "available".
"""

from datetime import datetime

import pytest

from tests.conftest import make_token

MONDAY = datetime(2026, 6, 22)  # day portion only; time is irrelevant for ?date=


def _slots(client, token, practitioner_id, date=MONDAY):
    resp = client.get(
        f"/api/v1/appointments/slots/{practitioner_id}",
        params={"date": date.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    return {s["start_time"][:16]: s["available"] for s in resp.json()}


def _create_appt(client, token, practitioner_id, patient_id, hour, minute, duration):
    start = datetime(2026, 6, 22, hour, minute, 0)
    resp = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": str(patient_id),
            "practitioner_id": str(practitioner_id),
            "start_time": start.isoformat(),
            "duration_minutes": duration,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_no_bookings_all_slots_available(client, gp_user, practitioner, schedule):
    """With no appointments, every slot in the schedule is available."""
    token = make_token(gp_user)
    slots = _slots(client, token, practitioner.id)
    assert slots, "Expected at least one slot"
    assert all(slots.values()), "All slots should be available with no bookings"


def test_15min_booking_blocks_only_its_slot(client, receptionist_user, gp_user, practitioner, patient, schedule):
    """A 15-minute booking at 09:00 marks only 09:00 as unavailable."""
    rec_token = make_token(receptionist_user)
    gp_token = make_token(gp_user)

    _create_appt(client, rec_token, practitioner.id, patient.id, 9, 0, 15)

    slots = _slots(client, gp_token, practitioner.id)
    assert slots["2026-06-22T09:00"] is False, "09:00 should be unavailable"
    assert slots["2026-06-22T09:15"] is True,  "09:15 should still be available"
    assert slots["2026-06-22T09:30"] is True,  "09:30 should still be available"


def test_30min_booking_blocks_two_slots(client, receptionist_user, gp_user, practitioner, patient, schedule):
    """A 30-minute booking at 09:00 blocks both 09:00 and 09:15 slots."""
    rec_token = make_token(receptionist_user)
    gp_token = make_token(gp_user)

    _create_appt(client, rec_token, practitioner.id, patient.id, 9, 0, 30)

    slots = _slots(client, gp_token, practitioner.id)
    assert slots["2026-06-22T09:00"] is False, "09:00 should be unavailable"
    assert slots["2026-06-22T09:15"] is False, "09:15 overlaps 30-min booking — must be unavailable"
    assert slots["2026-06-22T09:30"] is True,  "09:30 is after the booking ends — should be available"


def test_cancelled_booking_does_not_block_slots(client, receptionist_user, gp_user, practitioner, patient, schedule):
    """Cancelled appointments are excluded from slot blocking."""
    rec_token = make_token(receptionist_user)
    gp_token = make_token(gp_user)

    appt = _create_appt(client, rec_token, practitioner.id, patient.id, 9, 0, 30)
    client.patch(
        f"/api/v1/appointments/{appt['id']}/status",
        json={"status": "Cancelled"},
        headers={"Authorization": f"Bearer {rec_token}"},
    )

    slots = _slots(client, gp_token, practitioner.id)
    assert slots["2026-06-22T09:00"] is True,  "Cancelled booking should free 09:00"
    assert slots["2026-06-22T09:15"] is True,  "Cancelled booking should free 09:15"


def test_no_schedule_returns_empty_slots(client, gp_user, practitioner):
    """No schedule entry for the practitioner → empty slot list (not an error)."""
    token = make_token(gp_user)
    resp = client.get(
        f"/api/v1/appointments/slots/{practitioner.id}",
        params={"date": MONDAY.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json() == []
