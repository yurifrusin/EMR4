import json
from datetime import datetime

import pytest

from app.config import settings
from app.models.appointments import Appointment, AppointmentAuditLog
import app.routers.appointments as appointments_router
from app.routers.appointments import _BERNIE_SESSION_STORE
from app.services.bernie import BernieSessionEventType, BernieSessionState
from tests.conftest import make_token


INTERPRET_URL = "/api/v1/appointments/proposals/bernie/interpret-booking-instruction"
WRAPPER_URL = "/api/v1/appointments/proposals/bernie/supervised-booking"
CONFIRM_URL = "/api/v1/appointments/proposals/create/confirm-bernie"
SESSION_BASE = "/api/v1/appointments/bernie/sessions"
REFERENCE_DATE = "2026-06-22"


@pytest.fixture(autouse=True)
def _freeze_bernie_route_outcome_clock(monkeypatch):
    def fixed_now(tz):
        return datetime(2026, 6, 22, 8, 0, 0, tzinfo=tz)

    monkeypatch.setattr(appointments_router, "_clinic_local_now", fixed_now)


def _auth(token: str, idempotency_key: str | None = None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    if idempotency_key is not None:
        headers["Idempotency-Key"] = idempotency_key
    return headers


def _create_recognition_session(client, token: str, surface_id: str) -> dict:
    active = client.get(
        f"{SESSION_BASE}/active",
        params={"surface_id": surface_id, "reference_date": REFERENCE_DATE},
        headers=_auth(token),
    )
    assert active.status_code == 200, active.text
    session = active.json()["session"]

    event = client.post(
        f"{SESSION_BASE}/{session['session_id']}/events",
        json={
            "surface_id": surface_id,
            "event_type": "staff_instruction",
            "expected_revision": 0,
            "event_id": f"{surface_id}-staff",
            "payload": {"intent_ref": f"{surface_id}-intent"},
        },
        headers=_auth(token),
    )
    assert event.status_code == 200, event.text
    return event.json()["session"]


def _session_tail(session_id: str):
    session = _BERNIE_SESSION_STORE.get_session(session_id)
    assert session is not None
    return session


def test_interpret_route_appends_compact_server_outcome_without_phi(
    client, gp_user, practitioner, patient, monkeypatch
):
    monkeypatch.setattr(settings, "bernie_booking_interpreter_provider", "fake")
    token = make_token(gp_user)
    surface_id = "diary-n8-interpret"
    session = _create_recognition_session(client, token, surface_id)

    resp = client.post(
        INTERPRET_URL,
        json={
            "instruction": (
                f"Please find practitioner_id:{practitioner.id} "
                f"patient_id:{patient.id} date_from:today duration:15"
            ),
            "reference_date": REFERENCE_DATE,
            "server_session_id": session["session_id"],
            "server_session_surface_id": surface_id,
            "server_session_expected_revision": session["revision"],
            "server_session_idempotency_key": "interpret-1",
        },
        headers=_auth(token),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["result"] == "interpreted"
    updated = _session_tail(session["session_id"])
    assert updated.state is BernieSessionState.context_enrichment
    assert updated.revision == session["revision"] + 1
    assert data["server_session"]["session_id"] == session["session_id"]
    assert data["server_session"]["surface_id"] == surface_id
    assert data["server_session"]["revision"] == updated.revision
    assert data["server_session"]["state"] == "context_enrichment"
    outcome = updated.events[-1]
    assert outcome.event_type == "interpretation_outcome"
    assert outcome.payload["result"] == "interpreted"
    assert outcome.payload["has_command_candidate"] is True
    assert "instruction" not in outcome.payload
    assert "patient_name" not in outcome.payload
    assert "raw_instruction" not in outcome.payload


def test_supervised_booking_stages_server_proposal_and_session_bound_evidence(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    surface_id = "diary-n8-proposal"
    session = _create_recognition_session(client, token, surface_id)
    interpreted = _BERNIE_SESSION_STORE.append_server_outcome_event(
        session_id=session["session_id"],
        event_type=BernieSessionEventType.interpretation_outcome,
        target_state=BernieSessionState.context_enrichment,
        expected_revision=session["revision"],
        payload={"result": "interpreted", "safe": True},
    )
    assert interpreted.accepted is True
    before = (db.query(Appointment).count(), db.query(AppointmentAuditLog).count())

    resp = client.post(
        WRAPPER_URL,
        json={
            "reference_date": REFERENCE_DATE,
            "command": {
                "practitioner_id": str(practitioner.id),
                "patient_id": str(patient.id),
                "date_from": "today",
                "duration_minutes": "15",
            },
            "selected_candidate_index": 0,
            "patient_id": str(patient.id),
            "reason": "N8 route outcome test",
            "server_session_id": session["session_id"],
            "server_session_surface_id": surface_id,
            "server_session_expected_revision": interpreted.session.revision,
            "server_session_idempotency_key": "supervised-1",
        },
        headers=_auth(token),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["result"] == "confirmation_ready"
    assert data["server_session"]["session_id"] == session["session_id"]
    assert data["server_session"]["surface_id"] == surface_id
    assert data["server_session"]["state"] == "proposal_preview"
    ui_view_model = data["staff_review"]["ui_view_model"]
    assert ui_view_model["schema_version"] == "bernie.ui_view_model.v1"
    assert ui_view_model["confirmation_state"] == {
        "value": "ready",
        "source": "derived",
    }
    assert ui_view_model["flags"]["show_confirm_button"] is True
    assert ui_view_model["flags"]["show_success_copy"] is False
    assert ui_view_model["primary_copy"].startswith("No appointment has been made yet")
    assert data["staff_review"]["confirm_payload"]["session_binding"] is not None
    serialized_confirm_payload = json.dumps(data["staff_review"]["confirm_payload"])
    for forbidden in [
        "ui_view_model",
        "copy_mode",
        "confirmation_state",
        "freshness_state",
        "primary_copy",
        "secondary_copy",
    ]:
        assert forbidden not in serialized_confirm_payload
    assert data["selection_proposal"]["session_binding"] == data["staff_review"]["confirm_payload"]["session_binding"]
    signed_payload = data["staff_review"]["confirm_payload"]["signed_confirmation_evidence"]["payload"]
    assert signed_payload["session_binding"] == data["staff_review"]["confirm_payload"]["session_binding"]
    updated = _session_tail(session["session_id"])
    assert updated.state is BernieSessionState.proposal_preview
    assert updated.patient_id == patient.id
    assert updated.practitioner_id == practitioner.id
    assert updated.candidate_freshness_ids == [
        data["selection_proposal"]["selected_candidate"]["candidate_freshness_id"]
    ]
    assert updated.staged_proposal_freshness_id == data["selection_proposal"]["proposal_freshness_id"]
    assert [event.event_type.value for event in updated.events[-3:]] == [
        "context_outcome",
        "slot_search_outcome",
        "proposal_outcome",
    ]
    assert (db.query(Appointment).count(), db.query(AppointmentAuditLog).count()) == before


def test_supervised_booking_without_server_session_has_no_ui_view_model_delivery(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    before = (db.query(Appointment).count(), db.query(AppointmentAuditLog).count())

    resp = client.post(
        WRAPPER_URL,
        json={
            "reference_date": REFERENCE_DATE,
            "command": {
                "practitioner_id": str(practitioner.id),
                "patient_id": str(patient.id),
                "date_from": "today",
                "duration_minutes": "15",
            },
            "selected_candidate_index": 0,
            "patient_id": str(patient.id),
            "reason": "D5 no server session response compatibility",
        },
        headers=_auth(token),
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["server_session"] is None
    assert data["staff_review"]["ui_view_model"] is None
    assert data["result"] == "confirmation_ready"
    assert (db.query(Appointment).count(), db.query(AppointmentAuditLog).count()) == before


def test_session_bound_confirm_appends_confirmed_outcome_after_write(
    client, db, gp_user, practitioner, patient, schedule
):
    token = make_token(gp_user)
    surface_id = "diary-n8-confirm"
    session = _create_recognition_session(client, token, surface_id)
    interpreted = _BERNIE_SESSION_STORE.append_server_outcome_event(
        session_id=session["session_id"],
        event_type=BernieSessionEventType.interpretation_outcome,
        target_state=BernieSessionState.context_enrichment,
        expected_revision=session["revision"],
        payload={"result": "interpreted", "safe": True},
    )
    assert interpreted.accepted is True
    proposal = client.post(
        WRAPPER_URL,
        json={
            "reference_date": REFERENCE_DATE,
            "command": {
                "practitioner_id": str(practitioner.id),
                "patient_id": str(patient.id),
                "date_from": "today",
                "duration_minutes": "15",
            },
            "selected_candidate_index": 0,
            "patient_id": str(patient.id),
            "reason": "N8 confirm outcome test",
            "server_session_id": session["session_id"],
            "server_session_surface_id": surface_id,
            "server_session_expected_revision": interpreted.session.revision,
        },
        headers=_auth(token),
    )
    assert proposal.status_code == 200, proposal.text
    payload = proposal.json()["staff_review"]["confirm_payload"]
    payload["confirmed"] = True
    before = (db.query(Appointment).count(), db.query(AppointmentAuditLog).count())

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "route-outcome-confirm-key"))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert "bernie_session_binding_verified" in data["audit_evidence"]
    assert (db.query(Appointment).count(), db.query(AppointmentAuditLog).count()) == (
        before[0] + 1,
        before[1] + 1,
    )
    updated = _session_tail(session["session_id"])
    assert updated.state is BernieSessionState.confirmed
    assert [event.event_type.value for event in updated.events[-2:]] == [
        "confirm_submitted",
        "confirmation_outcome",
    ]
    assert updated.events[-1].payload["appointment_id"] == data["appointment"]["id"]
