from __future__ import annotations

import copy
import hmac
import json
import uuid
from contextlib import contextmanager
from datetime import date, datetime, time, timedelta, timezone
from types import SimpleNamespace

import pytest

from app.models.appointments import AppointmentStatus, BookingChannel
from app.models.tenancy import UserRole
from app.schemas.appointments import (
    AppointmentStatusCommand,
    AppointmentStatusProposalConfirmationIn,
    AppointmentStatusProposalOut,
    AppointmentWaitingAreaCommand,
    AppointmentWaitingAreaProposalOut,
)
from app.services.appointment_status_physical import (
    StatusConfirmAuthorityRevoked,
    StatusConfirmPhysicalDecision,
    StatusConfirmTargetUnavailable,
)
from app.services.appointment_status_product_adapter import (
    PROPOSAL_VERSION_BINDING_SCHEMA,
    STATUS_CONFIRM_EVIDENCE_PURPOSE,
    appointment_status_state,
    authenticated_session_reference,
    compose_product_status_confirm,
    mint_status_proposal_version_binding,
    status_proposal_freshness_id,
    status_signed_confirmation_payload,
    verify_status_proposal_version_binding,
)
from app.services.bernie_turn_evidence import mint_signed_confirmation_evidence


SESSION_SECRET = b"session-secret-for-authenticated-status-ref"
VERSION_SECRET = b"proposal-version-binding-secret-32b"
IDEMPOTENCY_SECRET = b"idempotency-secret-for-status-confirm"
BINDING_SECRET = b"session-binding-secret-for-status-confirm"
EVIDENCE_SECRET = "authored-synthetic-evidence-secret"


def _appointment(
    *,
    status: AppointmentStatus = AppointmentStatus.Booked,
    version: int = 7,
    waiting_area_id: uuid.UUID | None = None,
) -> SimpleNamespace:
    start = datetime(2026, 8, 13, 0, 0, tzinfo=timezone.utc)
    practitioner_id = uuid.uuid4()
    return SimpleNamespace(
        id=uuid.uuid4(),
        practice_id=uuid.uuid4(),
        patient_id=None,
        patient_name_provisional="Synthetic Person",
        practitioner_id=practitioner_id,
        appointment_type_id=None,
        location_id=None,
        start_time=start,
        appointment_date=date(2026, 8, 13),
        start_time_local=time(10, 0),
        end_time=start + timedelta(minutes=15),
        duration_minutes=15,
        status=status,
        reason="Authored synthetic status rehearsal",
        notes=None,
        cancellation_reason=None,
        status_reason_code=None,
        booked_via=BookingChannel.Receptionist,
        waiting_room=None,
        waiting_area_id=waiting_area_id,
        queue_position=None,
        appointment_state_version=version,
        created_at=start - timedelta(days=1),
        patient=None,
        practitioner=SimpleNamespace(
            id=practitioner_id,
            first_name="Synthetic",
            last_name="Practitioner",
            provider_number=None,
            ahpra_number=None,
        ),
        appointment_type=None,
        breaks_overlap=[],
    )


