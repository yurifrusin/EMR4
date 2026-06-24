"""
Non-mutating update/status proposal contract for existing appointments.

Every test proves the Appointment row is unchanged after the proposal call.
"""
from datetime import date, datetime, time, timezone

import pytest

from app.models.appointments import Appointment, AppointmentStatus, BookingChannel
from app.models.diary import DiaryBreak, DiaryColumn, DiaryTemplate, WaitingArea
from app.models.tenancy import Practitioner
from tests.conftest import make_token

THURSDAY = date(2026, 6, 26)   # a fixed future Thursday, guaranteed no conflict seeds
TODAY = date.today()

UPDATE_URL = "/api/v1/appointments/proposals/update/{appt_id}"
STATUS_URL = "/api/v1/appointments/proposals/status/{appt_id}"


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _make_appt(
    db, practice, practitioner, patient,
    appt_date=THURSDAY,
    start_h=9, start_m=0, duration=15,
    status=AppointmentStatus.Booked,
    waiting_area_id=None,
):
    appt = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(appt_date, time(start_h, start_m), tzinfo=timezone.utc),
        appointment_date=appt_date,
        start_time_local=time(start_h, start_m),
        duration_minutes=duration,
        status=status,
        booked_via=BookingChannel.Receptionist,
        waiting_area_id=waiting_area_id,
    )
    db.add(appt)
    db.flush()
    return appt


def _make_area(db, practice):
    area = WaitingArea(
        practice_id=practice.id,
        name="Main Waiting",
        is_active=True,
    )
    db.add(area)
    db.flush()
    return area


@pytest.fixture()
def diary_with_break(db, practice, practitioner):
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


# ─── Update proposal tests ────────────────────────────────────────────────────

