"""Selected authored-synthetic same-ID staff move cases for an owned PG capsule.

Collection is only through the exact isolated Stage 1 adapter and node IDs.
This module does not create a database, app, listener, provider, or grant.
"""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.appointments import (
    Appointment, AppointmentAuditLog, AppointmentCommandIdempotency,
    AppointmentStatus,
)
from app.models.diary_events import DiaryCommittedEvent
from app.models.tenancy import User, UserCapabilityGrant, UserRole
from app.services.auth_service import create_access_token


MOVE = "/api/v1/appointments/proposals/move-time/{}"
CONFIRM = "/api/v1/appointments/proposals/update/confirm"


def _headers(user, key=None):
    token = create_access_token({
        "sub": str(user.id), "practice_id": str(user.practice_id),
        "role": user.role.value,
    })
    headers = {"Authorization": f"Bearer {token}"}
    if key is not None:
        headers["Idempotency-Key"] = key
    return headers


def _intent(row, user, *, clock="11:00", day=None):
    return {
        "schema_version": "appointment.move_time_intent.v1",
        "tenant_id": str(user.practice_id), "actor_id": str(user.id),
        "role": "reception", "source_appointment_id": str(row.id),
        "source_state_version": row.appointment_state_version,
        "source_revision": row.appointment_state_version,
        "target_date": (day or row.appointment_date).isoformat(),
        "target_start_local": clock, "authority": "proposal_only",
    }


def _proposal(client, row, user, *, key="g4-proposal-a", intent=None):
    response = client.post(MOVE.format(row.id), json=intent or _intent(row, user),
                           headers=_headers(user, key))
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["safe"] is True and data["requires_confirmation"] is True
    assert data["move_binding"]["appointment_id"] == str(row.id)
    assert data["move_binding"]["source_state_version"] == row.appointment_state_version
    assert data["move_binding"]["source_revision"] == row.appointment_state_version
    assert data["signed_confirmation_evidence_required"] is True
    assert data["signed_confirmation_evidence"]
    payload = deepcopy(data["confirm_payload"])
    assert payload["update_proposal"]["move_binding"] == data["move_binding"]
    payload["confirmed"] = True
    return data, payload


def _snapshot(db, practice_id):
    with Session(bind=db.get_bind()) as observer:
        rows = observer.query(Appointment).filter_by(practice_id=practice_id).all()
        audits = observer.query(AppointmentAuditLog).filter_by(practice_id=practice_id).all()
        commands = observer.query(AppointmentCommandIdempotency).filter_by(practice_id=practice_id).all()
        events = observer.query(DiaryCommittedEvent).filter_by(practice_id=practice_id).all()
        return {
            "rows": [(r.id, r.appointment_state_version, r.start_time, r.appointment_date,
                      r.start_time_local, r.status, r.patient_id,
                      r.patient_name_provisional, r.practitioner_id, r.appointment_type_id,
                      r.location_id, r.duration_minutes, r.reason, r.notes) for r in rows],
            "audits": [(r.id, r.appointment_id, r.command_id, r.action) for r in audits],
            "commands": [(r.id, r.state, r.target_appointment_id, r.audit_log_id,
                          r.request_body_hash, r.response_body_hash) for r in commands],
            "events": [(r.id, r.appointment_id, r.command_id, r.audit_log_id,
                        r.event_type, r.aggregate_revision) for r in events],
        }


def _confirmed(client, payload, user, key):
    response = client.post(CONFIRM, json=payload, headers=_headers(user, key))
    assert response.status_code == 200, response.text
    assert response.json()["safe"] is True
    return response


