"""Focused authored-synthetic checks for status-confirm HTTP convergence."""

import copy

from app.routers import appointments as appointment_router
from app.schemas.appointments import (
    AppointmentStatusProposalConfirmationIn,
    AppointmentStatusProposalOut,
)
from app.services import appointment_status_product_adapter as adapter
from sqlalchemy.orm import sessionmaker
from tests.conftest import make_token
from tests.test_appointment_status_mutations import _make_appt, _make_area, _post_status_proposal


def test_pretransaction_http_payload_enters_the_exact_product_adapter(
    client, db, gp_user, practice, practitioner, patient
):
    appointment = _make_appt(db, practice, practitioner, patient)
    token = make_token(gp_user)
    proposal_response = _post_status_proposal(
        client,
        token,
        appointment.id,
        {"status": "Confirmed"},
    )
    assert proposal_response.status_code == 200
    payload = proposal_response.json()["confirm_payload"]
    payload["confirmed"] = True
    body = AppointmentStatusProposalConfirmationIn.model_validate(payload)

    assert isinstance(body.status_proposal, AppointmentStatusProposalOut)
    transport = adapter._transport(body, idempotency_key="focused-http-key")  # noqa: SLF001
    assert transport["command"]["kind"] == "status"
    ingress = adapter._proposal_server_ingress(  # noqa: SLF001
        body=body,
        authenticated_user=gp_user,
        session_reference=adapter.authenticated_session_reference(
            token,
            secret=appointment_router._status_confirm_domain_secret(  # noqa: SLF001
                "authenticated-session"
            ),
        ),
        evidence_secret=appointment_router._status_confirm_evidence_secret(),  # noqa: SLF001
        proposal_version_binding=body.status_proposal_version_binding,
        proposal_version_binding_secret=appointment_router._status_confirm_domain_secret(  # noqa: SLF001
            "proposal-version"
        ),
    )
    assert ingress.authority_current is True
    assert ingress.current_state["source_version"] == 1


def test_waiting_area_state_produces_the_same_prelock_and_locked_request(
    client, db, gp_user, practice, practitioner, patient
):
    area = _make_area(db, practice)
    appointment = _make_appt(db, practice, practitioner, patient)
    appointment.waiting_area_id = area.id
    db.commit()
    token = make_token(gp_user)
    proposal_response = _post_status_proposal(
        client,
        token,
        appointment.id,
        {"status": "Arrived"},
    )
    payload = proposal_response.json()["confirm_payload"]
    payload["confirmed"] = True
    body = AppointmentStatusProposalConfirmationIn.model_validate(payload)
    db.commit()

    session_reference = adapter.authenticated_session_reference(
        token,
        secret=appointment_router._status_confirm_domain_secret(  # noqa: SLF001
            "authenticated-session"
        ),
    )
    ingress = adapter._proposal_server_ingress(  # noqa: SLF001
        body=body,
        authenticated_user=gp_user,
        session_reference=session_reference,
        evidence_secret=appointment_router._status_confirm_evidence_secret(),  # noqa: SLF001
        proposal_version_binding=body.status_proposal_version_binding,
        proposal_version_binding_secret=appointment_router._status_confirm_domain_secret(  # noqa: SLF001
            "proposal-version"
        ),
    )
    transport = adapter._transport(body, idempotency_key="waiting-area-check")  # noqa: SLF001
    before = adapter.status_confirm_admission_adapter(
        {"structure": "valid", "transport": transport, "server": ingress.as_adapter_mapping()}
    )
    factory = sessionmaker(bind=db.get_bind())
    with factory() as fresh:
        locked_appointment = appointment_router._get_appointment(  # noqa: SLF001
            appointment.id,
            practice.id,
            fresh,
        )
        locked_ingress = adapter._locked_server_ingress(  # noqa: SLF001
            body=body,
            authenticated_user=gp_user,
            appointment=locked_appointment,
            session_reference=session_reference,
            evidence_secret=appointment_router._status_confirm_evidence_secret(),  # noqa: SLF001
        )
        after = adapter.status_confirm_admission_adapter(
            {
                "structure": "valid",
                "transport": transport,
                "server": locked_ingress.as_adapter_mapping(),
            }
        )
    assert before["kernel_request"]["request_digest"] == after["kernel_request"]["request_digest"], (
        ingress.current_state,
        locked_ingress.current_state,
        before,
        after,
    )


def test_waiting_area_http_path_keeps_the_same_admitted_request(
    client, db, gp_user, practice, practitioner, patient, monkeypatch
):
    area = _make_area(db, practice)
    appointment = _make_appt(db, practice, practitioner, patient)
    appointment.waiting_area_id = area.id
    db.commit()
    token = make_token(gp_user)
    proposal_response = _post_status_proposal(
        client,
        token,
        appointment.id,
        {"status": "Arrived"},
    )
    payload = proposal_response.json()["confirm_payload"]
    payload["confirmed"] = True
    db.commit()
    observations = []
    original = adapter.status_confirm_admission_adapter

    def observing(value):
        result = original(value)
        observations.append(
            {
                "state": copy.deepcopy(value["server"]["current_state"]),
                "request": copy.deepcopy(result.get("kernel_request")),
            }
        )
        return result

    monkeypatch.setattr(adapter, "status_confirm_admission_adapter", observing)
    response = client.post(
        "/api/v1/appointments/proposals/status/confirm",
        json=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": "waiting-http-observation",
        },
    )
    assert response.json().get("safe") is True, (response.json(), observations)
    assert len(observations) == 2
    assert observations[0]["request"]["request_digest"] == observations[1]["request"]["request_digest"]
