from copy import deepcopy
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

import pytest

import app.routers.appointments as appointments_router
from app.config import settings
from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentCommandIdempotency,
    AppointmentStatus,
    BookingChannel,
)
from app.schemas.appointments import BernieUpdateProposalConfirmationIn
from app.services.appointment_idempotency import claim_appointment_command
from tests.conftest import make_token


ROOT = Path(__file__).resolve().parents[1]
ROUTE_TEST_DOC = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_update_confirm_route_tests.md"
)
PREFLIGHT_DOC = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_update_confirm_preflight.md"
)
DEEPSEEK_PREFLIGHT_REVIEW = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "review-deepseek-sprint139-update-confirm-idempotency-preflight.md"
)
DEEPSEEK_ROUTE_REVIEW = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "review-deepseek-sprint140-update-confirm-idempotency-route-contract.md"
)
ROUTER = ROOT / "app" / "routers" / "appointments.py"
UPDATE_TESTS = ROOT / "tests" / "test_appointment_update_proposal.py"

OPERATION_ID = "confirmAppointmentUpdateProposal"
ROUTE_FAMILY = "update-confirm"
CONFIRM_URL = "/api/v1/appointments/proposals/update/confirm"
UPDATE_PROPOSAL_URL = "/api/v1/appointments/proposals/update/{appt_id}"
RAW_UPDATE_URL = "/api/v1/appointments/{appt_id}"
RAW_UPDATE_DOC = "PUT /api/v1/appointments/{appointment_id}"
THURSDAY = date(2026, 6, 26)

PASSING_CONTRACT_TESTS = {
    "test_update_confirm_route_test_contract_records_scope",
    "test_update_confirm_contract_lists_future_behavior_cases",
    "test_update_confirm_contract_records_update_specific_gotchas",
    "test_update_confirm_contract_records_deepseek_family_selection_review",
    "test_update_confirm_contract_records_canonicalization_boundary",
    "test_current_router_wires_update_confirm_idempotency_surface",
    "test_current_router_keeps_proposal_delete_and_raw_update_out_of_scope",
    "test_existing_update_confirm_tests_cover_semantics_to_preserve",
    "test_route_contract_test_inventory_matches_wired_surface",
    "test_missing_idempotency_key_blocks_before_update_or_audit_mutation",
    "test_invalid_update_confirm_payload_does_not_create_ledger_by_default",
    "test_first_confirmed_update_writes_update_audit_and_ledger",
    "test_same_key_same_body_update_replay_has_no_second_update_or_audit_write",
    "test_same_key_different_update_body_conflicts_without_mutation",
    "test_active_in_progress_update_key_fails_closed_without_mutation",
    "test_stale_in_progress_update_key_fails_closed_without_mutation",
    "test_failed_transient_update_key_fails_closed_without_mutation",
    "test_idempotency_key_does_not_bypass_confirmed_true_signed_evidence_freshness_or_revalidation",
    "test_revalidation_block_after_started_claim_rolls_back_or_removes_claim",
    "test_empty_idempotency_key_is_treated_as_missing",
    "test_confirmed_warnings_are_part_of_same_key_body_conflict",
    "test_replay_after_intervening_raw_update_returns_stored_response_without_revalidation",
}


@pytest.fixture(autouse=True)
def _freeze_update_contract_clock(monkeypatch):
    def fixed_now(tz):
        return datetime(2026, 6, 22, 8, 0, 0, tzinfo=tz)

    monkeypatch.setattr(appointments_router, "_clinic_local_now", fixed_now)


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


def _make_appt(db, practice, practitioner, patient, *, start_h=9, duration=15):
    appt = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(THURSDAY, time(start_h, 0), tzinfo=timezone.utc),
        appointment_date=THURSDAY,
        start_time_local=time(start_h, 0),
        duration_minutes=duration,
        status=AppointmentStatus.Booked,
        booked_via=BookingChannel.Receptionist,
        reason="Sprint 141 original",
    )
    db.add(appt)
    db.flush()
    return appt


def _update_payload(
    client,
    token: str,
    appt_id,
    *,
    start_h=10,
    duration=30,
    reason="Sprint 141 updated",
) -> dict:
    resp = client.post(
        UPDATE_PROPOSAL_URL.format(appt_id=appt_id),
        json={
            "appointment_date": THURSDAY.isoformat(),
            "start_time_local": f"{start_h:02d}:00:00",
            "duration_minutes": duration,
            "reason": reason,
        },
        headers=_auth(token, f"update-prop-sprint141-{appt_id}"),
    )
    assert resp.status_code == 200, resp.text
    payload = resp.json()["confirm_payload"]
    payload["confirmed"] = True
    return payload