def _advance_durable_authority_generation(db, user, payload):
    """Change authority through the migrated grant trigger, then read it back."""
    binding = payload["update_proposal"]["move_binding"]
    signed_generation = binding["authority_generation"]
    key = (user.practice_id, user.id, "appointment.read")
    with Session(bind=db.get_bind()) as observer:
        before = observer.query(User).filter_by(id=user.id, practice_id=user.practice_id).one()
        assert before.authority_generation == signed_generation
        assert before.is_active is True and before.role == UserRole.Receptionist
        assert observer.query(UserCapabilityGrant).filter_by(
            practice_id=key[0], user_id=key[1], capability_code=key[2],
        ).one_or_none() is None
    db.add(UserCapabilityGrant(
        practice_id=key[0], user_id=key[1], capability_code=key[2],
    ))
    db.commit()
    with Session(bind=db.get_bind()) as observer:
        after = observer.query(User).filter_by(id=user.id, practice_id=user.practice_id).one()
        assert after.authority_generation == signed_generation + 1
        assert after.is_active is True and after.role == UserRole.Receptionist
        assert observer.query(UserCapabilityGrant).filter_by(
            practice_id=key[0], user_id=key[1], capability_code=key[2],
        ).one_or_none() is not None


def test_signed_move_commits_same_id_time_only_version_audit_event(
    client, db, practice, seeded_appointment, reception_user,
):
    row = seeded_appointment
    before = _snapshot(db, practice.id)
    assert len(before["rows"]) == 1 and not before["audits"]
    assert not before["commands"] and not before["events"]
    proposal, payload = _proposal(client, row, reception_user)
    assert _snapshot(db, practice.id) == before  # Proposal has no write effect.
    response = _confirmed(client, payload, reception_user, "g4-happy")
    after = _snapshot(db, practice.id)
    assert len(after["rows"]) == len(after["audits"]) == len(after["commands"]) == len(after["events"]) == 1
    old, new = before["rows"][0], after["rows"][0]
    assert new[0] == old[0] == row.id and new[1] == old[1] + 1
    assert new[2] != old[2] and new[3] == old[3]
    assert new[4].strftime("%H:%M") == "11:00"
    assert new[5:] == old[5:]  # Every non-time field survives the move.
    audit, command, event = after["audits"][0], after["commands"][0], after["events"][0]
    assert command[1] == "completed" and command[2] == row.id
    assert audit[0] == command[3] and audit[2] == command[0]
    assert event[1] == row.id and event[2] == command[0] and event[3] == audit[0]
    assert event[4] == "diary.appointment_rescheduled" and event[5] == 1
    assert response.json()["appointment"]["id"] == str(row.id)
    assert proposal["move_binding"]["target_start_local"][:5] == "11:00"


@pytest.mark.parametrize("extra", [
    {"patient_id": str(uuid4())}, {"practitioner_id": str(uuid4())},
    {"duration_minutes": 45}, {"location_id": str(uuid4())},
    {"notes": "replace"}, {"status": "Cancelled"},
])
def test_non_time_intent_fields_are_refused_before_claim(
    client, db, practice, seeded_appointment, reception_user, extra,
):
    before = _snapshot(db, practice.id)
    intent = _intent(seeded_appointment, reception_user) | extra
    response = client.post(MOVE.format(seeded_appointment.id), json=intent,
                           headers=_headers(reception_user, "g4-non-time"))
    assert response.status_code == 422, response.text
    assert _snapshot(db, practice.id) == before


@pytest.mark.parametrize("change", [
    {"tenant_id": str(uuid4())}, {"actor_id": str(uuid4())},
    {"source_appointment_id": str(uuid4())},
    {"source_state_version": 999}, {"source_revision": 999},
])
def test_source_identity_version_revision_refusal_has_no_command(
    client, db, practice, seeded_appointment, reception_user, change,
):
    before = _snapshot(db, practice.id)
    response = client.post(MOVE.format(seeded_appointment.id),
                           json=_intent(seeded_appointment, reception_user) | change,
                           headers=_headers(reception_user, "g4-stale"))
    assert response.status_code in (403, 409, 422), response.text
    assert _snapshot(db, practice.id) == before


def test_inactive_practitioner_refused_without_command(
    client, db, practice, practitioner, seeded_appointment, reception_user,
):
    practitioner.is_active = False
    db.commit()
    before = _snapshot(db, practice.id)
    response = client.post(MOVE.format(seeded_appointment.id),
                           json=_intent(seeded_appointment, reception_user),
                           headers=_headers(reception_user, "g4-inactive"))
    assert response.status_code == 409, response.text
    assert response.json()["detail"]["code"] == "MOVE_PRACTITIONER_INACTIVE"
    assert _snapshot(db, practice.id) == before


