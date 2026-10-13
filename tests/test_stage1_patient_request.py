"""Synthetic request/create checks for a separately reviewed disposable DB run.

These tests do not bootstrap a server, database or patient identity on their own.
"""

from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
import secrets
import threading
import uuid
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.config import settings
from app.models.appointments import Appointment, AppointmentAuditLog, AppointmentCommandIdempotency, AppointmentType
from app.models.patient_requests import PatientBookingRequest
from app.models.diary_events import DiaryCommittedEvent
from app.models.patients import Patient
from app.models.tenancy import Practice, PracticeLocation, Practitioner, User, UserRole
from app.services.auth_service import create_access_token
from app.services.patient_request_contract import capability_digest
from app.services.appointment_conflicts import set_appointment_practice_context
from app.schemas.appointments import AppointmentCreateCommand, AppointmentCreateProposalConfirmationIn


BASE = "/api/v1/appointments"


def _staff_headers(user, key=None):
    token = create_access_token({
        "sub": str(user.id), "practice_id": str(user.practice_id),
        "role": user.role.value,
    })
    result = {"Authorization": f"Bearer {token}"}
    if key:
        result["Idempotency-Key"] = key
    return result


@pytest.fixture
def request_case(db, practice, reception_user, seeded_appointment, monkeypatch):
    set_appointment_practice_context(db, practice.id)
    patient = Patient(
        practice_id=practice.id, first_name="Alex", last_name="Chen",
        date_of_birth=date(1990, 1, 1),
    )
    kind = AppointmentType(practice_id=practice.id, name="Follow-up", default_duration=15)
    db.add_all([patient, kind])
    db.flush()
    secret = "stage1-synthetic-only-secret-32-byte-minimum"
    token = secrets.token_hex(32)
    monkeypatch.setattr(settings, "secret_key", secret)
    monkeypatch.setattr(settings, "stage1_patient_request_enabled", True)
    monkeypatch.setattr(settings, "stage1_patient_request_practice_id", str(practice.id))
    monkeypatch.setattr(settings, "stage1_patient_request_patient_id", str(patient.id))
    zone = practice.timezone
    row = PatientBookingRequest(
        practice_id=practice.id, patient_id=patient.id,
        practitioner_id=seeded_appointment.practitioner_id,
        appointment_type_id=kind.id, location_id=seeded_appointment.location_id,
        duration_minutes=15, practice_timezone=zone,
        capability_digest=capability_digest(token, secret.encode()),
        capability_expires_at=datetime.now(timezone.utc) + timedelta(hours=2),
        state="draft", request_version=1,
    )
    set_appointment_practice_context(db, practice.id)
    db.add(row)
    db.commit()
    return row, token, patient, kind


def _patient_headers(token, key=None):
    headers = {"X-Patient-Request-Capability": token}
    if key:
        headers["Idempotency-Key"] = key
    return headers


def _submit(client, row, token):
    options = client.get(f"{BASE}/patient-requests/{row.id}/options?request_version=1", headers=_patient_headers(token))
    assert options.status_code == 200, options.text
    assert len({item["date"] for item in options.json()}) == 7
    option = options.json()[0]
    body = {
        "schema_version": "patient.request_submission.v1",
        "request_id": str(row.id), "request_version": 1,
        "date": option["date"], "earliest_local": "14:00",
        "latest_local": "17:00", "reason_code": "follow_up", "authority": "request_only",
    }
    response = client.post(f"{BASE}/patient-requests/{row.id}/submit", json=body,
                           headers=_patient_headers(token, "submit-one"))
    assert response.status_code == 200, response.text
    assert response.json()["state"] == "submitted"
    return body, option


def _proposal(client, row, user, option):
    response = client.post(f"{BASE}/staff/patient-requests/{row.id}/proposals/create",
                           json={"request_version": 2, "selected": option},
                           headers=_staff_headers(user))
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["safe"] is True
    assert data["patient_request_binding"]["request_id"] == str(row.id)
    payload = deepcopy(data["confirm_payload"])
    payload["confirmed"] = True
    return payload


