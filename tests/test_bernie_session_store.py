from datetime import date
import uuid

from app.services.bernie import (
    BernieSessionEventRejectionCode,
    BernieSessionEventType,
    BernieSessionState,
    InMemoryBernieSessionStore,
    build_session_confirmation_binding,
)


def _ids():
    return uuid.uuid4(), uuid.uuid4(), "diary-main"


def _store_with_session():
    practice_id, user_id, surface_id = _ids()
    store = InMemoryBernieSessionStore()
    session = store.create_session(
        practice_id=practice_id,
        user_id=user_id,
        surface_id=surface_id,
        request_reference_date=date(2026, 7, 3),
        session_id="session-1",
    )
    return store, session, practice_id, user_id, surface_id


def test_append_event_advances_revision_and_state_once():
    store, session, practice_id, user_id, surface_id = _store_with_session()

    result = store.append_client_event(
        session_id=session.session_id,
        practice_id=practice_id,
        user_id=user_id,
        surface_id=surface_id,
        event_type=BernieSessionEventType.staff_instruction,
        expected_revision=0,
        event_id="event-1",
        payload={"intent_ref": "intent-1"},
    )

    assert result.accepted is True
    assert result.session is not None
    assert result.session.revision == 1
    assert result.session.state is BernieSessionState.recognition
    assert result.session.turn_count == 1
    assert result.session.last_event_id == "event-1"


def test_stale_revision_rejects_without_mutation():
    store, session, practice_id, user_id, surface_id = _store_with_session()
    first = store.append_client_event(
        session_id=session.session_id,
        practice_id=practice_id,
        user_id=user_id,
        surface_id=surface_id,
        event_type=BernieSessionEventType.staff_instruction,
        expected_revision=0,
        event_id="event-1",
        payload={"intent_ref": "intent-1"},
    )
    assert first.accepted is True

    stale = store.append_client_event(
        session_id=session.session_id,
        practice_id=practice_id,
        user_id=user_id,
        surface_id=surface_id,
        event_type=BernieSessionEventType.staff_instruction,
        expected_revision=0,
        event_id="event-2",
        payload={"intent_ref": "intent-2"},
    )

    current = store.get_session(session.session_id)
    assert stale.accepted is False
    assert stale.code is BernieSessionEventRejectionCode.stale_session_revision
    assert current is not None
    assert current.revision == 1
    assert [event.event_id for event in current.events] == ["event-1"]


def test_future_revision_rejects_without_mutation():
    store, session, practice_id, user_id, surface_id = _store_with_session()

    result = store.append_client_event(
        session_id=session.session_id,
        practice_id=practice_id,
        user_id=user_id,
        surface_id=surface_id,
        event_type=BernieSessionEventType.staff_instruction,
        expected_revision=2,
        event_id="event-1",
        payload={"intent_ref": "intent-1"},
    )

    current = store.get_session(session.session_id)
    assert result.accepted is False
    assert result.code is BernieSessionEventRejectionCode.future_session_revision
    assert current is not None
    assert current.revision == 0
    assert current.events == []


def test_idempotent_replay_returns_original_result_but_conflicting_replay_rejects():
    store, session, practice_id, user_id, surface_id = _store_with_session()
    first = store.append_client_event(
        session_id=session.session_id,
        practice_id=practice_id,
        user_id=user_id,
        surface_id=surface_id,
        event_type=BernieSessionEventType.staff_instruction,
        expected_revision=0,
        event_id="event-1",
        idempotency_key="idem-1",
        payload={"intent_ref": "intent-1"},
    )

    replay = store.append_client_event(
        session_id=session.session_id,
        practice_id=practice_id,
        user_id=user_id,
        surface_id=surface_id,
        event_type=BernieSessionEventType.staff_instruction,
        expected_revision=0,
        event_id="event-1",
        idempotency_key="idem-1",
        payload={"intent_ref": "intent-1"},
    )
    conflict = store.append_client_event(
        session_id=session.session_id,
        practice_id=practice_id,
        user_id=user_id,
        surface_id=surface_id,
        event_type=BernieSessionEventType.staff_instruction,
        expected_revision=0,
        event_id="event-1",
        idempotency_key="idem-1",
        payload={"intent_ref": "changed"},
    )

    current = store.get_session(session.session_id)
    assert first.accepted is True
    assert replay.accepted is True
    assert replay.session == first.session
    assert conflict.accepted is False
    assert conflict.code is BernieSessionEventRejectionCode.idempotency_conflict
    assert current is not None
    assert len(current.events) == 1


