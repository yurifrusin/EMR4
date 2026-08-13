from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

import app.routers.appointments as appointments_router
from app.config import settings
from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentCommandIdempotency,
)
from app.schemas.appointments import AppointmentCreateProposalConfirmationIn
from app.services.appointment_idempotency import claim_appointment_command
from tests.conftest import make_token


ROOT = Path(__file__).resolve().parents[1]
ROUTE_TEST_DOC = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_staff_create_confirm_route_tests.md"
)
ROUTER = ROOT / "app" / "routers" / "appointments.py"
PROPOSAL_URL = "/api/v1/appointments/proposals/create"
CONFIRM_URL = "/api/v1/appointments/proposals/create/confirm"
THURSDAY = date(2026, 6, 25)
OPERATION_ID = "confirmAppointmentCreateProposal"
ROUTE_FAMILY = "create-confirm"


@pytest.fixture(autouse=True)
def _freeze_proposal_clock(monkeypatch):
    def fixed_now(tz):
        return datetime(2026, 6, 22, 8, 0, 0, tzinfo=tz)

    monkeypatch.setattr(appointments_router, "_clinic_local_now", fixed_now)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _auth(token: str, idempotency_key: str | None = None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    if idempotency_key is not None:
        headers["Idempotency-Key"] = idempotency_key
    return headers


def _base_body(patient, practitioner, *, start="09:00:00", duration=15) -> dict:
    return {
        "patient_id": str(patient.id),
        "practitioner_id": str(practitioner.id),
        "appointment_date": THURSDAY.isoformat(),
        "start_time_local": start,
        "duration_minutes": duration,
    }


def _proposal(client, token, patient, practitioner, *, start="09:00:00", duration=15):
    resp = client.post(
        PROPOSAL_URL,
        json=_base_body(patient, practitioner, start=start, duration=duration),
        headers=_auth(token, "staff-create-proposal-key"),
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def _confirm_payload(proposal: dict) -> dict:
    payload = proposal["confirm_payload"]
    payload["confirmed"] = True
    return payload


def _canonical_request_body(payload: dict) -> dict:
    return AppointmentCreateProposalConfirmationIn(**payload).model_dump(mode="json")


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


def _ledger_count(db) -> int:
    return db.query(AppointmentCommandIdempotency).count()


def test_staff_create_confirm_route_test_contract_records_wired_scope():
    text = _read(ROUTE_TEST_DOC)

    assert "| Sprint | 131 |" in text
    assert "POST /api/v1/appointments/proposals/create/confirm" in text
    assert "confirm_create_proposal_route" in text
    assert OPERATION_ID in text
    assert ROUTE_FAMILY in text
    assert "confirm-bernie" in text
    assert "proposal-only `POST /api/v1/appointments/proposals/create`" in text


def test_router_keeps_staff_create_confirm_idempotency_surface_scoped():
    router_text = _read(ROUTER)
    route_start = router_text.index("def _idempotency_key_required_error(")
    route_end = router_text.index("def confirm_update_proposal_route(")
    update_start = route_end
    update_end = router_text.index("def propose_update_appointment(")
    create_confirm_route = router_text[route_start:route_end]
    update_route = router_text[update_start:update_end]
    bernie_start = router_text.index("def confirm_bernie_create_proposal(")
    bernie_end = router_text.index("def select_no_slot_suggestion(")
    status_start = router_text.index("def confirm_status_proposal_route(")
    status_end = router_text.index("def _a5_check_in_gate_open(")
    status_scope_end = router_text.index("def get_waiting_room(")
    status_route = router_text[status_start:status_end]
    delete_start = router_text.index("def confirm_delete_proposal_route(")
    delete_end = router_text.index("def propose_delete_appointment(")
    delete_route = router_text[delete_start:delete_end]
    non_bernie_later_routes = (
        router_text[update_end:status_start]
        + router_text[status_scope_end:delete_start]
        + router_text[delete_end:bernie_start]
        + router_text[bernie_end:]
    )

    assert "Idempotency-Key" in create_confirm_route
    assert "claim_appointment_command" in create_confirm_route
    assert "complete_appointment_command" in create_confirm_route
    assert "_STAFF_CREATE_CONFIRM_OPERATION_ID" in create_confirm_route
    assert "_STAFF_CREATE_CONFIRM_ROUTE_FAMILY" in create_confirm_route
    assert "Idempotency-Key" in status_route
    assert "compose_product_status_confirm(" in status_route
    assert "claim_appointment_command(" not in status_route
    assert "complete_appointment_command(" not in status_route
    assert "Idempotency-Key" in update_route
    assert "_UPDATE_CONFIRM_ROUTE_FAMILY" in update_route
    assert "Idempotency-Key" in delete_route
    assert "_DELETE_CONFIRM_ROUTE_FAMILY" in delete_route
    # Proposal handlers now have Idempotency-Key syntactic validation
    assert "claim_appointment_command(" not in non_bernie_later_routes
    assert "complete_appointment_command(" not in non_bernie_later_routes


def test_missing_idempotency_key_blocks_before_writes(client, db, gp_user, patient, practitioner):
    token = make_token(gp_user)
    payload = _confirm_payload(_proposal(client, token, patient, practitioner))
    before_appts = db.query(Appointment).count()
    before_audits = db.query(AppointmentAuditLog).count()

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token))

    assert resp.status_code == 400, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_required"
    assert db.query(Appointment).count() == before_appts
    assert db.query(AppointmentAuditLog).count() == before_audits
    assert _ledger_count(db) == 0