def _confirm(client, user, payload, key):
    return client.post(f"{BASE}/proposals/create/confirm", json=payload,
                       headers=_staff_headers(user, key))


def _persistent_snapshot(db, practice_id):
    """Observe committed rows through a separate session after a request."""
    binding = db.get_bind()
    assert isinstance(binding, Engine), "committed-state observer requires a separate DB connection"
    with Session(bind=binding) as observer:
        set_appointment_practice_context(observer, practice_id)
        return {
            "appointments": sorted([
                (row.id, row.patient_id, row.start_time)
                for row in observer.query(Appointment).filter_by(practice_id=practice_id).all()
            ], key=lambda item: str(item[0])),
            "requests": sorted([
                (row.id, row.state, row.request_version, row.booked_appointment_id,
                 row.booked_command_id, row.booked_at)
                for row in observer.query(PatientBookingRequest).filter_by(practice_id=practice_id).all()
            ], key=lambda item: str(item[0])),
            "commands": sorted([
                (row.id, row.state, row.target_appointment_id, row.audit_log_id)
                for row in observer.query(AppointmentCommandIdempotency).filter_by(practice_id=practice_id).all()
            ], key=lambda item: str(item[0])),
            "audits": sorted([
                (row.id, row.appointment_id, row.command_id)
                for row in observer.query(AppointmentAuditLog).filter_by(practice_id=practice_id).all()
            ], key=lambda item: str(item[0])),
            "events": sorted([
                (row.id, row.appointment_id, row.command_id, row.audit_log_id)
                for row in observer.query(DiaryCommittedEvent).filter_by(practice_id=practice_id).all()
            ], key=lambda item: str(item[0])),
        }


def _second_request(row, *, booked_appointment_id, booked_command_id):
    return PatientBookingRequest(
        practice_id=row.practice_id, patient_id=row.patient_id,
        practitioner_id=row.practitioner_id, appointment_type_id=row.appointment_type_id,
        location_id=row.location_id, duration_minutes=row.duration_minutes,
        practice_timezone=row.practice_timezone, capability_digest="1" * 64,
        capability_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        state="booked", request_version=2,
        preference_date=row.preference_date, earliest_local=row.earliest_local,
        latest_local=row.latest_local, reason_code="follow_up",
        submitted_at=datetime.now(timezone.utc), booked_at=datetime.now(timezone.utc),
        booked_appointment_id=booked_appointment_id, booked_command_id=booked_command_id,
    )


def test_submit_is_request_only_and_capability_is_scoped(client, db, practice, reception_user, request_case):
    row, token, _, _ = request_case
    before = (
        db.query(Appointment).filter_by(practice_id=practice.id).count(),
        db.query(AppointmentAuditLog).filter_by(practice_id=practice.id).count(),
        db.query(AppointmentCommandIdempotency).filter_by(practice_id=practice.id).count(),
        db.query(DiaryCommittedEvent).filter_by(practice_id=practice.id).count(),
    )
    body, _ = _submit(client, row, token)
    assert before == (
        db.query(Appointment).filter_by(practice_id=practice.id).count(),
        db.query(AppointmentAuditLog).filter_by(practice_id=practice.id).count(),
        db.query(AppointmentCommandIdempotency).filter_by(practice_id=practice.id).count(),
        db.query(DiaryCommittedEvent).filter_by(practice_id=practice.id).count(),
    )
    replay = client.post(f"{BASE}/patient-requests/{row.id}/submit", json=body,
                         headers=_patient_headers(token, "submit-one"))
    assert replay.status_code == 200 and replay.json()["state"] == "submitted"
    changed = {**body, "latest_local": "16:00"}
    assert client.post(f"{BASE}/patient-requests/{row.id}/submit", json=changed,
                       headers=_patient_headers(token, "submit-one")).status_code == 409
    for request_id, bearer in [(row.id, secrets.token_hex(32)), (uuid.uuid4(), token)]:
        response = client.get(f"{BASE}/patient-requests/{request_id}",
                              headers=_patient_headers(bearer))
        assert response.status_code == 404
        assert response.json()["detail"]["code"] == "REQUEST_UNAVAILABLE"