def _canonical_request_body(payload: dict) -> dict:
    return BernieUpdateProposalConfirmationIn(**payload).model_dump(mode="json")


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


def test_update_confirm_route_test_contract_records_scope():
    text = _read(ROUTE_TEST_DOC)
    preflight = _read(PREFLIGHT_DOC)

    assert "| Sprint | 140 |" in text
    assert "Sprint 141 wiring completed" in text
    assert CONFIRM_URL in text
    assert "confirm_update_proposal_route" in text
    assert "confirm_update_proposal" in text
    assert "BernieUpdateProposalConfirmationIn" in text
    assert OPERATION_ID in text
    assert ROUTE_FAMILY in text
    assert "Recommended Sprint 140" in preflight


def test_update_confirm_contract_lists_future_behavior_cases():
    text = _compact(_read(ROUTE_TEST_DOC))

    for phrase in (
        "missing `Idempotency-Key` returns a fail-closed error",
        "invalid update confirmation payload does not create a ledger row",
        "one completed ledger row",
        "same-key/same-body replay returns the stored response",
        "without a second appointment update, audit row, helper call, or revalidation pass",
        "same-key/different-body returns `409 idempotency_key_conflict`",
        "`409 idempotency_key_in_progress`",
        "`409 idempotency_key_stale_in_progress`",
        "`503 idempotency_key_failed_transient`",
        "does not bypass `confirmed=true`, signed confirmation",
        "blocked revalidation after a started claim rolls back or removes the claim",
        "full validated confirmation-body hashing remains consistent",
    ):
        assert phrase in text


def test_update_confirm_contract_records_update_specific_gotchas():
    text = _compact(_read(ROUTE_TEST_DOC))

    for phrase in (
        "`confirm_update_proposal_route` currently delegates directly to",
        "`confirm_update_proposal` re-runs `propose_update_appointment()`",
        "replay must return at the route wrapper before that revalidation step",
        "must use `db.rollback()`",
        "_apply_appointment_update()` currently commits internally",
        "add a scoped `commit=False` path",
        "raw `PUT /api/v1/appointments/{appointment_id}` must keep default",
        "_UPDATE_CONFIRM_METADATA_FIELDS` is signed-evidence payload shaping only",
        "date, time, duration, practitioner",
    ):
        assert phrase in text


def test_update_confirm_contract_records_deepseek_family_selection_review():
    text = _compact(_read(ROUTE_TEST_DOC))
    preflight_review = _compact(_read(DEEPSEEK_PREFLIGHT_REVIEW))
    route_review = _compact(_read(DEEPSEEK_ROUTE_REVIEW))
    review = f"{preflight_review} {route_review}"

    assert "DeepSeek" in review
    assert "update-confirm" in review
    assert "delete-confirm" in review
    assert "revalidation" in review
    assert "Replay must short-circuit" in route_review
    assert "Full validated confirmation-body hashing" in route_review
    assert "Sprint 140" in text


def test_update_confirm_contract_records_canonicalization_boundary():
    text = _compact(_read(ROUTE_TEST_DOC))
    router_text = _read(ROUTER)

    for phrase in (
        "Use full validated confirmation-body hashing",
        '`request_body=body.model_dump(mode="json")`',
        "`signed_confirmation_evidence`",
        "`update_proposal_freshness_id`",
        "`turn_ref`",
        "`session_binding`",
        "`confirmed_warnings`",
        "`409 idempotency_key_conflict`",
    ):
        assert phrase in text
    assert "_UPDATE_CONFIRM_METADATA_FIELDS" in router_text


def test_current_router_wires_update_confirm_idempotency_surface():
    router_text = _read(ROUTER)
    update_route = _route_body(
        router_text,
        "def confirm_update_proposal_route(",
        "def propose_update_appointment(",
    )
    update_helper = _route_body(
        router_text,
        "def confirm_update_proposal(",
        "def _appointment_status_command_payload(",
    )
    apply_update = _route_body(
        router_text,
        "def _apply_appointment_update(",
        "@router.put",
    )

    assert "Header(" in update_route
    assert "Idempotency-Key" in update_route
    assert "claim_appointment_command(" in update_route
    assert "complete_appointment_command(" in update_route
    assert "_UPDATE_CONFIRM_OPERATION_ID" in router_text
    assert "_UPDATE_CONFIRM_ROUTE_FAMILY" in router_text
    assert "commit=False" in update_route
    assert "claim_appointment_command(" not in update_helper
    assert "complete_appointment_command(" not in update_helper
    assert "Header(" not in update_helper
    assert "propose_update_appointment(" in update_helper
    assert "_apply_appointment_update(" in update_helper
    assert "commit: bool = True" in apply_update
    assert "if commit:" in apply_update
    assert "db.flush()" in apply_update


