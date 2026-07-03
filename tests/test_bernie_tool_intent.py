from datetime import date, datetime, time, timezone

from app.models.appointments import Appointment, AppointmentAuditLog, AppointmentStatus, BookingChannel
from tests.conftest import make_token


TOOL_INTENT_URL = "/api/v1/appointments/proposals/bernie/tool-intent"
UPDATE_CONFIRM_URL = "/api/v1/appointments/proposals/update/confirm"
REQUEST_DATE = date(2026, 6, 26)


def _make_appt(
    db,
    practice,
    practitioner,
    patient,
    *,
    start_h=15,
    start_m=0,
    duration=15,
    status=AppointmentStatus.Booked,
):
    appt = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(REQUEST_DATE, time(start_h, start_m), tzinfo=timezone.utc),
        appointment_date=REQUEST_DATE,
        start_time_local=time(start_h, start_m),
        duration_minutes=duration,
        status=status,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt)
    db.flush()
    return appt


def _frame(appt, practitioner):
    return {
        "type": "diary_day_booking",
        "appointment_id": str(appt.id),
        "appointment_date": appt.appointment_date.isoformat(),
        "start_time_local": appt.start_time_local.isoformat(),
        "patient_label": "Margaret Thompson",
        "booking_patient_id": str(appt.patient_id),
        "booking_practitioner_id": str(appt.practitioner_id),
        "practitioner_label": f"{practitioner.first_name} {practitioner.last_name}",
    }


def _post_tool_intent(client, token, instruction, frames):
    return client.post(
        TOOL_INTENT_URL,
        json={
            "instruction": instruction,
            "reference_date": REQUEST_DATE.isoformat(),
            "context_frames": frames,
        },
        headers={"Authorization": f"Bearer {token}"},
    )


