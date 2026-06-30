"""
POST /api/v1/appointments/proposals/bernie/supervised-booking.

Proves the Sprint 46 Bernie wrapper composes deterministic normalize, slot
search, and slot-selection/create-proposal evidence without appointment writes,
audit writes, confirmation, LLM/provider calls, or UI behaviour.
"""

from datetime import date, datetime, time, timezone
import inspect

from app.models.appointments import Appointment, AppointmentAuditLog, AppointmentStatus, BookingChannel
from app.models.patients import Patient
from app.models.tenancy import Practitioner
from app.schemas.appointments import SlotCandidate, SlotSearchProposalOut
import app.routers.appointments as appointments_router
from tests.conftest import make_token

WRAPPER_URL = "/api/v1/appointments/proposals/bernie/supervised-booking"
REFERENCE_DATE = "2026-06-22"


def _post_wrapper(client, token, body: dict):
    return client.post(
        WRAPPER_URL,
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )


def _base_body(practitioner, **overrides):
    body = {
        "reference_date": REFERENCE_DATE,
        "command": {
            "practitioner_id": str(practitioner.id),
            "date_from": "today",
            "duration_minutes": "15",
        },
    }
    body.update(overrides)
    return body


def _candidate_payload():
    return {
        "appointment_date": REFERENCE_DATE,
        "start_time": "2026-06-21T23:00:00+00:00",
        "end_time": "2026-06-21T23:15:00+00:00",
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
        "warnings": [],
    }


def _make_appt(db, practice, practitioner, patient):
    appt = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime(2026, 6, 21, 23, 0, tzinfo=timezone.utc),
        appointment_date=date(2026, 6, 22),
        start_time_local=time(9, 0),
        duration_minutes=15,
        status=AppointmentStatus.Booked,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt)
    db.flush()
    return appt


def test_supervised_booking_requires_auth(client, practitioner):
    resp = client.post(WRAPPER_URL, json=_base_body(practitioner))

    assert resp.status_code == 401


def test_blocked_normalization_does_not_execute_slot_search(client, gp_user, monkeypatch):
    token = make_token(gp_user)

    def forbidden_search(*args, **kwargs):
        raise AssertionError("blocked normalization must not execute slot search")

    monkeypatch.setattr(appointments_router, "_build_slot_search_proposal", forbidden_search)
    resp = _post_wrapper(client, token, {
        "reference_date": REFERENCE_DATE,
        "command": {
            "date_from": "today",
            "duration_minutes": "15",
        },
    })

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["intent"] == "bernie_supervised_booking"
    assert data["result"] == "blocked"
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert data["search_proposal"] is None
    assert data["selection_proposal"] is None
    assert data["staff_review"]["status"] == "blocked"
    assert data["staff_review"]["confirmation_ready"] is False
    assert data["staff_review"]["selected_slot"] is None
    assert data["staff_review"]["candidate_slots"] == []
    assert data["staff_review"]["warning_summary"] == "0 warning(s), 1 blocked issue(s)."
    assert data["staff_review"]["evidence_summary"] == "Blocked review payload; no confirm evidence is available."
    assert data["staff_review"]["confirm_payload"] is None
    assert data["staff_review"]["blocks"][0]["code"] == "missing_practitioner_id"
    assert data["normalization"]["safe"] is False
    assert data["blocks"][0]["code"] == "missing_practitioner_id"


def test_safe_command_returns_candidate_selection_response_without_mutating(
    client,
    db,
    gp_user,
    practitioner,
    schedule,
):
    token = make_token(gp_user)
    appointment_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()

    resp = _post_wrapper(client, token, _base_body(practitioner))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["intent"] == "bernie_supervised_booking"
    assert data["result"] == "candidate_selection_required"
    assert data["safe"] is True
    assert data["requires_confirmation"] is False
    assert data["autonomy_tier"] == "execute_with_report"
    assert data["normalization"]["safe"] is True
    assert data["search_proposal"]["intent"] == "search_slots"
    assert data["search_proposal"]["candidates"][0]["start_time_local"] == "09:00:00"
    assert data["selection_proposal"] is None
    review = data["staff_review"]
    assert review["status"] == "candidate_selection_required"
    assert review["confirmation_ready"] is False
    assert review["selected_slot"] is None
    assert review["candidate_slots"][0] == {
        "appointment_date": REFERENCE_DATE,
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
        "warnings": [],
    }
    assert review["warning_summary"] == "No warnings or blocked issues."
    assert review["evidence_summary"] == "Candidate slot summaries are review-only until staff selects one slot."
    assert review["confirm_endpoint"] is None
    assert review["confirm_payload"] is None
    assert db.query(Appointment).count() == appointment_before
    assert db.query(AppointmentAuditLog).count() == audit_before


