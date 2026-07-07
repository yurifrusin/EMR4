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
from app.models.diary import WaitingArea
from app.schemas.appointments import AppointmentStatusProposalConfirmationIn
from app.services.appointment_idempotency import claim_appointment_command
from tests.conftest import make_token


ROOT = Path(__file__).resolve().parents[1]
ROUTE_TEST_DOC = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_status_confirm_route_tests.md"
)
PREFLIGHT_DOC = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_status_confirm_preflight.md"
)
DEEPSEEK_REVIEW = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "review-deepseek-sprint136-status-confirm-idempotency-preflight.md"
)
ROUTER = ROOT / "app" / "routers" / "appointments.py"
STATUS_TESTS = ROOT / "tests" / "test_appointment_status_mutations.py"
REASON_CODE_TESTS = ROOT / "tests" / "test_reason_code_backend.py"
APPOINTMENT_AUDIT_TESTS = ROOT / "tests" / "test_appointment_audit.py"

OPERATION_ID = "confirmAppointmentStatusProposal"
ROUTE_FAMILY = "status-confirm"
CONFIRM_URL = "/api/v1/appointments/proposals/status-confirm"
STATUS_PROPOSAL_URL = "/api/v1/appointments/proposals/status/{appt_id}"
WAITING_AREA_PROPOSAL_URL = "/api/v1/appointments/proposals/waiting-area/{appt_id}"
CANONICAL_OPENAPI_PATH = "/api/v1/appointments/proposals/status/confirm"
THURSDAY = date(2026, 6, 25)

PASSING_CONTRACT_TESTS = {
    "test_status_confirm_route_test_contract_records_scope",
    "test_status_confirm_contract_lists_future_behavior_cases",
    "test_status_confirm_contract_records_deepseek_family_selection_review",
    "test_current_router_wires_status_confirm_idempotency_surface",
    "test_existing_status_confirm_tests_cover_semantics_to_preserve",
    "test_status_confirm_metadata_boundary_is_documented",
    "test_route_contract_test_inventory_matches_wired_surface",
    "test_missing_idempotency_key_blocks_before_status_or_audit_mutation",
    "test_invalid_status_confirm_payload_does_not_create_ledger_by_default",
    "test_first_confirmed_status_change_writes_status_audit_and_ledger",
    "test_first_confirmed_waiting_area_change_writes_waiting_area_audit_and_ledger",
    "test_same_key_same_body_status_replay_has_no_second_status_or_audit_write",
    "test_same_key_same_body_waiting_area_replay_has_no_second_waiting_area_or_audit_write",
    "test_same_key_different_status_body_conflicts_without_mutation",
    "test_active_in_progress_status_key_fails_closed_without_mutation",
    "test_stale_in_progress_status_key_fails_closed_without_mutation",
    "test_failed_transient_status_key_fails_closed_without_mutation",
    "test_idempotency_key_does_not_bypass_confirmed_true_signed_evidence_or_freshness",
    "test_status_and_waiting_area_union_variants_hash_as_distinct_effective_commands",
}


@pytest.fixture(autouse=True)
def _freeze_status_contract_clock(monkeypatch):
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


def _make_appt(db, practice, practitioner, patient, *, status=AppointmentStatus.Booked):
    appt = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(THURSDAY, time(9, 0), tzinfo=timezone.utc),
        appointment_date=THURSDAY,
        start_time_local=time(9, 0),
        duration_minutes=15,
        status=status,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt)
    db.flush()
    return appt


def _make_area(db, practice):
    area = WaitingArea(practice_id=practice.id, name="Sprint 138 Waiting")
    db.add(area)
    db.flush()
    return area


def _row_counts(db) -> tuple[int, int, int]:
    return (
        db.query(Appointment).count(),
        db.query(AppointmentAuditLog).count(),
        db.query(AppointmentCommandIdempotency).count(),
    )


def _status_payload(client, token: str, appt_id, *, status_value="Confirmed") -> dict:
    proposal = client.post(
        STATUS_PROPOSAL_URL.format(appt_id=appt_id),
        json={"status": status_value},
        headers=_auth(token),
    )
    assert proposal.status_code == 200, proposal.text
    payload = proposal.json()["confirm_payload"]
    payload["confirmed"] = True
    return payload


def _waiting_area_payload(client, token: str, appt_id, area_id) -> dict:
    proposal = client.post(
        WAITING_AREA_PROPOSAL_URL.format(appt_id=appt_id),
        json={"waiting_area_id": str(area_id)},
        headers=_auth(token),
    )
    assert proposal.status_code == 200, proposal.text
    payload = proposal.json()["confirm_payload"]
    payload["confirmed"] = True
    return payload


def _canonical_request_body(payload: dict) -> dict:
    return AppointmentStatusProposalConfirmationIn(**payload).model_dump(mode="json")


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