def test_signed_request_create_exact_replay_and_later_readback(client, db, reception_user, request_case):
    row, token, _, _ = request_case
    _, option = _submit(client, row, token)
    payload = _proposal(client, row, reception_user, option)
    before_stripped = _persistent_snapshot(db, reception_user.practice_id)
    stripped = deepcopy(payload)
    stripped["create_proposal"].pop("patient_request_binding")
    assert _confirm(client, reception_user, stripped, "stripped").json()["safe"] is False
    assert _persistent_snapshot(db, reception_user.practice_id) == before_stripped
    response = _confirm(client, reception_user, payload, "create-one")
    assert response.status_code == 200 and response.json()["safe"] is True, response.text
    appointment_id = uuid.UUID(response.json()["appointment"]["id"])
    db.refresh(row)
    assert row.state == "booked" and row.booked_appointment_id == appointment_id
    command = db.query(AppointmentCommandIdempotency).filter_by(id=row.booked_command_id).one()
    assert command.target_appointment_id == appointment_id and command.state == "completed"
    replay = _confirm(client, reception_user, payload, "create-one")
    assert replay.status_code == 200 and replay.json()["historical_receipt"] is True
    assert replay.json()["appointment"]["id"] == str(appointment_id)
    assert _confirm(client, reception_user, payload, "different-key").status_code == 409
    changed = deepcopy(payload)
    changed["confirmed_warnings"].append("changed")
    assert _confirm(client, reception_user, changed, "create-one").status_code == 409
    read = client.get(f"{BASE}/patient-requests/{row.id}", headers=_patient_headers(token))
    assert read.status_code == 200 and read.json()["booked_appointment_id"] == str(appointment_id)


def test_nonbooked_request_cannot_claim_completed_links(db, practice, request_case):
    row, _, _, _ = request_case
    row.state = "submitted"
    row.booked_appointment_id = uuid.uuid4()
    row.booked_command_id = uuid.uuid4()
    row.booked_at = datetime.now(timezone.utc)
    with pytest.raises(IntegrityError):
        db.flush()
    db.rollback()


@pytest.mark.parametrize("dimension,expected_constraint", [
    ("practitioner", "fk_patient_request_practitioner"),
    ("appointment_type", "fk_patient_request_type"),
    ("location", "fk_patient_request_location"),
])
def test_cross_practice_request_dimensions_rejected_by_scoped_fk(
    db, practice, request_case, dimension, expected_constraint,
):
    row, _, _, _ = request_case
    foreign_practice = Practice(name="Unrelated synthetic practice", timezone=practice.timezone)
    db.add(foreign_practice)
    db.flush()
    if dimension == "practitioner":
        foreign = Practitioner(
            practice_id=foreign_practice.id, first_name="Other", last_name="Doctor",
        )
    elif dimension == "appointment_type":
        foreign = AppointmentType(practice_id=foreign_practice.id, name="Other type")
    else:
        foreign = PracticeLocation(practice_id=foreign_practice.id, name="Other site")
    db.add(foreign)
    db.flush()
    candidate = PatientBookingRequest(
        practice_id=practice.id, patient_id=row.patient_id,
        practitioner_id=(foreign.id if dimension == "practitioner" else row.practitioner_id),
        appointment_type_id=(foreign.id if dimension == "appointment_type" else row.appointment_type_id),
        location_id=(foreign.id if dimension == "location" else row.location_id),
        duration_minutes=15, practice_timezone=practice.timezone,
        capability_digest="4" * 64,
        capability_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        state="draft", request_version=1,
    )
    set_appointment_practice_context(db, practice.id)
    db.add(candidate)
    with pytest.raises(IntegrityError) as error:
        db.flush()
    assert getattr(error.value.orig.diag, "constraint_name", None) == expected_constraint
    db.rollback()


