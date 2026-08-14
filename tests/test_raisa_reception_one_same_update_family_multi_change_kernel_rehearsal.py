"""Provider-free authored-synthetic rehearsal for the combined appointment update kernel.

M1-M7 prove that changed practitioner, local time and duration travel through
the existing appointment update proposal/confirm path as one command, including
stale truth, a newly created conflict, an inactive target practitioner, exact
same-key replay, different-body key conflict, correlated audit/idempotency and
an injected pre-commit rollback followed by a clean same-key retry.

Evidence label: provider_free_live_local_backend_postgresql_authored_synthetic.
"""

import json
from copy import deepcopy
from datetime import date, datetime, time, timezone

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker
from starlette.responses import Response

import app.routers.appointments as appointments_router
from app.models.appointments import (
    Appointment,
    AppointmentAuditAction,
    AppointmentAuditLog,
    AppointmentCommandIdempotency,
    AppointmentStatus,
    BookingChannel,
)
from app.models.patients import Patient
from app.models.tenancy import Practice, Practitioner, User, UserRole
from app.schemas.appointments import BernieUpdateProposalConfirmationIn
from app.services.auth_service import hash_password
from tests.conftest import make_token

PROPOSAL_URL = "/api/v1/appointments/proposals/update/{appt_id}"
CONFIRM_URL = "/api/v1/appointments/proposals/update/confirm"
OPERATION_ID = "confirmAppointmentUpdateProposal"
ROUTE_FAMILY = "update-confirm"

APPT_DATE = date(2027, 3, 11)  # fixed future Thursday
FROZEN_NOW = datetime(2027, 3, 8, 8, 0, 0, tzinfo=timezone.utc)  # Monday 08:00


@pytest.fixture(autouse=True)
def _freeze_rehearsal_clock(monkeypatch):
    """Keep the authored-synthetic fixtures future/open under temporal guards."""

    def fixed_now(tz):
        return datetime(2027, 3, 8, 8, 0, 0, tzinfo=tz)

    monkeypatch.setattr(appointments_router, "_clinic_local_now", fixed_now)


@pytest.fixture()
def rehearsal_practice(db):
    p = Practice(name="Raisa Rehearsal Clinic")
    db.add(p)
    db.flush()
    return p


@pytest.fixture()
def rehearsal_practitioners(db, rehearsal_practice):
    original = Practitioner(
        practice_id=rehearsal_practice.id,
        first_name="Raisa",
        last_name="Original",
        ahpra_number="MED0000000101",
        is_active=True,
    )
    target = Practitioner(
        practice_id=rehearsal_practice.id,
        first_name="Raisa",
        last_name="Target",
        ahpra_number="MED0000000102",
        is_active=True,
    )
    db.add_all([original, target])
    db.flush()
    return original, target


@pytest.fixture()
def rehearsal_patient(db, rehearsal_practice):
    p = Patient(
        practice_id=rehearsal_practice.id,
        first_name="Author",
        last_name="Synthetic",
        date_of_birth=date(1992, 4, 18),
    )
    db.add(p)
    db.flush()
    return p


@pytest.fixture()
def rehearsal_user(db, rehearsal_practice):
    u = User(
        practice_id=rehearsal_practice.id,
        email="rehearsal.rec@test.local",
        password_hash=hash_password("Password1!"),
        role=UserRole.Receptionist,
        is_active=True,
    )
    db.add(u)
    db.flush()
    return u


def _make_appointment(
    db, practice, practitioner, patient, *, start_h=9, start_m=0, duration=15
):
    appt = Appointment(
        practice_id=practice.id,
        patient_id=patient.id,
        practitioner_id=practitioner.id,
        start_time=datetime.combine(
            APPT_DATE, time(start_h, start_m), tzinfo=timezone.utc
        ),
        appointment_date=APPT_DATE,
        start_time_local=time(start_h, start_m),
        duration_minutes=duration,
        status=AppointmentStatus.Booked,
        booked_via=BookingChannel.Receptionist,
    )
    db.add(appt)
    db.flush()
    return appt


def _auth(token, idempotency_key):
    return {
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": idempotency_key,
    }


