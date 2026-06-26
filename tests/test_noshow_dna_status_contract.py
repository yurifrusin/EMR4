"""
NoShow / DNA status contract - explicit proof suite.

Pins the NoShow and DNA attendance outcomes explicitly through:
  - proposals/status (non-mutating terminal branch)
  - same-status block (already_in_status)
  - re-transition from terminal (already_terminal warning)
  - clears_waiting_area side-effect on proposal
  - GET /slots availability (non-blocking semantics via the slot API)
  - PATCH /{id}/status write path clearing waiting_area_id in DB
  - Cross-practice isolation on proposals

No diary frontend, taskpane, Command Centre, cancellation-reason, or
recurrence surface is touched here.
"""
from datetime import date, datetime, time, timezone

import pytest

from app.models.appointments import Appointment, AppointmentStatus, BookingChannel
from app.models.diary import WaitingArea
from tests.conftest import make_token

STATUS_URL = "/api/v1/appointments/proposals/status/{appt_id}"
SLOTS_URL = "/api/v1/appointments/slots/{practitioner_id}"

MONDAY = date(2026, 6, 22)   # Mon; schedule fixture covers Mon-Fri
THURSDAY = date(2026, 6, 26) # fixed future date; no conflict seeds on this day


# Helpers

def _make_appt(db, practice, practitioner, patient,
               status=AppointmentStatus.Booked,
               appt_date=THURSDAY, start_h=9,
               waiting_area_id=None):
    a = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(appt_date, time(start_h, 0), tzinfo=timezone.utc),
        appointment_date=appt_date,
        start_time_local=time(start_h, 0),
        duration_minutes=15,
        status=status,
        booked_via=BookingChannel.Receptionist,
        waiting_area_id=waiting_area_id,
    )
    db.add(a)
    db.flush()
    return a


def _make_area(db, practice):
    area = WaitingArea(practice_id=practice.id, name="Reception", is_active=True)
    db.add(area)
    db.flush()
    return area


def _propose_status(client, token, appt_id, new_status: str):
    return client.post(
        STATUS_URL.format(appt_id=appt_id),
        json={"status": new_status},
        headers={"Authorization": f"Bearer {token}"},
    )


def _patch_status(client, token, appt_id, new_status: str):
    return client.patch(
        f"/api/v1/appointments/{appt_id}/status",
        json={"status": new_status},
        headers={"Authorization": f"Bearer {token}"},
    )


# Proposal contract: NoShow and DNA are terminal (proposal tier)

@pytest.mark.parametrize("outcome", ["NoShow", "DNA"])
def test_status_proposal_noshow_dna_terminal_branch(
        outcome, client, db, gp_user, practice, practitioner, patient):
    """proposals/status to NoShow/DNA returns terminal proposal contract; DB unchanged."""
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    before_status = appt.status

    resp = _propose_status(client, token, appt.id, outcome)

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["intent"] == "update_appointment_status"
    assert data["safe"] is True
    assert data["requires_confirmation"] is True
    # Terminal status -> always proposal regardless of warnings
    assert data["autonomy_tier"] == "proposal"
    assert data["warnings"] == []
    assert data["blocks"] == []
    assert data["command"]["status"] == outcome
    assert data["command"]["clears_waiting_area"] is False
    # DB row must not be mutated by the proposal
    db.refresh(appt)
    assert appt.status == before_status


# Same-status block

@pytest.mark.parametrize("outcome", ["NoShow", "DNA"])
def test_status_proposal_same_noshow_dna_blocked(
        outcome, client, db, gp_user, practice, practitioner, patient):
    """Proposing the status the appointment already has (NoShow/DNA) -> already_in_status block."""
    status_enum = AppointmentStatus[outcome]
    appt = _make_appt(db, practice, practitioner, patient, status=status_enum)
    token = make_token(gp_user)

    resp = _propose_status(client, token, appt.id, outcome)

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert any(b["code"] == "already_in_status" for b in data["blocks"])
    # Row unchanged
    db.refresh(appt)
    assert appt.status == status_enum


# Re-transition away from existing NoShow/DNA

@pytest.mark.parametrize("terminal", ["NoShow", "DNA"])
def test_status_proposal_retransition_from_noshow_dna_warns_already_terminal(
        terminal, client, db, gp_user, practice, practitioner, patient):
    """Re-transitioning away from NoShow/DNA -> already_terminal warning, tier=proposal, row unchanged."""
    status_enum = AppointmentStatus[terminal]
    appt = _make_appt(db, practice, practitioner, patient, status=status_enum)
    token = make_token(gp_user)

    resp = _propose_status(client, token, appt.id, "Booked")

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["autonomy_tier"] == "proposal"
    assert any(w["code"] == "already_terminal" for w in data["warnings"])
    # Row unchanged
    db.refresh(appt)
    assert appt.status == status_enum


