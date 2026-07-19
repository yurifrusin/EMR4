import json
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from threading import Barrier

import pytest
from sqlalchemy.orm import sessionmaker
from starlette.responses import Response

import app.routers.appointments as appointments_router
from app.models.appointments import (
    Appointment,
    AppointmentAuditLog,
    AppointmentCommandIdempotency,
)
from app.models.bernie_sessions import BernieBookingSession, BernieSessionEventRow
from app.models.tenancy import User
from app.services.bernie import DatabaseBernieSessionStore
from tests.conftest import make_token
from tests.test_api_spine_bernie_create_confirm_idempotency_route_contract import (
    _auth,
    _bound_confirm_payload,
)


CONFIRM_URL = "/api/v1/appointments/proposals/create/confirm-bernie"
SECRET = appointments_router._staff_create_confirm_idempotency_secret()


@pytest.fixture(autouse=True)
def _freeze_bernie_contract_clock(monkeypatch):
    def fixed_now(tz):
        return datetime(2026, 6, 22, 8, 0, 0, tzinfo=tz)

    monkeypatch.setattr(appointments_router, "_clinic_local_now", fixed_now)


def _database_counts(db) -> tuple[int, int, int]:
    return (
        db.query(Appointment).count(),
        db.query(AppointmentAuditLog).count(),
        db.query(AppointmentCommandIdempotency).count(),
    )


def _session_event_count(db, *, practice_id, session_id: str) -> int:
    return db.query(BernieSessionEventRow).filter(
        BernieSessionEventRow.practice_id == practice_id,
        BernieSessionEventRow.session_id == session_id,
    ).count()


def _invoke_confirmation(SessionFactory, *, user_id, payload: dict, key: str):
    with SessionFactory() as worker_db:
        current_user = worker_db.query(User).filter(User.id == user_id).one()
        return appointments_router.confirm_bernie_create_proposal(
            body=deepcopy(payload),
            idempotency_key=key,
            db=worker_db,
            current_user=current_user,
        )


def _response_tuple(result) -> tuple[int, dict]:
    if isinstance(result, Response):
        return result.status_code, json.loads(result.body)
    return 200, result.model_dump(mode="json")


def _prepare_bound_confirmation(
    client,
    db,
    gp_user,
    practitioner,
    patient,
    *,
    surface_id: str,
) -> tuple[dict, object, object, str]:
    token = make_token(gp_user)
    payload = _bound_confirm_payload(
        client,
        db,
        token,
        practitioner,
        patient,
        surface_id=surface_id,
    )
    practice_id = gp_user.practice_id
    user_id = gp_user.id
    session_id = payload["session_binding"]["session_id"]
    db.commit()
    return payload, practice_id, user_id, session_id


def test_concurrent_same_key_confirmation_commits_exactly_one_correlated_chain(
    engine,
    client,
    db,
    gp_user,
    practitioner,
    patient,
    schedule,
) -> None:
    payload, practice_id, user_id, session_id = _prepare_bound_confirmation(
        client,
        db,
        gp_user,
        practitioner,
        patient,
        surface_id="stage2-confirm-race",
    )
    before_rows = _database_counts(db)
    before_events = _session_event_count(
        db,
        practice_id=practice_id,
        session_id=session_id,
    )
    db.commit()
    SessionFactory = sessionmaker(bind=engine)
    start = Barrier(2)

    def confirm():
        start.wait(timeout=10)
        return _response_tuple(
            _invoke_confirmation(
                SessionFactory,
                user_id=user_id,
                payload=payload,
                key="stage2-same-key-race",
            )
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(lambda _: confirm(), range(2)))

    assert [status for status, _ in outcomes] == [200, 200]
    assert outcomes[0][1] == outcomes[1][1]
    db.expire_all()
    assert _database_counts(db) == (
        before_rows[0] + 1,
        before_rows[1] + 1,
        before_rows[2] + 1,
    )
    assert _session_event_count(
        db,
        practice_id=practice_id,
        session_id=session_id,
    ) == before_events + 2

    ledger = db.query(AppointmentCommandIdempotency).one()
    audit = db.query(AppointmentAuditLog).filter(
        AppointmentAuditLog.id == ledger.audit_log_id,
    ).one()
    assert ledger.state == "completed"
    assert audit.command_id == ledger.id
    assert audit.appointment_id == ledger.target_appointment_id
    assert ledger.bernie_session_id == session_id
    assert audit.bernie_session_id == session_id
    receipt = outcomes[0][1]["confirmation_receipt"]
    assert receipt["correlation_id"] == str(ledger.id)
    assert receipt["audit_event_id"] == str(audit.id)
    assert receipt["session_id"] == session_id
    assert db.query(BernieSessionEventRow).filter(
        BernieSessionEventRow.session_id == session_id,
        BernieSessionEventRow.event_type == "confirmation_outcome",
    ).count() == 1


