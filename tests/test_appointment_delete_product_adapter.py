from __future__ import annotations

import copy
import hashlib
import hmac
import json
import uuid
from contextlib import contextmanager
from types import SimpleNamespace

import pytest

from app.models.appointments import AppointmentStatus
from app.models.tenancy import UserRole
from app.schemas.appointments import (
    AppointmentDeleteCommand,
    AppointmentDeleteProposalConfirmationIn,
    AppointmentDeleteProposalOut,
    AppointmentProposalIssue,
)
from app.services.appointment_delete_composition import (
    canonical_delete_confirm_envelope_bytes,
)
from app.services.appointment_delete_physical import (
    DeleteConfirmPhysicalDecision,
    DeleteConfirmTargetUnavailable,
)
from app.services.appointment_delete_product_adapter import (
    DELETE_CONFIRM_EVIDENCE_PURPOSE,
    DELETE_PROPOSAL_VERSION_BINDING_SCHEMA,
    appointment_delete_state,
    authenticated_session_reference,
    compose_product_delete_confirm,
    delete_command_payload,
    delete_proposal_freshness_id,
    delete_signed_confirmation_payload,
    mint_delete_proposal_version_binding,
    required_warning_codes,
    verify_delete_proposal_version_binding,
)
from app.services.bernie_turn_evidence import mint_signed_confirmation_evidence


SESSION_SECRET = b"session-secret-for-authenticated-delete-ref"
VERSION_SECRET = b"proposal-version-binding-secret-32b"
IDEMPOTENCY_SECRET = b"idempotency-secret-for-delete-confirm"
BINDING_SECRET = b"session-binding-secret-for-delete-confirm"
EVIDENCE_SECRET = "authored-synthetic-delete-evidence-secret"


def _appointment(
    *,
    status: AppointmentStatus = AppointmentStatus.Booked,
    version: int = 7,
    waiting_area_id: uuid.UUID | None = None,
    status_reason_code: str | None = None,
    cancellation_reason: str | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        practice_id=uuid.uuid4(),
        patient_id=None,
        status=status,
        status_reason_code=status_reason_code,
        waiting_area_id=waiting_area_id,
        cancellation_reason=cancellation_reason,
        appointment_state_version=version,
    )