def test_first_confirmed_create_writes_appointment_audit_and_ledger(
    client, db, gp_user, patient, practitioner
):
    token = make_token(gp_user)
    payload = _confirm_payload(_proposal(client, token, patient, practitioner))
    before_appts = db.query(Appointment).count()
    before_audits = db.query(AppointmentAuditLog).count()

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "create-confirm-1"))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is True
    assert data["autonomy_tier"] == "confirmed_write"
    assert db.query(Appointment).count() == before_appts + 1
    assert db.query(AppointmentAuditLog).count() == before_audits + 1
    ledger = db.query(AppointmentCommandIdempotency).one()
    assert ledger.state == "completed"
    assert ledger.operation_id == OPERATION_ID
    assert ledger.route_family == ROUTE_FAMILY
    assert ledger.response_status_code == 200
    assert ledger.response_body_json["appointment"]["id"] == data["appointment"]["id"]
    assert ledger.target_appointment_id is not None


def test_same_key_same_body_replays_stored_response_without_second_write(
    client, db, gp_user, patient, practitioner
):
    token = make_token(gp_user)
    payload = _confirm_payload(_proposal(client, token, patient, practitioner))

    first = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "replay-key"))
    assert first.status_code == 200, first.text
    after_first_appts = db.query(Appointment).count()
    after_first_audits = db.query(AppointmentAuditLog).count()

    second = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "replay-key"))

    assert second.status_code == 200, second.text
    assert second.json() == first.json()
    assert db.query(Appointment).count() == after_first_appts
    assert db.query(AppointmentAuditLog).count() == after_first_audits
    assert _ledger_count(db) == 1


def test_same_key_different_body_conflicts_without_second_write(
    client, db, gp_user, patient, practitioner
):
    token = make_token(gp_user)
    first_payload = _confirm_payload(_proposal(client, token, patient, practitioner))
    first = client.post(CONFIRM_URL, json=first_payload, headers=_auth(token, "conflict-key"))
    assert first.status_code == 200, first.text
    after_first_appts = db.query(Appointment).count()
    after_first_audits = db.query(AppointmentAuditLog).count()

    second_payload = _confirm_payload(
        _proposal(client, token, patient, practitioner, start="09:30:00")
    )
    second = client.post(CONFIRM_URL, json=second_payload, headers=_auth(token, "conflict-key"))

    assert second.status_code == 409, second.text
    assert second.json()["detail"]["code"] == "idempotency_key_conflict"
    assert db.query(Appointment).count() == after_first_appts
    assert db.query(AppointmentAuditLog).count() == after_first_audits
    assert _ledger_count(db) == 1


def test_active_in_progress_key_fails_closed_without_second_write(
    client, db, gp_user, patient, practitioner
):
    token = make_token(gp_user)
    payload = _confirm_payload(_proposal(client, token, patient, practitioner))
    claim = _preclaim(db, gp_user, payload, key="in-progress-key")
    assert claim.kind == "started"
    before_appts = db.query(Appointment).count()
    before_audits = db.query(AppointmentAuditLog).count()

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "in-progress-key"))

    assert resp.status_code == 409, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_in_progress"
    assert db.query(Appointment).count() == before_appts
    assert db.query(AppointmentAuditLog).count() == before_audits
    assert _ledger_count(db) == 1


def test_stale_in_progress_key_fails_closed_without_second_write(
    client, db, gp_user, patient, practitioner
):
    token = make_token(gp_user)
    payload = _confirm_payload(_proposal(client, token, patient, practitioner))
    claim = _preclaim(db, gp_user, payload, key="stale-key")
    claim.record.updated_at = datetime(2000, 1, 1, tzinfo=timezone.utc)
    db.flush()
    before_appts = db.query(Appointment).count()
    before_audits = db.query(AppointmentAuditLog).count()

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "stale-key"))

    assert resp.status_code == 409, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_stale_in_progress"
    assert db.query(Appointment).count() == before_appts
    assert db.query(AppointmentAuditLog).count() == before_audits
    assert _ledger_count(db) == 1


def test_failed_transient_key_fails_closed_without_second_write(
    client, db, gp_user, patient, practitioner
):
    token = make_token(gp_user)
    payload = _confirm_payload(_proposal(client, token, patient, practitioner))
    claim = _preclaim(db, gp_user, payload, key="failed-transient-key")
    claim.record.state = "failed_transient"
    db.flush()
    before_appts = db.query(Appointment).count()
    before_audits = db.query(AppointmentAuditLog).count()

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "failed-transient-key"))

    assert resp.status_code == 503, resp.text
    assert resp.json()["detail"]["code"] == "idempotency_key_failed_transient"
    assert db.query(Appointment).count() == before_appts
    assert db.query(AppointmentAuditLog).count() == before_audits
    assert _ledger_count(db) == 1


def test_business_rule_failure_after_claim_removes_or_rolls_back_claim(
    client, db, gp_user, patient, practitioner
):
    token = make_token(gp_user)
    payload = _confirm_payload(_proposal(client, token, patient, practitioner))
    payload["create_proposal"]["command"]["duration_minutes"] = 30
    before_appts = db.query(Appointment).count()
    before_audits = db.query(AppointmentAuditLog).count()

    resp = client.post(CONFIRM_URL, json=payload, headers=_auth(token, "business-block-key"))

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    assert db.query(Appointment).count() == before_appts
    assert db.query(AppointmentAuditLog).count() == before_audits
    assert _ledger_count(db) == 0


def test_proposal_only_create_route_remains_out_of_scope(client, db, gp_user, patient, practitioner):
    token = make_token(gp_user)
    before_appts = db.query(Appointment).count()

    resp = client.post(
        PROPOSAL_URL,
        json=_base_body(patient, practitioner),
        headers=_auth(token, "proposal-only-create-key"),
    )

    assert resp.status_code == 200, resp.text
    assert resp.json()["confirm_endpoint"] == CONFIRM_URL
    assert db.query(Appointment).count() == before_appts
    assert _ledger_count(db) == 0