def test_terminal_source_cannot_return_to_booked_through_move(
    client, db, practice, seeded_appointment, reception_user,
):
    seeded_appointment.status = AppointmentStatus.Cancelled
    db.commit()
    db.refresh(seeded_appointment)
    before = _snapshot(db, practice.id)
    response = client.post(MOVE.format(seeded_appointment.id),
                           json=_intent(seeded_appointment, reception_user),
                           headers=_headers(reception_user, "g4-terminal"))
    assert response.status_code in (400, 409), response.text
    assert _snapshot(db, practice.id) == before


@pytest.mark.parametrize("day,code", [
    ("2027-10-03", "MOVE_LOCAL_TIME_NONEXISTENT"),
    ("2027-04-04", "MOVE_LOCAL_TIME_AMBIGUOUS"),
])
def test_sydney_dst_gap_and_fold_refused_before_claim(
    client, db, practice, seeded_appointment, reception_user, day, code,
):
    practice.timezone = "Australia/Sydney"
    db.commit()
    before = _snapshot(db, practice.id)
    intent = _intent(seeded_appointment, reception_user, clock="02:30")
    intent["target_date"] = day
    response = client.post(MOVE.format(seeded_appointment.id), json=intent,
                           headers=_headers(reception_user, "g4-dst"))
    assert response.status_code == 422, response.text
    assert response.json()["detail"]["code"] == code
    assert _snapshot(db, practice.id) == before


def test_completed_replay_same_body_once_changed_body_conflicts(
    client, db, practice, seeded_appointment, reception_user,
):
    _, payload = _proposal(client, seeded_appointment, reception_user)
    first = _confirmed(client, payload, reception_user, "g4-replay")
    after = _snapshot(db, practice.id)
    replay = _confirmed(client, payload, reception_user, "g4-replay")
    assert replay.json() == first.json() and _snapshot(db, practice.id) == after
    changed = deepcopy(payload)
    changed["confirmed_warnings"] = ["different-body"]
    conflict = client.post(CONFIRM, json=changed,
                           headers=_headers(reception_user, "g4-replay"))
    assert conflict.status_code == 409, conflict.text
    assert _snapshot(db, practice.id) == after


def test_authority_generation_change_blocks_confirmation(
    client, db, practice, seeded_appointment, reception_user,
):
    _, payload = _proposal(client, seeded_appointment, reception_user)
    before = _snapshot(db, practice.id)
    _advance_durable_authority_generation(db, reception_user, payload)
    response = client.post(CONFIRM, json=payload,
                           headers=_headers(reception_user, "g4-authority"))
    assert response.status_code == 403, response.text
    assert response.json()["detail"]["code"] == "MOVE_ACTOR_CHANGED"
    assert _snapshot(db, practice.id) == before


def test_completed_move_replay_rechecks_current_authority_generation(
    client, db, practice, seeded_appointment, reception_user,
):
    _, payload = _proposal(client, seeded_appointment, reception_user)
    _confirmed(client, payload, reception_user, "g4-authority-replay")
    completed = _snapshot(db, practice.id)
    _advance_durable_authority_generation(db, reception_user, payload)
    replay = client.post(CONFIRM, json=payload,
                         headers=_headers(reception_user, "g4-authority-replay"))
    assert replay.status_code == 403, replay.text
    assert replay.json()["detail"]["code"] == "MOVE_ACTOR_CHANGED"
    assert _snapshot(db, practice.id) == completed


@pytest.mark.parametrize("revocation", ["is_active", "role"])
@pytest.mark.parametrize("phase", ["before_confirmation", "completed_replay"])
def test_live_reception_revocation_blocks_confirmation_and_completed_replay(
    client, db, practice, seeded_appointment, reception_user, revocation, phase,
):
    _, payload = _proposal(client, seeded_appointment, reception_user)
    if phase == "completed_replay":
        _confirmed(client, payload, reception_user, "g4-live-replay")
    before = _snapshot(db, practice.id)
    if revocation == "is_active":
        reception_user.is_active = False
    else:
        from app.models.tenancy import UserRole
        reception_user.role = UserRole.GP
    db.commit()
    response = client.post(CONFIRM, json=payload,
                           headers=_headers(reception_user, "g4-live-replay"))
    if revocation == "is_active":
        assert response.status_code == 401, response.text
        assert response.json()["detail"] == "User not found or inactive"
    else:
        assert response.status_code == 403, response.text
        assert response.json()["detail"]["code"] == "MOVE_ACTOR_UNAUTHORIZED"
    assert _snapshot(db, practice.id) == before