def test_extend_appointment_intent_returns_update_proposal_without_mutating(
    client,
    db,
    gp_user,
    practice,
    practitioner,
    patient,
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    appointment_count = db.query(Appointment).count()
    audit_count = db.query(AppointmentAuditLog).count()

    resp = _post_tool_intent(
        client,
        token,
        "Bernie extend Margaret Thompson's 3pm booking with Dr Shera to 30 minutes.",
        [_frame(appt, practitioner)],
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["intent"] == "bernie_tool_intent"
    assert data["result"] == "proposal_ready"
    assert data["tool_intent"] == "extend_appointment"
    assert data["safe"] is True, data
    assert data["requires_confirmation"] is True
    assert data["autonomy_tier"] == "proposal"
    assert data["source_attribution"]["proposal_authority"] == "appointment_update_proposal"
    assert data["source_attribution"]["write_authority"] == "signed_update_confirm_endpoint"

    proposal = data["proposal"]
    assert proposal["intent"] == "update_appointment"
    assert proposal["safe"] is True
    assert proposal["requires_confirmation"] is True
    assert proposal["autonomy_tier"] == "proposal"
    assert proposal["command"]["appointment_id"] == str(appt.id)
    assert proposal["command"]["duration_minutes"] == 30
    assert data["confirm_endpoint"] == UPDATE_CONFIRM_URL
    assert data["confirm_payload"]["confirmed"] is False
    assert data["confirm_payload"]["update_proposal"]["command"]["appointment_id"] == str(appt.id)
    assert data["update_proposal_freshness_id"]
    assert data["signed_confirmation_evidence_required"] is True
    assert data["signed_confirmation_evidence"]["purpose"] == "bernie_confirm_update_proposal"

    db.refresh(appt)
    assert appt.duration_minutes == 15
    assert db.query(Appointment).count() == appointment_count
    assert db.query(AppointmentAuditLog).count() == audit_count


def test_extend_appointment_confirm_endpoint_updates_once_with_audit_evidence(
    client,
    db,
    gp_user,
    practice,
    practitioner,
    patient,
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    proposal_resp = _post_tool_intent(
        client,
        token,
        "Bernie extend Margaret Thompson's 3pm booking with Dr Shera to 30 minutes.",
        [_frame(appt, practitioner)],
    )
    assert proposal_resp.status_code == 200, proposal_resp.text
    payload = proposal_resp.json()["confirm_payload"]
    payload["confirmed"] = True

    confirm_resp = client.post(
        UPDATE_CONFIRM_URL,
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()
    assert data["intent"] == "confirm_update_appointment"
    assert data["safe"] is True, data
    assert data["autonomy_tier"] == "confirmed_write"
    assert data["appointment"]["id"] == str(appt.id)
    assert data["appointment"]["duration_minutes"] == 30
    assert "bernie_confirm_update_proposal" in data["audit_evidence"]
    assert "bernie_signed_confirmation_evidence_verified" in data["audit_evidence"]

    db.refresh(appt)
    assert appt.duration_minutes == 30
    audit_rows = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.appointment_id == appt.id
    ).all()
    assert len(audit_rows) == 1
    assert "bernie_confirm_update_proposal" in audit_rows[0].confirmed_warnings
    assert "source_update_proposal" in audit_rows[0].confirmed_warnings
    assert "source_tool_intent_proposal" in audit_rows[0].confirmed_warnings
    assert "bernie_signed_confirmation_evidence_verified" in audit_rows[0].confirmed_warnings


def test_update_confirm_requires_explicit_staff_confirmation(
    client,
    db,
    gp_user,
    practice,
    practitioner,
    patient,
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    proposal_resp = _post_tool_intent(
        client,
        token,
        "Bernie extend Margaret Thompson's 3pm booking with Dr Shera to 30 minutes.",
        [_frame(appt, practitioner)],
    )
    payload = proposal_resp.json()["confirm_payload"]

    confirm_resp = client.post(
        UPDATE_CONFIRM_URL,
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()
    assert data["safe"] is False
    assert data["blocks"][0]["code"] == "explicit_confirmation_required"
    db.refresh(appt)
    assert appt.duration_minutes == 15
    assert db.query(AppointmentAuditLog).count() == 0


def test_update_confirm_blocks_tampered_signed_evidence_without_mutating(
    client,
    db,
    gp_user,
    practice,
    practitioner,
    patient,
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    proposal_resp = _post_tool_intent(
        client,
        token,
        "Bernie extend Margaret Thompson's 3pm booking with Dr Shera to 30 minutes.",
        [_frame(appt, practitioner)],
    )
    payload = proposal_resp.json()["confirm_payload"]
    payload["confirmed"] = True
    payload["signed_confirmation_evidence"]["purpose"] = "bernie_confirm_create_proposal"

    confirm_resp = client.post(
        UPDATE_CONFIRM_URL,
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()
    assert data["safe"] is False
    assert data["blocks"][0]["code"] == "signed_evidence_wrong_purpose"
    db.refresh(appt)
    assert appt.duration_minutes == 15
    assert db.query(AppointmentAuditLog).count() == 0


def test_update_confirm_blocks_stale_current_appointment_state(
    client,
    db,
    gp_user,
    practice,
    practitioner,
    patient,
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    proposal_resp = _post_tool_intent(
        client,
        token,
        "Bernie extend Margaret Thompson's 3pm booking with Dr Shera to 30 minutes.",
        [_frame(appt, practitioner)],
    )
    payload = proposal_resp.json()["confirm_payload"]
    payload["confirmed"] = True

    appt.duration_minutes = 20
    db.flush()

    confirm_resp = client.post(
        UPDATE_CONFIRM_URL,
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert confirm_resp.status_code == 200, confirm_resp.text
    data = confirm_resp.json()
    assert data["safe"] is False
    codes = {block["code"] for block in data["blocks"]}
    assert "signed_evidence_mismatch" in codes
    assert "stale_update_proposal_freshness_id" in codes
    db.refresh(appt)
    assert appt.duration_minutes == 20
    assert db.query(AppointmentAuditLog).count() == 0


def test_extend_intent_requires_target_duration(
    client,
    db,
    gp_user,
    practice,
    practitioner,
    patient,
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    resp = _post_tool_intent(
        client,
        token,
        "Bernie extend Margaret Thompson's 3pm booking with Dr Shera.",
        [_frame(appt, practitioner)],
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["result"] == "clarification_required"
    assert data["proposal"] is None
    assert data["blocks"][0]["code"] == "target_duration_required"


def test_extend_intent_requires_single_matching_appointment_context(
    client,
    db,
    gp_user,
    practice,
    practitioner,
    patient,
):
    first = _make_appt(db, practice, practitioner, patient, start_h=15)
    second = _make_appt(db, practice, practitioner, patient, start_h=15, start_m=15)
    token = make_token(gp_user)

    first_frame = _frame(first, practitioner)
    second_frame = _frame(second, practitioner)
    second_frame["start_time_local"] = "15:00:00"

    resp = _post_tool_intent(
        client,
        token,
        "Bernie extend Margaret Thompson's 3pm booking with Dr Shera to 30 minutes.",
        [first_frame, second_frame],
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["result"] == "clarification_required"
    assert data["proposal"] is None
    assert data["blocks"][0]["code"] == "ambiguous_appointment_context"


def test_unsupported_tool_intent_does_not_create_proposal(
    client,
    db,
    gp_user,
    practice,
    practitioner,
    patient,
):
    appt = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)

    resp = _post_tool_intent(
        client,
        token,
        "Bernie cancel Margaret Thompson's 3pm booking with Dr Shera.",
        [_frame(appt, practitioner)],
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["result"] == "unsupported"
    assert data["proposal"] is None
    assert data["source_attribution"]["write_authority"] == "none"
