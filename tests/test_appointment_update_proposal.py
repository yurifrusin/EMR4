"""
Non-mutating update/status proposal contract for existing appointments.

Every test proves the Appointment row is unchanged after the proposal call.
"""
from datetime import date, datetime, time, timezone

import pytest

import app.routers.appointments as appointments_router
from app.models.appointments import Appointment, AppointmentAuditLog, AppointmentStatus, BookingChannel
from app.models.diary import DiaryBreak, DiaryColumn, DiaryTemplate, WaitingArea
from app.models.tenancy import Practitioner
from tests.conftest import make_token

THURSDAY = date(2026, 6, 26)   # a fixed future Thursday, guaranteed no conflict seeds
TODAY = date.today()


@pytest.fixture(autouse=True)
def _freeze_update_proposal_clock(monkeypatch):
    """Keep fixed June 2026 update-proposal fixtures future/open under temporal guards."""
    def fixed_now(tz):
        return datetime(2026, 6, 22, 8, 0, 0, tzinfo=tz)

    monkeypatch.setattr(appointments_router, "_clinic_local_now", fixed_now)

UPDATE_URL = "/api/v1/appointments/proposals/update/{appt_id}"
UPDATE_CONFIRM_URL = "/api/v1/appointments/proposals/update/confirm"
STATUS_URL = "/api/v1/appointments/proposals/status/{appt_id}"
WAITING_AREA_URL = "/api/v1/appointments/proposals/waiting-area/{appt_id}"
_update_confirm_key_counter = 0
_proposal_key_counter = 0


def _proposal_headers(token):
    global _proposal_key_counter
    _proposal_key_counter += 1
    return {
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": f"proposal-test-{_proposal_key_counter}",
    }


def _status_proposal_headers(token):
    global _proposal_key_counter
    _proposal_key_counter += 1
    return {
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": f"status-proposal-test-{_proposal_key_counter}",
    }


def _update_confirm_headers(token):
    global _update_confirm_key_counter
    _update_confirm_key_counter += 1
    return {
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": f"update-confirm-test-{_update_confirm_key_counter}",
    }


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
        headers=_proposal_headers(token),
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
    assert data["confirm_endpoint"] == UPDATE_CONFIRM_URL
    assert data["confirm_payload"]["confirmed"] is False
    assert data["confirm_payload"]["update_proposal"]["command"]["appointment_id"] == str(appt.id)
    assert data["update_proposal_freshness_id"]
    assert data["signed_confirmation_evidence_required"] is True
    assert data["signed_confirmation_evidence"]["purpose"] == "bernie_confirm_update_proposal"
    # DB row unchanged
    db.refresh(appt)
    assert appt.status == before_status
    assert db.query(Appointment).count() == before_count
    # Row still has old time, not the proposed time
    assert appt.start_time_local == time(9, 0)


def test_update_proposal_confirm_payload_writes_with_signed_audit_evidence(
        client, db, gp_user, practice, practitioner, patient):
    appt = _make_appt(db, practice, practitioner, patient, start_h=9)
    token = make_token(gp_user)

    proposal_resp = client.post(
        UPDATE_URL.format(appt_id=appt.id),
        json={
            "appointment_date": THURSDAY.isoformat(),
            "start_time_local": "10:00:00",
            "duration_minutes": 30,
        },
        headers=_proposal_headers(token),
    )
    assert proposal_resp.status_code == 200, proposal_resp.text
    payload = proposal_resp.json()["confirm_payload"]
    payload["confirmed"] = True

    confirm_resp = client.post(
        UPDATE_CONFIRM_URL,
        json=payload,
        headers=_update_confirm_headers(token),
    )

    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()
    assert data["safe"] is True
    assert data["autonomy_tier"] == "confirmed_write"
    assert data["appointment"]["id"] == str(appt.id)
    assert data["appointment"]["start_time_local"] == "10:00:00"
    assert data["appointment"]["duration_minutes"] == 30
    assert "bernie_confirm_update_proposal" in data["audit_evidence"]
    assert "bernie_signed_confirmation_evidence_verified" in data["audit_evidence"]

    db.refresh(appt)
    assert appt.start_time_local == time(10, 0)
    assert appt.duration_minutes == 30
    audit_rows = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt.id
    ).all()
    assert len(audit_rows) == 1
    assert "bernie_confirm_update_proposal" in audit_rows[0].confirmed_warnings
    assert "bernie_signed_confirmation_evidence_verified" in audit_rows[0].confirmed_warnings