def test_current_router_keeps_proposal_delete_and_raw_update_out_of_scope():
    router_text = _read(ROUTER)
    update_proposal_route = _route_body(
        router_text,
        "def propose_update_appointment(",
        "def _block_bernie_update_confirmation(",
    )
    raw_update_route = _route_body(
        router_text,
        "def update_appointment(",
        "def get_checkin_defaults(",
    )
    delete_proposal_route = _route_body(
        router_text,
        "def propose_delete_appointment(",
        "@router.get(\"/slots/{practitioner_id}\"",
    )

    # Proposal handlers now have Idempotency-Key syntactic validation
    # raw update and delete must still NOT have it
    assert "claim_appointment_command(" not in update_proposal_route
    assert "Idempotency-Key" not in raw_update_route
    assert "claim_appointment_command(" not in raw_update_route
    assert "_apply_appointment_update(" in raw_update_route
    assert "commit=False" not in raw_update_route
    # Proposal handlers now have Idempotency-Key syntactic validation
    assert "claim_appointment_command(" not in delete_proposal_route
    assert RAW_UPDATE_DOC not in _route_body(
        router_text,
        "def confirm_update_proposal_route(",
        "def propose_update_appointment(",
    )


def test_existing_update_confirm_tests_cover_semantics_to_preserve():
    update_tests = _read(UPDATE_TESTS)

    for phrase in (
        "test_update_proposal_confirm_payload_writes_with_signed_audit_evidence",
        "test_update_confirm_revalidates_same_day_elapsed_window_without_write",
        "UPDATE_CONFIRM_URL",
        "signed_confirmation_evidence",
        "update_proposal_freshness_id",
        "AppointmentAuditLog",
        "AppointmentAuditAction.update",
    ):
        assert phrase in update_tests or phrase in _read(ROUTER)


def test_route_contract_test_inventory_matches_wired_surface():
    test_functions = {
        name
        for name, value in globals().items()
        if name.startswith("test_") and callable(value)
    }
    assert test_functions == PASSING_CONTRACT_TESTS


def test_missing_idempotency_key_blocks_before_update_or_audit_mutation(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _update_payload(client, token, appt.id)
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token))

    assert resp.status_code == 400, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_required"
    db.refresh(appt)
    assert appt.start_time_local == time(9, 0)
    assert _row_counts(db) == before


def test_invalid_update_confirm_payload_does_not_create_ledger_by_default(client, db, gp_user):
    token = make_token(gp_user)

    resp = client.post(
        CONFIRM_URL,
        json={"confirmed": True, "update_proposal": {"not": "valid"}},
        headers=_auth(token, "update-invalid-key"),
    )

    assert resp.status_code == 422, resp.text
    assert db.query(AppointmentCommandIdempotency).count() == 0


def test_first_confirmed_update_writes_update_audit_and_ledger(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _update_payload(client, token, appt.id)
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "update-first-key"))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["appointment"]["id"] == str(appt.id)
    assert data["appointment"]["start_time_local"] == "10:00:00"
    db.refresh(appt)
    assert appt.start_time_local == time(10, 0)
    assert appt.duration_minutes == 30
    assert _row_counts(db) == (before[0], before[1] + 1, before[2] + 1)
    ledger = db.query(AppointmentCommandIdempotency).one()
    assert ledger.state == "completed"
    assert ledger.operation_id == OPERATION_ID
    assert ledger.route_family == ROUTE_FAMILY
    assert ledger.response_body_json == data
    assert ledger.target_appointment_id == appt.id


def test_same_key_same_body_update_replay_has_no_second_update_or_audit_write(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _update_payload(client, token, appt.id)

    first = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "update-replay-key"))
    assert first.status_code == 200, first.text
    after_first = _row_counts(db)

    second = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "update-replay-key"))

    assert second.status_code == 200, second.text
    assert second.json() == first.json()
    db.refresh(appt)
    assert appt.start_time_local == time(10, 0)
    assert _row_counts(db) == after_first


