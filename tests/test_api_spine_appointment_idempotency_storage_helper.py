from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.models.appointments import AppointmentCommandIdempotency
from app.services.appointment_idempotency import (
    canonical_json,
    claim_appointment_command,
    complete_appointment_command,
    hash_idempotency_key,
    sha256_canonical_json,
)


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "app" / "services" / "appointment_idempotency.py"
APPOINTMENTS_ROUTER = ROOT / "app" / "routers" / "appointments.py"
HELPER_DOC = ROOT / "orchestration" / "api_spine_appointment_idempotency_storage_helper.md"
SECRET = b"test-idempotency-secret"


def _claim(db, practice, user, *, key="idem-1", body=None, stale_after=None, now=None):
    return claim_appointment_command(
        db,
        practice_id=practice.id,
        actor_user_id=str(user.id),
        actor_role=user.role.value,
        operation_id="confirmAppointmentCreateProposal",
        route_family="create-confirm",
        raw_idempotency_key=key,
        request_body=body or {"confirmed": True, "proposal_id": "proposal-1"},
        secret=SECRET,
        stale_after=stale_after,
        now=now,
    )


def test_canonical_hash_is_stable_and_key_hash_is_hmac():
    body_a = {"b": 2, "a": {"z": 1}}
    body_b = {"a": {"z": 1}, "b": 2}

    assert canonical_json(body_a) == '{"a":{"z":1},"b":2}'
    assert sha256_canonical_json(body_a) == sha256_canonical_json(body_b)
    assert hash_idempotency_key("idem-1", SECRET) != "idem-1"
    assert hash_idempotency_key("idem-1", SECRET) != hash_idempotency_key(
        "idem-1", b"other-secret"
    )


def test_storage_helper_doc_records_scope_and_next_slice():
    text = HELPER_DOC.read_text(encoding="utf-8")

    assert "# API Spine Appointment Idempotency Storage Helper" in text
    assert "| Sprint | 129 |" in text
    assert "Storage helper foundation only; appointment routes remain unwired" in text
    assert "does not commit" in text
    assert "appointment routes still do not bind HTTP `Idempotency-Key`" in text
    assert "Recommended Sprint 130" in text
    assert "route integration preflight" in text


def test_claim_creates_in_progress_ledger_before_any_route_wiring(db, practice, gp_user):
    decision = _claim(db, practice, gp_user)

    assert decision.kind == "started"
    assert decision.record.state == "in_progress"
    assert decision.record.practice_id == practice.id
    assert decision.record.actor_user_id == str(gp_user.id)
    assert decision.record.actor_role == gp_user.role.value
    assert decision.record.request_body_hash
    assert decision.record.response_body_json is None
    assert decision.record.target_appointment_id is None


def test_completed_same_key_same_body_replays_stored_response(db, practice, gp_user):
    first = _claim(db, practice, gp_user)
    complete_appointment_command(
        db,
        first.record,
        response_status_code=201,
        response_body={"appointment_id": "appt-1", "status": "Booked"},
        result_kind="confirmed_write",
    )

    replay = _claim(db, practice, gp_user)

    assert replay.kind == "replay"
    assert replay.response_status_code == 201
    assert replay.response_body_json == {"appointment_id": "appt-1", "status": "Booked"}
    assert replay.record.id == first.record.id


def test_same_key_different_body_conflicts_without_second_row(db, practice, gp_user):
    _claim(db, practice, gp_user, body={"confirmed": True, "proposal_id": "a"})

    conflict = _claim(db, practice, gp_user, body={"confirmed": True, "proposal_id": "b"})

    assert conflict.kind == "conflict"
    assert db.query(AppointmentCommandIdempotency).count() == 1


def test_in_progress_retry_does_not_create_second_row(db, practice, gp_user):
    first = _claim(db, practice, gp_user)

    retry = _claim(db, practice, gp_user)

    assert retry.kind == "in_progress"
    assert retry.record.id == first.record.id
    assert db.query(AppointmentCommandIdempotency).count() == 1


def test_stale_in_progress_is_refused_without_second_write(db, practice, gp_user):
    first = _claim(db, practice, gp_user)
    first.record.updated_at = datetime(2026, 7, 7, 7, 0, tzinfo=timezone.utc)
    db.flush()

    stale = _claim(
        db,
        practice,
        gp_user,
        stale_after=timedelta(minutes=10),
        now=datetime(2026, 7, 7, 7, 30, tzinfo=timezone.utc),
    )

    assert stale.kind == "stale_in_progress"
    assert stale.record.id == first.record.id
    assert stale.record.state == "in_progress"
    assert db.query(AppointmentCommandIdempotency).count() == 1


def test_failed_transient_row_is_reported_without_retrying(db, practice, gp_user):
    first = _claim(db, practice, gp_user)
    first.record.state = "failed_transient"
    db.flush()

    retry = _claim(db, practice, gp_user)

    assert retry.kind == "failed_transient"
    assert retry.record.id == first.record.id
    assert db.query(AppointmentCommandIdempotency).count() == 1


def test_helper_source_keeps_routes_and_commits_out_of_scope():
    helper_text = HELPER.read_text(encoding="utf-8")
    route_text = APPOINTMENTS_ROUTER.read_text(encoding="utf-8", errors="replace")

    assert "db.commit(" not in helper_text
    assert "Appointment(" not in helper_text
    assert ".with_for_update()" in helper_text
    assert "Idempotency-Key" not in route_text
    assert "AppointmentCommandIdempotency" not in route_text