def test_selected_candidate_returns_confirmation_ready_evidence_without_mutating(
    client,
    db,
    gp_user,
    practitioner,
    patient,
    schedule,
):
    token = make_token(gp_user)
    appointment_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()

    resp = _post_wrapper(client, token, _base_body(
        practitioner,
        selected_candidate_index=0,
        patient_id=str(patient.id),
        reason="Follow-up",
    ))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["result"] == "confirmation_ready"
    assert data["safe"] is True
    assert data["requires_confirmation"] is True
    assert data["autonomy_tier"] == "proposal"
    assert data["selection_proposal"]["intent"] == "select_slot_for_create_proposal"
    assert data["selection_proposal"]["safe"] is True
    assert data["selection_proposal"]["create_proposal"]["intent"] == "create_appointment"
    command = data["selection_proposal"]["create_proposal"]["command"]
    assert command["patient_id"] == str(patient.id)
    assert command["practitioner_id"] == str(practitioner.id)
    assert command["appointment_date"] == REFERENCE_DATE
    assert command["start_time_local"] == "09:00:00"
    assert command["reason"] == "Follow-up"
    review = data["staff_review"]
    assert review["status"] == "confirmation_ready"
    assert review["confirmation_ready"] is True
    assert review["selected_slot"] == {
        "appointment_date": REFERENCE_DATE,
        "start_time_local": "09:00:00",
        "duration_minutes": 15,
        "warnings": [],
    }
    assert review["candidate_slots"] == []
    assert review["warning_summary"] == "No warnings or blocked issues."
    assert review["evidence_summary"] == "Confirm payload carries slot-selection and create-proposal evidence for explicit staff approval."
    assert review["confirm_endpoint"] == "/api/v1/appointments/proposals/create/confirm-bernie"
    assert review["confirm_evidence"] == [
        "bernie_confirm_create_proposal",
        "source_slot_selection_proposal",
        "source_create_proposal",
    ]
    assert review["confirm_payload"]["confirmed"] is False
    assert review["confirm_payload"]["confirmed_warnings"] == []
    assert review["confirm_payload"]["selection_proposal"] == data["selection_proposal"]
    assert db.query(Appointment).count() == appointment_before
    assert db.query(AppointmentAuditLog).count() == audit_before


def test_identity_evidence_reports_linked_patient_and_caller_id_context(
    client,
    db,
    gp_user,
    practitioner,
    patient,
    schedule,
):
    patient.medicare_number = "2958303372"
    patient.phone_mobile = "0412 345 678"
    db.flush()
    token = make_token(gp_user)

    resp = _post_wrapper(client, token, _base_body(
        practitioner,
        patient_id=str(patient.id),
        context_frames=[{"type": "caller_id", "phone_number": "0412345678"}],
    ))

    assert resp.status_code == 200, resp.text
    evidence = resp.json()["staff_review"]["identity_evidence"]
    assert evidence["patient_id"] == str(patient.id)
    assert evidence["patient_label"] == "Margaret Thompson"
    assert evidence["confidence"] == "high"
    assert evidence["verification_status"] == "requires_staff_verification"
    assert "date_of_birth" in evidence["matched_fields"]
    assert "medicare_on_record" in evidence["matched_fields"]
    assert "caller_id_phone_match" in evidence["matched_fields"]
    assert evidence["supporting_context"] == ["caller_id"]
    assert "confirm dob" in evidence["staff_prompt"].lower()


def test_identity_evidence_flags_same_name_same_dob_duplicates(
    client,
    db,
    gp_user,
    practice,
    practitioner,
    patient,
    schedule,
):
    duplicate = Patient(
        practice_id=practice.id,
        first_name=patient.first_name,
        last_name=patient.last_name,
        date_of_birth=patient.date_of_birth,
    )
    db.add(duplicate)
    db.flush()
    token = make_token(gp_user)

    resp = _post_wrapper(client, token, _base_body(
        practitioner,
        patient_id=str(patient.id),
    ))

    assert resp.status_code == 200, resp.text
    evidence = resp.json()["staff_review"]["identity_evidence"]
    assert evidence["confidence"] == "ambiguous"
    assert "same_name_and_dob_duplicate" in evidence["warnings"]
    assert "Medicare/card" in evidence["staff_prompt"]


def test_selected_candidate_conflict_revalidation_blocks_without_mutating(
    client,
    db,
    gp_user,
    practice,
    practitioner,
    patient,
    monkeypatch,
):
    _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    appointment_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()

    def stale_search(body, db, practice_id):
        return SlotSearchProposalOut(
            safe=True,
            autonomy_tier="execute_with_report",
            summary="Stubbed stale candidate.",
            resolved_duration_minutes=15,
            candidates=[SlotCandidate(**_candidate_payload())],
        )

    monkeypatch.setattr(appointments_router, "_build_slot_search_proposal", stale_search)
    resp = _post_wrapper(client, token, _base_body(
        practitioner,
        selected_candidate_index=0,
        patient_id=str(patient.id),
    ))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["result"] == "blocked"
    assert data["safe"] is False
    assert data["selection_proposal"]["safe"] is False
    assert data["selection_proposal"]["create_proposal"]["blocks"][0]["code"] == "appointment_conflict"
    assert data["blocks"][0]["code"] == "appointment_conflict"
    assert data["staff_review"]["status"] == "blocked"
    assert data["staff_review"]["confirmation_ready"] is False
    assert data["staff_review"]["selected_slot"]["start_time_local"] == "09:00:00"
    assert data["staff_review"]["confirm_payload"] is None
    assert db.query(Appointment).count() == appointment_before
    assert db.query(AppointmentAuditLog).count() == audit_before


def test_supervised_booking_preserves_practice_scope(client, db, gp_user_b, practice, practitioner):
    token = make_token(gp_user_b)

    resp = _post_wrapper(client, token, _base_body(practitioner))

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Practitioner not found"


def test_supervised_booking_source_has_no_llm_confirmation_or_mutation_calls():
    source = inspect.getsource(appointments_router.propose_bernie_supervised_booking)

    assert "normalize_slot_search_command" in source
    assert "_build_slot_search_proposal" in source
    assert "_build_create_appointment_proposal" in source
    assert "confirm_bernie_create_proposal" not in source
    assert "_create_appointment_from_body" not in source
    assert "generate_content" not in source
    assert "Gemini" not in source
    assert "AiService" not in source
    assert "_get_default_provider" not in source
    assert "db.add" not in source
    assert "db.commit" not in source
    assert "_write_audit" not in source
