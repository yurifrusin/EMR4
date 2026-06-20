"""
Patient-identity / patient-link contract for appointments.

Splits patient identity from attendance status:
- A provisional booking carries patient_name_provisional (no patient_id).
- A linked booking carries patient_id and exposes the full PatientBrief.
- A provisional can be linked to a real patient later via PUT patient_id.

WEDNESDAY = 2026-06-24 (a real Wednesday; fits the Mon-Fri schedule fixture).
"""
from datetime import date, datetime

import pytest

from tests.conftest import make_token

WEDNESDAY = date(2026, 6, 24)


def _start(hour: int, minute: int = 0) -> str:
    return datetime(WEDNESDAY.year, WEDNESDAY.month, WEDNESDAY.day, hour, minute).isoformat()


# ─── Provisional booking (name only) ─────────────────────────────────────────

def test_provisional_booking_creates_201(client, gp_user, practitioner, schedule):
    """POST with patient_name_provisional and no patient_id → 201."""
    token = make_token(gp_user)
    resp = client.post(
        "/api/v1/appointments",
        json={
            "patient_name_provisional": "John Doe",
            "practitioner_id": str(practitioner.id),
            "start_time": _start(10),
            "duration_minutes": 15,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["patient_name_provisional"] == "John Doe"
    assert data["patient_id"] is None
    assert data["patient"] is None


def test_no_patient_identity_returns_422(client, gp_user, practitioner, schedule):
    """POST with neither patient_id nor patient_name_provisional → 422."""
    token = make_token(gp_user)
    resp = client.post(
        "/api/v1/appointments",
        json={
            "practitioner_id": str(practitioner.id),
            "start_time": _start(10),
            "duration_minutes": 15,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


def test_full_patient_booking_still_works(client, gp_user, practitioner, patient, schedule):
    """POST with patient_id only (no provisional name) → 201 with patient populated."""
    token = make_token(gp_user)
    resp = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": str(patient.id),
            "practitioner_id": str(practitioner.id),
            "start_time": _start(11),
            "duration_minutes": 15,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["patient_id"] == str(patient.id)
    assert data["patient"] is not None
    assert data["patient_name_provisional"] is None


def test_both_patient_id_and_name_accepted(client, gp_user, practitioner, patient, schedule):
    """POST with both patient_id and patient_name_provisional → 201."""
    token = make_token(gp_user)
    resp = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": str(patient.id),
            "patient_name_provisional": "Walk-in name",
            "practitioner_id": str(practitioner.id),
            "start_time": _start(11, 30),
            "duration_minutes": 15,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["patient_id"] == str(patient.id)
    assert data["patient"] is not None


# ─── GET returns provisional fields ──────────────────────────────────────────

def test_get_provisional_appointment_returns_name(client, gp_user, practitioner, schedule):
    """GET on a provisional appointment → patient_name_provisional set, patient None."""
    token = make_token(gp_user)
    create = client.post(
        "/api/v1/appointments",
        json={
            "patient_name_provisional": "Phone Caller",
            "practitioner_id": str(practitioner.id),
            "start_time": _start(14),
            "duration_minutes": 15,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create.status_code == 201
    appt_id = create.json()["id"]

    resp = client.get(
        f"/api/v1/appointments/{appt_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["patient_name_provisional"] == "Phone Caller"
    assert data["patient_id"] is None
    assert data["patient"] is None


# ─── Link provisional to real patient via PUT ─────────────────────────────────

def test_link_provisional_to_patient_via_put(client, gp_user, practitioner, patient, schedule):
    """PUT patient_id onto a provisional booking links the real patient record."""
    token = make_token(gp_user)
    create = client.post(
        "/api/v1/appointments",
        json={
            "patient_name_provisional": "Walk-in Smith",
            "practitioner_id": str(practitioner.id),
            "start_time": _start(15),
            "duration_minutes": 15,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create.status_code == 201
    appt_id = create.json()["id"]

    resp = client.put(
        f"/api/v1/appointments/{appt_id}",
        json={"patient_id": str(patient.id)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["patient_id"] == str(patient.id)
    assert data["patient"] is not None
    assert data["patient"]["first_name"] == patient.first_name


def test_link_to_wrong_practice_patient_returns_404(
        client, gp_user, practitioner, patient_b, schedule):
    """PUT with a patient_id from another practice → 404."""
    token = make_token(gp_user)
    create = client.post(
        "/api/v1/appointments",
        json={
            "patient_name_provisional": "Provisional",
            "practitioner_id": str(practitioner.id),
            "start_time": _start(15, 30),
            "duration_minutes": 15,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create.status_code == 201
    appt_id = create.json()["id"]

    resp = client.put(
        f"/api/v1/appointments/{appt_id}",
        json={"patient_id": str(patient_b.id)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


# ─── Status transitions on provisional ───────────────────────────────────────

def test_status_change_on_provisional_booking(client, gp_user, practitioner, schedule):
    """PATCH status on a provisional appointment succeeds; patient stays None."""
    token = make_token(gp_user)
    create = client.post(
        "/api/v1/appointments",
        json={
            "patient_name_provisional": "Arrived Walk-in",
            "practitioner_id": str(practitioner.id),
            "start_time": _start(16),
            "duration_minutes": 15,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create.status_code == 201
    appt_id = create.json()["id"]

    resp = client.patch(
        f"/api/v1/appointments/{appt_id}/status",
        json={"status": "Arrived"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "Arrived"
    assert data["patient"] is None
    assert data["patient_name_provisional"] == "Arrived Walk-in"
