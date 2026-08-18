from __future__ import annotations

import inspect
import textwrap
from uuid import UUID

import pytest
from fastapi import HTTPException

from app.routers import appointments as appointments_router
from app.schemas.appointments import (
    AppointmentCheckInCommand,
    AppointmentCheckInProposalConfirmationIn,
    AppointmentCheckInProposalOut,
)
from app.services.appointment_check_in_product_adapter import CheckInAdapterResult


APPOINTMENT_ID = UUID("30000000-0000-0000-0000-000000000001")
EVIDENCE = "opaque-authored-synthetic-check-in-evidence"


def _body(*, confirmed: bool = True) -> AppointmentCheckInProposalConfirmationIn:
    freshness = "0" * 32
    proposal = AppointmentCheckInProposalOut(
        safe=True,
        requires_confirmation=True,
        autonomy_tier="execute_with_report",
        summary="Synthetic check-in",
        command=AppointmentCheckInCommand(
            appointment_id=APPOINTMENT_ID,
            waiting_area_id=None,
            waiting_area_id_supplied=False,
        ),
        warnings=[],
        blocks=[],
        check_in_proposal_freshness_id=freshness,
        signed_confirmation_evidence=EVIDENCE,
        signed_confirmation_evidence_required=True,
    )
    return AppointmentCheckInProposalConfirmationIn(
        confirmed=confirmed,
        check_in_proposal=proposal,
        confirmed_warnings=[],
        check_in_proposal_freshness_id=freshness,
        signed_confirmation_evidence=EVIDENCE,
        signed_confirmation_evidence_required=True,
    )


def _stop(reason: str, *, status_code: int = 409) -> CheckInAdapterResult:
    return CheckInAdapterResult(
        kind="stopped",
        outcome="validation_rejected",
        reason=reason,
        response_status_code=status_code,
        response_body=None,
        committed=False,
    )


def test_route_delegates_once_after_the_unchanged_default_off_gate() -> None:
    source = textwrap.dedent(
        inspect.getsource(appointments_router.confirm_check_in_proposal_route)
    )

    assert source.count("compose_product_check_in(") == 1
    assert source.index("_a5_check_in_gate_open(current_user)") < source.index(
        "_normalize_idempotency_key(idempotency_key)"
    ) < source.index("compose_product_check_in(")
    for forbidden in (
        "claim_appointment_check_in_command(",
        "verify_check_in_evidence_token(",
        "record_appointment_checked_in_event(",
        "complete_appointment_command(",
        "db.commit(",
    ):
        assert forbidden not in source


def test_dependency_binder_owns_the_exact_existing_transaction_primitives() -> None:
    source = inspect.getsource(appointments_router._a5_check_in_dependencies)

    for required in (
        "claim_appointment_check_in_command(",
        "with_for_update()",
        "verify_check_in_evidence_token(",
        "_write_audit(",
        "record_appointment_checked_in_event(",
        "complete_appointment_command(",
        "commit=db.commit",
        "rollback=db.rollback",
        "populate_existing()",
    ):
        assert required in source
    assert "Appointment.status ==" not in source


@pytest.mark.parametrize(
    ("reason", "status_code", "detail_code"),
    [
        ("idempotency_key_conflict", 409, "idempotency_key_conflict"),
        ("command_in_progress", 409, "idempotency_key_in_progress"),
        (
            "stale_command_in_progress",
            409,
            "idempotency_key_stale_in_progress",
        ),
        ("prior_command_failed", 503, "idempotency_key_failed_transient"),
        (
            "confirmation_replay_rejected",
            409,
            "confirmation_replay_rejected",
        ),
    ],
)
def test_idempotency_stops_preserve_the_existing_http_contract(
    reason: str,
    status_code: int,
    detail_code: str,
) -> None:
    with pytest.raises(HTTPException) as captured:
        appointments_router._a5_check_in_adapter_response(
            _stop(reason, status_code=status_code),
            body=_body(),
        )

    assert captured.value.status_code == status_code
    assert captured.value.detail["code"] == detail_code


def test_missing_appointment_preserves_the_existing_404_contract() -> None:
    with pytest.raises(HTTPException) as captured:
        appointments_router._a5_check_in_adapter_response(
            _stop("appointment_not_found"),
            body=_body(),
        )

    assert captured.value.status_code == 404
    assert captured.value.detail == "Appointment not found"


def test_adapter_validation_stop_maps_to_the_existing_blocked_response() -> None:
    response = appointments_router._a5_check_in_adapter_response(
        _stop("signed_evidence_tampered"),
        body=_body(),
    )

    assert response.safe is False
    assert response.requires_confirmation is True
    assert response.autonomy_tier == "blocked"
    assert response.summary == "Cannot confirm check-in proposal. See blocked issues."
    assert [block.code for block in response.blocks] == ["signed_evidence_tampered"]
    assert response.audit_evidence == [
        "rayleen_check_in_confirmation",
        "source_check_in_proposal",
        "source_current_appointment_state",
    ]


def test_post_evidence_waiting_area_stop_retains_verified_audit_marker() -> None:
    response = appointments_router._a5_check_in_adapter_response(
        _stop("waiting_area_not_active"),
        body=_body(),
    )

    assert [block.code for block in response.blocks] == ["waiting_area_not_active"]
    assert response.audit_evidence[-1] == (
        "check_in_signed_confirmation_evidence_verified"
    )


def test_invalid_confirmation_envelope_preserves_explicit_confirmation_code() -> None:
    response = appointments_router._a5_check_in_adapter_response(
        _stop("confirmation_envelope_invalid"),
        body=_body(confirmed=False),
    )

    assert [block.code for block in response.blocks] == [
        "explicit_confirmation_required"
    ]


@pytest.mark.parametrize(
    "reason",
    [
        "idempotency_claim_failed",
        "stored_replay_invalid",
        "precommit_composition_failed",
        "commit_outcome_unknown",
        "committed_readback_unavailable",
    ],
)
def test_internal_adapter_stops_never_downgrade_to_a_false_client_success(
    reason: str,
) -> None:
    with pytest.raises(RuntimeError, match=reason):
        appointments_router._a5_check_in_adapter_response(
            _stop(reason, status_code=503),
            body=_body(),
        )