def _propose(client, token, appt_id, *, practitioner_id, start_h=14, duration=30):
    resp = client.post(
        PROPOSAL_URL.format(appt_id=appt_id),
        json={
            "practitioner_id": str(practitioner_id),
            "appointment_date": APPT_DATE.isoformat(),
            "start_time_local": f"{start_h:02d}:00:00",
            "duration_minutes": duration,
        },
        headers=_auth(token, f"rehearsal-prop-{appt_id}"),
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def _confirmed_payload(proposal):
    payload = deepcopy(proposal["confirm_payload"])
    payload["confirmed"] = True
    return payload


def _counts(db):
    return (
        db.query(Appointment).count(),
        db.query(AppointmentAuditLog).count(),
        db.query(AppointmentCommandIdempotency).count(),
    )


def _response_tuple(result):
    if isinstance(result, Response):
        return result.status_code, json.loads(result.body)
    return 200, result.model_dump(mode="json")


def _invoke_confirm(SessionFactory, *, user_id, payload, key):
    with SessionFactory() as worker_db:
        current_user = worker_db.query(User).filter(User.id == user_id).one()
        result = appointments_router.confirm_update_proposal_route(
            body=BernieUpdateProposalConfirmationIn(**payload),
            idempotency_key=key,
            db=worker_db,
            current_user=current_user,
        )
    return _response_tuple(result)


def _invoke_confirm_raising(SessionFactory, *, user_id, payload, key):
    with SessionFactory() as worker_db:
        current_user = worker_db.query(User).filter(User.id == user_id).one()
        appointments_router.confirm_update_proposal_route(
            body=BernieUpdateProposalConfirmationIn(**payload),
            idempotency_key=key,
            db=worker_db,
            current_user=current_user,
        )


# ── M1: one full proposal carries practitioner, local time and duration ───────


def test_m1_proposal_carries_all_three_values_without_any_mutation(
    client,
    db,
    rehearsal_practice,
    rehearsal_practitioners,
    rehearsal_patient,
    rehearsal_user,
):
    original, target = rehearsal_practitioners
    appt = _make_appointment(db, rehearsal_practice, original, rehearsal_patient)
    token = make_token(rehearsal_user)
    before = _counts(db)

    proposal = _propose(client, token, appt.id, practitioner_id=target.id)

    assert proposal["intent"] == "update_appointment"
    assert proposal["safe"] is True
    assert proposal["requires_confirmation"] is True
    assert proposal["autonomy_tier"] == "proposal"
    assert proposal["patient_identity"] == "linked"
    assert proposal["blocks"] == []
    cmd = proposal["command"]
    assert cmd["appointment_id"] == str(appt.id)
    assert cmd["practitioner_id"] == str(target.id)
    assert cmd["start_time_local"] == "14:00:00"
    assert cmd["duration_minutes"] == 30

    confirm_payload = proposal["confirm_payload"]
    assert confirm_payload["confirmed"] is False
    proposal_cmd = confirm_payload["update_proposal"]["command"]
    assert proposal_cmd["practitioner_id"] == str(target.id)
    assert proposal_cmd["start_time_local"] == "14:00:00"
    assert proposal_cmd["duration_minutes"] == 30

    # The proposal performs no appointment, audit or idempotency mutation.
    assert _counts(db) == before
    db.refresh(appt)
    assert appt.practitioner_id == original.id
    assert appt.start_time_local == time(9, 0)
    assert appt.duration_minutes == 15


# ── M2: confirmation commits all three values with one correlated audit/ledger ─


def test_m2_confirmation_commits_three_values_with_correlated_audit_and_ledger(
    engine,
    client,
    db,
    rehearsal_practice,
    rehearsal_practitioners,
    rehearsal_patient,
    rehearsal_user,
):
    original, target = rehearsal_practitioners
    appt = _make_appointment(db, rehearsal_practice, original, rehearsal_patient)
    token = make_token(rehearsal_user)
    proposal = _propose(client, token, appt.id, practitioner_id=target.id)
    payload = _confirmed_payload(proposal)
    db.commit()
    SessionFactory = sessionmaker(bind=engine)
    before = _counts(db)

    status, data = _invoke_confirm(
        SessionFactory,
        user_id=rehearsal_user.id,
        payload=payload,
        key="rehearsal-m2-key",
    )

    assert status == 200, data
    assert data["safe"] is True
    assert data["autonomy_tier"] == "confirmed_write"
    assert data["appointment"]["id"] == str(appt.id)
    assert data["appointment"]["practitioner_id"] == str(target.id)
    assert data["appointment"]["start_time_local"] == "14:00:00"
    assert data["appointment"]["duration_minutes"] == 30
    assert "bernie_confirm_update_proposal" in data["audit_evidence"]

    db.expire_all()
    db.refresh(appt)
    assert appt.practitioner_id == target.id
    assert appt.start_time_local == time(14, 0)
    assert appt.duration_minutes == 30
    assert _counts(db) == (before[0], before[1] + 1, before[2] + 1)

    ledger = db.query(AppointmentCommandIdempotency).one()
    assert ledger.state == "completed"
    assert ledger.operation_id == OPERATION_ID
    assert ledger.route_family == ROUTE_FAMILY
    assert ledger.result_kind == "confirmed_write"
    assert ledger.target_appointment_id == appt.id
    assert ledger.audit_log_id is not None
    assert ledger.response_body_json == data

    audit = db.query(AppointmentAuditLog).one()
    assert audit.action == AppointmentAuditAction.update
    assert audit.appointment_id == appt.id
    assert audit.command_id == ledger.id
    assert ledger.audit_log_id == audit.id


# ── M3: stale authoritative truth blocks confirmation without mutation ────────


def test_m3_stale_truth_blocks_combined_confirmation_without_mutation(
    client,
    db,
    rehearsal_practice,
    rehearsal_practitioners,
    rehearsal_patient,
    rehearsal_user,
):
    original, target = rehearsal_practitioners
    appt = _make_appointment(db, rehearsal_practice, original, rehearsal_patient)
    token = make_token(rehearsal_user)
    proposal = _propose(client, token, appt.id, practitioner_id=target.id)
    payload = _confirmed_payload(proposal)

    # Independently committed intervening authoritative truth change.
    appt.reason = "intervening stale-truth change"
    db.commit()
    before = _counts(db)

    resp = client.post(
        CONFIRM_URL, json=payload, headers=_auth(token, "rehearsal-m3-key")
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    block_codes = [block["code"] for block in data["blocks"]]
    assert "stale_update_proposal_freshness_id" in block_codes
    assert _counts(db) == before
    db.refresh(appt)
    assert appt.practitioner_id == original.id
    assert appt.start_time_local == time(9, 0)
    assert appt.duration_minutes == 15
    assert appt.reason == "intervening stale-truth change"


# ── M4: a newly created target conflict blocks confirmation without mutation ──


def test_m4_new_conflict_blocks_combined_confirmation_without_mutation(
    client,
    db,
    rehearsal_practice,
    rehearsal_practitioners,
    rehearsal_patient,
    rehearsal_user,
):
    original, target = rehearsal_practitioners
    appt = _make_appointment(db, rehearsal_practice, original, rehearsal_patient)
    token = make_token(rehearsal_user)
    proposal = _propose(client, token, appt.id, practitioner_id=target.id)
    payload = _confirmed_payload(proposal)

    # Insert a conflicting appointment for the target practitioner at the
    # proposed interval (14:00-14:30) after the proposal was issued.
    _make_appointment(
        db,
        rehearsal_practice,
        target,
        rehearsal_patient,
        start_h=14,
        start_m=0,
        duration=15,
    )
    db.commit()
    before = _counts(db)

    resp = client.post(
        CONFIRM_URL, json=payload, headers=_auth(token, "rehearsal-m4-key")
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    block_codes = [block["code"] for block in data["blocks"]]
    assert "update_proposal_revalidation_blocked" in block_codes
    assert "appointment_conflict" in block_codes
    assert _counts(db) == before
    db.refresh(appt)
    assert appt.practitioner_id == original.id
    assert appt.start_time_local == time(9, 0)
    assert appt.duration_minutes == 15


# ── M5: deactivating the target practitioner blocks confirmation ──────────────


def test_m5_inactive_target_practitioner_blocks_combined_confirmation_without_mutation(
    client,
    db,
    rehearsal_practice,
    rehearsal_practitioners,
    rehearsal_patient,
    rehearsal_user,
):
    original, target = rehearsal_practitioners
    appt = _make_appointment(db, rehearsal_practice, original, rehearsal_patient)
    token = make_token(rehearsal_user)
    proposal = _propose(client, token, appt.id, practitioner_id=target.id)
    payload = _confirmed_payload(proposal)

    target.is_active = False
    db.commit()
    before = _counts(db)

    resp = client.post(
        CONFIRM_URL, json=payload, headers=_auth(token, "rehearsal-m5-key")
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["safe"] is False
    assert data["autonomy_tier"] == "blocked"
    block_codes = [block["code"] for block in data["blocks"]]
    assert "update_proposal_revalidation_blocked" in block_codes
    assert "practitioner_inactive" in block_codes
    assert _counts(db) == before
    db.refresh(appt)
    assert appt.practitioner_id == original.id
    assert appt.start_time_local == time(9, 0)
    assert appt.duration_minutes == 15


# ── M6: exact same-key replay and different-body key conflict ─────────────────


def test_m6_exact_replay_returns_stored_and_different_body_conflicts_without_mutation(
    engine,
    client,
    db,
    rehearsal_practice,
    rehearsal_practitioners,
    rehearsal_patient,
    rehearsal_user,
):
    original, target = rehearsal_practitioners
    appt = _make_appointment(db, rehearsal_practice, original, rehearsal_patient)
    token = make_token(rehearsal_user)
    proposal = _propose(client, token, appt.id, practitioner_id=target.id)
    payload = _confirmed_payload(proposal)
    db.commit()
    SessionFactory = sessionmaker(bind=engine)

    first_status, first_body = _invoke_confirm(
        SessionFactory,
        user_id=rehearsal_user.id,
        payload=payload,
        key="rehearsal-m6-key",
    )
    assert first_status == 200
    db.expire_all()
    after_first = _counts(db)

    # Exact replay from a fresh session returns the exact stored body unchanged.
    replay_status, replay_body = _invoke_confirm(
        SessionFactory,
        user_id=rehearsal_user.id,
        payload=payload,
        key="rehearsal-m6-key",
    )
    assert replay_status == 200
    assert replay_body == first_body
    db.expire_all()
    assert _counts(db) == after_first

    # A different validated body with the same key is a typed conflict.
    changed = deepcopy(payload)
    changed["confirmed_warnings"] = ["m6-different-body"]
    with pytest.raises(HTTPException) as excinfo:
        _invoke_confirm(
            SessionFactory,
            user_id=rehearsal_user.id,
            payload=changed,
            key="rehearsal-m6-key",
        )
    assert excinfo.value.status_code == 409
    assert excinfo.value.detail["code"] == "idempotency_key_conflict"
    db.expire_all()
    assert _counts(db) == after_first
    db.refresh(appt)
    assert appt.practitioner_id == target.id
    assert appt.start_time_local == time(14, 0)
    assert appt.duration_minutes == 30


# ── M7: injected pre-commit rollback then clean same-key retry and replay ─────


def test_m7_injected_precommit_failure_rolls_back_then_clean_retry_and_mutation_free_replay(
    engine,
    client,
    db,
    rehearsal_practice,
    rehearsal_practitioners,
    rehearsal_patient,
    rehearsal_user,
    monkeypatch,
):
    original, target = rehearsal_practitioners
    appt = _make_appointment(db, rehearsal_practice, original, rehearsal_patient)
    token = make_token(rehearsal_user)
    proposal = _propose(client, token, appt.id, practitioner_id=target.id)
    payload = _confirmed_payload(proposal)
    db.commit()
    SessionFactory = sessionmaker(bind=engine)
    before = _counts(db)
    original_complete = appointments_router.complete_appointment_command

    def fail_before_commit(*args, **kwargs):
        raise RuntimeError("injected M7 pre-commit failure")

    with monkeypatch.context() as scoped_patch:
        scoped_patch.setattr(
            appointments_router, "complete_appointment_command", fail_before_commit
        )
        with pytest.raises(RuntimeError, match="injected M7 pre-commit failure"):
            _invoke_confirm_raising(
                SessionFactory,
                user_id=rehearsal_user.id,
                payload=payload,
                key="rehearsal-m7-key",
            )

    assert appointments_router.complete_appointment_command is original_complete
    db.expire_all()
    assert _counts(db) == before
    db.refresh(appt)
    assert appt.practitioner_id == original.id
    assert appt.start_time_local == time(9, 0)
    assert appt.duration_minutes == 15
    assert db.query(AppointmentAuditLog).count() == 0
    assert db.query(AppointmentCommandIdempotency).count() == 0

    # Clean same-key retry commits exactly one correlated update/audit/ledger.
    retry_status, retry_body = _invoke_confirm(
        SessionFactory,
        user_id=rehearsal_user.id,
        payload=payload,
        key="rehearsal-m7-key",
    )
    assert retry_status == 200
    assert retry_body["safe"] is True
    db.expire_all()
    assert _counts(db) == (before[0], before[1] + 1, before[2] + 1)
    db.refresh(appt)
    assert appt.practitioner_id == target.id
    assert appt.start_time_local == time(14, 0)
    assert appt.duration_minutes == 30
    ledger = db.query(AppointmentCommandIdempotency).one()
    audit = db.query(AppointmentAuditLog).one()
    assert ledger.state == "completed"
    assert ledger.target_appointment_id == appt.id
    assert audit.command_id == ledger.id
    assert ledger.audit_log_id == audit.id

    # Mutation-free replay after the clean retry.
    replay_status, replay_body = _invoke_confirm(
        SessionFactory,
        user_id=rehearsal_user.id,
        payload=payload,
        key="rehearsal-m7-key",
    )
    assert replay_status == 200
    assert replay_body == retry_body
    db.expire_all()
    assert _counts(db) == (before[0], before[1] + 1, before[2] + 1)