def _user(appointment: SimpleNamespace, **overrides: object) -> SimpleNamespace:
    values = {
        "id": uuid.uuid4(),
        "practice_id": appointment.practice_id,
        "role": UserRole.Receptionist,
        "is_active": True,
        "authority_generation": 3,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _body(
    appointment: SimpleNamespace,
    user: SimpleNamespace,
    *,
    confirmed_warnings: list[str] | None = None,
    status_reason_code: str = "PATIENT_CANCELLED",
    cancellation_reason: str | None = None,
) -> tuple[AppointmentDeleteProposalConfirmationIn, dict[str, object]]:
    clears_waiting_area = appointment.waiting_area_id is not None
    command = AppointmentDeleteCommand(
        appointment_id=appointment.id,
        clears_waiting_area=clears_waiting_area,
        cancellation_reason=cancellation_reason,
        status_reason_code=status_reason_code,
    )
    current_state = appointment_delete_state(appointment)
    freshness = delete_proposal_freshness_id(command, current_state)
    evidence_payload = delete_signed_confirmation_payload(
        practice_id=user.practice_id,
        actor_id=user.id,
        command=command,
        current_state=current_state,
        freshness_id=freshness,
    )
    evidence = mint_signed_confirmation_evidence(
        evidence_payload,
        evidence_purpose=DELETE_CONFIRM_EVIDENCE_PURPOSE,
        secret=EVIDENCE_SECRET,
    )
    binding = mint_delete_proposal_version_binding(
        evidence,
        source_version=current_state["source_version"],
        secret=VERSION_SECRET,
    )
    required = required_warning_codes(current_state, command)
    proposal = AppointmentDeleteProposalOut(
        safe=True,
        requires_confirmation=True,
        autonomy_tier="proposal",
        summary="Confirm authored-synthetic appointment deletion.",
        command=command,
        warnings=[
            AppointmentProposalIssue(
                code=code,
                severity="warning",
                message="Deleting this appointment will remove the patient from the waiting area.",
            )
            for code in required
        ],
        blocks=[],
        delete_proposal_freshness_id=freshness,
        signed_confirmation_evidence=evidence,
        signed_confirmation_evidence_required=True,
    )
    return (
        AppointmentDeleteProposalConfirmationIn(
            confirmed=True,
            delete_proposal=proposal,
            confirmed_warnings=confirmed_warnings
            if confirmed_warnings is not None
            else list(required),
            delete_proposal_freshness_id=freshness,
            signed_confirmation_evidence=evidence,
            signed_confirmation_evidence_required=True,
        ),
        binding,
    )


class FakeCommandSession:
    def __init__(self, appointment: SimpleNamespace) -> None:
        self.appointment = appointment
        self.audits: list[object] = []
        self.refresh_count = 0
        self.closed = False

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


class FakeDeleteTransaction:
    def __init__(self, appointment: SimpleNamespace) -> None:
        self.appointment = appointment
        self.records: dict[tuple[str, str, str], SimpleNamespace] = {}
        self.entries = 0

    @contextmanager
    def __call__(self, db: FakeCommandSession, **arguments: object):
        self.entries += 1
        if str(self.appointment.id) != str(arguments["target_appointment_id"]):
            raise DeleteConfirmTargetUnavailable("target unavailable")

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
                authority_generation=arguments["signed_authority_generation"],
                completed_receipt_version=None,
                response_status_code=None,
                response_body_hash=None,
                response_body_json=None,
                response_body_canonical_bytes=None,
                result_kind=None,
                audit_log_id=None,
                pre_state_version=None,
                post_state_version=None,
                bernie_session_id=None,
            )
            self.records[key] = record

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
            or record.authority_generation != arguments["signed_authority_generation"]
        ):
            kind = "conflict"
        elif record.state == "completed" and record.completed_receipt_version is None:
            kind = "legacy_receipt_not_replayable"
        elif record.state != "completed":
            kind = "in_progress_not_replayable"
        elif (
            not isinstance(record.response_body_canonical_bytes, bytes)
            or record.response_body_hash
            != hashlib.sha256(record.response_body_canonical_bytes).hexdigest()
            or json.loads(record.response_body_canonical_bytes)
            != record.response_body_json
        ):
            kind = "receipt_integrity_failure"
        else:
            kind = "replay"

        decision = DeleteConfirmPhysicalDecision(
            kind=kind,
            user=None,
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
    body: AppointmentDeleteProposalConfirmationIn,
    binding: dict[str, object],
    appointment: SimpleNamespace,
    user: SimpleNamespace,
    *,
    db: FakeCommandSession | None = None,
    physical: FakeDeleteTransaction | None = None,
    bearer: str = "synthetic-authenticated-bearer",
    session_secret: bytes = SESSION_SECRET,
    version_secret: bytes = VERSION_SECRET,
):
    db = db or FakeCommandSession(appointment)
    physical = physical or FakeDeleteTransaction(appointment)
    session_calls = {"count": 0}

    def command_session_factory() -> FakeCommandSession:
        session_calls["count"] += 1
        return db

    result = compose_product_delete_confirm(
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
        transaction_factory=physical,
    )
    return result, db, physical, session_calls


def test_clean_execute_and_response_loss_retry_are_byte_identical() -> None:
    appointment = _appointment()
    user = _user(appointment)
    body, binding = _body(appointment, user)
    db = FakeCommandSession(appointment)
    physical = FakeDeleteTransaction(appointment)

    first, _, _, _ = _run(body, binding, appointment, user, db=db, physical=physical)
    second, _, _, _ = _run(body, binding, appointment, user, db=db, physical=physical)

    assert first.kind == "committed"
    assert second.kind == "replay"
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.body == second.body
    assert first.stored_response_bytes == second.stored_response_bytes
    assert canonical_delete_confirm_envelope_bytes(first.body) == canonical_delete_confirm_envelope_bytes(
        second.body
    )
    assert appointment.status is AppointmentStatus.Cancelled
    assert appointment.appointment_state_version == 8
    assert appointment.waiting_area_id is None
    assert db.refresh_count == 1
    assert len(db.audits) == 1
    audit = db.audits[0]
    record = next(iter(physical.records.values()))
    assert audit.command_id == record.id
    assert record.audit_log_id == audit.id
    assert audit.action.value == "delete"
    assert audit.status_after.value == "Cancelled"
    assert audit.audit_contract_version == 1
    assert audit.authority_generation == 3
    assert audit.pre_state_version == 7
    assert audit.post_state_version == 8
    assert audit.waiting_area_after_id is None
    assert audit.audit_evidence_codes == [
        "delete_product_adapter_v1",
        "delete_signed_confirmation_evidence_verified",
        "delete_current_authority_rechecked",
    ]
    assert "synthetic-authenticated-bearer" not in json.dumps(first.body)


