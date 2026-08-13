"""Generate deterministic authored-synthetic status-confirm product-adapter evidence."""

from __future__ import annotations

import argparse
import copy
import hashlib
import hmac
import json
import sys
import uuid
from contextlib import contextmanager
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.models.appointments import AppointmentStatus, BookingChannel  # noqa: E402
from app.models.tenancy import UserRole  # noqa: E402
from app.schemas.appointments import (  # noqa: E402
    AppointmentStatusCommand,
    AppointmentStatusProposalConfirmationIn,
    AppointmentStatusProposalOut,
    AppointmentWaitingAreaCommand,
    AppointmentWaitingAreaProposalOut,
)
from app.services.appointment_status_physical import (  # noqa: E402
    StatusConfirmAuthorityRevoked,
    StatusConfirmPhysicalDecision,
)
from app.services.appointment_status_product_adapter import (  # noqa: E402
    STATUS_CONFIRM_EVIDENCE_PURPOSE,
    appointment_status_state,
    authenticated_session_reference,
    compose_product_status_confirm,
    mint_status_proposal_version_binding,
    status_confirm_admission_adapter,
    status_proposal_freshness_id,
    status_signed_confirmation_payload,
    verify_status_proposal_version_binding,
)
from app.services.bernie_turn_evidence import (  # noqa: E402
    mint_signed_confirmation_evidence,
)