def test_move_binding_expiration_blocks_write_after_claim(
    client, db, practice, seeded_appointment, reception_user, monkeypatch,
):
    import app.routers.appointments as routes

    proposal, payload = _proposal(client, seeded_appointment, reception_user)
    before = _snapshot(db, practice.id)
    expiry = datetime.fromisoformat(proposal["move_binding"]["expires_at"].replace("Z", "+00:00"))

    class ExpiredClock(datetime):
        @classmethod
        def now(cls, tz=None):
            later = expiry + timedelta(seconds=1)
            return later if tz is None else later.astimezone(tz)

    monkeypatch.setattr(routes, "datetime", ExpiredClock)
    response = client.post(CONFIRM, json=payload,
                           headers=_headers(reception_user, "g4-expired"))
    assert response.status_code in (200, 409), response.text
    if response.status_code == 200:
        assert response.json()["safe"] is False
    after = _snapshot(db, practice.id)
    assert after["rows"] == before["rows"]
    assert after["audits"] == before["audits"] and after["events"] == before["events"]
    assert not any(command[1] == "completed" and command[2] == seeded_appointment.id
                   for command in after["commands"])


def test_signed_move_marker_cannot_be_removed_or_changed(
    client, db, practice, seeded_appointment, reception_user,
):
    _, payload = _proposal(client, seeded_appointment, reception_user)
    before = _snapshot(db, practice.id)
    for altered, expected_codes in (
        (None, {"signed_evidence_mismatch"}),
        ({**payload["update_proposal"]["move_binding"], "source_revision": 999},
         {"signed_evidence_mismatch", "move_source_changed"}),
    ):
        changed = deepcopy(payload)
        changed["update_proposal"]["move_binding"] = altered
        response = client.post(CONFIRM, json=changed,
                               headers=_headers(reception_user, "g4-marker-" + str(altered is None)))
        assert response.status_code == 200, response.text
        refused = response.json()
        assert refused["safe"] is False and refused["appointment"] is None
        assert expected_codes <= {block["code"] for block in refused["blocks"]}
        assert _snapshot(db, practice.id) == before


def test_second_confirmation_of_same_version_loses_without_second_effect(
    client, db, practice, seeded_appointment, reception_user,
):
    _, first_payload = _proposal(client, seeded_appointment, reception_user, key="g4-first-proposal")
    _, second_payload = _proposal(client, seeded_appointment, reception_user, key="g4-second-proposal")
    _confirmed(client, first_payload, reception_user, "g4-winner")
    after = _snapshot(db, practice.id)
    loser = client.post(CONFIRM, json=second_payload,
                        headers=_headers(reception_user, "g4-loser"))
    assert loser.status_code in (200, 400, 409), loser.text
    if loser.status_code == 200:
        assert loser.json()["safe"] is False
    final = _snapshot(db, practice.id)
    assert final["rows"] == after["rows"]
    assert final["audits"] == after["audits"] and final["events"] == after["events"]
    assert sum(command[1] == "completed" and command[2] == seeded_appointment.id
               for command in final["commands"]) == 1


def test_database_exclusion_rejects_competing_slot(
    db, practice, seeded_appointment,
):
    row = seeded_appointment
    before = _snapshot(db, practice.id)
    with Session(bind=db.get_bind()) as contender:
        contender.add(Appointment(
            practice_id=practice.id, patient_id=row.patient_id,
            practitioner_id=row.practitioner_id, start_time=row.start_time + timedelta(minutes=15),
            appointment_date=row.appointment_date,
            start_time_local=(datetime.combine(row.appointment_date, row.start_time_local)
                              + timedelta(minutes=15)).time(),
            duration_minutes=30, status=row.status,
        ))
        with pytest.raises(IntegrityError) as caught:
            contender.commit()
        assert "ex_appointments_practice_practitioner_no_overlap" in str(caught.value.orig)
        contender.rollback()
    assert _snapshot(db, practice.id) == before


