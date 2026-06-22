"""
Waiting Area check-in contract for PATCH /api/v1/appointments/{id}/status.

Covers the three model_fields_set cases for optional waiting_area_id:
  - field absent  → existing area unchanged (backward compat)
  - explicit null → area cleared
  - UUID value    → area assigned (with cross-practice / inactive guard)

TUESDAY = 2026-06-23 (a real Tuesday; fits the Mon-Fri schedule fixture).
"""
from datetime import date, datetime, time, timezone

import pytest

from app.models.appointments import Appointment, AppointmentStatus, BookingChannel
from app.models.diary import WaitingArea
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


def _patch_status(client, token, appt_id, payload: dict):
    return client.patch(
        f"/api/v1/appointments/{appt_id}/status",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )


# ─── Auth gate ─────────────────────────────────────────────────────────────────

def test_checkin_requires_auth(client, db, practice, practitioner, patient):
    """PATCH /status without token → 401."""
    appt = _make_appt(db, practice, practitioner, patient)
    resp = client.patch(
        f"/api/v1/appointments/{appt.id}/status",
        json={"status": "Arrived"},
    )
    assert resp.status_code == 401


# ─── Backward compat: field absent ────────────────────────────────────────────

def test_status_patch_without_area_field_preserves_existing_area(
        client, db, gp_user, practice, practitioner, patient):
    """PATCH /status with no waiting_area_id field → existing area unchanged."""
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient,
                      waiting_area_id=area.id)
    token = make_token(gp_user)

    resp = _patch_status(client, token, appt.id, {"status": "Confirmed"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "Confirmed"
    assert data["waiting_area_id"] == str(area.id)


# ─── Assign area ───────────────────────────────────────────────────────────────

def test_status_patch_with_area_assigns_atomically(
        client, db, gp_user, practice, practitioner, patient):
    """PATCH /status with waiting_area_id → status + area set in one call."""
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    resp = _patch_status(client, token, appt.id, {
        "status": "Arrived",
        "waiting_area_id": str(area.id),
    })

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "Arrived"
    assert data["waiting_area_id"] == str(area.id)


# ─── Clear area (explicit null) ────────────────────────────────────────────────

def test_status_patch_with_null_area_clears_assignment(
        client, db, gp_user, practice, practitioner, patient):
    """PATCH /status with waiting_area_id=null → area cleared."""
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient,
                      waiting_area_id=area.id)
    token = make_token(gp_user)

    resp = _patch_status(client, token, appt.id, {
        "status": "InConsult",
        "waiting_area_id": None,
    })

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "InConsult"
    assert data["waiting_area_id"] is None


# ─── Cross-practice guard ──────────────────────────────────────────────────────

def test_status_patch_with_cross_practice_area_returns_404(
        client, db, gp_user, practice, practice_b, practitioner, patient):
    """PATCH /status with a waiting_area_id from another practice → 404."""
    area_b = WaitingArea(
        practice_id=practice_b.id,
        name="Other Practice Area",
        display_order=0,
        is_active=True,
    )
    db.add(area_b)
    db.flush()

    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    resp = _patch_status(client, token, appt.id, {
        "status": "Arrived",
        "waiting_area_id": str(area_b.id),
    })

    assert resp.status_code == 404


# ─── Inactive area guard ───────────────────────────────────────────────────────

def test_status_patch_with_inactive_area_returns_404(
        client, db, gp_user, practice, practitioner, patient):
    """PATCH /status with an inactive waiting_area_id → 404."""
    area = _make_area(db, practice, is_active=False)
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    resp = _patch_status(client, token, appt.id, {
        "status": "Arrived",
        "waiting_area_id": str(area.id),
    })

    assert resp.status_code == 404


# ─── Re-assign to different area ──────────────────────────────────────────────

def test_status_patch_can_reassign_to_different_area(
        client, db, gp_user, practice, practitioner, patient):
    """A second PATCH /status with a different waiting_area_id updates the area."""
    area1 = _make_area(db, practice, name="Area 1", order=0)
    area2 = _make_area(db, practice, name="Area 2", order=1)
    appt = _make_appt(db, practice, practitioner, patient,
                      waiting_area_id=area1.id)
    token = make_token(gp_user)

    resp = _patch_status(client, token, appt.id, {
        "status": "Confirmed",
        "waiting_area_id": str(area2.id),
    })

    assert resp.status_code == 200
    data = resp.json()
    assert data["waiting_area_id"] == str(area2.id)


# ─── Area preserved when only status changes ──────────────────────────────────

def test_status_change_without_area_field_does_not_clear_existing_area(
        client, db, gp_user, practice, practitioner, patient):
    """Multiple status transitions without touching area field keep the area intact."""
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient,
                      status=AppointmentStatus.Arrived,
                      waiting_area_id=area.id)
    token = make_token(gp_user)

    # Move to InConsult without specifying area
    resp = _patch_status(client, token, appt.id, {"status": "InConsult"})
    assert resp.status_code == 200
    assert resp.json()["waiting_area_id"] == str(area.id)

    # Move to Completed without specifying area
    resp = _patch_status(client, token, appt.id, {"status": "Completed"})
    assert resp.status_code == 200
    assert resp.json()["waiting_area_id"] == str(area.id)