# Waiting-area cleared on NoShow/DNA proposal

@pytest.mark.parametrize("outcome", ["NoShow", "DNA"])
def test_status_proposal_noshow_dna_clears_waiting_area(
        outcome, client, db, gp_user, practice, practitioner, patient):
    """Proposing NoShow/DNA while patient is in a waiting area warns and surfaces clears_waiting_area.

    The proposal must not mutate the appointment or the waiting_area_id.
    """
    area = _make_area(db, practice)
    appt = _make_appt(
        db, practice, practitioner, patient,
        status=AppointmentStatus.Arrived,
        waiting_area_id=area.id,
    )
    token = make_token(gp_user)

    resp = _propose_status(client, token, appt.id, outcome)

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["autonomy_tier"] == "proposal"
    assert data["command"]["clears_waiting_area"] is True
    assert any(w["code"] == "waiting_area_cleared" for w in data["warnings"])
    # Row must not be mutated
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Arrived
    assert appt.waiting_area_id == area.id


# PATCH write path clears waiting_area_id in DB

@pytest.mark.parametrize("outcome", ["NoShow", "DNA"])
def test_patch_noshow_dna_clears_waiting_area_id_in_db(
        outcome, client, db, gp_user, practice, practitioner, patient):
    """PATCH /{id}/status to NoShow/DNA clears waiting_area_id on the appointment row."""
    area = _make_area(db, practice)
    appt = _make_appt(
        db, practice, practitioner, patient,
        status=AppointmentStatus.Arrived,
        waiting_area_id=area.id,
    )
    token = make_token(gp_user)

    resp = _patch_status(client, token, appt.id, outcome)

    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == outcome
    # waiting_area_id cleared in DB for terminal status
    db.refresh(appt)
    assert appt.waiting_area_id is None
    assert appt.status == AppointmentStatus[outcome]


# Slots API: NoShow/DNA do not block their slot

@pytest.mark.parametrize("outcome", ["NoShow", "DNA"])
def test_slots_noshow_dna_appointment_leaves_slot_available(
        outcome, client, db, gp_user, practice, practitioner, patient, schedule):
    """A NoShow/DNA appointment must not block its slot in GET /slots.

    Proves non-blocking via the public slot-availability API, not just via
    the internal create-conflict path.
    """
    status_enum = AppointmentStatus[outcome]
    # Place a NoShow/DNA appointment at 09:00 on Monday
    _make_appt(
        db, practice, practitioner, patient,
        status=status_enum,
        appt_date=MONDAY,
        start_h=9,
    )
    token = make_token(gp_user)

    resp = client.get(
        SLOTS_URL.format(practitioner_id=practitioner.id),
        params={"date": MONDAY.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    slots = resp.json()
    nine_am_slots = [s for s in slots if s["start_time"].startswith(f"{MONDAY}T09:00")]
    assert nine_am_slots, "09:00 slot missing from response"
    assert nine_am_slots[0]["available"] is True, (
        f"09:00 slot should be available when the appointment is {outcome}"
    )


# Cross-practice isolation

@pytest.mark.parametrize("outcome", ["NoShow", "DNA"])
def test_status_proposal_noshow_dna_cross_practice_returns_404(
        outcome, client, db, gp_user, practice_b, patient_b):
    """NoShow/DNA status proposal on another practice's appointment returns 404."""
    from app.models.tenancy import Practitioner

    pr_b = Practitioner(
        practice_id=practice_b.id,
        first_name="Cross",
        last_name="Practice",
        ahpra_number="MED1234512345",
    )
    db.add(pr_b)
    db.flush()
    appt_b = Appointment(
        practice_id=practice_b.id,
        patient_id=patient_b.id,
        practitioner_id=pr_b.id,
        start_time=datetime.combine(THURSDAY, time(9, 0), tzinfo=timezone.utc),
        appointment_date=THURSDAY,
        start_time_local=time(9, 0),
        duration_minutes=15,
        status=AppointmentStatus.Booked,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt_b)
    db.flush()

    resp = _propose_status(client, make_token(gp_user), appt_b.id, outcome)
    assert resp.status_code == 404
