from copy import deepcopy
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from app.config import settings
from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentCommandIdempotency,
    AppointmentStatus,
    BookingChannel,
)
from app.models.diary import WaitingArea
from app.schemas.appointments import AppointmentDeleteProposalConfirmationIn
from app.services.appointment_idempotency import claim_appointment_command
from tests.conftest import make_token


ROOT = Path(__file__).resolve().parents[1]
ROUTE_TEST_DOC = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_delete_confirm_route_tests.md"
)
PREFLIGHT_DOC = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_delete_confirm_preflight.md"
)
DEEPSEEK_PREFLIGHT_REVIEW = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "review-deepseek-sprint142-delete-confirm-idempotency-preflight.md"
)
DEEPSEEK_ROUTE_REVIEW = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "review-deepseek-sprint143-delete-confirm-idempotency-route-contract.md"
)
ROUTER = ROOT / "app" / "routers" / "appointments.py"
DELETE_TESTS = ROOT / "tests" / "test_appointment_status_mutations.py"
AUDIT_TESTS = ROOT / "tests" / "test_appointment_audit.py"
REASON_TESTS = ROOT / "tests" / "test_reason_code_backend.py"

OPERATION_ID = "confirmAppointmentDeleteProposal"
ROUTE_FAMILY = "delete-confirm"
CONFIRM_URL = "/api/v1/appointments/proposals/delete-confirm"
DELETE_PROPOSAL_URL = "/api/v1/appointments/proposals/delete/{appt_id}"
RAW_DELETE_URL = "/api/v1/appointments/{appt_id}"
RAW_DELETE_DOC = "DELETE /api/v1/appointments/{appointment_id}"
THURSDAY = date(2026, 6, 26)