def test_update_confirm_revalidates_same_day_elapsed_window_without_write(
        client, db, gp_user, practice, practitioner, patient, monkeypatch):
    appt = _make_appt(db, practice, practitioner, patient, start_h=14)
    token = make_token(gp_user)

    def proposal_time(tz):
        return datetime(2026, 6, 22, 8, 0, 0, tzinfo=tz)

    monkeypatch.setattr(appointments_router, "_clinic_local_now", proposal_time)
    proposal_resp = client.post(
        UPDATE_URL.format(appt_id=appt.id),
        json={
            "appointment_date": "2026-06-22",
            "start_time_local": "09:00:00",
            "duration_minutes": 15,
        },
        headers=_proposal_headers(token),
    )
    assert proposal_resp.status_code == 200, proposal_resp.text
    proposal = proposal_resp.json()
    assert proposal["safe"] is True

    def confirm_time(tz):
        return datetime(2026, 6, 22, 9, 15, 0, tzinfo=tz)

    monkeypatch.setattr(appointments_router, "_clinic_local_now", confirm_time)
    payload = proposal["confirm_payload"]
    payload["confirmed"] = True
    db.commit()
    before_audits = db.query(AppointmentAuditLog).count()

    confirm_resp = client.post(
        UPDATE_CONFIRM_URL,
        json=payload,
        headers=_update_confirm_headers(token),
    )

    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    block_codes = [block["code"] for block in data["blocks"]]
    assert "update_proposal_revalidation_blocked" in block_codes
    assert "same_day_window_elapsed" in block_codes
    db.refresh(appt)
    assert appt.appointment_date == THURSDAY
    assert appt.start_time_local == time(14, 0)
    assert db.query(AppointmentAuditLog).count() == before_audits


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
        headers=_proposal_headers(token),
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
        headers=_proposal_headers(token),
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
        headers=_proposal_headers(token),
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
        headers=_proposal_headers(token),
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
        headers=_proposal_headers(token),
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



# ─── Update proposal idempotency-key tests ──────────────────────────────────


def test_update_proposal_requires_idempotency_key(
        client, db, gp_user, practice, practitioner, patient):
    """Missing Idempotency-Key on update proposal returns 400."""
    appt = _make_appt(db, practice, practitioner, patient, start_h=9)
    token = make_token(gp_user)
    before = db.query(Appointment).count()

    resp = client.post(
        UPDATE_URL.format(appt_id=appt.id),
        json={"duration_minutes": 30},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 400, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_required"
    assert db.query(Appointment).count() == before


def test_update_proposal_blank_idempotency_key_is_missing(
        client, db, gp_user, practice, practitioner, patient):
    """Whitespace-only Idempotency-Key on update proposal returns 400."""
    appt = _make_appt(db, practice, practitioner, patient, start_h=9)
    token = make_token(gp_user)
    before = db.query(Appointment).count()

    resp = client.post(
        UPDATE_URL.format(appt_id=appt.id),
        json={"duration_minutes": 30},
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": "   ",
        },
    )

    assert resp.status_code == 400, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_required"
    assert db.query(Appointment).count() == before


