from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.bernie_sessions import BernieBookingSession, BernieSessionEventRow
from app.services.bernie import (
    BernieSessionEventRejectionCode,
    BernieSessionEventType,
    BernieSessionState,
    DatabaseBernieSessionStore,
)


SECRET = settings.secret_key.encode("utf-8")


def _store(db, practice_id) -> DatabaseBernieSessionStore:
    return DatabaseBernieSessionStore(db, practice_id=practice_id, secret=SECRET)


def test_durable_session_recovers_across_fresh_database_session(
    engine,
    db,
    practice,
    gp_user,
) -> None:
    created = _store(db, practice.id).create_session(
        practice_id=practice.id,
        user_id=gp_user.id,
        surface_id="stage2-restart",
        request_reference_date=datetime(2026, 7, 19, tzinfo=timezone.utc).date(),
    )
    appended = _store(db, practice.id).append_client_event(
        session_id=created.session_id,
        practice_id=practice.id,
        user_id=gp_user.id,
        surface_id="stage2-restart",
        event_type=BernieSessionEventType.staff_instruction,
        expected_revision=0,
        event_id="restart-event-1",
        idempotency_key="restart-idem-1",
        payload={"intent_ref": "synthetic-intent-1"},
    )
    assert appended.accepted is True
    db.commit()

    SessionFactory = sessionmaker(bind=engine)
    with SessionFactory() as restarted_db:
        recovered = _store(restarted_db, practice.id).get_session(created.session_id)

    assert recovered is not None
    assert recovered.state is BernieSessionState.recognition
    assert recovered.revision == 1
    assert recovered.last_event_id == "restart-event-1"
    assert [event.event_id for event in recovered.events] == ["restart-event-1"]
    assert recovered.events[0].idempotency_key is None


def test_event_identity_is_hashed_and_replay_survives_restart(
    engine,
    db,
    practice,
    gp_user,
) -> None:
    created = _store(db, practice.id).create_session(
        practice_id=practice.id,
        user_id=gp_user.id,
        surface_id="stage2-event-replay",
    )
    first = _store(db, practice.id).append_client_event(
        session_id=created.session_id,
        practice_id=practice.id,
        user_id=gp_user.id,
        surface_id="stage2-event-replay",
        event_type=BernieSessionEventType.staff_instruction,
        expected_revision=0,
        event_id="event-replay-1",
        idempotency_key="raw-key-must-not-persist",
        payload={"intent_ref": "synthetic-intent-2"},
    )
    assert first.accepted is True
    db.commit()

    row = db.query(BernieSessionEventRow).one()
    assert row.idempotency_key_hash
    assert row.idempotency_key_hash != "raw-key-must-not-persist"
    assert "raw-key-must-not-persist" not in str(row.payload)

    SessionFactory = sessionmaker(bind=engine)
    with SessionFactory() as restarted_db:
        replay = _store(restarted_db, practice.id).append_client_event(
            session_id=created.session_id,
            practice_id=practice.id,
            user_id=gp_user.id,
            surface_id="stage2-event-replay",
            event_type=BernieSessionEventType.staff_instruction,
            expected_revision=0,
            event_id="different-client-event-id-is-ignored-for-same-idem",
            idempotency_key="raw-key-must-not-persist",
            payload={"intent_ref": "synthetic-intent-2"},
        )
        restarted_db.commit()

    assert replay.accepted is True
    assert replay.session is not None
    assert replay.session.revision == 1
    assert db.query(BernieSessionEventRow).count() == 1


def test_payload_guards_reject_phi_keys_and_oversized_structured_evidence(
    db,
    practice,
    gp_user,
) -> None:
    created = _store(db, practice.id).create_session(
        practice_id=practice.id,
        user_id=gp_user.id,
        surface_id="stage2-payload-guards",
    )
    phi = _store(db, practice.id).append_client_event(
        session_id=created.session_id,
        practice_id=practice.id,
        user_id=gp_user.id,
        surface_id="stage2-payload-guards",
        event_type=BernieSessionEventType.staff_instruction,
        expected_revision=0,
        payload={"raw_instruction": "synthetic name"},
    )
    oversized = _store(db, practice.id).append_client_event(
        session_id=created.session_id,
        practice_id=practice.id,
        user_id=gp_user.id,
        surface_id="stage2-payload-guards",
        event_type=BernieSessionEventType.staff_instruction,
        expected_revision=0,
        payload={"intent_ref": "x" * 20_000},
    )
    unstructured = _store(db, practice.id).append_client_event(
        session_id=created.session_id,
        practice_id=practice.id,
        user_id=gp_user.id,
        surface_id="stage2-payload-guards",
        event_type=BernieSessionEventType.staff_instruction,
        expected_revision=0,
        payload={"intent_ref": "synthetic free text with spaces"},
    )
    unknown_field = _store(db, practice.id).append_client_event(
        session_id=created.session_id,
        practice_id=practice.id,
        user_id=gp_user.id,
        surface_id="stage2-payload-guards",
        event_type=BernieSessionEventType.staff_instruction,
        expected_revision=0,
        payload={"intent_ref": "synthetic-intent-3", "comment": "hidden"},
    )

    assert phi.code is BernieSessionEventRejectionCode.phi_payload_not_allowed
    assert oversized.code is BernieSessionEventRejectionCode.event_payload_too_large
    assert unstructured.code is BernieSessionEventRejectionCode.event_payload_not_structured
    assert unknown_field.code is BernieSessionEventRejectionCode.event_payload_not_structured
    assert db.query(BernieSessionEventRow).count() == 0