def test_proposal_version_binding_is_exact_and_cross_evidence_safe() -> None:
    appointment = _appointment()
    user = _user(appointment)
    body, binding = _body(appointment, user)
    evidence = body.signed_confirmation_evidence

    assert binding["schema_version"] == DELETE_PROPOSAL_VERSION_BINDING_SCHEMA
    assert verify_delete_proposal_version_binding(
        binding,
        signed_confirmation_evidence=evidence,
        secret=VERSION_SECRET,
    ) == 7

    tampered = dict(binding)
    tampered["source_version"] = 8
    with pytest.raises(ValueError, match="does not verify"):
        verify_delete_proposal_version_binding(
            tampered,
            signed_confirmation_evidence=evidence,
            secret=VERSION_SECRET,
        )

    other_evidence = dict(evidence)
    other_evidence["signature"] = "0" * 64
    with pytest.raises(ValueError, match="evidence mismatch"):
        verify_delete_proposal_version_binding(
            binding,
            signed_confirmation_evidence=other_evidence,
            secret=VERSION_SECRET,
        )

    wrong_shape = {**binding, "unexpected": True}
    with pytest.raises(ValueError, match="shape"):
        verify_delete_proposal_version_binding(
            wrong_shape,
            signed_confirmation_evidence=evidence,
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


def test_unsupported_delete_variant_blocked_before_session() -> None:
    appointment = _appointment()
    user = _user(appointment)
    body, binding = _body(appointment, user)
    # Replace the typed proposal with a non-delete object. Pydantic assignment
    # is not validated, so the adapter must reject it before any session work.
    body.delete_proposal = SimpleNamespace(  # type: ignore[assignment]
        intent="update_appointment_status",
        blocks=[],
    )

    result, _db, physical, session_calls = _run(body, binding, appointment, user)

    assert result.kind == "blocked"
    assert result.body["blocks"][0]["code"] == "unsupported_delete_confirm_variant"
    assert session_calls["count"] == 0
    assert physical.entries == 0


def test_initial_inactive_or_unrecognised_role_stops_before_transaction() -> None:
    for overrides in ({"is_active": False}, {"role": "Guest"}):
        appointment = _appointment()
        user = _user(appointment, **overrides)
        body, binding = _body(appointment, user)

        result, db, physical, _session_calls = _run(body, binding, appointment, user)

        assert result.kind == "error"
        assert result.status_code == 403
        assert physical.entries == 0
        assert db.audits == []


def test_warning_mismatch_and_signed_evidence_tamper_fail_closed() -> None:
    appointment = _appointment(waiting_area_id=uuid.uuid4())
    user = _user(appointment)
    body, binding = _body(appointment, user, confirmed_warnings=[])

    warning_result, db, _physical, _session = _run(body, binding, appointment, user)
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


def test_command_session_closed_after_use() -> None:
    appointment = _appointment()
    user = _user(appointment)
    body, binding = _body(appointment, user)
    db = FakeCommandSession(appointment)
    physical = FakeDeleteTransaction(appointment)

    result, db, physical, session_calls = _run(
        body, binding, appointment, user, db=db, physical=physical
    )

    assert result.kind == "committed"
    assert db.closed is True
    assert session_calls["count"] == 1


def test_domain_separated_session_reference_binds_actor_and_practice() -> None:
    appointment = _appointment()
    user = _user(appointment)
    ref = authenticated_session_reference(
        "synthetic-authenticated-bearer",
        secret=SESSION_SECRET,
        actor_id=user.id,
        practice_id=user.practice_id,
    )
    assert len(ref) == 64
    other_user = _user(appointment)
    other_ref = authenticated_session_reference(
        "synthetic-authenticated-bearer",
        secret=SESSION_SECRET,
        actor_id=other_user.id,
        practice_id=user.practice_id,
    )
    assert ref != other_ref
    other_practice = _user(appointment, practice_id=uuid.uuid4())
    other_practice_ref = authenticated_session_reference(
        "synthetic-authenticated-bearer",
        secret=SESSION_SECRET,
        actor_id=user.id,
        practice_id=other_practice.practice_id,
    )
    assert ref != other_practice_ref
    with pytest.raises(ValueError):
        authenticated_session_reference("", secret=SESSION_SECRET, actor_id=user.id, practice_id=user.practice_id)
    with pytest.raises(ValueError):
        authenticated_session_reference("token", secret=b"short", actor_id=user.id, practice_id=user.practice_id)


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


def test_missing_authority_generation_stops_before_command_session() -> None:
    appointment = _appointment()
    user = _user(appointment)
    body, binding = _body(appointment, user)
    del user.authority_generation

    result, _db, physical, session_calls = _run(body, binding, appointment, user)

    assert result.kind == "error"
    assert result.status_code == 403
    assert session_calls["count"] == 0
    assert physical.entries == 0


def test_server_owned_authority_generation_is_never_client_supplied() -> None:
    appointment = _appointment()
    user = _user(appointment, authority_generation=11)
    body, binding = _body(appointment, user)
    body.delete_proposal.confirm_payload = {
        "authority_generation": 999,
        "practice_id": "client-practice",
        "actor_role": "PracticeOwner",
    }

    result, _db, physical, _ = _run(body, binding, appointment, user)

    assert result.kind == "committed"
    record = next(iter(physical.records.values()))
    assert record.authority_generation == 11
    assert record.actor_role == "Receptionist"


def test_route_does_not_import_or_call_delete_confirm_services() -> None:
    router = __import__("app.routers.appointments", fromlist=["app"]).__file__
    with open(router, encoding="utf-8") as handle:
        text = handle.read()
    assert "appointment_delete_composition" not in text
    assert "appointment_delete_product_adapter" not in text
    assert "compose_product_delete_confirm" not in text
    assert "compose_delete_confirm" not in text


def test_service_contains_no_provider_network_or_process_import() -> None:
    import ast
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    service_paths = (
        root / "app/services/appointment_delete_composition.py",
        root / "app/services/appointment_delete_product_adapter.py",
    )
    forbidden_prefixes = (
        "google",
        "requests",
        "httpx",
        "socket",
        "subprocess",
        "asyncio.subprocess",
        "sqlalchemy",
    )
    for path in service_paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
        assert not any(name.startswith(forbidden_prefixes) for name in imported)


def test_required_warning_codes_only_fires_when_waiting_area_non_null() -> None:
    appointment = _appointment()
    user = _user(appointment)
    command = delete_command_payload(
        AppointmentDeleteCommand(
            appointment_id=appointment.id,
            clears_waiting_area=False,
            cancellation_reason=None,
            status_reason_code="PATIENT_CANCELLED",
        )
    )
    assert required_warning_codes(
        {"waiting_area_id": None, "status": "Booked"}, command
    ) == []

    appointment_with_area = _appointment(waiting_area_id=uuid.uuid4())
    command_with_clear = delete_command_payload(
        AppointmentDeleteCommand(
            appointment_id=appointment_with_area.id,
            clears_waiting_area=True,
            cancellation_reason=None,
            status_reason_code="PATIENT_CANCELLED",
        )
    )
    assert required_warning_codes(
        {"waiting_area_id": str(uuid.uuid4()), "status": "Booked"}, command_with_clear
    ) == ["waiting_area_cleared"]


def test_signed_payload_excludes_source_version() -> None:
    appointment = _appointment()
    user = _user(appointment)
    current_state = appointment_delete_state(appointment)
    command = AppointmentDeleteCommand(
        appointment_id=appointment.id,
        clears_waiting_area=False,
        cancellation_reason=None,
        status_reason_code="PATIENT_CANCELLED",
    )
    payload = delete_signed_confirmation_payload(
        practice_id=user.practice_id,
        actor_id=user.id,
        command=command,
        current_state=current_state,
        freshness_id="fresh",
    )
    assert "source_version" not in payload
    assert "source_version" not in payload["current_state"]
    assert set(payload["current_state"]) == {
        "appointment_id",
        "status",
        "waiting_area_id",
        "status_reason_code",
        "cancellation_reason",
    }
    assert isinstance(payload["command"], dict)
    assert payload["command"]["kind"] == "delete"


def test_stale_freshness_or_tampered_freshness_id_stops_closed() -> None:
    appointment = _appointment()
    user = _user(appointment)
    body, binding = _body(appointment, user)
    tampered = body.model_copy(deep=True)
    tampered.delete_proposal_freshness_id = "0" * 32

    result, _db, physical, session_calls = _run(tampered, binding, appointment, user)

    assert result.kind == "error"
    assert result.status_code == 403
    assert session_calls["count"] == 0
    assert physical.entries == 0


def test_already_cancelled_status_is_blocked_before_effect() -> None:
    appointment = _appointment(status=AppointmentStatus.Cancelled)
    user = _user(appointment)
    body, binding = _body(appointment, user)

    result, db, physical, _ = _run(body, binding, appointment, user)

    assert result.kind == "blocked"
    assert result.body["blocks"][0]["code"] == "already_cancelled"
    assert db.audits == []
    assert physical.entries == 0