EVIDENCE_DIR = ROOT / "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-product-adapter-rehearsal"
CONTRACT_PATH = EVIDENCE_DIR / "product-adapter-rehearsal-contract.json"
SCHEMA_PATH = EVIDENCE_DIR / "product-adapter-rehearsal-evidence.schema.json"
DEFAULT_OUTPUT = EVIDENCE_DIR / "product-adapter-rehearsal-evidence.json"
IMPLEMENTATION_PATHS = (
    "app/services/appointment_status_product_adapter.py",
    "scripts/raisa_provider_free_unmounted_status_confirm_product_adapter_rehearsal.py",
    "tests/test_raisa_provider_free_unmounted_status_confirm_product_adapter.py",
)
SESSION_SECRET = b"session-secret-for-authenticated-status-ref"
VERSION_SECRET = b"proposal-version-binding-secret-32b"
IDEMPOTENCY_SECRET = b"idempotency-secret-for-status-confirm"
SESSION_BINDING_SECRET = b"session-binding-secret-for-status-confirm"
SIGNED_EVIDENCE_SECRET = "authored-synthetic-evidence-secret"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _appointment(
    *,
    version: int = 7,
    status: AppointmentStatus = AppointmentStatus.Booked,
    waiting_area_id: uuid.UUID | None = None,
) -> SimpleNamespace:
    start = datetime(2026, 8, 13, 0, 0, tzinfo=timezone.utc)
    practitioner_id = uuid.uuid4()
    return SimpleNamespace(
        id=uuid.uuid4(),
        practice_id=uuid.uuid4(),
        patient_id=None,
        patient_name_provisional="Authored Synthetic Person",
        practitioner_id=practitioner_id,
        appointment_type_id=None,
        location_id=None,
        start_time=start,
        appointment_date=date(2026, 8, 13),
        start_time_local=time(10, 0),
        end_time=start + timedelta(minutes=15),
        duration_minutes=15,
        status=status,
        reason="Authored synthetic adapter rehearsal",
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


def _proposal_packet(
    appointment: SimpleNamespace,
    user: SimpleNamespace,
    *,
    target_status: AppointmentStatus = AppointmentStatus.Confirmed,
):
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
    state = appointment_status_state(appointment)
    freshness = status_proposal_freshness_id(command, state)
    payload = status_signed_confirmation_payload(
        practice_id=user.practice_id,
        actor_id=user.id,
        command=command,
        current_state=state,
        freshness_id=freshness,
    )
    signed = mint_signed_confirmation_evidence(
        payload,
        evidence_purpose=STATUS_CONFIRM_EVIDENCE_PURPOSE,
        secret=SIGNED_EVIDENCE_SECRET,
    )
    version_binding = mint_status_proposal_version_binding(
        signed,
        source_version=state["source_version"],
        secret=VERSION_SECRET,
    )
    proposal = AppointmentStatusProposalOut(
        safe=True,
        requires_confirmation=True,
        autonomy_tier="proposal",
        summary="Confirm authored-synthetic status.",
        command=command,
        warnings=[],
        blocks=[],
        status_proposal_freshness_id=freshness,
        signed_confirmation_evidence=signed,
        signed_confirmation_evidence_required=True,
    )
    body = AppointmentStatusProposalConfirmationIn(
        confirmed=True,
        status_proposal=proposal,
        confirmed_warnings=[],
        status_proposal_freshness_id=freshness,
        signed_confirmation_evidence=signed,
        signed_confirmation_evidence_required=True,
    )
    return body, version_binding


class _FakeSession:
    def __init__(self, appointment: SimpleNamespace) -> None:
        self.appointment = appointment
        self.audits: list[Any] = []
        self.practice_contexts: list[str] = []
        self.refresh_count = 0

    def execute(self, _statement: Any, parameters: dict[str, str]) -> None:
        self.practice_contexts.append(parameters["practice_id"])

    def add(self, value: Any) -> None:
        self.audits.append(value)

    def flush(self) -> None:
        return None

    def refresh(self, value: Any) -> None:
        if value is not self.appointment:
            raise ValueError("unexpected refresh target")
        value.appointment_state_version += 1
        self.refresh_count += 1

    def close(self) -> None:
        return None


class _FakeTransaction:
    def __init__(self, appointment: SimpleNamespace) -> None:
        self.appointment = appointment
        self.records: dict[tuple[str, str, str], SimpleNamespace] = {}
        self.entries = 0

    @contextmanager
    def __call__(self, db: _FakeSession, **arguments: Any):
        self.entries += 1
        practice = SimpleNamespace(id=arguments["practice_id"])
        if not arguments["practice_is_active"](practice):
            raise ValueError("practice unavailable")
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
                self.records.pop(key, None)
            raise StatusConfirmAuthorityRevoked("authority unavailable")
        if inserted:
            kind = "new_command"
        elif (
            record.request_body_hash != arguments["request_body_hash"]
            or not hmac.compare_digest(
                record.session_binding_digest,
                arguments["session_binding_digest"],
            )
        ):
            kind = "conflict"
        else:
            kind = "replay"
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


def _run_product(
    *,
    appointment: SimpleNamespace,
    user: SimpleNamespace,
    body: AppointmentStatusProposalConfirmationIn,
    version_binding: dict[str, Any],
    db: _FakeSession | None = None,
    physical: _FakeTransaction | None = None,
    bearer: str = "synthetic-authenticated-bearer",
    user_loader=None,
):
    db = db or _FakeSession(appointment)
    physical = physical or _FakeTransaction(appointment)
    session_calls = {"count": 0}

    def session_factory():
        session_calls["count"] += 1
        return db

    result = compose_product_status_confirm(
        body,
        authenticated_user=user,
        authenticated_bearer_token=bearer,
        idempotency_key="authored-synthetic-idempotency-key",
        proposal_version_binding=version_binding,
        command_session_factory=session_factory,
        authenticated_session_secret=SESSION_SECRET,
        proposal_version_binding_secret=VERSION_SECRET,
        idempotency_secret=IDEMPOTENCY_SECRET,
        session_binding_secret=SESSION_BINDING_SECRET,
        evidence_secret=SIGNED_EVIDENCE_SECRET,
        user_loader=user_loader or (lambda _db, _actor_id: user),
        transaction_factory=physical,
    )
    return result, db, physical, session_calls


def _compose_twice():
    appointment = _appointment()
    user = SimpleNamespace(
        id=uuid.uuid4(),
        practice_id=appointment.practice_id,
        role=UserRole.Receptionist,
        is_active=True,
    )
    body, version_binding = _proposal_packet(appointment, user)
    db = _FakeSession(appointment)
    physical = _FakeTransaction(appointment)

    first, _, _, _ = _run_product(
        appointment=appointment,
        user=user,
        body=body,
        version_binding=version_binding,
        db=db,
        physical=physical,
    )
    second, _, _, _ = _run_product(
        appointment=appointment,
        user=user,
        body=body,
        version_binding=version_binding,
        db=db,
        physical=physical,
    )
    return appointment, user, body, version_binding, db, physical, first, second


def _base_admission_input() -> dict[str, Any]:
    target = str(uuid.uuid4())
    return {
        "structure": "valid",
        "transport": {
            "operation_id": "confirmAppointmentStatusProposal",
            "route_family": "status-confirm",
            "idempotency_key": "synthetic-key",
            "confirmed": True,
            "proposal_intent": "update_appointment_status",
            "proposal_safe": True,
            "requires_confirmation": True,
            "autonomy_tier": "proposal",
            "command": {
                "kind": "status",
                "appointment_id": target,
                "status": "Confirmed",
                "status_reason_code": None,
                "waiting_area_id": None,
                "waiting_area_id_supplied": False,
                "clears_waiting_area": False,
            },
            "proposal_warning_codes": [],
            "confirmed_warning_codes": [],
            "freshness_id": "f" * 32,
            "signed_evidence_required": True,
        },
        "server": {
            "practice_id": str(uuid.uuid4()),
            "actor_id": str(uuid.uuid4()),
            "actor_role": "Receptionist",
            "session_id": "a" * 64,
            "authority_current": True,
            "current_state": {
                "appointment_id": target,
                "status": "Booked",
                "status_reason_code": None,
                "waiting_area_id": None,
                "source_version": 7,
            },
            "expected_freshness_id": "f" * 32,
            "evidence_status": "verified",
            "evidence_purpose": STATUS_CONFIRM_EVIDENCE_PURPOSE,
            "expected_evidence_purpose": STATUS_CONFIRM_EVIDENCE_PURPOSE,
            "evidence_binding": "exact",
        },
    }


def _set_path(value: dict[str, Any], path: tuple[str, ...], replacement: Any) -> None:
    cursor = value
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = replacement


def _hostile_mutation_counts() -> tuple[int, int]:
    base = _base_admission_input()
    if status_confirm_admission_adapter(base)["kind"] != "kernel_request_ready":
        raise AssertionError("base status-only admission was not ready")
    invalid_groups: list[tuple[tuple[str, ...], list[Any]]] = [
        (("structure",), [None, False, "", "invalid"]),
        (("transport", "operation_id"), [None, "", "other", 1]),
        (("transport", "route_family"), [None, "", "other", 1]),
        (("transport", "idempotency_key"), [None, "", "   ", 1]),
        (("transport", "confirmed"), [False, None, 0, ""]),
        (("transport", "proposal_intent"), [None, "", "create", 1]),
        (("transport", "proposal_safe"), [False, None, 0, ""]),
        (("transport", "requires_confirmation"), [False, None, 0, ""]),
        (("transport", "autonomy_tier"), [None, "", "blocked", "ambient"]),
        (("transport", "command", "kind"), [None, "", "waiting_area", "delete"]),
        (("server", "authority_current"), [False, None, 0, ""]),
        (("server", "session_id"), [None, "", "short", "a" * 63]),
        (("transport", "signed_evidence_required"), [False, None, 0, ""]),
        (("server", "evidence_status"), [None, "", "invalid", "tampered"]),
        (("server", "evidence_purpose"), [None, "", "other", 1]),
        (("server", "expected_evidence_purpose"), [None, "", "other", 1]),
        (("server", "evidence_binding"), [None, "", "partial", "invalid"]),
        (("transport", "freshness_id"), [None, "", "0" * 32, 1]),
        (("server", "current_state", "appointment_id"), [None, "", str(uuid.uuid4()), 1]),
        (("server", "current_state", "source_version"), [None, 0, -1, "7"]),
        (("server", "current_state", "status"), ["Completed", "Cancelled", "DNA", "NoShow"]),
    ]
    attempted = 0
    rejected = 0
    for path, replacements in invalid_groups:
        for replacement in replacements:
            candidate = copy.deepcopy(base)
            _set_path(candidate, path, replacement)
            attempted += 1
            if status_confirm_admission_adapter(candidate)["kind"] != "kernel_request_ready":
                rejected += 1
    return attempted, rejected


def build_evidence() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    input_hashes = {
        relative: _sha256(ROOT / relative)
        for relative in contract["frozen_inputs"]
    }
    if input_hashes != contract["frozen_inputs"]:
        raise AssertionError("one or more frozen input hashes changed")
    route_text = (ROOT / "app/routers/appointments.py").read_text(encoding="utf-8")
    route_import_absent = "appointment_status_product_adapter" not in route_text
    if not route_import_absent:
        raise AssertionError("product adapter was imported by the route")

    appointment, _user, body, binding, db, physical, first, second = _compose_twice()
    bound_version = verify_status_proposal_version_binding(
        binding,
        signed_confirmation_evidence=body.signed_confirmation_evidence,
        secret=VERSION_SECRET,
    )
    tampered_binding = dict(binding)
    tampered_binding["source_version"] = bound_version + 1
    tampered_binding_rejected = False
    try:
        verify_status_proposal_version_binding(
            tampered_binding,
            signed_confirmation_evidence=body.signed_confirmation_evidence,
            secret=VERSION_SECRET,
        )
    except ValueError:
        tampered_binding_rejected = True

    attempted, rejected = _hostile_mutation_counts()
    if attempted < contract["minimum_hostile_mutations"] or rejected != attempted:
        raise AssertionError("hostile mutation threshold did not pass")
    audit = db.audits[0]
    record = next(iter(physical.records.values()))
    session_ref = authenticated_session_reference(
        "synthetic-authenticated-bearer", secret=SESSION_SECRET
    )

    stale_proposal = _appointment(version=7)
    stale_user = SimpleNamespace(
        id=uuid.uuid4(),
        practice_id=stale_proposal.practice_id,
        role=UserRole.Receptionist,
        is_active=True,
    )
    stale_body, stale_binding = _proposal_packet(stale_proposal, stale_user)
    changed_locked = copy.deepcopy(stale_proposal)
    changed_locked.appointment_state_version = 8
    stale_result, stale_db, stale_physical, _ = _run_product(
        appointment=changed_locked,
        user=stale_user,
        body=stale_body,
        version_binding=stale_binding,
    )

    same_appointment = _appointment(status=AppointmentStatus.Confirmed)
    same_user = SimpleNamespace(
        id=uuid.uuid4(),
        practice_id=same_appointment.practice_id,
        role=UserRole.Receptionist,
        is_active=True,
    )
    same_body, same_binding = _proposal_packet(same_appointment, same_user)
    same_result, same_db, same_physical, _ = _run_product(
        appointment=same_appointment,
        user=same_user,
        body=same_body,
        version_binding=same_binding,
    )

    terminal_appointment = _appointment(status=AppointmentStatus.Completed)
    terminal_user = SimpleNamespace(
        id=uuid.uuid4(),
        practice_id=terminal_appointment.practice_id,
        role=UserRole.Receptionist,
        is_active=True,
    )
    terminal_body, terminal_binding = _proposal_packet(
        terminal_appointment, terminal_user
    )
    terminal_result, terminal_db, terminal_physical, _ = _run_product(
        appointment=terminal_appointment,
        user=terminal_user,
        body=terminal_body,
        version_binding=terminal_binding,
    )

    warning_appointment = _appointment(waiting_area_id=uuid.uuid4())
    warning_user = SimpleNamespace(
        id=uuid.uuid4(),
        practice_id=warning_appointment.practice_id,
        role=UserRole.Receptionist,
        is_active=True,
    )
    warning_body, warning_binding = _proposal_packet(
        warning_appointment,
        warning_user,
        target_status=AppointmentStatus.Cancelled,
    )
    warning_result, warning_db, warning_physical, _ = _run_product(
        appointment=warning_appointment,
        user=warning_user,
        body=warning_body,
        version_binding=warning_binding,
    )

    waiting_proposal = AppointmentWaitingAreaProposalOut(
        safe=True,
        requires_confirmation=True,
        autonomy_tier="proposal",
        summary="Authored-synthetic waiting-area proposal.",
        command=AppointmentWaitingAreaCommand(
            appointment_id=stale_proposal.id,
            waiting_area_id=uuid.uuid4(),
            clears_waiting_area=False,
        ),
    )
    waiting_body = AppointmentStatusProposalConfirmationIn(
        confirmed=True,
        status_proposal=waiting_proposal,
        signed_confirmation_evidence=stale_body.signed_confirmation_evidence,
    )
    waiting_result, waiting_db, waiting_physical, waiting_session_calls = _run_product(
        appointment=stale_proposal,
        user=stale_user,
        body=waiting_body,
        version_binding=stale_binding,
    )

    revocation_appointment = _appointment()
    revocation_user = SimpleNamespace(
        id=uuid.uuid4(),
        practice_id=revocation_appointment.practice_id,
        role=UserRole.Receptionist,
        is_active=True,
    )
    revocation_body, revocation_binding = _proposal_packet(
        revocation_appointment, revocation_user
    )
    authority_calls = {"count": 0}

    def revoked_after_claim(_db, _actor_id):
        authority_calls["count"] += 1
        if authority_calls["count"] == 1:
            return revocation_user
        return SimpleNamespace(
            id=revocation_user.id,
            practice_id=revocation_user.practice_id,
            role=revocation_user.role,
            is_active=False,
        )

    revocation_result, revocation_db, revocation_physical, _ = _run_product(
        appointment=revocation_appointment,
        user=revocation_user,
        body=revocation_body,
        version_binding=revocation_binding,
        user_loader=revoked_after_claim,
    )

    tampered_body = stale_body.model_copy(deep=True)
    tampered_body.signed_confirmation_evidence["signature"] = "0" * 64
    evidence_result, evidence_db, evidence_physical, evidence_session_calls = _run_product(
        appointment=stale_proposal,
        user=stale_user,
        body=tampered_body,
        version_binding=stale_binding,
    )
    scenario_results = {
        "clean_execute": first.kind == "committed" and first.status_code == 200,
        "byte_identical_response_loss_replay": (
            second.kind == "replay"
            and first.stored_response_bytes == second.stored_response_bytes
        ),
        "bearer_minimisation": (
            len(session_ref) == 64
            and "synthetic-authenticated-bearer" not in json.dumps(first.body)
        ),
        "distinct_bearer_session_separation": session_ref
        != authenticated_session_reference("different-bearer", secret=SESSION_SECRET),
        "current_authority_before_and_after_idempotency": (
            len(db.practice_contexts) == 4
            and revocation_result.status_code == 403
            and revocation_db.audits == []
            and revocation_physical.records == {}
        ),
        "waiting_area_union_pretransaction_rejection": (
            waiting_result.kind == "blocked"
            and waiting_session_calls["count"] == 0
            and waiting_physical.entries == 0
            and waiting_db.audits == []
        ),
        "signed_proposal_version_binding": bound_version == 7 and tampered_binding_rejected,
        "changed_locked_generation_stop": (
            stale_result.kind == "blocked"
            and stale_result.body["blocks"][0]["code"]
            == "locked_request_digest_changed"
            and stale_db.audits == []
            and stale_physical.records == {}
        ),
        "same_state_and_terminal_stop": (
            same_result.kind == "blocked"
            and terminal_result.kind == "blocked"
            and same_db.audits == []
            and terminal_db.audits == []
            and same_physical.entries == 0
            and terminal_physical.entries == 0
        ),
        "warning_and_evidence_stop": (
            warning_result.kind == "blocked"
            and warning_db.audits == []
            and warning_physical.entries == 0
            and evidence_result.status_code == 403
            and evidence_session_calls["count"] == 0
            and evidence_physical.entries == 0
            and evidence_db.audits == []
        ),
        "single_mutation_single_audit_adjacent_version": (
            appointment.appointment_state_version == 8
            and db.refresh_count == 1
            and len(db.audits) == 1
        ),
        "command_audit_session_correlation": (
            audit.command_id == record.id
            and record.audit_log_id == audit.id
            and record.bernie_session_id == audit.bernie_session_id
            and audit.bernie_session_id == session_ref
        ),
        "complete_canonical_public_envelope": (
            first.body == json.loads(first.stored_response_bytes)
            and first.body["appointment"]["status"] == "Confirmed"
        ),
    }
    if not all(scenario_results.values()):
        failed = [name for name, passed in scenario_results.items() if not passed]
        raise AssertionError(f"scenario failures: {failed}")

    evidence = {
        "schema_version": "raisa.status_confirm_product_adapter_rehearsal_evidence.v1",
        "result": "raisa_provider_free_unmounted_status_confirm_product_adapter_rehearsal_pass",
        "source_head": contract["source_head"],
        "contract_sha256": _sha256(CONTRACT_PATH),
        "input_hashes": input_hashes,
        "implementation_hashes": {
            relative: _sha256(ROOT / relative) for relative in IMPLEMENTATION_PATHS
        },
        "route_unchanged": input_hashes["app/routers/appointments.py"]
        == contract["frozen_inputs"]["app/routers/appointments.py"],
        "route_import_absent": route_import_absent,
        "scenario_results": scenario_results,
        "hostile_mutations": {
            "attempted": attempted,
            "rejected": rejected,
            "minimum_required": contract["minimum_hostile_mutations"],
        },
        "side_effects": {
            "route_calls": 0,
            "database_connections": 0,
            "provider_calls": 0,
            "network_calls": 0,
            "product_patient_records": 0,
        },
        "claim_boundary": contract["claim_boundary"],
    }
    validate(instance=evidence, schema=schema)
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    evidence = build_evidence()
    rendered = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != rendered:
            raise SystemExit("committed product-adapter evidence is stale")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "hostile_mutations": evidence["hostile_mutations"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