def _user(appointment: SimpleNamespace, **overrides: object) -> SimpleNamespace:
    values = {
        "id": uuid.uuid4(),
        "practice_id": appointment.practice_id,
        "role": UserRole.Receptionist,
        "is_active": True,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _body(
    appointment: SimpleNamespace,
    user: SimpleNamespace,
    *,
    target_status: AppointmentStatus = AppointmentStatus.Confirmed,
    confirmed_warnings: list[str] | None = None,
) -> tuple[AppointmentStatusProposalConfirmationIn, dict[str, object]]:
    command = AppointmentStatusCommand(
        appointment_id=appointment.id,
        status=target_status,
        waiting_area_id=None,
        waiting_area_id_supplied=False,
        clears_waiting_area=target_status
        in {
            AppointmentStatus.Completed,
            AppointmentStatus.Cancelled,
            AppointmentStatus.DNA,
            AppointmentStatus.NoShow,
        },
        status_reason_code=None,
    )
    current_state = appointment_status_state(appointment)
    freshness = status_proposal_freshness_id(command, current_state)
    evidence_payload = status_signed_confirmation_payload(
        practice_id=user.practice_id,
        actor_id=user.id,
        command=command,
        current_state=current_state,
        freshness_id=freshness,
    )
    evidence = mint_signed_confirmation_evidence(
        evidence_payload,
        evidence_purpose=STATUS_CONFIRM_EVIDENCE_PURPOSE,
        secret=EVIDENCE_SECRET,
    )
    binding = mint_status_proposal_version_binding(
        evidence,
        source_version=current_state["source_version"],
        secret=VERSION_SECRET,
    )
    proposal = AppointmentStatusProposalOut(
        safe=True,
        requires_confirmation=True,
        autonomy_tier="proposal",
        summary="Confirm authored-synthetic appointment status.",
        command=command,
        warnings=[],
        blocks=[],
        status_proposal_freshness_id=freshness,
        signed_confirmation_evidence=evidence,
        signed_confirmation_evidence_required=True,
    )
    return (
        AppointmentStatusProposalConfirmationIn(
            confirmed=True,
            status_proposal=proposal,
            confirmed_warnings=confirmed_warnings or [],
            status_proposal_freshness_id=freshness,
            signed_confirmation_evidence=evidence,
            signed_confirmation_evidence_required=True,
        ),
        binding,
    )


class FakeCommandSession:
    def __init__(self, appointment: SimpleNamespace) -> None:
        self.appointment = appointment
        self.audits: list[object] = []
        self.context_practice_ids: list[str] = []
        self.refresh_count = 0
        self.closed = False

    def execute(self, _statement: object, parameters: dict[str, str]) -> None:
        self.context_practice_ids.append(parameters["practice_id"])

    def add(self, value: object) -> None:
        self.audits.append(value)

    def flush(self) -> None:
        return None

    def refresh(self, value: object) -> None:
        assert value is self.appointment
        self.appointment.appointment_state_version += 1
        self.refresh_count += 1

    def close(self) -> None:
        self.closed = True


class FakeStatusTransaction:
    def __init__(self, appointment: SimpleNamespace) -> None:
        self.appointment = appointment
        self.records: dict[tuple[str, str, str], SimpleNamespace] = {}
        self.entries = 0

    @contextmanager
    def __call__(self, db: FakeCommandSession, **arguments: object):
        self.entries += 1
        practice = SimpleNamespace(id=arguments["practice_id"])
        if str(self.appointment.id) != str(arguments["target_appointment_id"]):
            raise StatusConfirmTargetUnavailable("target unavailable")
        if not arguments["practice_is_active"](practice):
            raise StatusConfirmTargetUnavailable("practice unavailable")
        if not arguments["current_authority"](practice, self.appointment):
            raise StatusConfirmAuthorityRevoked("authority unavailable")

        key = (
            str(arguments["practice_id"]),
            str(arguments["actor_user_id"]),
            str(arguments["idempotency_key_hash"]),
        )
        record = self.records.get(key)
        inserted = record is None
        if inserted:
            record = SimpleNamespace(
                id=uuid.uuid4(),
                state="in_progress",
                actor_role=arguments["actor_role"],
                target_appointment_id=self.appointment.id,
                request_body_hash=arguments["request_body_hash"],
                session_binding_digest=arguments["session_binding_digest"],
                response_body_hash=None,
                response_body_json=None,
                response_body_canonical_bytes=None,
            )
            self.records[key] = record

        if not arguments["current_authority"](practice, self.appointment):
            if inserted:
                del self.records[key]
            raise StatusConfirmAuthorityRevoked("authority unavailable")

        if inserted:
            kind = "new_command"
        elif (
            record.actor_role != arguments["actor_role"]
            or str(record.target_appointment_id) != str(arguments["target_appointment_id"])
            or record.request_body_hash != arguments["request_body_hash"]
            or not hmac.compare_digest(
                record.session_binding_digest,
                arguments["session_binding_digest"],
            )
        ):
            kind = "conflict"
        elif record.state == "completed":
            kind = "replay"
        else:
            kind = "in_progress_not_replayable"

        decision = StatusConfirmPhysicalDecision(
            kind=kind,
            appointment=self.appointment,
            record=record,
            pre_state_version=self.appointment.appointment_state_version,
            response_body_canonical_bytes=(
                record.response_body_canonical_bytes if kind == "replay" else None
            ),
        )
        before = copy.deepcopy(vars(self.appointment))
        audit_count = len(db.audits)
        try:
            yield decision
        except Exception:
            vars(self.appointment).clear()
            vars(self.appointment).update(before)
            del db.audits[audit_count:]
            if inserted:
                self.records.pop(key, None)
            raise


def _run(
    body: AppointmentStatusProposalConfirmationIn,
    binding: dict[str, object],
    appointment: SimpleNamespace,
    user: SimpleNamespace,
    *,
    db: FakeCommandSession | None = None,
    physical: FakeStatusTransaction | None = None,
    bearer: str = "synthetic-authenticated-bearer",
    user_loader=None,
    session_secret: bytes = SESSION_SECRET,
    version_secret: bytes = VERSION_SECRET,
):
    db = db or FakeCommandSession(appointment)
    physical = physical or FakeStatusTransaction(appointment)
    session_calls = {"count": 0}

    def command_session_factory() -> FakeCommandSession:
        session_calls["count"] += 1
        return db

    result = compose_product_status_confirm(
        body,
        authenticated_user=user,
        authenticated_bearer_token=bearer,
        idempotency_key="synthetic-idempotency-key",
        proposal_version_binding=binding,
        command_session_factory=command_session_factory,
        authenticated_session_secret=session_secret,
        proposal_version_binding_secret=version_secret,
        idempotency_secret=IDEMPOTENCY_SECRET,
        session_binding_secret=BINDING_SECRET,
        evidence_secret=EVIDENCE_SECRET,
        user_loader=user_loader or (lambda _db, _actor_id: user),
        transaction_factory=physical,
    )
    return result, db, physical, session_calls


def test_clean_execute_and_response_loss_retry_are_byte_identical() -> None:
    appointment = _appointment()
    user = _user(appointment)
    body, binding = _body(appointment, user)
    db = FakeCommandSession(appointment)
    physical = FakeStatusTransaction(appointment)

    first, _, _, _ = _run(body, binding, appointment, user, db=db, physical=physical)
    second, _, _, _ = _run(body, binding, appointment, user, db=db, physical=physical)

    assert first.kind == "committed"
    assert second.kind == "replay"
    assert first.stored_response_bytes == second.stored_response_bytes
    assert json.loads(first.stored_response_bytes) == first.body == second.body
    assert appointment.status is AppointmentStatus.Confirmed
    assert appointment.appointment_state_version == 8
    assert db.refresh_count == 1
    assert len(db.audits) == 1
    audit = db.audits[0]
    record = next(iter(physical.records.values()))
    assert audit.command_id == record.id
    assert record.audit_log_id == audit.id
    assert record.bernie_session_id == audit.bernie_session_id
    assert audit.bernie_session_id == authenticated_session_reference(
        "synthetic-authenticated-bearer", secret=SESSION_SECRET
    )
    assert "synthetic-authenticated-bearer" not in json.dumps(first.body)
    assert len(audit.bernie_session_id) == 64


def test_proposal_version_binding_is_exact_and_cross_evidence_safe() -> None:
    appointment = _appointment()
    user = _user(appointment)
    body, binding = _body(appointment, user)
    evidence = body.signed_confirmation_evidence

    assert binding["schema_version"] == PROPOSAL_VERSION_BINDING_SCHEMA
    assert verify_status_proposal_version_binding(
        binding,
        signed_confirmation_evidence=evidence,
        secret=VERSION_SECRET,
    ) == 7

    tampered = dict(binding)
    tampered["source_version"] = 8
    with pytest.raises(ValueError, match="does not verify"):
        verify_status_proposal_version_binding(
            tampered,
            signed_confirmation_evidence=evidence,
            secret=VERSION_SECRET,
        )

    other_evidence = dict(evidence)
    other_evidence["signature"] = "0" * 64
    with pytest.raises(ValueError, match="evidence mismatch"):
        verify_status_proposal_version_binding(
            binding,
            signed_confirmation_evidence=other_evidence,
            secret=VERSION_SECRET,
        )


@pytest.mark.parametrize(
    ("bearer", "session_secret", "version_secret"),
    [
        ("", SESSION_SECRET, VERSION_SECRET),
        ("synthetic-authenticated-bearer", b"short", VERSION_SECRET),
        ("synthetic-authenticated-bearer", SESSION_SECRET, b"short"),
    ],
)
def test_invalid_server_owned_session_or_version_inputs_stop_before_session(
    bearer: str,
    session_secret: bytes,
    version_secret: bytes,
) -> None:
    appointment = _appointment()
    user = _user(appointment)
    body, binding = _body(appointment, user)

    result, _db, physical, session_calls = _run(
        body,
        binding,
        appointment,
        user,
        bearer=bearer,
        session_secret=session_secret,
        version_secret=version_secret,
    )

    assert result.kind == "error"
    assert result.status_code == 403
    assert session_calls["count"] == 0
    assert physical.entries == 0


def test_waiting_area_union_is_rejected_before_session_construction() -> None:
    appointment = _appointment()
    user = _user(appointment)
    status_body, binding = _body(appointment, user)
    waiting_proposal = AppointmentWaitingAreaProposalOut(
        safe=True,
        requires_confirmation=True,
        autonomy_tier="proposal",
        summary="Authored synthetic waiting-area proposal.",
        command=AppointmentWaitingAreaCommand(
            appointment_id=appointment.id,
            waiting_area_id=uuid.uuid4(),
            clears_waiting_area=False,
        ),
    )
    body = AppointmentStatusProposalConfirmationIn(
        confirmed=True,
        status_proposal=waiting_proposal,
        signed_confirmation_evidence=status_body.signed_confirmation_evidence,
    )

    result, _db, physical, session_calls = _run(body, binding, appointment, user)

    assert result.kind == "blocked"
    assert result.body["blocks"][0]["code"] == "unsupported_status_confirm_variant"
    assert session_calls["count"] == 0
    assert physical.entries == 0


def test_revocation_on_second_current_authority_check_rolls_back() -> None:
    appointment = _appointment()
    user = _user(appointment)
    body, binding = _body(appointment, user)
    calls = {"count": 0}

    def user_loader(_db, _actor_id):
        calls["count"] += 1
        if calls["count"] == 1:
            return user
        return _user(appointment, id=user.id, is_active=False)

    result, db, physical, _ = _run(
        body,
        binding,
        appointment,
        user,
        user_loader=user_loader,
    )

    assert result.kind == "error"
    assert result.status_code == 403
    assert result.body["detail"]["code"] == "current_authority_unavailable"
    assert appointment.status is AppointmentStatus.Booked
    assert appointment.appointment_state_version == 7
    assert db.audits == []
    assert physical.records == {}


@pytest.mark.parametrize(
    "user_overrides",
    [
        {"is_active": False},
        {"role": "Guest"},
    ],
)
def test_initial_inactive_or_unrecognised_role_stops_before_transaction(
    user_overrides: dict[str, object],
) -> None:
    appointment = _appointment()
    user = _user(appointment, **user_overrides)
    body, binding = _body(appointment, user)

    result, db, physical, _ = _run(body, binding, appointment, user)

    assert result.kind == "error"
    assert result.status_code == 403
    assert result.body["detail"]["code"] == "current_authority_unavailable"
    assert physical.entries == 0
    assert db.audits == []


def test_current_practice_mismatch_is_rejected_inside_authority_boundary() -> None:
    appointment = _appointment()
    user = _user(appointment, practice_id=uuid.uuid4())
    body, binding = _body(appointment, user)

    result, db, physical, _ = _run(body, binding, appointment, user)

    assert result.kind == "error"
    assert result.status_code == 403
    assert physical.entries == 1
    assert db.audits == []
    assert physical.records == {}


def test_revocation_on_first_current_authority_check_creates_no_claim() -> None:
    appointment = _appointment()
    user = _user(appointment)
    body, binding = _body(appointment, user)
    revoked = _user(appointment, id=user.id, is_active=False)

    result, db, physical, _ = _run(
        body,
        binding,
        appointment,
        user,
        user_loader=lambda _db, _actor_id: revoked,
    )

    assert result.kind == "error"
    assert result.status_code == 403
    assert db.audits == []
    assert physical.records == {}


@pytest.mark.parametrize(
    "binding_mutator",
    [
        lambda _binding: {},
        lambda binding: {**binding, "unexpected": True},
        lambda binding: {**binding, "source_version": 0},
        lambda binding: {**binding, "signature": "0" * 64},
    ],
)
def test_invalid_proposal_version_binding_stops_before_command_session(
    binding_mutator,
) -> None:
    appointment = _appointment()
    user = _user(appointment)
    body, binding = _body(appointment, user)

    result, db, physical, session_calls = _run(
        body,
        binding_mutator(binding),
        appointment,
        user,
    )

    assert result.kind == "error"
    assert result.status_code == 403
    assert session_calls["count"] == 0
    assert physical.entries == 0
    assert db.audits == []


def test_changed_locked_generation_stops_without_effect() -> None:
    proposal_snapshot = _appointment(version=7)
    user = _user(proposal_snapshot)
    body, binding = _body(proposal_snapshot, user)
    locked = copy.deepcopy(proposal_snapshot)
    locked.appointment_state_version = 8

    result, db, physical, _ = _run(body, binding, locked, user)

    assert result.kind == "blocked"
    assert result.body["blocks"][0]["code"] == "locked_request_digest_changed"
    assert db.audits == []
    assert locked.appointment_state_version == 8
    assert physical.records == {}


@pytest.mark.parametrize("status", [AppointmentStatus.Completed, AppointmentStatus.Cancelled])
def test_terminal_source_or_same_state_is_blocked_before_effect(status: AppointmentStatus) -> None:
    appointment = _appointment(status=status)
    user = _user(appointment)
    body, binding = _body(appointment, user, target_status=AppointmentStatus.Confirmed)

    result, db, _physical, _ = _run(body, binding, appointment, user)

    assert result.kind == "blocked"
    assert result.body["blocks"][0]["code"] == "transition_policy_deferred"
    assert db.audits == []


def test_same_state_is_blocked_before_effect() -> None:
    appointment = _appointment(status=AppointmentStatus.Confirmed)
    user = _user(appointment)
    body, binding = _body(appointment, user, target_status=AppointmentStatus.Confirmed)

    result, db, _physical, _ = _run(body, binding, appointment, user)

    assert result.kind == "blocked"
    assert result.body["blocks"][0]["code"] == "already_in_status"
    assert db.audits == []


def test_warning_mismatch_and_signed_evidence_tamper_fail_closed() -> None:
    appointment = _appointment(waiting_area_id=uuid.uuid4())
    user = _user(appointment)
    body, binding = _body(
        appointment,
        user,
        target_status=AppointmentStatus.Cancelled,
        confirmed_warnings=[],
    )

    warning_result, db, _physical, _ = _run(body, binding, appointment, user)
    assert warning_result.kind == "blocked"
    assert warning_result.body["blocks"][0]["code"] == "warning_acknowledgement_mismatch"
    assert db.audits == []

    tampered_body = body.model_copy(deep=True)
    tampered_body.signed_confirmation_evidence["signature"] = "0" * 64
    evidence_result, _db, physical, session_calls = _run(
        tampered_body,
        binding,
        appointment,
        user,
    )
    assert evidence_result.kind == "error"
    assert evidence_result.status_code == 403
    assert session_calls["count"] == 0
    assert physical.entries == 0


def test_bad_public_projection_rolls_back_the_authored_synthetic_effect() -> None:
    appointment = _appointment()
    appointment.practitioner = None
    user = _user(appointment)
    body, binding = _body(appointment, user)

    result, db, physical, _ = _run(body, binding, appointment, user)

    assert result.kind == "error"
    assert result.status_code == 503
    assert result.body["detail"]["code"] == "status_confirm_transaction_unavailable"
    assert appointment.status is AppointmentStatus.Booked
    assert appointment.appointment_state_version == 7
    assert db.audits == []
    assert physical.records == {}