def test_cross_owner_and_wrong_surface_reject_without_mutation():
    store, session, practice_id, user_id, surface_id = _store_with_session()

    for wrong_practice, wrong_user, wrong_surface in (
        (uuid.uuid4(), user_id, surface_id),
        (practice_id, uuid.uuid4(), surface_id),
        (practice_id, user_id, "other-surface"),
    ):
        result = store.append_client_event(
            session_id=session.session_id,
            practice_id=wrong_practice,
            user_id=wrong_user,
            surface_id=wrong_surface,
            event_type=BernieSessionEventType.staff_instruction,
            expected_revision=0,
            payload={"intent_ref": "intent-1"},
        )
        assert result.accepted is False
        assert result.code is BernieSessionEventRejectionCode.session_owner_mismatch

    current = store.get_session(session.session_id)
    assert current is not None
    assert current.revision == 0
    assert current.events == []


def test_transient_state_client_event_rejects():
    store, session, practice_id, user_id, surface_id = _store_with_session()
    entered_recognition = store.append_client_event(
        session_id=session.session_id,
        practice_id=practice_id,
        user_id=user_id,
        surface_id=surface_id,
        event_type=BernieSessionEventType.staff_instruction,
        expected_revision=0,
        payload={"intent_ref": "intent-1"},
    )
    assert entered_recognition.accepted is True

    result = store.append_client_event(
        session_id=session.session_id,
        practice_id=practice_id,
        user_id=user_id,
        surface_id=surface_id,
        event_type=BernieSessionEventType.diary_navigated,
        expected_revision=1,
        payload={"visible_diary_date": "2026-07-04"},
    )

    assert result.accepted is False
    assert result.code is BernieSessionEventRejectionCode.event_not_allowed_in_transient_state


def test_diary_navigation_marks_candidate_and_proposal_evidence_stale():
    store, session, practice_id, user_id, surface_id = _store_with_session()
    store._sessions[session.session_id] = session.model_copy(update={
        "state": BernieSessionState.proposal_preview,
        "revision": 7,
        "candidate_freshness_ids": ["candidate-a"],
        "staged_proposal_freshness_id": "proposal-a",
    })

    result = store.append_client_event(
        session_id=session.session_id,
        practice_id=practice_id,
        user_id=user_id,
        surface_id=surface_id,
        event_type=BernieSessionEventType.diary_navigated,
        expected_revision=7,
        payload={"visible_diary_date": "2026-07-04"},
    )

    assert result.accepted is True
    assert result.session is not None
    assert result.session.revision == 8
    assert result.session.state is BernieSessionState.proposal_preview
    assert result.session.candidate_freshness_ids == []
    assert result.session.staged_proposal_freshness_id is None
    assert result.session.stale_reason_code == "diary_context_changed"


def test_phi_heavy_payload_key_rejects_without_event_append():
    store, session, practice_id, user_id, surface_id = _store_with_session()

    result = store.append_client_event(
        session_id=session.session_id,
        practice_id=practice_id,
        user_id=user_id,
        surface_id=surface_id,
        event_type=BernieSessionEventType.staff_instruction,
        expected_revision=0,
        payload={"raw_instruction": "Make an appointment for Margaret Thompson"},
    )

    current = store.get_session(session.session_id)
    assert result.accepted is False
    assert result.code is BernieSessionEventRejectionCode.phi_payload_not_allowed
    assert current is not None
    assert current.revision == 0
    assert current.events == []


def test_session_confirmation_binding_is_phi_minimised_and_session_bound():
    store, session, practice_id, user_id, surface_id = _store_with_session()
    session = session.model_copy(update={
        "patient_id": uuid.uuid4(),
        "practitioner_id": uuid.uuid4(),
        "revision": 4,
    })

    binding = build_session_confirmation_binding(
        session,
        candidate_freshness_id="candidate-a",
        proposal_freshness_id="proposal-a",
        appointment_date=date(2026, 7, 4),
        start_time_local="15:00:00",
        duration_minutes=15,
    )

    assert binding["practice_id"] == str(practice_id)
    assert binding["staff_user_id"] == str(user_id)
    assert binding["surface_id"] == surface_id
    assert binding["session_id"] == "session-1"
    assert binding["session_revision"] == 4
    assert binding["reference_date"] == "2026-07-03"
    assert binding["candidate_freshness_id"] == "candidate-a"
    assert binding["proposal_freshness_id"] == "proposal-a"
    assert binding["appointment_date"] == "2026-07-04"
    assert "patient_name" not in binding
    assert "medicare" not in binding