def test_update_proposal_requires_auth(client, db, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    resp = client.post(UPDATE_URL.format(appt_id=appt.id), json={})
    assert resp.status_code == 401


def test_update_proposal_returns_typed_command_without_mutating(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, start_h=9)
    token = make_token(gp_user)
    before_status = appt.status
    before_count = db.query(Appointment).count()

    resp = client.post(
        UPDATE_URL.format(appt_id=appt.id),
        json={
            "appointment_date": THURSDAY.isoformat(),
            "start_time_local": "10:00:00",
            "duration_minutes": 30,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["intent"] == "update_appointment"
    assert data["safe"] is True
    assert data["requires_confirmation"] is True
    assert data["autonomy_tier"] == "proposal"
    assert data["patient_identity"] == "linked"
    assert data["warnings"] == []
    assert data["blocks"] == []
    assert data["command"]["appointment_id"] == str(appt.id)
    assert data["command"]["appointment_date"] == THURSDAY.isoformat()
    assert data["command"]["start_time_local"] == "10:00:00"
    assert data["command"]["duration_minutes"] == 30
    # DB row unchanged
    db.refresh(appt)
    assert appt.status == before_status
    assert db.query(Appointment).count() == before_count
    # Row still has old time, not the proposed time
    assert appt.start_time_local == time(9, 0)


def test_update_proposal_blocked_on_conflict(
        client, db, gp_user, practice, practitioner, patient):
    # Existing occupies 10:00–10:30
    existing = _make_appt(db, practice, practitioner, patient, start_h=10, duration=30)
    # Subject we're proposing to move
    subject = _make_appt(db, practice, practitioner, patient, start_h=14, duration=15)
    token = make_token(gp_user)

    resp = client.post(
        UPDATE_URL.format(appt_id=subject.id),
        json={
            "appointment_date": THURSDAY.isoformat(),
            "start_time_local": "10:15:00",
            "duration_minutes": 15,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert data["blocks"][0]["code"] == "appointment_conflict"
    assert data["conflict"]["appointment_id"] == str(existing.id)
    # Subject row unchanged
    db.refresh(subject)
    assert subject.start_time_local == time(14, 0)


def test_update_proposal_blocked_on_terminal_status(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(
        db, practice, practitioner, patient,
        status=AppointmentStatus.Completed,
    )
    token = make_token(gp_user)
    before_count = db.query(Appointment).count()

    resp = client.post(
        UPDATE_URL.format(appt_id=appt.id),
        json={"start_time_local": "11:00:00", "appointment_date": THURSDAY.isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert data["blocks"][0]["code"] == "terminal_status"
    assert db.query(Appointment).count() == before_count


def test_update_proposal_warns_break_overlap(
        client, db, gp_user, practice, practitioner, patient, diary_with_break):
    appt = _make_appt(db, practice, practitioner, patient, start_h=14)
    token = make_token(gp_user)

    resp = client.post(
        UPDATE_URL.format(appt_id=appt.id),
        json={
            "appointment_date": THURSDAY.isoformat(),
            "start_time_local": "10:45:00",
            "duration_minutes": 15,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["autonomy_tier"] == "proposal"
    assert "MORNING TEA" in data["breaks_overlap"]
    assert data["warnings"][0]["code"] == "break_overlap"
    # Row unchanged
    db.refresh(appt)
    assert appt.start_time_local == time(14, 0)


def test_update_proposal_warns_provisional_patient(
        client, db, gp_user, practice, practitioner):
    """Appointment with only a provisional name (no patient_id) → provisional warning."""
    appt = Appointment(
        practice_id=practice.id,
        patient_name_provisional="Walk-in",
        practitioner_id=practitioner.id,
        start_time=datetime.combine(THURSDAY, time(15, 0), tzinfo=timezone.utc),
        appointment_date=THURSDAY,
        start_time_local=time(15, 0),
        duration_minutes=15,
        status=AppointmentStatus.Booked,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt)
    db.flush()
    token = make_token(gp_user)

    resp = client.post(
        UPDATE_URL.format(appt_id=appt.id),
        json={"duration_minutes": 30},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["patient_identity"] == "provisional"
    assert any(w["code"] == "provisional_patient" for w in data["warnings"])
    # Row unchanged
    db.refresh(appt)
    assert appt.duration_minutes == 15


def test_update_proposal_merges_current_values(
        client, db, gp_user, practice, practitioner, patient):
    """Unset fields in the body are filled from the existing appointment."""
    appt = _make_appt(
        db, practice, practitioner, patient,
        start_h=9, duration=45,
    )
    token = make_token(gp_user)

    # Only change duration; everything else should come from the existing row
    resp = client.post(
        UPDATE_URL.format(appt_id=appt.id),
        json={"duration_minutes": 20},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    cmd = data["command"]
    assert cmd["appointment_date"] == appt.appointment_date.isoformat()
    assert cmd["start_time_local"] == "09:00:00"
    assert cmd["duration_minutes"] == 20
    assert cmd["practitioner_id"] == str(practitioner.id)
    # Row still has original duration
    db.refresh(appt)
    assert appt.duration_minutes == 45


# ─── Status proposal tests ────────────────────────────────────────────────────

def test_status_proposal_requires_auth(client, db, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient)
    resp = client.post(
        STATUS_URL.format(appt_id=appt.id),
        json={"status": "Confirmed"},
    )
    assert resp.status_code == 401


def test_status_proposal_routine_transition_execute_with_report(
        client, db, gp_user, practice, practitioner, patient):
    """Booked → Confirmed with no warnings → autonomy_tier = execute_with_report."""
    appt = _make_appt(db, practice, practitioner, patient, status=AppointmentStatus.Booked)
    token = make_token(gp_user)
    before_status = appt.status

    resp = client.post(
        STATUS_URL.format(appt_id=appt.id),
        json={"status": "Confirmed"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["intent"] == "update_appointment_status"
    assert data["safe"] is True
    assert data["requires_confirmation"] is True
    assert data["autonomy_tier"] == "execute_with_report"
    assert data["warnings"] == []
    assert data["blocks"] == []
    assert data["command"]["status"] == "Confirmed"
    assert data["command"]["clears_waiting_area"] is False
    # Row unchanged
    db.refresh(appt)
    assert appt.status == before_status


def test_status_proposal_warns_clears_waiting_area(
        client, db, gp_user, practice, practitioner, patient):
    """Moving to Completed while patient is in a waiting area warns about clearing it."""
    area = _make_area(db, practice)
    appt = _make_appt(
        db, practice, practitioner, patient,
        status=AppointmentStatus.Arrived,
        waiting_area_id=area.id,
    )
    token = make_token(gp_user)

    resp = client.post(
        STATUS_URL.format(appt_id=appt.id),
        json={"status": "Completed"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["command"]["clears_waiting_area"] is True
    assert any(w["code"] == "waiting_area_cleared" for w in data["warnings"])
    assert data["autonomy_tier"] == "proposal"   # terminal status → always proposal
    # Row unchanged
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Arrived
    assert appt.waiting_area_id == area.id


def test_status_proposal_blocked_on_same_status(
        client, db, gp_user, practice, practitioner, patient):
    """Proposing the status the appointment already has → blocked."""
    appt = _make_appt(
        db, practice, practitioner, patient,
        status=AppointmentStatus.Confirmed,
    )
    token = make_token(gp_user)

    resp = client.post(
        STATUS_URL.format(appt_id=appt.id),
        json={"status": "Confirmed"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert data["blocks"][0]["code"] == "already_in_status"


def test_status_proposal_warns_already_terminal(
        client, db, gp_user, practice, practitioner, patient):
    """Re-transitioning a terminal appointment → warning, tier = proposal."""
    appt = _make_appt(
        db, practice, practitioner, patient,
        status=AppointmentStatus.Cancelled,
    )
    token = make_token(gp_user)

    resp = client.post(
        STATUS_URL.format(appt_id=appt.id),
        json={"status": "Booked"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["autonomy_tier"] == "proposal"
    assert any(w["code"] == "already_terminal" for w in data["warnings"])
    # Row unchanged
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Cancelled


# ─── Update proposal hardening tests ─────────────────────────────────────────

def test_update_proposal_blocked_explicit_null_practitioner(
        client, db, gp_user, practice, practitioner, patient):
    """Explicit {practitioner_id: null} → clean BLOCK, not a 404."""
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    resp = client.post(
        UPDATE_URL.format(appt_id=appt.id),
        json={"practitioner_id": None},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert any(b["code"] == "practitioner_required" for b in data["blocks"])
    # Row unchanged
    db.refresh(appt)
    assert appt.practitioner_id == practitioner.id


def test_update_proposal_blocked_clear_patient_id_with_no_provisional(
        client, db, gp_user, practice, practitioner, patient):
    """Clearing patient_id on a linked appointment (no provisional name) → BLOCK."""
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    resp = client.post(
        UPDATE_URL.format(appt_id=appt.id),
        json={"patient_id": None},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert any(b["code"] == "patient_identity_required" for b in data["blocks"])
    # Row unchanged
    db.refresh(appt)
    assert appt.patient_id == patient.id


def test_update_proposal_null_patient_id_with_provisional_is_safe(
        client, db, gp_user, practice, practitioner, patient):
    """Downgrading to provisional by sending patient_id=null + provisional name is safe."""
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    resp = client.post(
        UPDATE_URL.format(appt_id=appt.id),
        json={"patient_id": None, "patient_name_provisional": "Walk-in"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["patient_identity"] == "provisional"
    assert any(w["code"] == "provisional_patient" for w in data["warnings"])
    # Row unchanged
    db.refresh(appt)
    assert appt.patient_id == patient.id


def test_update_proposal_cross_practice_returns_404(
        client, db, gp_user, practice_b, patient_b):
    """Proposing an update for another practice's appointment returns 404."""
    import uuid as _uuid
    pr_b = Practitioner(
        practice_id=practice_b.id,
        first_name="Other",
        last_name="Doctor",
        ahpra_number="MED9999999999",
    )
    db.add(pr_b)
    db.flush()
    appt_b = Appointment(
        practice_id=practice_b.id,
        patient_id=patient_b.id,
        practitioner_id=pr_b.id,
        start_time=datetime.combine(THURSDAY, time(10, 0), tzinfo=timezone.utc),
        appointment_date=THURSDAY,
        start_time_local=time(10, 0),
        duration_minutes=15,
        status=AppointmentStatus.Booked,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt_b)
    db.flush()

    resp = client.post(
        UPDATE_URL.format(appt_id=appt_b.id),
        json={"duration_minutes": 30},
        headers={"Authorization": f"Bearer {make_token(gp_user)}"},
    )
    assert resp.status_code == 404


def test_update_proposal_nonexistent_appointment_returns_404(
        client, db, gp_user):
    """Random UUID → 404."""
    import uuid as _uuid
    resp = client.post(
        UPDATE_URL.format(appt_id=_uuid.uuid4()),
        json={},
        headers={"Authorization": f"Bearer {make_token(gp_user)}"},
    )
    assert resp.status_code == 404


def test_update_proposal_empty_body_reflects_current_values(
        client, db, gp_user, practice, practitioner, patient):
    """Empty body → safe proposal whose command mirrors the existing appointment."""
    appt = _make_appt(db, practice, practitioner, patient, start_h=11, duration=30)
    token = make_token(gp_user)

    resp = client.post(
        UPDATE_URL.format(appt_id=appt.id),
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    cmd = data["command"]
    assert cmd["appointment_id"] == str(appt.id)
    assert cmd["appointment_date"] == appt.appointment_date.isoformat()
    assert cmd["start_time_local"] == "11:00:00"
    assert cmd["duration_minutes"] == 30
    assert cmd["practitioner_id"] == str(practitioner.id)
    # Row unchanged
    db.refresh(appt)
    assert appt.duration_minutes == 30


def test_update_proposal_valid_practitioner_change(
        client, db, gp_user, practice, practitioner, patient):
    """Changing to a different valid practitioner → safe, command has new practitioner."""
    pr2 = Practitioner(
        practice_id=practice.id,
        first_name="Sam",
        last_name="Jones",
        ahpra_number="MED0007654321",
    )
    db.add(pr2)
    db.flush()
    appt = _make_appt(db, practice, practitioner, patient, start_h=14)
    token = make_token(gp_user)

    resp = client.post(
        UPDATE_URL.format(appt_id=appt.id),
        json={"practitioner_id": str(pr2.id)},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["command"]["practitioner_id"] == str(pr2.id)
    # Row unchanged — proposal is non-mutating
    db.refresh(appt)
    assert appt.practitioner_id == practitioner.id