def test_status_confirm_route_test_contract_records_scope():
    text = _read(ROUTE_TEST_DOC)
    preflight = _read(PREFLIGHT_DOC)

    assert "| Sprint | 137 |" in text
    assert CONFIRM_URL in text
    assert CANONICAL_OPENAPI_PATH in text
    assert "confirm_status_proposal_route" in text
    assert "AppointmentStatusProposalConfirmationIn" in text
    assert OPERATION_ID in text
    assert ROUTE_FAMILY in text
    assert "Status-confirm idempotency route-test contract" in preflight


def test_status_confirm_contract_lists_future_behavior_cases():
    text = _compact(_read(ROUTE_TEST_DOC))

    for phrase in (
        "missing `Idempotency-Key` returns a fail-closed error",
        "invalid status confirmation payload does not create a ledger row",
        "same-key/same-body status replay returns the stored response",
        "same-key/same-body waiting-area replay returns the stored response",
        "same-key/different-body returns `409 idempotency_key_conflict`",
        "`409 idempotency_key_in_progress`",
        "`409 idempotency_key_stale_in_progress`",
        "`503 idempotency_key_failed_transient`",
        "does not bypass `confirmed=true`",
        "union variants canonicalize",
    ):
        assert phrase in text


def test_status_confirm_contract_records_deepseek_family_selection_review():
    text = _compact(_read(ROUTE_TEST_DOC))
    review = _compact(_read(DEEPSEEK_REVIEW))

    assert "DeepSeek's review found that `status-confirm` has the cleanest" in review
    assert "status-confirm is self-contained" in review
    assert "no `turn_ref` or `session_binding`" in review
    assert "less destructive than delete-confirm" in review
    assert "DeepSeek" in text


def test_current_router_wires_status_confirm_idempotency_surface():
    router_text = _read(ROUTER)
    status_route = _route_body(
        router_text,
        "def confirm_status_proposal_route(",
        "def get_waiting_room(",
    )
    update_route = _route_body(
        router_text,
        "def confirm_update_proposal_route(",
        "def propose_update_appointment(",
    )
    delete_route = _route_body(
        router_text,
        "def confirm_delete_proposal_route(",
        "def propose_delete_appointment(",
    )

    assert "Header(" in status_route
    assert "Idempotency-Key" in status_route
    assert "claim_appointment_command(" in status_route
    assert "complete_appointment_command(" in status_route
    assert "_STATUS_CONFIRM_OPERATION_ID" in router_text
    assert "_STATUS_CONFIRM_ROUTE_FAMILY" in router_text
    assert "commit=False" in status_route
    assert "Header(" not in update_route
    assert "Idempotency-Key" not in update_route
    assert "Header(" not in delete_route
    assert "Idempotency-Key" not in delete_route


def test_existing_status_confirm_tests_cover_semantics_to_preserve():
    status_tests = _read(STATUS_TESTS)
    reason_tests = _read(REASON_CODE_TESTS)
    audit_tests = _read(APPOINTMENT_AUDIT_TESTS)
    combined = "\n".join([status_tests, reason_tests, audit_tests])

    for phrase in (
        "test_status_confirm_route_writes_once_with_signed_evidence",
        "test_status_confirm_route_blocks_tampered_status_without_write",
        "test_status_confirm_preserves_waiting_area_when_field_omitted",
        "test_status_confirm_clears_waiting_area_when_null_supplied",
        "test_r9_status_confirm_allows_past_date_with_signed_evidence_and_audit",
        "test_r9_status_confirm_past_date_blocks_tampered_status_without_write",
        "status_reason_code",
        "AppointmentAuditAction.status_change",
    ):
        assert phrase in combined


def test_status_confirm_metadata_boundary_is_documented():
    text = _read(ROUTE_TEST_DOC)
    compact = _compact(text)
    router_text = _read(ROUTER)

    assert "_STATUS_CONFIRM_METADATA_FIELDS" in text
    assert "must not be treated as the idempotency request-body canonicalizer" in text
    assert "full validated confirmation body" in compact
    for field in (
        "confirm_endpoint",
        "confirm_payload",
        "status_proposal_freshness_id",
        "signed_confirmation_evidence",
        "signed_confirmation_evidence_required",
    ):
        assert field in router_text


def test_route_contract_test_inventory_matches_wired_surface():
    test_functions = [
        (name, value)
        for name, value in globals().items()
        if name.startswith("test_") and callable(value)
    ]
    assert {name for name, _ in test_functions} == PASSING_CONTRACT_TESTS


def test_missing_idempotency_key_blocks_before_status_or_audit_mutation(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _status_payload(client, token, appt.id)
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token))

    assert resp.status_code == 400, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_required"
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == before


def test_invalid_status_confirm_payload_does_not_create_ledger_by_default(client, db, gp_user):
    token = make_token(gp_user)

    resp = client.post(
        CONFIRM_URL,
        json={"confirmed": True, "status_proposal": {"not": "valid"}},
        headers=_auth(token, "status-invalid-key"),
    )

    assert resp.status_code == 422, resp.text
    assert db.query(AppointmentCommandIdempotency).count() == 0