def test_cross_practice_patient_link_rejected_by_scoped_fk(db, practice, request_case):
    row, _, _, _ = request_case
    other_practice = Practice(name="Other synthetic practice", timezone=practice.timezone)
    db.add(other_practice)
    db.flush()
    foreign_practitioner = Practitioner(
        practice_id=other_practice.id, first_name="Other", last_name="Doctor",
    )
    foreign_type = AppointmentType(practice_id=other_practice.id, name="Other type")
    foreign_location = PracticeLocation(practice_id=other_practice.id, name="Other site")
    db.add_all([foreign_practitioner, foreign_type, foreign_location])
    db.flush()
    set_appointment_practice_context(db, practice.id)
    original_patient_id = row.patient_id
    original_timezone = practice.timezone
    other_practice_id = other_practice.id
    other_practitioner_id = foreign_practitioner.id
    other_type_id = foreign_type.id
    other_location_id = foreign_location.id
    db.commit()
    set_appointment_practice_context(db, other_practice_id)
    wrong = PatientBookingRequest(
        practice_id=other_practice_id, patient_id=original_patient_id,
        practitioner_id=other_practitioner_id, appointment_type_id=other_type_id,
        location_id=other_location_id, duration_minutes=15,
        practice_timezone=original_timezone,
        capability_digest="0" * 64,
        capability_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        state="draft", request_version=1,
    )
    db.add(wrong)
    with pytest.raises(IntegrityError) as error:
        db.flush()  # The patient is the sole cross-practice reference.
    assert getattr(error.value.orig.diag, "constraint_name", None) == "fk_patient_request_patient"
    db.rollback()
    set_appointment_practice_context(db, other_practice_id)
    assert db.execute(
        text("SELECT count(*) FROM patient_booking_requests WHERE practice_id = :practice_id"),
        {"practice_id": other_practice_id},
    ).scalar_one() == 0


def test_command_target_association_and_duplicate_booked_links_are_database_enforced(
    client, db, practice, reception_user, seeded_appointment, request_case,
):
    row, token, _, _ = request_case
    _, option = _submit(client, row, token)
    payload = _proposal(client, row, reception_user, option)
    confirmed = _confirm(client, reception_user, payload, "db-link-original")
    assert confirmed.status_code == 200 and confirmed.json()["safe"] is True
    db.refresh(row)
    assert row.booked_appointment_id != seeded_appointment.id

    # Both unique link keys must exist, regardless of which one rejects first.
    names = {
        name for (name,) in db.execute(
            text(
                "SELECT conname FROM pg_constraint WHERE conrelid = "
                "'patient_booking_requests'::regclass"
            )
        ).all()
    }
    assert {"uq_patient_request_booked_appointment", "uq_patient_request_booked_command"} <= names
    db.add(_second_request(
        row, booked_appointment_id=row.booked_appointment_id,
        booked_command_id=row.booked_command_id,
    ))
    with pytest.raises(IntegrityError):
        db.flush()
    db.rollback()

    # A distinct command targeting the newly booked appointment cannot be
    # paired with the older seeded appointment, even in the same practice.
    set_appointment_practice_context(db, practice.id)
    wrong_target = AppointmentCommandIdempotency(
        practice_id=practice.id, actor_user_id=str(reception_user.id),
        actor_role="Receptionist", operation_id="requestLinkMismatchTest",
        route_family="test-only", idempotency_key_hash="2" * 64,
        request_body_hash="3" * 64, request_body_canonicalization_version=1,
        state="in_progress", target_appointment_id=row.booked_appointment_id,
    )
    db.add(wrong_target)
    db.flush()
    db.add(_second_request(
        row, booked_appointment_id=seeded_appointment.id,
        booked_command_id=wrong_target.id,
    ))
    with pytest.raises(IntegrityError) as error:
        db.flush()
    assert getattr(error.value.orig.diag, "constraint_name", None) == "fk_patient_request_command_target"
    db.rollback()

