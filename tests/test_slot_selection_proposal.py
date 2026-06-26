"""
POST /api/v1/appointments/proposals/slot-search/selection.

Proves a supervised Bernie slot-search candidate selection can be converted into
existing create-proposal evidence without creating an appointment, writing audit
rows, calling LLMs, or changing UI behaviour.
"""

from datetime import date, datetime, time, timezone
import inspect

from app.models.appointments import Appointment, AppointmentAuditLog, AppointmentStatus, BookingChannel
import app.routers.appointments as appointments_router
from tests.conftest import make_token

NORMALIZED_SEARCH_URL = "/api/v1/appointments/proposals/slot-search/normalized"
SELECTION_URL = "/api/v1/appointments/proposals/slot-search/selection"
REFERENCE_DATE = "2026-06-22"


def _normalized_search(client, token, practitioner):
    return client.post(
        NORMALIZED_SEARCH_URL,
        params={"reference_date": REFERENCE_DATE},
        json={
            "practitioner_id": str(practitioner.id),
            "date_from": "today",
            "duration_minutes": "15",
        },
        headers={"Authorization": f"Bearer {token}"},
    )


def _post_selection(client, token, body: dict):
    return client.post(
        SELECTION_URL,
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )


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


def test_slot_selection_requires_auth(client, patient):
    resp = client.post(SELECTION_URL, json={
        "selected_candidate": _candidate_payload(),
        "practitioner_id": "00000000-0000-0000-0000-000000000001",
        "patient_id": str(patient.id),
    })

    assert resp.status_code == 401


def test_select_index_returns_create_proposal_without_mutating(
    client,
    db,
    gp_user,
    practitioner,
    patient,
    schedule,
):
    token = make_token(gp_user)
    search_resp = _normalized_search(client, token, practitioner)
    assert search_resp.status_code == 200, search_resp.text
    appointment_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()

    resp = _post_selection(client, token, {
        "search_execution": search_resp.json(),
        "selected_candidate_index": 0,
        "patient_id": str(patient.id),
        "reason": "Follow-up",
    })

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["intent"] == "select_slot_for_create_proposal"
    assert data["safe"] is True
    assert data["requires_confirmation"] is True
    assert data["autonomy_tier"] == "proposal"
    assert data["blocks"] == []
    assert data["create_proposal"]["intent"] == "create_appointment"
    assert data["create_proposal"]["autonomy_tier"] == "proposal"
    assert data["create_proposal"]["command"]["patient_id"] == str(patient.id)
    assert data["create_proposal"]["command"]["practitioner_id"] == str(practitioner.id)
    assert data["create_proposal"]["command"]["appointment_date"] == REFERENCE_DATE
    assert data["create_proposal"]["command"]["start_time_local"] == "09:00:00"
    assert data["create_proposal"]["command"]["reason"] == "Follow-up"
    assert db.query(Appointment).count() == appointment_before
    assert db.query(AppointmentAuditLog).count() == audit_before


def test_selected_candidate_mismatch_is_blocked(
    client,
    gp_user,
    practitioner,
    patient,
    schedule,
):
    token = make_token(gp_user)
    search_resp = _normalized_search(client, token, practitioner)
    selected = search_resp.json()["proposal"]["candidates"][0]
    selected["start_time_local"] = "09:15:00"

    resp = _post_selection(client, token, {
        "search_execution": search_resp.json(),
        "selected_candidate_index": 0,
        "selected_candidate": selected,
        "patient_id": str(patient.id),
    })

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert data["create_proposal"] is None
    assert data["blocks"][0]["code"] == "selected_candidate_mismatch"


def test_explicit_candidate_reuses_create_proposal_conflict_semantics(
    client,
    db,
    gp_user,
    practice,
    practitioner,
    patient,
):
    _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    appointment_before = db.query(Appointment).count()
    audit_before = db.query(AppointmentAuditLog).count()

    resp = _post_selection(client, token, {
        "selected_candidate": _candidate_payload(),
        "practitioner_id": str(practitioner.id),
        "patient_id": str(patient.id),
    })

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert data["blocks"][0]["code"] == "appointment_conflict"
    assert data["create_proposal"]["blocks"][0]["code"] == "appointment_conflict"
    assert db.query(Appointment).count() == appointment_before
    assert db.query(AppointmentAuditLog).count() == audit_before


def test_slot_selection_has_no_llm_or_mutation_calls():
    source = inspect.getsource(appointments_router.propose_slot_selection_for_create)

    assert "_build_create_appointment_proposal" in source
    assert "generate_content" not in source
    assert "Gemini" not in source
    assert "db.add" not in source
    assert "db.commit" not in source
    assert "_write_audit" not in source