def test_update_proposal_valid_key_reaches_evaluation(
        client, db, gp_user, practice, practitioner, patient):
    """Nonblank Idempotency-Key on update proposal reaches normal evaluation."""
    appt = _make_appt(db, practice, practitioner, patient, start_h=9)
    token = make_token(gp_user)

    resp = client.post(
        UPDATE_URL.format(appt_id=appt.id),
        json={"duration_minutes": 30},
        headers=_proposal_headers(token),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["intent"] == "update_appointment"
    assert data["safe"] is True
    assert "claim_appointment_command" not in str(data)
    # DB row unchanged
    db.refresh(appt)
    assert appt.duration_minutes == 15


# ─── Status proposal idempotency-key tests ──────────────────────────────────


def test_status_proposal_requires_idempotency_key(
        client, db, gp_user, practice, practitioner, patient):
    """Missing Idempotency-Key on status proposal returns 400."""
    appt = _make_appt(db, practice, practitioner, patient, start_h=9)
    token = make_token(gp_user)
    before = db.query(Appointment).count()

    resp = client.post(
        STATUS_URL.format(appt_id=appt.id),
        json={"status": "Confirmed"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 400, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_required"
    assert db.query(Appointment).count() == before


def test_status_proposal_blank_idempotency_key_is_missing(
        client, db, gp_user, practice, practitioner, patient):
    """Whitespace-only Idempotency-Key on status proposal returns 400."""
    appt = _make_appt(db, practice, practitioner, patient, start_h=9)
    token = make_token(gp_user)
    before = db.query(Appointment).count()

    resp = client.post(
        STATUS_URL.format(appt_id=appt.id),
        json={"status": "Confirmed"},
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": "   ",
        },
    )

    assert resp.status_code == 400, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_required"
    assert db.query(Appointment).count() == before


def test_status_proposal_valid_key_reaches_evaluation(
        client, db, gp_user, practice, practitioner, patient):
    """Nonblank Idempotency-Key on status proposal reaches normal evaluation."""
    appt = _make_appt(db, practice, practitioner, patient, start_h=9)
    token = make_token(gp_user)

    resp = client.post(
        STATUS_URL.format(appt_id=appt.id),
        json={"status": "Confirmed"},
        headers=_status_proposal_headers(token),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["intent"] == "update_appointment_status"
    assert data["safe"] is True
    # DB row unchanged
    db.refresh(appt)
    assert appt.status.value == "Booked"


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
        headers=_status_proposal_headers(token),
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
        headers=_status_proposal_headers(token),
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
        headers=_status_proposal_headers(token),
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
        headers=_status_proposal_headers(token),
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
        headers=_proposal_headers(token),
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
        headers=_proposal_headers(token),
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
        headers=_proposal_headers(token),
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
        headers=_proposal_headers(make_token(gp_user)),
    )
    assert resp.status_code == 404


def test_update_proposal_nonexistent_appointment_returns_404(
        client, db, gp_user):
    """Random UUID → 404."""
    import uuid as _uuid
    resp = client.post(
        UPDATE_URL.format(appt_id=_uuid.uuid4()),
        json={},
        headers=_proposal_headers(make_token(gp_user)),
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
        headers=_proposal_headers(token),
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
        headers=_proposal_headers(token),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["command"]["practitioner_id"] == str(pr2.id)
    # Row unchanged — proposal is non-mutating
    db.refresh(appt)
    assert appt.practitioner_id == practitioner.id


# ─── Status proposal coverage gaps ───────────────────────────────────────────

def test_status_proposal_cross_practice_returns_404(
        client, db, gp_user, practice_b, patient_b):
    """Status proposal on another practice's appointment returns 404."""
    pr_b = Practitioner(
        practice_id=practice_b.id,
        first_name="Other",
        last_name="Doctor",
        ahpra_number="MED8888888888",
    )
    db.add(pr_b)
    db.flush()
    appt_b = Appointment(
        practice_id=practice_b.id,
        patient_id=patient_b.id,
        practitioner_id=pr_b.id,
        start_time=datetime.combine(THURSDAY, time(11, 0), tzinfo=timezone.utc),
        appointment_date=THURSDAY,
        start_time_local=time(11, 0),
        duration_minutes=15,
        status=AppointmentStatus.Booked,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt_b)
    db.flush()

    resp = client.post(
        STATUS_URL.format(appt_id=appt_b.id),
        json={"status": "Confirmed"},
        headers=_status_proposal_headers(make_token(gp_user)),
    )
    assert resp.status_code == 404


def test_status_proposal_nonexistent_appointment_returns_404(
        client, db, gp_user):
    """Status proposal on a random UUID returns 404."""
    import uuid as _uuid
    resp = client.post(
        STATUS_URL.format(appt_id=_uuid.uuid4()),
        json={"status": "Confirmed"},
        headers=_status_proposal_headers(make_token(gp_user)),
    )
    assert resp.status_code == 404


def test_status_proposal_warns_waiting_area_assigned_on_terminal(
        client, db, gp_user, practice, practitioner, patient):
    """Terminal status + non-null waiting_area_id → waiting_area_assigned_on_terminal warning."""
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient, status=AppointmentStatus.Arrived)
    token = make_token(gp_user)

    resp = client.post(
        STATUS_URL.format(appt_id=appt.id),
        json={"status": "Completed", "waiting_area_id": str(area.id)},
        headers=_status_proposal_headers(token),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["autonomy_tier"] == "proposal"
    assert any(w["code"] == "waiting_area_assigned_on_terminal" for w in data["warnings"])
    # Row unchanged
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Arrived


# ─── Waiting-area proposal tests ──────────────────────────────────────────────

def test_waiting_area_proposal_assign_new_area(
        client, db, gp_user, practice, practitioner, patient):
    """Assigning a patient to a waiting area (not currently in one) → safe, execute_with_report."""
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    resp = client.post(
        WAITING_AREA_URL.format(appt_id=appt.id),
        json={"waiting_area_id": str(area.id)},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["intent"] == "update_appointment_waiting_area"
    assert data["safe"] is True
    assert data["requires_confirmation"] is True
    assert data["autonomy_tier"] == "execute_with_report"
    assert data["warnings"] == []
    assert data["blocks"] == []
    assert data["command"]["waiting_area_id"] == str(area.id)
    assert data["command"]["clears_waiting_area"] is False
    # Row unchanged
    db.refresh(appt)
    assert appt.waiting_area_id is None


def test_waiting_area_proposal_clear_area(
        client, db, gp_user, practice, practitioner, patient):
    """Clearing the waiting area (waiting_area_id=null) warns waiting_area_cleared."""
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient, waiting_area_id=area.id)
    token = make_token(gp_user)

    resp = client.post(
        WAITING_AREA_URL.format(appt_id=appt.id),
        json={"waiting_area_id": None},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["autonomy_tier"] == "proposal"
    assert data["command"]["clears_waiting_area"] is True
    assert any(w["code"] == "waiting_area_cleared" for w in data["warnings"])
    # Row unchanged
    db.refresh(appt)
    assert appt.waiting_area_id == area.id


def test_waiting_area_proposal_blocked_already_in_area(
        client, db, gp_user, practice, practitioner, patient):
    """Proposing the same waiting area the appointment is already in → blocked."""
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient, waiting_area_id=area.id)
    token = make_token(gp_user)

    resp = client.post(
        WAITING_AREA_URL.format(appt_id=appt.id),
        json={"waiting_area_id": str(area.id)},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert any(b["code"] == "already_in_area" for b in data["blocks"])
    # Row unchanged
    db.refresh(appt)
    assert appt.waiting_area_id == area.id


def test_waiting_area_proposal_cross_practice_returns_404(
        client, db, gp_user, practice_b, patient_b):
    """Waiting-area proposal on another practice's appointment returns 404."""
    pr_b = Practitioner(
        practice_id=practice_b.id,
        first_name="Other",
        last_name="Doctor",
        ahpra_number="MED7777777777",
    )
    db.add(pr_b)
    db.flush()
    appt_b = Appointment(
        practice_id=practice_b.id,
        patient_id=patient_b.id,
        practitioner_id=pr_b.id,
        start_time=datetime.combine(THURSDAY, time(12, 0), tzinfo=timezone.utc),
        appointment_date=THURSDAY,
        start_time_local=time(12, 0),
        duration_minutes=15,
        status=AppointmentStatus.Booked,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt_b)
    db.flush()

    resp = client.post(
        WAITING_AREA_URL.format(appt_id=appt_b.id),
        json={"waiting_area_id": None},
        headers={"Authorization": f"Bearer {make_token(gp_user)}"},
    )
    assert resp.status_code == 404


def test_waiting_area_proposal_nonexistent_appointment_returns_404(
        client, db, gp_user):
    """Waiting-area proposal on a random UUID returns 404."""
    import uuid as _uuid
    resp = client.post(
        WAITING_AREA_URL.format(appt_id=_uuid.uuid4()),
        json={"waiting_area_id": None},
        headers={"Authorization": f"Bearer {make_token(gp_user)}"},
    )
    assert resp.status_code == 404


# ─── Diary move/resize scenario tests ────────────────────────────────────────

def test_update_proposal_resize_blocked_into_next_booking(
        client, db, gp_user, practice, practitioner, patient):
    """Extending duration into the next booking's slot → appointment_conflict block.

    This is the canonical diary resize-down gesture: drag the bottom edge of a
    card to make it longer, bumping the card below it.
    """
    # Existing booking starts exactly where subject would end after the resize.
    next_booking = _make_appt(
        db, practice, practitioner, patient,
        start_h=9, start_m=15, duration=15,
    )
    subject = _make_appt(
        db, practice, practitioner, patient,
        start_h=9, start_m=0, duration=15,
    )
    token = make_token(gp_user)

    resp = client.post(
        UPDATE_URL.format(appt_id=subject.id),
        json={
            "appointment_date": THURSDAY.isoformat(),
            "start_time_local": "09:00:00",
            "duration_minutes": 30,   # 09:00–09:30 overlaps next_booking at 09:15
        },
        headers=_proposal_headers(token),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert any(b["code"] == "appointment_conflict" for b in data["blocks"])
    assert data["conflict"]["appointment_id"] == str(next_booking.id)
    # Subject row unchanged — proposal is non-mutating
    db.refresh(subject)
    assert subject.duration_minutes == 15
    assert subject.start_time_local == time(9, 0)


def test_update_proposal_drag_to_practitioner_with_conflict(
        client, db, gp_user, practice, practitioner, patient):
    """Dragging to a different practitioner column where they're already booked → conflict block.

    This is the canonical diary drag-across-columns gesture.
    """
    pr2 = Practitioner(
        practice_id=practice.id,
        first_name="Second",
        last_name="Doctor",
        ahpra_number="MED0005551234",
    )
    db.add(pr2)
    db.flush()
    # pr2 already has an appointment at 10:00
    pr2_existing = _make_appt(
        db, practice, pr2, patient,
        start_h=10, start_m=0, duration=15,
    )
    # Subject is currently booked with practitioner (different column), no conflict there
    subject = _make_appt(
        db, practice, practitioner, patient,
        start_h=10, start_m=0, duration=15,
    )
    token = make_token(gp_user)

    resp = client.post(
        UPDATE_URL.format(appt_id=subject.id),
        json={
            "practitioner_id": str(pr2.id),
            "appointment_date": THURSDAY.isoformat(),
            "start_time_local": "10:00:00",
            "duration_minutes": 15,
        },
        headers=_proposal_headers(token),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert any(b["code"] == "appointment_conflict" for b in data["blocks"])
    assert data["conflict"]["appointment_id"] == str(pr2_existing.id)
    # Subject row unchanged — proposal is non-mutating
    db.refresh(subject)
    assert subject.practitioner_id == practitioner.id


def test_update_proposal_adjacent_slot_is_safe(
        client, db, gp_user, practice, practitioner, patient):
    """An appointment ending exactly where another starts is NOT a conflict.

    _overlaps uses strict open-interval semantics: end_a > start_b.
    When end_a == start_b the condition is False, so adjacency is safe.
    This is important for back-to-back diary scheduling.
    """
    # Booking at 09:15; subject ends at exactly 09:15 → adjacent, not overlapping
    adjacent = _make_appt(
        db, practice, practitioner, patient,
        start_h=9, start_m=15, duration=15,
    )
    subject = _make_appt(
        db, practice, practitioner, patient,
        start_h=9, start_m=0, duration=15,
    )
    token = make_token(gp_user)

    resp = client.post(
        UPDATE_URL.format(appt_id=subject.id),
        json={
            "appointment_date": THURSDAY.isoformat(),
            "start_time_local": "09:00:00",
            "duration_minutes": 15,   # ends at 09:15 — exactly when adjacent starts
        },
        headers=_proposal_headers(token),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["blocks"] == []
    assert data["conflict"] is None
    # Both rows unchanged
    db.refresh(subject)
    db.refresh(adjacent)
    assert subject.start_time_local == time(9, 0)
    assert adjacent.start_time_local == time(9, 15)


def test_update_proposal_resize_shrink_is_safe(
        client, db, gp_user, practice, practitioner, patient):
    """Shrinking a booking that would otherwise conflict with the next appointment → safe.

    Resize-up may be blocked; resize-down should clear the conflict.
    """
    # Booking at 09:20 — close enough that a 30-min subject at 09:00 would overlap,
    # but a 15-min subject at 09:00 (ends 09:15) clears it.
    next_booking = _make_appt(
        db, practice, practitioner, patient,
        start_h=9, start_m=20, duration=15,
    )
    subject = _make_appt(
        db, practice, practitioner, patient,
        start_h=9, start_m=0, duration=30,   # currently ends at 09:30, overlaps next
    )
    token = make_token(gp_user)

    resp = client.post(
        UPDATE_URL.format(appt_id=subject.id),
        json={
            "appointment_date": THURSDAY.isoformat(),
            "start_time_local": "09:00:00",
            "duration_minutes": 15,   # shrink to end at 09:15 — clears 09:20 booking
        },
        headers=_proposal_headers(token),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["blocks"] == []
    assert data["conflict"] is None
    # Subject row unchanged — proposal is non-mutating
    db.refresh(subject)
    assert subject.duration_minutes == 30