def test_revoked_receptionist_cannot_replay(client, db, reception_user, request_case, monkeypatch):
    import app.routers.appointments as router

    row, token, _, _ = request_case
    _, option = _submit(client, row, token)
    payload = _proposal(client, row, reception_user, option)
    assert _confirm(client, reception_user, payload, "revoked-key").status_code == 200
    reception_user.is_active = False
    db.commit()
    claimed = {"count": 0}
    original_claim = router.claim_appointment_command

    def counted_claim(*args, **kwargs):
        claimed["count"] += 1
        return original_claim(*args, **kwargs)

    monkeypatch.setattr(router, "claim_appointment_command", counted_claim)
    assert _confirm(client, reception_user, payload, "revoked-key").status_code in {401, 403}
    assert claimed["count"] == 0  # Current authority precedes receipt lookup.


def test_cancel_and_marker_substitution_refuse_booking(client, db, reception_user, request_case):
    row, token, _, _ = request_case
    _, option = _submit(client, row, token)
    payload = _proposal(client, row, reception_user, option)
    changed = deepcopy(payload)
    changed["create_proposal"]["patient_request_binding"]["request_id"] = str(uuid.uuid4())
    substituted = _confirm(client, reception_user, changed, "substituted")
    assert substituted.status_code in {200, 409}
    if substituted.status_code == 200:
        assert substituted.json()["safe"] is False
    cancel = client.post(f"{BASE}/patient-requests/{row.id}/cancel",
                         json={"request_version": 2}, headers=_patient_headers(token))
    assert cancel.status_code == 200 and cancel.json()["state"] == "cancelled"
    assert _confirm(client, reception_user, payload, "after-cancel").status_code == 409
    db.refresh(row)
    assert row.booked_appointment_id is None and row.booked_command_id is None


def test_created_id_survives_later_staff_time_move(client, db, reception_user, request_case):
    row, token, _, _ = request_case
    _, option = _submit(client, row, token)
    payload = _proposal(client, row, reception_user, option)
    created = _confirm(client, reception_user, payload, "create-then-move")
    assert created.status_code == 200 and created.json()["safe"] is True
    appointment_id = created.json()["appointment"]["id"]
    appointment = db.query(Appointment).filter_by(id=uuid.UUID(appointment_id)).one()
    before = (appointment.patient_id, appointment.practitioner_id,
              appointment.appointment_type_id, appointment.location_id,
              appointment.duration_minutes, appointment.reason)
    intent = {
        "schema_version": "appointment.move_time_intent.v1",
        "tenant_id": str(reception_user.practice_id), "actor_id": str(reception_user.id),
        "role": "reception", "source_appointment_id": appointment_id,
        "source_state_version": appointment.appointment_state_version,
        "source_revision": appointment.appointment_state_version,
        "target_date": appointment.appointment_date.isoformat(),
        "target_start_local": "11:00", "authority": "proposal_only",
    }
    proposed = client.post(f"{BASE}/proposals/move-time/{appointment_id}",
                           json=intent, headers=_staff_headers(reception_user, "move-proposal"))
    assert proposed.status_code == 200 and proposed.json()["safe"] is True
    move_payload = proposed.json()["confirm_payload"]
    move_payload["confirmed"] = True
    moved = client.post(f"{BASE}/proposals/update/confirm", json=move_payload,
                        headers=_staff_headers(reception_user, "move-confirm"))
    assert moved.status_code == 200 and moved.json()["safe"] is True
    db.refresh(row)
    db.refresh(appointment)
    assert row.booked_appointment_id == appointment.id == uuid.UUID(appointment_id)
    assert (appointment.patient_id, appointment.practitioner_id,
            appointment.appointment_type_id, appointment.location_id,
            appointment.duration_minutes, appointment.reason) == before
    assert appointment.start_time_local.strftime("%H:%M") == "11:00"