def test_injected_precommit_failure_rolls_back_every_effect_then_retry_succeeds_once(
    engine,
    client,
    db,
    gp_user,
    practitioner,
    patient,
    schedule,
    monkeypatch,
) -> None:
    payload, practice_id, user_id, session_id = _prepare_bound_confirmation(
        client,
        db,
        gp_user,
        practitioner,
        patient,
        surface_id="stage2-precommit-failure",
    )
    before_rows = _database_counts(db)
    before_events = _session_event_count(
        db,
        practice_id=practice_id,
        session_id=session_id,
    )
    session_before = DatabaseBernieSessionStore(
        db,
        practice_id=practice_id,
        secret=SECRET,
    ).get_session(session_id)
    assert session_before is not None
    db.commit()
    SessionFactory = sessionmaker(bind=engine)
    original_complete = appointments_router.complete_appointment_command

    def fail_before_commit(*args, **kwargs):
        raise RuntimeError("injected Stage 2 pre-commit failure")

    with monkeypatch.context() as scoped_patch:
        scoped_patch.setattr(
            appointments_router,
            "complete_appointment_command",
            fail_before_commit,
        )
        with pytest.raises(RuntimeError, match="injected Stage 2 pre-commit failure"):
            _invoke_confirmation(
                SessionFactory,
                user_id=user_id,
                payload=payload,
                key="stage2-precommit-key",
            )

    assert appointments_router.complete_appointment_command is original_complete
    db.expire_all()
    assert _database_counts(db) == before_rows
    assert _session_event_count(
        db,
        practice_id=practice_id,
        session_id=session_id,
    ) == before_events
    recovered = DatabaseBernieSessionStore(
        db,
        practice_id=practice_id,
        secret=SECRET,
    ).get_session(session_id)
    assert recovered is not None
    assert recovered.state == session_before.state
    assert recovered.revision == session_before.revision
    db.commit()

    status_code, response = _response_tuple(
        _invoke_confirmation(
            SessionFactory,
            user_id=user_id,
            payload=payload,
            key="stage2-precommit-key",
        )
    )

    assert status_code == 200
    assert response["safe"] is True
    db.expire_all()
    assert _database_counts(db) == (
        before_rows[0] + 1,
        before_rows[1] + 1,
        before_rows[2] + 1,
    )
    assert _session_event_count(
        db,
        practice_id=practice_id,
        session_id=session_id,
    ) == before_events + 2


def test_postcommit_replay_from_fresh_database_session_returns_stored_receipt(
    engine,
    client,
    db,
    gp_user,
    practitioner,
    patient,
    schedule,
) -> None:
    payload, practice_id, user_id, session_id = _prepare_bound_confirmation(
        client,
        db,
        gp_user,
        practitioner,
        patient,
        surface_id="stage2-postcommit-replay",
    )
    db.commit()
    SessionFactory = sessionmaker(bind=engine)

    first_status, first_body = _response_tuple(
        _invoke_confirmation(
            SessionFactory,
            user_id=user_id,
            payload=payload,
            key="stage2-postcommit-key",
        )
    )
    db.expire_all()
    after_first_rows = _database_counts(db)
    after_first_events = _session_event_count(
        db,
        practice_id=practice_id,
        session_id=session_id,
    )
    stored_response = db.query(AppointmentCommandIdempotency).one().response_body_json
    db.commit()

    replay_status, replay_body = _response_tuple(
        _invoke_confirmation(
            SessionFactory,
            user_id=user_id,
            payload=payload,
            key="stage2-postcommit-key",
        )
    )

    assert first_status == replay_status == 200
    assert first_body == replay_body == stored_response
    db.expire_all()
    assert _database_counts(db) == after_first_rows
    assert _session_event_count(
        db,
        practice_id=practice_id,
        session_id=session_id,
    ) == after_first_events


def test_expired_session_purge_preserves_minimal_committed_correlation_chain(
    engine,
    client,
    db,
    gp_user,
    practitioner,
    patient,
    schedule,
) -> None:
    payload, practice_id, user_id, session_id = _prepare_bound_confirmation(
        client,
        db,
        gp_user,
        practitioner,
        patient,
        surface_id="stage2-purge-correlation",
    )
    db.commit()
    SessionFactory = sessionmaker(bind=engine)
    status_code, response = _response_tuple(
        _invoke_confirmation(
            SessionFactory,
            user_id=user_id,
            payload=payload,
            key="stage2-purge-correlation-key",
        )
    )
    assert status_code == 200

    db.expire_all()
    session_row = db.query(BernieBookingSession).filter_by(session_id=session_id).one()
    session_row.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db.commit()
    purged = DatabaseBernieSessionStore(
        db,
        practice_id=practice_id,
        secret=SECRET,
    ).purge_expired_sessions(now=datetime.now(timezone.utc), limit=10)
    db.commit()

    assert purged == 1
    assert db.query(BernieBookingSession).filter_by(session_id=session_id).count() == 0
    assert db.query(BernieSessionEventRow).filter_by(session_id=session_id).count() == 0
    assert db.query(Appointment).count() == 1
    assert db.query(AppointmentAuditLog).count() == 1
    ledger = db.query(AppointmentCommandIdempotency).one()
    audit = db.query(AppointmentAuditLog).one()
    assert ledger.state == "completed"
    assert ledger.bernie_session_id == audit.bernie_session_id == session_id
    assert ledger.audit_log_id == audit.id
    assert audit.command_id == ledger.id
    assert ledger.response_body_json == response
    assert ledger.response_body_json["confirmation_receipt"]["session_id"] == session_id