def test_concurrent_expected_revision_accepts_exactly_one_transition(
    engine,
    db,
    practice,
    gp_user,
) -> None:
    created = _store(db, practice.id).create_session(
        practice_id=practice.id,
        user_id=gp_user.id,
        surface_id="stage2-concurrency",
    )
    practice_id = practice.id
    user_id = gp_user.id
    session_id = created.session_id
    db.commit()
    SessionFactory = sessionmaker(bind=engine)

    def append(event_id: str):
        with SessionFactory() as worker_db:
            result = _store(worker_db, practice_id).append_client_event(
                session_id=session_id,
                practice_id=practice_id,
                user_id=user_id,
                surface_id="stage2-concurrency",
                event_type=BernieSessionEventType.staff_instruction,
                expected_revision=0,
                event_id=event_id,
                payload={"intent_ref": event_id},
            )
            if result.accepted:
                worker_db.commit()
            else:
                worker_db.rollback()
            return result.accepted, result.code

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(append, ("concurrent-a", "concurrent-b")))

    assert [accepted for accepted, _ in outcomes].count(True) == 1
    rejected_codes = [code for accepted, code in outcomes if not accepted]
    assert rejected_codes == [BernieSessionEventRejectionCode.stale_session_revision]
    db.expire_all()
    persisted = _store(db, practice_id).get_session(session_id)
    assert persisted is not None
    assert persisted.revision == 1
    assert len(persisted.events) == 1


def test_retention_windows_and_bounded_purge_remove_only_session_detail(
    db,
    practice,
    gp_user,
) -> None:
    now = datetime(2026, 7, 19, 9, 0, tzinfo=timezone.utc)
    incomplete = _store(db, practice.id).create_session(
        practice_id=practice.id,
        user_id=gp_user.id,
        surface_id="stage2-retention-incomplete",
        now=now,
    )
    incomplete_row = db.query(BernieBookingSession).filter_by(
        session_id=incomplete.session_id
    ).one()
    assert incomplete_row.expires_at == now + timedelta(hours=24)

    completed = _store(db, practice.id).create_session(
        practice_id=practice.id,
        user_id=gp_user.id,
        surface_id="stage2-retention-completed",
        now=now,
    )
    completed_row = db.query(BernieBookingSession).filter_by(
        session_id=completed.session_id
    ).one()
    completed_row.state = BernieSessionState.confirmation.value
    completed_row.revision = 1
    db.flush()
    outcome_at = now + timedelta(hours=1)
    outcome = _store(db, practice.id).append_server_outcome_event(
        session_id=completed.session_id,
        event_type=BernieSessionEventType.confirmation_outcome,
        target_state=BernieSessionState.confirmed,
        expected_revision=1,
        payload={"result": "confirmed", "confirmed": True},
        occurred_at=outcome_at,
    )
    assert outcome.accepted is True
    assert completed_row.expires_at == outcome_at + timedelta(days=30)

    expired = _store(db, practice.id).create_session(
        practice_id=practice.id,
        user_id=gp_user.id,
        surface_id="stage2-retention-expired",
        now=now - timedelta(hours=25),
    )
    expired_event = _store(db, practice.id).append_client_event(
        session_id=expired.session_id,
        practice_id=practice.id,
        user_id=gp_user.id,
        surface_id="stage2-retention-expired",
        event_type=BernieSessionEventType.staff_instruction,
        expected_revision=0,
        event_id="expired-event",
        payload={"intent_ref": "expired-synthetic"},
        occurred_at=now - timedelta(hours=25),
    )
    assert expired_event.accepted is True

    purged = _store(db, practice.id).purge_expired_sessions(now=now, limit=1)
    db.commit()

    assert purged == 1
    assert db.query(BernieBookingSession).filter_by(session_id=expired.session_id).count() == 0
    assert db.query(BernieSessionEventRow).filter_by(session_id=expired.session_id).count() == 0
    assert db.query(BernieBookingSession).filter_by(session_id=incomplete.session_id).count() == 1
    assert db.query(BernieBookingSession).filter_by(session_id=completed.session_id).count() == 1
