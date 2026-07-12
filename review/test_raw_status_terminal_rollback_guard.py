"""
review/test_raw_status_terminal_rollback_guard.py — FAILING TEST PROPOSAL

Defect: PATCH /api/v1/appointments/{id}/status does not block
terminal-to-non-terminal status transitions. A Completed appointment can
be rolled back to Booked via the raw-compat PATCH path.

This test documents the current (broken) behaviour. The assertion at the
end is written to FAIL until the guard is added, at which point changing
the assertion to expect a 422 response will make the test pass.

Related to: _apply_appointment_status_update in appointments.py (line 2512).
The proposal path (propose_status_update) issues only a warning for
already_terminal transitions, not a block. The raw PATCH has no guard at all.
"""

import datetime

import pytest

from tests.conftest import make_token

FUTURE_DATE = datetime.datetime(2026, 7, 20)


def _create_appt(client, token, practitioner_id, patient_id):
    start = FUTURE_DATE.replace(hour=9, minute=0, second=0)
    resp = client.post(
        "/api/v1/appointments",
        json={
            "patient_id": str(patient_id),
            "practitioner_id": str(practitioner_id),
            "start_time": start.isoformat(),
            "duration_minutes": 15,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_terminal_to_non_terminal_status_rollback_blocked(
    client, gp_user, practitioner, patient
):
    """
    This test documents the defect: changing a Completed appointment back
    to Booked succeeds via the raw PATCH status endpoint. The test is
    written to FAIL (asserting the transition is blocked). Fix the
    production code so this assertion passes.
    """
    token = make_token(gp_user)
    appt = _create_appt(client, token, practitioner.id, patient.id)
    appt_id = appt["id"]

    # Set to Completed first
    resp1 = client.patch(
        f"/api/v1/appointments/{appt_id}/status",
        json={"status": "Completed"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp1.status_code == 200, resp1.text
    assert resp1.json()["status"] == "Completed"

    # ATTEMPT ROLLBACK: change Completed back to Booked
    # This is the defect - the server should block this with a 422
    resp2 = client.patch(
        f"/api/v1/appointments/{appt_id}/status",
        json={"status": "Booked"},
        headers={"Authorization": f"Bearer {token}"},
    )
    # TODO: After guard fix, change to assert resp2.status_code == 422
    # Current broken behaviour allows the transition
    assert resp2.status_code == 422, (
        f"Expected 422 blocking terminal->non-terminal transition, "
        f"got {resp2.status_code}: {resp2.text}"
    )


def test_terminal_dna_to_non_terminal_rollback_blocked(
    client, gp_user, practitioner, patient
):
    """
    Same defect: changing DNA back to Booked.
    """
    token = make_token(gp_user)
    appt = _create_appt(client, token, practitioner.id, patient.id)
    appt_id = appt["id"]

    # Set to DNA
    resp1 = client.patch(
        f"/api/v1/appointments/{appt_id}/status",
        json={
            "status": "DNA",
            "status_reason_code": "DID_NOT_ATTEND",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp1.status_code == 200, resp1.text
    assert resp1.json()["status"] == "DNA"

    # Attempt rollback
    resp2 = client.patch(
        f"/api/v1/appointments/{appt_id}/status",
        json={"status": "Confirmed"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp2.status_code == 422, (
        f"Expected 422 blocking DNA->Confirmed transition, "
        f"got {resp2.status_code}: {resp2.text}"
    )


def test_non_terminal_transition_is_allowed(
    client, gp_user, practitioner, patient
):
    """
    Non-terminal transitions (e.g., Booked->Confirmed->Arrived) should
    still work after the guard fix.
    """
    token = make_token(gp_user)
    appt = _create_appt(client, token, practitioner.id, patient.id)
    appt_id = appt["id"]

    # Booked -> Confirmed
    resp1 = client.patch(
        f"/api/v1/appointments/{appt_id}/status",
        json={"status": "Confirmed"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp1.status_code == 200, resp1.text
    assert resp1.json()["status"] == "Confirmed"

    # Confirmed -> Arrived
    resp2 = client.patch(
        f"/api/v1/appointments/{appt_id}/status",
        json={"status": "Arrived"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp2.status_code == 200, resp2.text
    assert resp2.json()["status"] == "Arrived"