def test_same_key_different_update_body_conflicts_without_mutation(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _update_payload(client, token, appt.id)
    first = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "update-conflict-key"))
    assert first.status_code == 200, first.text
    after_first = _row_counts(db)

    changed = deepcopy(payload)
    changed["confirmed_warnings"] = ["changed-body"]
    second = client.post(CONFIRM_URL, json=changed, headers=_auth(token, "update-conflict-key"))

    assert second.status_code == 409, second.text
    assert second.json()["detail"]["code"] == "idempotency_key_conflict"
    db.refresh(appt)
    assert appt.start_time_local == time(10, 0)
    assert _row_counts(db) == after_first


def test_active_in_progress_update_key_fails_closed_without_mutation(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _update_payload(client, token, appt.id)
    claim = _preclaim(db, gp_user, payload, key="update-progress-key")
    assert claim.kind == "started"
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "update-progress-key"))

    assert resp.status_code == 409, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_in_progress"
    db.refresh(appt)
    assert appt.start_time_local == time(9, 0)
    assert _row_counts(db) == before


def test_stale_in_progress_update_key_fails_closed_without_mutation(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _update_payload(client, token, appt.id)
    claim = _preclaim(db, gp_user, payload, key="update-stale-key")
    claim.record.updated_at = datetime(2000, 1, 1, tzinfo=timezone.utc)
    db.flush()
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "update-stale-key"))

    assert resp.status_code == 409, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_stale_in_progress"
    db.refresh(appt)
    assert appt.start_time_local == time(9, 0)
    assert _row_counts(db) == before


def test_failed_transient_update_key_fails_closed_without_mutation(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _update_payload(client, token, appt.id)
    claim = _preclaim(db, gp_user, payload, key="update-failed-key")
    claim.record.state = "failed_transient"
    db.flush()
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "update-failed-key"))

    assert resp.status_code == 503, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_failed_transient"
    db.refresh(appt)
    assert appt.start_time_local == time(9, 0)
    assert _row_counts(db) == before


def test_idempotency_key_does_not_bypass_confirmed_true_signed_evidence_freshness_or_revalidation(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _update_payload(client, token, appt.id)
    payload["confirmed"] = False
    db.commit()
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "update-block-key"))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert any(block["code"] == "explicit_confirmation_required" for block in data["blocks"])
    db.refresh(appt)
    assert appt.start_time_local == time(9, 0)
    assert _row_counts(db) == before


def test_revalidation_block_after_started_claim_rolls_back_or_removes_claim(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _update_payload(client, token, appt.id, start_h=10, duration=30)
    _make_appt(db, practice, practitioner, patient, start_h=10, duration=15)
    db.commit()
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "update-revalidation-key"))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert any(block["code"] == "update_proposal_revalidation_blocked" for block in data["blocks"])
    db.refresh(appt)
    assert appt.start_time_local == time(9, 0)
    assert _row_counts(db) == before


def test_empty_idempotency_key_is_treated_as_missing(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _update_payload(client, token, appt.id)
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "   "))

    assert resp.status_code == 400, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_required"
    db.refresh(appt)
    assert appt.start_time_local == time(9, 0)
    assert _row_counts(db) == before


def test_confirmed_warnings_are_part_of_same_key_body_conflict(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _update_payload(client, token, appt.id)
    claim = _preclaim(db, gp_user, payload, key="update-warning-conflict-key")
    assert claim.kind == "started"
    changed = deepcopy(payload)
    changed["confirmed_warnings"] = ["semantic-warning-ack"]
    before = _row_counts(db)

    resp = client.post(
        CONFIRM_URL,
        json=changed,
        headers=_auth(token, "update-warning-conflict-key"),
    )

    assert resp.status_code == 409, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_conflict"
    db.refresh(appt)
    assert appt.start_time_local == time(9, 0)
    assert _row_counts(db) == before


def test_replay_after_intervening_raw_update_returns_stored_response_without_revalidation(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _update_payload(client, token, appt.id, reason="Stored response reason")
    first = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "update-raw-replay-key"))
    assert first.status_code == 200, first.text
    stored = first.json()
    raw = client.put(
        RAW_UPDATE_URL.format(appt_id=appt.id),
        json={"reason": "Intervening raw update"},
        headers=_auth(token),
    )
    assert raw.status_code == 200, raw.text
    after_raw = _row_counts(db)

    replay = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "update-raw-replay-key"))

    assert replay.status_code == 200, replay.text
    assert replay.json() == stored
    db.refresh(appt)
    assert appt.reason == "Intervening raw update"
    assert _row_counts(db) == after_raw