def test_first_confirmed_status_change_writes_status_audit_and_ledger(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _status_payload(client, token, appt.id)
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "status-first-key"))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Confirmed
    assert _row_counts(db) == (before[0], before[1] + 1, before[2] + 1)
    ledger = db.query(AppointmentCommandIdempotency).one()
    assert ledger.state == "completed"
    assert ledger.operation_id == OPERATION_ID
    assert ledger.route_family == ROUTE_FAMILY
    assert ledger.response_body_json == data
    assert ledger.target_appointment_id == appt.id


def test_first_confirmed_waiting_area_change_writes_waiting_area_audit_and_ledger(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _waiting_area_payload(client, token, appt.id, area.id)
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "waiting-first-key"))

    assert resp.status_code == 200, resp.text
    db.refresh(appt)
    assert appt.waiting_area_id == area.id
    assert _row_counts(db) == (before[0], before[1] + 1, before[2] + 1)
    ledger = db.query(AppointmentCommandIdempotency).one()
    assert ledger.state == "completed"
    assert ledger.target_appointment_id == appt.id


def test_same_key_same_body_status_replay_has_no_second_status_or_audit_write(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _status_payload(client, token, appt.id)

    first = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "status-replay-key"))
    assert first.status_code == 200, first.text
    after_first = _row_counts(db)

    second = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "status-replay-key"))

    assert second.status_code == 200, second.text
    assert second.json() == first.json()
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Confirmed
    assert _row_counts(db) == after_first


def test_same_key_same_body_waiting_area_replay_has_no_second_waiting_area_or_audit_write(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _waiting_area_payload(client, token, appt.id, area.id)

    first = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "waiting-replay-key"))
    assert first.status_code == 200, first.text
    after_first = _row_counts(db)

    second = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "waiting-replay-key"))

    assert second.status_code == 200, second.text
    assert second.json() == first.json()
    db.refresh(appt)
    assert appt.waiting_area_id == area.id
    assert _row_counts(db) == after_first


def test_same_key_different_status_body_conflicts_without_mutation(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    first_payload = _status_payload(client, token, appt.id, status_value="Confirmed")
    first = client.post(CONFIRM_URL, json=first_payload, headers=_auth(token, "status-conflict-key"))
    assert first.status_code == 200, first.text
    after_first = _row_counts(db)

    second_payload = _status_payload(client, token, appt.id, status_value="Arrived")
    second = client.post(CONFIRM_URL, json=second_payload, headers=_auth(token, "status-conflict-key"))

    assert second.status_code == 409, second.text
    assert second.json()["detail"]["code"] == "idempotency_key_conflict"
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Confirmed
    assert _row_counts(db) == after_first


def test_active_in_progress_status_key_fails_closed_without_mutation(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _status_payload(client, token, appt.id)
    claim = _preclaim(db, gp_user, payload, key="status-progress-key")
    assert claim.kind == "started"
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "status-progress-key"))

    assert resp.status_code == 409, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_in_progress"
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == before


def test_stale_in_progress_status_key_fails_closed_without_mutation(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _status_payload(client, token, appt.id)
    claim = _preclaim(db, gp_user, payload, key="status-stale-key")
    claim.record.updated_at = datetime(2000, 1, 1, tzinfo=timezone.utc)
    db.flush()
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "status-stale-key"))

    assert resp.status_code == 409, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_stale_in_progress"
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == before


def test_failed_transient_status_key_fails_closed_without_mutation(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _status_payload(client, token, appt.id)
    claim = _preclaim(db, gp_user, payload, key="status-failed-key")
    claim.record.state = "failed_transient"
    db.flush()
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "status-failed-key"))

    assert resp.status_code == 503, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_failed_transient"
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == before


def test_idempotency_key_does_not_bypass_confirmed_true_signed_evidence_or_freshness(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    appt = _make_appt(db, practice, practitioner, patient)
    payload = _status_payload(client, token, appt.id)
    payload["confirmed"] = False
    db.commit()
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "status-block-key"))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert any(block["code"] == "explicit_confirmation_required" for block in data["blocks"])
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert _row_counts(db) == before


def test_status_and_waiting_area_union_variants_hash_as_distinct_effective_commands(
    client, db, gp_user, practice, practitioner, patient
):
    token = make_token(gp_user)
    area = _make_area(db, practice)
    appt = _make_appt(db, practice, practitioner, patient)
    status_payload = _status_payload(client, token, appt.id)
    waiting_payload = _waiting_area_payload(client, token, appt.id, area.id)
    claim = _preclaim(db, gp_user, status_payload, key="status-union-key")
    assert claim.kind == "started"
    before = _row_counts(db)

    resp = client.post(CONFIRM_URL, json=waiting_payload, headers=_auth(token, "status-union-key"))

    assert resp.status_code == 409, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_conflict"
    db.refresh(appt)
    assert appt.status == AppointmentStatus.Booked
    assert appt.waiting_area_id is None
    assert _row_counts(db) == before