def test_post_claim_failure_rolls_back_row_command_audit_event(
    client, db, practice, seeded_appointment, reception_user, monkeypatch,
):
    import app.routers.appointments as routes

    before = _snapshot(db, practice.id)
    assert len(before["rows"]) == 1
    assert not before["audits"] and not before["commands"] and not before["events"]
    _, payload = _proposal(client, seeded_appointment, reception_user)
    assert _snapshot(db, practice.id) == before
    entered = []
    injected = []

    def fail_after_claim(session, record, **kwargs):
        # Read the request transaction before its injected exception rolls it back.
        rows = session.query(Appointment).populate_existing().filter_by(
            practice_id=practice.id).all()
        audits = session.query(AppointmentAuditLog).filter_by(
            practice_id=practice.id).all()
        commands = session.query(AppointmentCommandIdempotency).filter_by(
            practice_id=practice.id).all()
        events = session.query(DiaryCommittedEvent).filter_by(
            practice_id=practice.id).all()
        entered.append({
            "record_id": record.id,
            "record_state": record.state,
            "rows": [(r.id, r.appointment_state_version, r.start_time,
                      r.appointment_date, r.start_time_local, r.status,
                      r.patient_id, r.patient_name_provisional, r.practitioner_id,
                      r.appointment_type_id, r.location_id, r.duration_minutes,
                      r.reason, r.notes) for r in rows],
            "audits": [(r.id, r.appointment_id, r.command_id) for r in audits],
            "commands": [(r.id, r.state, r.target_appointment_id,
                          r.audit_log_id, r.request_body_hash,
                          r.response_body_hash) for r in commands],
            "events": [(r.id, r.appointment_id, r.command_id, r.audit_log_id,
                        r.event_type, r.aggregate_revision) for r in events],
            "event_enabled": routes.settings.reception_one_committed_event_runtime_enabled,
            "completion": {
                "result_kind": kwargs.get("result_kind"),
                "response_status_code": kwargs.get("response_status_code"),
                "target_appointment_id": kwargs.get("target_appointment_id"),
                "audit_log_id": kwargs.get("audit_log_id"),
                "response_appointment_id": kwargs.get("response_body", {}).get(
                    "appointment", {}).get("id"),
            },
        })
        failure = RuntimeError("synthetic_post_claim_stop")
        injected.append((type(failure).__name__, str(failure)))
        raise failure

    monkeypatch.setattr(routes, "complete_appointment_command", fail_after_claim)
    response = client.post(CONFIRM, json=payload,
                           headers=_headers(reception_user, "g4-post-claim"))
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert len(entered) == 1 and injected == [
        ("RuntimeError", "synthetic_post_claim_stop")]
    transaction = entered[0]
    assert transaction["record_state"] == "in_progress"
    assert len(transaction["rows"]) == len(transaction["audits"]) == len(
        transaction["commands"]) == 1
    old, moved = before["rows"][0], transaction["rows"][0]
    assert moved[0] == old[0] == seeded_appointment.id
    assert moved[1] == old[1] + 1 and moved[2] != old[2]
    assert moved[3] == old[3] and moved[4].strftime("%H:%M") == "11:00"
    assert moved[5:] == old[5:]
    audit = transaction["audits"][0]
    command = transaction["commands"][0]
    assert command[0] == transaction["record_id"] == audit[2]
    assert command[1] == "in_progress" and command[2:4] == (None, None)
    assert command[4] and command[5] is None
    assert audit[1] == seeded_appointment.id
    assert transaction["completion"] == {
        "result_kind": "confirmed_write", "response_status_code": 200,
        "target_appointment_id": seeded_appointment.id,
        "audit_log_id": audit[0],
        "response_appointment_id": str(seeded_appointment.id),
    }
    if transaction["event_enabled"]:
        assert len(transaction["events"]) == 1
        event = transaction["events"][0]
        assert event[1:4] == (seeded_appointment.id, command[0], audit[0])
        assert event[4:] == ("diary.appointment_rescheduled", 1)
    else:
        assert not transaction["events"]
    # A separate observer sees the entire original committed snapshot.
    assert _snapshot(db, practice.id) == before