PASSING_CONTRACT_TESTS = {
    "test_delete_confirm_route_test_contract_records_scope",
    "test_delete_confirm_contract_lists_future_behavior_cases",
    "test_delete_confirm_contract_records_delete_specific_gotchas",
    "test_delete_confirm_contract_records_deepseek_preflight_review",
    "test_current_router_wires_delete_confirm_idempotency_surface",
    "test_current_router_keeps_raw_and_proposal_delete_out_of_scope",
    "test_existing_delete_confirm_tests_cover_semantics_to_preserve",
    "test_route_contract_test_inventory_matches_wired_surface",
    "test_missing_idempotency_key_blocks_before_delete_or_audit_mutation",
    "test_blank_idempotency_key_is_treated_as_missing",
    "test_invalid_delete_confirm_payload_does_not_create_ledger_by_default",
    "test_first_confirmed_delete_writes_soft_cancel_audit_and_ledger",
    "test_same_key_same_body_delete_replay_has_no_second_audit_or_side_effect",
    "test_replay_after_intervening_raw_delete_returns_stored_response_without_revalidation",
    "test_same_key_different_delete_body_conflicts_without_mutation",
    "test_active_in_progress_delete_key_fails_closed_without_mutation",
    "test_stale_in_progress_delete_key_fails_closed_without_mutation",
    "test_failed_transient_delete_key_fails_closed_without_mutation",
    "test_idempotency_key_does_not_bypass_confirmed_signed_freshness_or_waiting_area_checks",
    "test_blocked_delete_checks_after_started_claim_roll_back_claim",
    "test_already_cancelled_delete_confirm_blocks_without_ledger_or_audit",
    "test_nonexistent_delete_confirm_blocks_without_ledger_or_audit",
    "test_confirmed_warnings_are_part_of_delete_same_key_body_conflict",
    "test_nested_delete_proposal_is_part_of_same_key_body_conflict",
    "test_same_key_replay_preserves_merged_confirmed_warnings",
    "test_invalid_status_reason_code_blocks_without_ledger",
    "test_missing_signed_delete_evidence_blocks_and_rolls_back_claim",
    "test_waiting_area_clear_true_without_waiting_area_blocks",
    "test_waiting_area_clear_false_with_waiting_area_blocks",
    "test_concurrent_different_keys_on_same_delete_are_appointment_write_concurrency",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _compact(text: str) -> str:
    return " ".join(text.split())


def _route_body(router_text: str, start_marker: str, end_marker: str) -> str:
    start = router_text.index(start_marker)
    end = router_text.index(end_marker, start)
    return router_text[start:end]


def _auth(token: str, idempotency_key: str | None = None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    if idempotency_key is not None:
        headers["Idempotency-Key"] = idempotency_key
    return headers


def _row_counts(db) -> tuple[int, int, int]:
    return (
        db.query(Appointment).count(),
        db.query(AppointmentAuditLog).count(),
        db.query(AppointmentCommandIdempotency).count(),
    )


def _make_area(db, practice):
    area = WaitingArea(practice_id=practice.id, name=f"Delete Area {uuid4()}")
    db.add(area)
    db.flush()
    return area


def _make_appt(
    db,
    practice,
    practitioner,
    patient,
    *,
    start_h=9,
    status=AppointmentStatus.Booked,
    waiting_area=None,
):
    appt = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(THURSDAY, time(start_h, 0), tzinfo=timezone.utc),
        appointment_date=THURSDAY,
        start_time_local=time(start_h, 0),
        duration_minutes=15,
        status=status,
        booked_via=BookingChannel.Receptionist,
        waiting_area_id=waiting_area.id if waiting_area is not None else None,
    )
    db.add(appt)
    db.flush()
    return appt


def _delete_payload(
    client,
    token: str,
    appt_id,
    *,
    cancellation_reason="Sprint 144 delete",
    status_reason_code=None,
) -> dict:
    body = {"cancellation_reason": cancellation_reason}
    if status_reason_code is not None:
        body["status_reason_code"] = status_reason_code
    resp = client.post(
        DELETE_PROPOSAL_URL.format(appt_id=appt_id),
        json=body,
        headers=_auth(token, f"delete-prop-sprint143-{appt_id}"),
    )
    assert resp.status_code == 200, resp.text
    payload = resp.json()["confirm_payload"]
    payload["confirmed"] = True
    return payload


def _canonical_request_body(payload: dict) -> dict:
    return AppointmentDeleteProposalConfirmationIn(**payload).model_dump(mode="json")


def _preclaim(db, user, payload: dict, *, key: str):
    return claim_appointment_command(
        db,
        practice_id=user.practice_id,
        actor_user_id=str(user.id),
        actor_role=user.role.value,
        operation_id=OPERATION_ID,
        route_family=ROUTE_FAMILY,
        raw_idempotency_key=key,
        request_body=_canonical_request_body(payload),
        secret=settings.secret_key.encode("utf-8"),
        stale_after=timedelta(minutes=10),
    )


def _post_confirm(client, token: str, payload: dict, key: str | None):
    return client.post(CONFIRM_URL, json=payload, headers=_auth(token, key))


def test_delete_confirm_route_test_contract_records_scope():
    text = _read(ROUTE_TEST_DOC)
    preflight = _read(PREFLIGHT_DOC)

    assert "| Sprint | 143 |" in text
    assert "Guarded route-test contract only" in text
    assert CONFIRM_URL in text
    assert "confirm_delete_proposal_route" in text
    assert "_apply_appointment_delete" in text
    assert "AppointmentDeleteProposalConfirmationIn" in text
    assert OPERATION_ID in text
    assert ROUTE_FAMILY in text
    assert "Recommended Sprint 143" in preflight


def test_delete_confirm_contract_lists_future_behavior_cases():
    text = _compact(_read(ROUTE_TEST_DOC))

    for phrase in (
        "missing `Idempotency-Key` returns a fail-closed error",
        "blank/whitespace `Idempotency-Key` is treated as missing",
        "invalid delete confirmation payload does not create a ledger row",
        "one completed ledger row",
        "clears `waiting_area_id`",
        "same-key/same-body replay returns the stored response",
        "intervening raw delete returns the stored response",
        "same-key/different-body returns `409 idempotency_key_conflict`",
        "`409 idempotency_key_in_progress`",
        "`409 idempotency_key_stale_in_progress`",
        "`503 idempotency_key_failed_transient`",
        "does not bypass `confirmed=true`, signed confirmation",
        "call `db.rollback()`",
    ):
        assert phrase in text


def test_delete_confirm_contract_records_delete_specific_gotchas():
    text = _compact(_read(ROUTE_TEST_DOC))

    for phrase in (
        "`_apply_appointment_delete()` currently commits internally",
        "add a scoped `commit=False` path",
        "Raw `DELETE /api/v1/appointments/{appointment_id}` must keep default",
        "does not re-run `propose_delete_appointment()`",
        "Replay must return before those destructive checks can run again",
        "duplicate audit rows or repeated clearing are release-blocking",
    ):
        assert phrase in text


def test_delete_confirm_contract_records_deepseek_preflight_review():
    review = _compact(_read(DEEPSEEK_PREFLIGHT_REVIEW))
    route_review = _compact(_read(DEEPSEEK_ROUTE_REVIEW))

    assert "DeepSeek" in review
    assert "delete-confirm" in review
    assert "_apply_appointment_delete()" in review
    assert "soft-cancel" in review
    assert "Raw `DELETE" in review
    assert "already-cancelled" in route_review
    assert "confirmed_warnings" in route_review
    assert "waiting-area mismatch" in route_review


def test_current_router_wires_delete_confirm_idempotency_surface():
    router_text = _read(ROUTER)
    delete_route = _route_body(
        router_text,
        "def confirm_delete_proposal_route(",
        "def propose_delete_appointment(",
    )
    apply_delete = _route_body(
        router_text,
        "def _apply_appointment_delete(",
        "@router.delete",
    )

    assert "Header(" in delete_route
    assert "Idempotency-Key" in delete_route
    assert "claim_appointment_command(" in delete_route
    assert "complete_appointment_command(" in delete_route
    assert "_DELETE_CONFIRM_OPERATION_ID" in router_text
    assert "_DELETE_CONFIRM_ROUTE_FAMILY" in router_text
    assert "commit=False" in delete_route
    assert "commit: bool = True" in apply_delete
    assert "if commit:" in apply_delete
    assert "db.flush()" in apply_delete


def test_current_router_keeps_raw_and_proposal_delete_out_of_scope():
    router_text = _read(ROUTER)
    raw_delete = _route_body(
        router_text,
        "def cancel_appointment(",
        "@router.post(\n    \"/proposals/delete-confirm\"",
    )
    proposal_delete = _route_body(
        router_text,
        "def propose_delete_appointment(",
        "@router.get(\"/slots/{practitioner_id}\"",
    )
    delete_route = _route_body(
        router_text,
        "def confirm_delete_proposal_route(",
        "def propose_delete_appointment(",
    )

    assert "Idempotency-Key" not in raw_delete
    assert "claim_appointment_command(" not in raw_delete
    assert "commit=False" not in raw_delete
    # Proposal handlers now have Idempotency-Key syntactic validation
    assert "claim_appointment_command(" not in proposal_delete
    assert RAW_DELETE_DOC not in delete_route


def test_existing_delete_confirm_tests_cover_semantics_to_preserve():
    combined = "\n".join([
        _read(DELETE_TESTS),
        _read(AUDIT_TESTS),
        _read(REASON_TESTS),
        _read(ROUTER),
    ])

    for phrase in (
        "DELETE_CONFIRM_URL",
        "test_delete_proposal_returns_signed_confirm_payload",
        "test_delete_confirm_soft_cancels_once_with_signed_evidence",
        "stale_delete_proposal_freshness_id",
        "stale_delete_waiting_area_state",
        "diary_confirm_delete_proposal",
        "source_delete_proposal",
        "status_reason_code",
        "AppointmentAuditAction.delete",
    ):
        assert phrase in combined


def test_route_contract_test_inventory_matches_wired_surface():
    test_functions = {
        name
        for name, value in globals().items()
        if name.startswith("test_") and callable(value)
    }
    assert test_functions == PASSING_CONTRACT_TESTS


def test_missing_idempotency_key_blocks_before_delete_or_audit_mutation(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _delete_payload(client, token, appt.id)
    before = _row_counts(db)

    resp = _post_confirm(client, token, payload, None)

    assert resp.status_code == 400, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_required"
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == before


def test_blank_idempotency_key_is_treated_as_missing(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _delete_payload(client, token, appt.id)
    before = _row_counts(db)

    resp = _post_confirm(client, token, payload, "   ")

    assert resp.status_code == 400, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_required"
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == before


def test_invalid_delete_confirm_payload_does_not_create_ledger_by_default(client, db, gp_user):
    token = make_token(gp_user)

    resp = client.post(
        CONFIRM_URL,
        json={"confirmed": True, "delete_proposal": {"not": "valid"}},
        headers=_auth(token, "delete-invalid-key"),
    )

    assert resp.status_code == 422, resp.text
    assert db.query(AppointmentCommandIdempotency).count() == 0


def test_first_confirmed_delete_writes_soft_cancel_audit_and_ledger(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient, waiting_area=area)
    payload = _delete_payload(client, token, appt.id)
    before = _row_counts(db)

    resp = _post_confirm(client, token, payload, "delete-first-key")

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["appointment"]["status"] == "Cancelled"
    assert data["appointment"]["waiting_area_id"] is None
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Cancelled
    assert appt.waiting_area_id is None
    assert appt.cancellation_reason == "Sprint 144 delete"
    assert _row_counts(db) == (before[0], before[1] + 1, before[2] + 1)
    ledger = db.query(AppointmentCommandIdempotency).one()
    assert ledger.state == "completed"
    assert ledger.operation_id == OPERATION_ID
    assert ledger.route_family == ROUTE_FAMILY
    assert ledger.response_body_json == data
    assert ledger.target_appointment_id == appt.id


def test_same_key_same_body_delete_replay_has_no_second_audit_or_side_effect(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _delete_payload(client, token, appt.id)
    first = _post_confirm(client, token, payload, "delete-replay-key")
    assert first.status_code == 200, first.text
    after_first = _row_counts(db)

    second = _post_confirm(client, token, payload, "delete-replay-key")

    assert second.status_code == 200, second.text
    assert second.json() == first.json()
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Cancelled
    assert _row_counts(db) == after_first


def test_replay_after_intervening_raw_delete_returns_stored_response_without_revalidation(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient, start_h=9)
    payload = _delete_payload(client, token, appt.id, cancellation_reason="Stored delete")
    first = _post_confirm(client, token, payload, "delete-raw-replay-key")
    assert first.status_code == 200, first.text
    stored = first.json()
    raw = client.delete(RAW_DELETE_URL.format(appt_id=appt.id), headers=_auth(token))
    assert raw.status_code == 204, raw.text
    after_raw = _row_counts(db)

    replay = _post_confirm(client, token, payload, "delete-raw-replay-key")

    assert replay.status_code == 200, replay.text
    assert replay.json() == stored
    assert _row_counts(db) == after_raw


def test_same_key_different_delete_body_conflicts_without_mutation(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _delete_payload(client, token, appt.id)
    first = _post_confirm(client, token, payload, "delete-conflict-key")
    assert first.status_code == 200, first.text
    after_first = _row_counts(db)

    changed = deepcopy(payload)
    changed["confirmed_warnings"] = ["different-warning"]
    second = _post_confirm(client, token, changed, "delete-conflict-key")

    assert second.status_code == 409, second.text
    assert second.json()["detail"]["code"] == "idempotency_key_conflict"
    assert _row_counts(db) == after_first


def test_active_in_progress_delete_key_fails_closed_without_mutation(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _delete_payload(client, token, appt.id)
    claim = _preclaim(db, gp_user, payload, key="delete-progress-key")
    assert claim.kind == "started"
    before = _row_counts(db)

    resp = _post_confirm(client, token, payload, "delete-progress-key")

    assert resp.status_code == 409, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_in_progress"
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == before


def test_stale_in_progress_delete_key_fails_closed_without_mutation(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _delete_payload(client, token, appt.id)
    claim = _preclaim(db, gp_user, payload, key="delete-stale-key")
    claim.record.updated_at = datetime(2000, 1, 1, tzinfo=timezone.utc)
    db.flush()
    before = _row_counts(db)

    resp = _post_confirm(client, token, payload, "delete-stale-key")

    assert resp.status_code == 409, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_stale_in_progress"
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == before


def test_failed_transient_delete_key_fails_closed_without_mutation(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _delete_payload(client, token, appt.id)
    claim = _preclaim(db, gp_user, payload, key="delete-failed-key")
    claim.record.state = "failed_transient"
    db.flush()
    before = _row_counts(db)

    resp = _post_confirm(client, token, payload, "delete-failed-key")

    assert resp.status_code == 503, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_failed_transient"
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == before


def test_idempotency_key_does_not_bypass_confirmed_signed_freshness_or_waiting_area_checks(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _delete_payload(client, token, appt.id)
    payload["confirmed"] = False
    db.commit()
    before = _row_counts(db)

    resp = _post_confirm(client, token, payload, "delete-confirmed-false-key")

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert any(block["code"] == "explicit_confirmation_required" for block in data["blocks"])
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == before


def test_blocked_delete_checks_after_started_claim_roll_back_claim(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _delete_payload(client, token, appt.id)
    payload["confirmed"] = False
    db.commit()
    before = _row_counts(db)

    resp = _post_confirm(client, token, payload, "delete-rollback-key")

    assert resp.status_code == 200, resp.text
    assert resp.json()["safe"] is False
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == before


def test_already_cancelled_delete_confirm_blocks_without_ledger_or_audit(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _delete_payload(client, token, appt.id)
    appt.status = AppointmentStatus.Cancelled
    db.commit()
    before = _row_counts(db)

    resp = _post_confirm(client, token, payload, "delete-already-cancelled-key")

    assert resp.status_code == 200, resp.text
    assert resp.json()["safe"] is False
    assert _row_counts(db) == before


def test_nonexistent_delete_confirm_blocks_without_ledger_or_audit(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _delete_payload(client, token, appt.id)
    db.delete(appt)
    db.commit()
    before = _row_counts(db)

    resp = _post_confirm(client, token, payload, "delete-nonexistent-key")

    assert resp.status_code == 404, resp.text
    assert _row_counts(db) == before


def test_confirmed_warnings_are_part_of_delete_same_key_body_conflict(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _delete_payload(client, token, appt.id)
    claim = _preclaim(db, gp_user, payload, key="delete-warning-conflict-key")
    assert claim.kind == "started"
    changed = deepcopy(payload)
    changed["confirmed_warnings"] = ["acknowledged-warning"]
    before = _row_counts(db)

    resp = _post_confirm(client, token, changed, "delete-warning-conflict-key")

    assert resp.status_code == 409, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_conflict"
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == before


def test_nested_delete_proposal_is_part_of_same_key_body_conflict(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _delete_payload(client, token, appt.id)
    claim = _preclaim(db, gp_user, payload, key="delete-nested-conflict-key")
    assert claim.kind == "started"
    changed = deepcopy(payload)
    changed["delete_proposal"]["command"]["cancellation_reason"] = "Different nested reason"
    before = _row_counts(db)

    resp = _post_confirm(client, token, changed, "delete-nested-conflict-key")

    assert resp.status_code == 409, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_conflict"
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == before


def test_same_key_replay_preserves_merged_confirmed_warnings(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient, waiting_area=area)
    payload = _delete_payload(client, token, appt.id)
    payload["confirmed_warnings"] = ["staff_acknowledged"]
    first = _post_confirm(client, token, payload, "delete-warning-replay-key")
    assert first.status_code == 200, first.text
    stored = first.json()
    audit = db.query(AppointmentAuditLog).one()
    assert "waiting_area_cleared" in audit.confirmed_warnings

    replay = _post_confirm(client, token, payload, "delete-warning-replay-key")

    assert replay.status_code == 200, replay.text
    assert replay.json() == stored
    assert db.query(AppointmentAuditLog).count() == 1


def test_invalid_status_reason_code_blocks_without_ledger(client, db, gp_user):
    token = make_token(gp_user)

    resp = client.post(
        CONFIRM_URL,
        json={
            "confirmed": True,
            "delete_proposal": {
                "safe": True,
                "requires_confirmation": True,
                "autonomy_tier": "proposal",
                "summary": "bad reason",
                "command": {
                    "appointment_id": str(uuid4()),
                    "clears_waiting_area": False,
                    "status_reason_code": "NOT_A_REASON",
                },
                "warnings": [],
                "blocks": [],
            },
        },
        headers=_auth(token, "delete-bad-reason-key"),
    )

    assert resp.status_code == 422, resp.text
    assert db.query(AppointmentCommandIdempotency).count() == 0


def test_missing_signed_delete_evidence_blocks_and_rolls_back_claim(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _delete_payload(client, token, appt.id)
    payload["signed_confirmation_evidence"] = None
    payload["signed_confirmation_evidence_required"] = True
    db.commit()
    before = _row_counts(db)

    resp = _post_confirm(client, token, payload, "delete-missing-evidence-key")

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert any(block["code"] == "signed_evidence_missing" for block in data["blocks"])
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == before


def test_waiting_area_clear_true_without_waiting_area_blocks(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient, waiting_area=area)
    payload = _delete_payload(client, token, appt.id)
    appt.waiting_area_id = None
    db.commit()
    before = _row_counts(db)

    resp = _post_confirm(client, token, payload, "delete-waiting-clear-true-key")

    assert resp.status_code == 200, resp.text
    assert resp.json()["safe"] is False
    assert any(block["code"] == "stale_delete_waiting_area_state" for block in resp.json()["blocks"])
    assert _row_counts(db) == before


def test_waiting_area_clear_false_with_waiting_area_blocks(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _delete_payload(client, token, appt.id)
    appt.waiting_area_id = _make_area(db, practice).id
    db.commit()
    before = _row_counts(db)

    resp = _post_confirm(client, token, payload, "delete-waiting-clear-false-key")

    assert resp.status_code == 200, resp.text
    assert resp.json()["safe"] is False
    assert any(block["code"] == "stale_delete_waiting_area_state" for block in resp.json()["blocks"])
    assert _row_counts(db) == before


def test_concurrent_different_keys_on_same_delete_are_appointment_write_concurrency(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _delete_payload(client, token, appt.id)
    first = _post_confirm(client, token, payload, "delete-first-concurrency-key")
    assert first.status_code == 200, first.text
    after_first = _row_counts(db)

    second = _post_confirm(client, token, payload, "delete-second-concurrency-key")

    assert second.status_code == 200, second.text
    assert second.json()["safe"] is False
    assert any(
        block["code"] in {"stale_delete_proposal_freshness_id", "stale_delete_waiting_area_state"}
        for block in second.json()["blocks"]
    )
    assert _row_counts(db) == after_first