def test_expired_signed_offer_refuses_create_after_claim(
    client, db, reception_user, request_case, monkeypatch,
):
    import app.routers.appointments as router

    row, token, _, _ = request_case
    _, option = _submit(client, row, token)
    payload = _proposal(client, row, reception_user, option)
    expiry = datetime.fromisoformat(
        payload["create_proposal"]["patient_request_binding"]["offer_expires_at"]
    )

    class LaterClock(datetime):
        @classmethod
        def now(cls, tz=None):
            return expiry + timedelta(microseconds=1)

    monkeypatch.setattr(router, "datetime", LaterClock)
    refused = _confirm(client, reception_user, payload, "stale-offer")
    assert refused.status_code == 409
    db.refresh(row)
    assert row.state == "submitted" and row.booked_appointment_id is None
    assert db.query(AppointmentCommandIdempotency).filter_by(
        practice_id=reception_user.practice_id,
        operation_id="confirmAppointmentCreateProposal",
    ).count() == 0


def test_long_duration_cross_date_is_rejected_at_proposal_and_confirmation(
    client, db, reception_user, request_case,
):
    import app.routers.appointments as router

    row, token, _, _ = request_case
    _submit(client, row, token)
    options = client.get(
        f"{BASE}/patient-requests/{row.id}/options?request_version=2",
        headers=_patient_headers(token),
    )
    assert options.status_code == 200
    late = next(item for item in options.json() if item["local_time"].startswith("16:00"))
    payload = _proposal(client, row, reception_user, late)

    # A 16:00 + 480-minute slot ends at 00:00 on the next local date.
    # The old time-only comparison treated that 00:00 as earlier than 17:00.
    row.duration_minutes = 480
    db.commit()
    before = _persistent_snapshot(db, reception_user.practice_id)
    refused_proposal = client.post(
        f"{BASE}/staff/patient-requests/{row.id}/proposals/create",
        json={"request_version": 2, "selected": late},
        headers=_staff_headers(reception_user),
    )
    assert refused_proposal.status_code == 409
    assert refused_proposal.json()["detail"]["code"] == "REQUEST_OPTION_OUTSIDE_PREFERENCE"
    assert _persistent_snapshot(db, reception_user.practice_id) == before

    # Re-sign a server-authored proposal shape solely to reach the confirm
    # guard directly; the ordinary proposal route above correctly refuses it.
    payload["create_proposal"]["command"]["duration_minutes"] = 480
    command = AppointmentCreateCommand.model_validate(payload["create_proposal"]["command"])
    freshness = router._compute_create_proposal_freshness_id(
        command=command, reference_date=command.appointment_date,
    )
    payload["create_proposal_freshness_id"] = freshness
    marker = payload["create_proposal"]["patient_request_binding"]
    signed_payload = router._staff_create_signed_confirmation_payload(
        practice_id=reception_user.practice_id, staff_user_id=reception_user.id,
        command=command, create_proposal_freshness_id=freshness,
        patient_request_binding=marker,
    )
    payload["signed_confirmation_evidence"] = router.mint_signed_confirmation_evidence(
        signed_payload,
        evidence_purpose=router._STAFF_CREATE_CONFIRM_ACTION.evidence_purpose,
    )
    refused_confirm = _confirm(client, reception_user, payload, "cross-date-confirm")
    assert refused_confirm.status_code == 409
    assert refused_confirm.json()["detail"]["code"] == "REQUEST_STALE"
    assert _persistent_snapshot(db, reception_user.practice_id) == before


def test_failure_after_appointment_flush_rolls_back_all_create_effects(
    client, db, reception_user, request_case, monkeypatch,
):
    import app.routers.appointments as router

    row, token, _, _ = request_case
    _, option = _submit(client, row, token)
    payload = _proposal(client, row, reception_user, option)
    before = _persistent_snapshot(db, reception_user.practice_id)
    reached = {"after_flush": False}

    def fail_at_audit(session, **kwargs):
        # _create_appointment_from_body has flushed the appointment before
        # calling this audit seam. The command claim is in the same transaction.
        assert session.query(Appointment).filter_by(
            practice_id=reception_user.practice_id,
        ).count() == len(before["appointments"]) + 1
        assert session.query(AppointmentCommandIdempotency).filter_by(
            practice_id=reception_user.practice_id,
        ).count() == len(before["commands"]) + 1
        reached["after_flush"] = True
        raise RuntimeError("synthetic post-flush failure")

    monkeypatch.setattr(router, "_write_audit", fail_at_audit)
    response = _confirm(client, reception_user, payload, "post-flush-failure")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert reached["after_flush"] is True
    assert _persistent_snapshot(db, reception_user.practice_id) == before


def test_two_independent_sessions_same_staff_serializes_distinct_keys(
    client, db, reception_user, request_case,
):
    from app.routers.appointments import confirm_create_proposal_route

    row, token, _, _ = request_case
    _, option = _submit(client, row, token)
    payload = _proposal(client, row, reception_user, option)
    before = _persistent_snapshot(db, reception_user.practice_id)
    binding = db.get_bind()
    assert isinstance(binding, Engine), "concurrency test requires independent DB connections"
    gate = threading.Barrier(2)

    # Both calls use the same staff actor and first contend on that User row.
    # This is a two-session end-to-end race, not isolated proof of request-row
    # locking across different staff actors.

    def contender(key):
        with Session(bind=binding) as session:
            actor = session.query(User).filter_by(
                id=reception_user.id, practice_id=reception_user.practice_id,
            ).one()
            gate.wait(timeout=10)
            try:
                result = confirm_create_proposal_route(
                    body=AppointmentCreateProposalConfirmationIn.model_validate(payload),
                    idempotency_key=key, db=session, current_user=actor,
                )
                return "confirmed" if result.safe else "blocked"
            except HTTPException as exc:
                session.rollback()
                assert exc.status_code == 409
                return "blocked"

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(contender, "contender-A")
        second = pool.submit(contender, "contender-B")
        results = [first.result(timeout=20), second.result(timeout=20)]
    assert sorted(results) == ["blocked", "confirmed"]
    after = _persistent_snapshot(db, reception_user.practice_id)
    assert len(after["appointments"]) == len(before["appointments"]) + 1
    assert len(after["commands"]) == len(before["commands"]) + 1
    assert len(after["audits"]) == len(before["audits"]) + 1
    assert len(after["requests"]) == len(before["requests"])
    linked = next(item for item in after["requests"] if item[0] == row.id)
    assert linked[1] == "booked"
    new_ids = {item[0] for item in after["appointments"]} - {
        item[0] for item in before["appointments"]
    }
    assert new_ids == {linked[3]}


def test_booked_readback_exact_24_hour_boundary_after_bearer_expiry(
    client, db, reception_user, request_case, monkeypatch,
):
    import app.services.patient_request_service as service

    row, token, _, _ = request_case
    _, option = _submit(client, row, token)
    payload = _proposal(client, row, reception_user, option)
    lost_response = _confirm(client, reception_user, payload, "boundary-key")
    assert lost_response.status_code == 200  # Caller discards the response body.
    db.refresh(row)
    committed_id = row.booked_appointment_id
    booked_at = row.booked_at
    row.capability_expires_at = booked_at + timedelta(minutes=1)
    db.commit()

    class BoundaryClock(datetime):
        current = booked_at + timedelta(minutes=1, microseconds=1)

        @classmethod
        def now(cls, tz=None):
            return cls.current

    monkeypatch.setattr(service, "datetime", BoundaryClock)
    recovered = client.get(f"{BASE}/patient-requests/{row.id}",
                           headers=_patient_headers(token))
    assert recovered.status_code == 200
    assert recovered.json()["booked_appointment_id"] == str(committed_id)
    BoundaryClock.current = booked_at + timedelta(hours=24)
    at_boundary = client.get(f"{BASE}/patient-requests/{row.id}",
                             headers=_patient_headers(token))
    assert at_boundary.status_code == 200
    BoundaryClock.current = booked_at + timedelta(hours=24, microseconds=1)
    after_boundary = client.get(f"{BASE}/patient-requests/{row.id}",
                                headers=_patient_headers(token))
    assert after_boundary.status_code == 404
