"""One-read local consumption of an admitted structural Diary scenario."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Literal
from uuid import UUID, uuid5

from app.models.appointments import AppointmentStatus
from app.models.tenancy import UserRole
from app.schemas.appointments import (
    AppointmentCheckInCommand,
    AppointmentCheckInProposalConfirmationIn,
    AppointmentCheckInProposalOut,
)
from app.services.appointment_check_in_product_adapter import (
    CHECK_IN_AUDIT_EVIDENCE,
    CHECK_IN_EVENT_SCHEMA_VERSION,
    CHECK_IN_EVENT_TYPE,
    CHECK_IN_OPERATION_ID,
    CHECK_IN_RECEIPT_SCHEMA_VERSION,
    CHECK_IN_ROUTE_FAMILY,
    CheckInDependencies,
    check_in_proposal_freshness_id,
    check_in_state_payload,
    compose_product_check_in,
)
from orchestration_harness import historical_diary_first_use_candidate_gate as gate
from orchestration_harness.governance_clockwork_tick import (
    HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_SUBGATE_BOUNDARIES,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "raisa-provider-free-exact-digest-historical-derived-minimised-check-in-"
    "context-adapter-test-consumption-rehearsal"
)
PLAN_SOURCE = "5eaac238e8d7541ffd395a5a3f8b8464ae5b68b8"
CLOCKWORK_SOURCE = "5792a993b33a5f0dc0fea78e1c20f7f4164f2c4a"
CLOCKWORK_CLOSEOUT_SOURCE = "ce1f3717fc89117a9db74ca1b95509f02fef5d82"
FIRST_USE_SOURCE = "4740813d53ebbc4872fe8c0c08ce2578b1982770"
CANDIDATE_GATE_SOURCE = "abcd4206a363b0c565c070e0f2cb9c54d627b3b3"
CANDIDATE_GATE_BLOB = "fe05dfb3b4c4e36ea3200b9532a3d40bcb30f7f7"
ORIGINAL_ADAPTER_SOURCE = "8de886c5148b3259428c8c517674f10ea92d937e"
CURRENT_ADAPTER_SOURCE = "c82c3a741053a9c8da260aa62e1a968af22bb54e"
CURRENT_ADAPTER_BLOB = "6955dec2e31e14c0ae4847acba22f9fb0087715b"
PROTECTED_COMMIT = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
SUBGATE_CONTRACT_SHA256 = (
    "da2507056f37482016125c3ccad909573c0495d86cdc135cd5b13714bc7c93ac"
)
SUCCESSOR_CONTRACT_SHA256 = (
    "6d4cfb8ae74317685a478097fa347ead932afb47033591e82ec19afbeebb9658"
)
FIXTURE_SHA256 = "2205ab83cec7c5639d39cc563cee80eec825ac33f17571151571d325e74f2dfe"
MAX_FIXTURE_BYTES = 64 * 1024
EXPECTED_UTILITY = {
    "event_count": 6,
    "distinct_relative_minutes": 4,
    "relative_minute_span": 19,
    "distinct_event_kinds": 2,
    "synthetic_subject_slots": 1,
    "resource_slots": 1,
}
EVIDENCE_LABEL = (
    "local_provider_free_historical_derived_minimised_fixture_adapter_test"
)
SUCCESS_DECISION = "consumed_for_exact_declared_local_adapter_test_only"
CLAIM_CEILING = (
    "one_exact_local_provider_free_adapter_test_consumption_no_real_practice_"
    "product_runtime_or_archive_validity_claim"
)
SYNTHETIC_NAMESPACE = UUID("d2ca1b0e-2e8d-58f5-83fd-0a8dfb5b8878")


@dataclass(frozen=True)
class ConsumptionPaths:
    fixture: Path
    control: Path
    result: Path
    successor_contract: Path
    subgate_contract: Path
    latch: Path


@dataclass(frozen=True)
class ConsumptionContract:
    fixture_sha256: str = FIXTURE_SHA256
    maximum_fixture_bytes: int = MAX_FIXTURE_BYTES
    expected_utility: dict[str, int] | None = None

    def utility(self) -> dict[str, int]:
        return dict(EXPECTED_UTILITY if self.expected_utility is None else self.expected_utility)


DEFAULT_PATHS = ConsumptionPaths(
    fixture=REPO_ROOT
    / "local_data/historical-diary-trove/derived-scenarios/"
    "2026-08-24-first-use-check-in-context-v1/scenario.json",
    control=REPO_ROOT
    / "local_data/historical-diary-trove/derived-scenarios/"
    "2026-08-24-first-use-check-in-context-v1/adapter-test-consumption-control.json",
    result=REPO_ROOT
    / "orchestration/continuity/"
    f"{OPERATION_ID}/occupied-result.json",
    successor_contract=REPO_ROOT
    / "orchestration/continuity/raisa-provider-free-governance-clockwork-"
    "historical-derived-minimised-scenario-consumption-subgate-rehearsal/"
    "next-tranche-contract.json",
    subgate_contract=REPO_ROOT
    / "orchestration/continuity/raisa-local-only-historical-derived-minimised-"
    "check-in-context-scenario-first-use-materialisation-rehearsal/"
    "next-tranche-contract.json",
    latch=REPO_ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json",
)
DEFAULT_CONTRACT = ConsumptionContract()


class ConsumptionError(RuntimeError):
    """The exact local consumption failed closed."""


def _reject(code: str) -> None:
    raise ConsumptionError(code)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _json_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _read_public_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_bytes())
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ConsumptionError(f"public_json_unreadable_{path.name}") from error
    if not isinstance(value, dict):
        _reject(f"public_json_object_required_{path.name}")
    return value


def _exclusive_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(_json_bytes(value))
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as error:
        raise ConsumptionError(f"exclusive_write_failed_{path.name}") from error


def _replace_json(path: Path, value: dict[str, Any]) -> None:
    temp = path.with_name(f".{path.name}.tmp")
    if temp.exists():
        _reject("control_temporary_path_preexists")
    _exclusive_json(temp, value)
    try:
        os.replace(temp, path)
    except OSError as error:
        try:
            temp.unlink(missing_ok=True)
        except OSError:
            pass
        raise ConsumptionError("control_replace_failed") from error


def _git(*arguments: str, text: bool = True) -> str | bytes:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
        text=text,
    )
    if completed.returncode != 0:
        _reject("git_binding_unreadable")
    return completed.stdout.strip() if text else completed.stdout


def _git_ref(ref: str) -> str:
    value = str(_git("rev-parse", "--verify", ref))
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
        _reject("git_full_object_id_required")
    return value


def _git_blob(ref: str, relative_path: str) -> str:
    value = str(_git("rev-parse", f"{ref}:{relative_path}"))
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
        _reject("git_blob_id_invalid")
    return value


def _git_ancestor(source: str, descendant: str) -> None:
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", source, descendant],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        _reject("required_source_not_ancestor")


def _assert_owned_paths(paths: ConsumptionPaths) -> None:
    ignored_root = (REPO_ROOT / "local_data/historical-diary-trove").resolve()
    fixture = paths.fixture.resolve()
    control = paths.control.resolve()
    if (
        not fixture.is_relative_to(ignored_root)
        or not control.is_relative_to(ignored_root)
        or fixture.parent != control.parent
        or fixture == control
    ):
        _reject("local_consumption_path_boundary_invalid")
    continuity_root = (REPO_ROOT / "orchestration/continuity").resolve()
    result = paths.result.resolve()
    if not result.is_relative_to(continuity_root):
        _reject("result_path_boundary_invalid")
    if paths.fixture.is_symlink() or paths.control.is_symlink() or paths.result.is_symlink():
        _reject("consumption_symlink_rejected")


def _validate_public_bindings(
    candidate_source: str,
    paths: ConsumptionPaths,
    *,
    require_control_absent: bool,
) -> dict[str, Any]:
    if re.fullmatch(r"[0-9a-f]{40}", candidate_source) is None:
        _reject("candidate_source_full_git_id_required")
    _assert_owned_paths(paths)
    if _git_ref("HEAD") != candidate_source:
        _reject("candidate_source_not_head")
    if str(_git("branch", "--show-current")) != "codex/ariadne-bernie-davida-parallel-seam":
        _reject("task_branch_mismatch")
    for source in (
        PLAN_SOURCE,
        CLOCKWORK_SOURCE,
        CLOCKWORK_CLOSEOUT_SOURCE,
        FIRST_USE_SOURCE,
        CANDIDATE_GATE_SOURCE,
        ORIGINAL_ADAPTER_SOURCE,
        CURRENT_ADAPTER_SOURCE,
    ):
        _git_ancestor(source, candidate_source)
    for ref in (
        "refs/heads/master",
        "refs/remotes/origin/master",
        "refs/heads/handoff/current",
        "refs/remotes/origin/handoff/current",
    ):
        if _git_ref(ref) != PROTECTED_COMMIT:
            _reject("protected_ref_mismatch")
    if str(_git("status", "--porcelain", "--untracked-files=no")):
        _reject("tracked_worktree_not_clean")
    gate_path = "orchestration_harness/historical_diary_first_use_candidate_gate.py"
    adapter_path = "app/services/appointment_check_in_product_adapter.py"
    core_path = "orchestration_harness/historical_diary_check_in_adapter_test_consumption.py"
    if _git_blob(candidate_source, gate_path) != CANDIDATE_GATE_BLOB:
        _reject("candidate_gate_blob_mismatch")
    if _git_blob(candidate_source, adapter_path) != CURRENT_ADAPTER_BLOB:
        _reject("current_adapter_blob_mismatch")
    if _git_blob(CURRENT_ADAPTER_SOURCE, adapter_path) != CURRENT_ADAPTER_BLOB:
        _reject("accepted_adapter_blob_mismatch")
    if _git_blob(candidate_source, core_path) != _git_blob("HEAD", core_path):
        _reject("consumption_core_blob_mismatch")

    successor_bytes = paths.successor_contract.read_bytes()
    subgate_bytes = paths.subgate_contract.read_bytes()
    if _sha256_bytes(successor_bytes) != SUCCESSOR_CONTRACT_SHA256:
        _reject("successor_contract_hash_mismatch")
    if _sha256_bytes(subgate_bytes) != SUBGATE_CONTRACT_SHA256:
        _reject("subgate_contract_hash_mismatch")
    successor = json.loads(successor_bytes)
    if (
        successor.get("operation_id") != OPERATION_ID
        or successor.get("accepted_first_use_source") != FIRST_USE_SOURCE
        or successor.get("accepted_unmounted_check_in_adapter_source")
        != ORIGINAL_ADAPTER_SOURCE
        or set(successor.get("clockwork_consumption_mode", []))
        != set(HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_SUBGATE_BOUNDARIES)
        or successor.get("fixture_ceiling", {}).get("sha256") != FIXTURE_SHA256
        or successor.get("fixture_ceiling", {}).get("maximum_reads") != 1
    ):
        _reject("successor_contract_semantics_mismatch")
    latch = _read_public_json(paths.latch)
    historical = {
        item for item in latch.get("protected_boundaries", []) if "historical" in item
    }
    if (
        latch.get("operation_id") != OPERATION_ID
        or latch.get("status") != "in_progress"
        or historical
        != set(HISTORICAL_DERIVED_MINIMISED_SCENARIO_CONSUMPTION_SUBGATE_BOUNDARIES)
    ):
        _reject("active_latch_consumption_mode_mismatch")
    if not paths.fixture.is_file():
        _reject("accepted_fixture_absent")
    if paths.fixture.stat().st_size > MAX_FIXTURE_BYTES:
        _reject("accepted_fixture_size_ceiling_exceeded")
    if require_control_absent and paths.control.exists():
        _reject("consumption_control_preexists")
    if paths.result.exists():
        _reject("occupied_result_preexists")
    return {
        "candidate_source": candidate_source,
        "protected_refs_aligned": True,
        "contract_hashes_verified": True,
        "accepted_adapter_blob_exact": True,
        "accepted_candidate_gate_blob_exact": True,
        "fixture_content_reads": 0,
    }


def _control(
    *,
    state: Literal["prepared", "consuming", "complete", "failed_closed"],
    candidate_source: str,
    logical_read_count: int,
    decision: str | None = None,
    result_sha256: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "raisa.historical_derived_check_in_adapter_consumption_control.v1",
        "operation_id": OPERATION_ID,
        "state": state,
        "candidate_source": candidate_source,
        "fixture_sha256_expected": FIXTURE_SHA256,
        "logical_fixture_read_count": logical_read_count,
        "fixture_retry_authorized": False,
        "historical_archive_reads": 0,
        "adapter_test_invocation_ceiling": 1,
        "decision": decision,
        "result_sha256": result_sha256,
    }


def prepare(
    candidate_source: str,
    *,
    paths: ConsumptionPaths = DEFAULT_PATHS,
) -> dict[str, Any]:
    """Create the sole prepared lease without opening or hashing the fixture."""

    reading = _validate_public_bindings(
        candidate_source,
        paths,
        require_control_absent=True,
    )
    value = _control(
        state="prepared",
        candidate_source=candidate_source,
        logical_read_count=0,
    )
    _exclusive_json(paths.control, value)
    return {
        "schema_version": "raisa.historical_derived_check_in_adapter_consumption_preflight.v1",
        "status": "prepared",
        "candidate_source": candidate_source,
        "fixture_content_reads": 0,
        "fixture_hash_operations": 0,
        "logical_fixture_read_count": 0,
        "historical_archive_reads": 0,
        "provider_or_model_calls": 0,
        "adapter_test_invocations": 0,
        "control_state": "prepared",
        **reading,
    }


class _AdapterTrace:
    def __init__(self, *, structural_digest: str, minute_span: int) -> None:
        self.practice_id = uuid5(SYNTHETIC_NAMESPACE, f"{structural_digest}:practice")
        self.actor_id = uuid5(SYNTHETIC_NAMESPACE, f"{structural_digest}:actor")
        self.appointment_id = uuid5(
            SYNTHETIC_NAMESPACE, f"{structural_digest}:appointment"
        )
        self.command_id = uuid5(SYNTHETIC_NAMESPACE, f"{structural_digest}:command")
        self.audit_id = uuid5(SYNTHETIC_NAMESPACE, f"{structural_digest}:audit")
        self.event_id = uuid5(SYNTHETIC_NAMESPACE, f"{structural_digest}:event")
        self.now = datetime(2036, 1, 1, tzinfo=timezone.utc) + timedelta(
            minutes=minute_span
        )
        self.idempotency_key = (
            "historical-derived-check-in-"
            + _sha256_bytes(f"{structural_digest}:idempotency".encode())[:32]
        )
        self.evidence = (
            "opaque-authored-synthetic-evidence-"
            + _sha256_bytes(f"{structural_digest}:evidence".encode())[:32]
        )
        self.actor = SimpleNamespace(
            id=self.actor_id,
            practice_id=self.practice_id,
            role=UserRole.Receptionist,
            is_active=True,
        )
        self.appointment = SimpleNamespace(
            id=self.appointment_id,
            practice_id=self.practice_id,
            status=AppointmentStatus.Booked,
            waiting_area_id=None,
            location_id=None,
        )
        self.calls: list[str] = []
        self.claim_kwargs: dict[str, Any] = {}
        self.verify_kwargs: dict[str, Any] = {}
        self.effect_plans: list[Any] = []
        self.audit_plans: list[Any] = []
        self.event_plans: list[Any] = []
        self.complete_kwargs: list[dict[str, Any]] = []
        self.commits = 0
        self.rollbacks = 0

    def claim(self, **kwargs: Any) -> SimpleNamespace:
        self.calls.append("claim")
        self.claim_kwargs = kwargs
        return SimpleNamespace(kind="started", record=SimpleNamespace(id=self.command_id))

    def load_locked_appointment(self, **_: Any) -> Any:
        self.calls.append("lock")
        return self.appointment

    def load_current_actor(self, **_: Any) -> Any:
        self.calls.append("reauthorize")
        return self.actor

    def load_waiting_area(self, **_: Any) -> None:
        self.calls.append("waiting_area")
        return None

    def verify_evidence(self, evidence: str, **kwargs: Any) -> tuple[bool, str, dict]:
        self.calls.append("verify")
        self.verify_kwargs = {"evidence": evidence, **kwargs}
        return True, "signed_evidence_verified", {}

    def stage_effect(self, **kwargs: Any) -> None:
        self.calls.append("effect")
        plan = kwargs["plan"]
        self.effect_plans.append(plan)
        self.appointment.status = AppointmentStatus.Arrived
        self.appointment.waiting_area_id = plan.waiting_area_id_after

    def write_audit(self, **kwargs: Any) -> SimpleNamespace:
        self.calls.append("audit")
        self.audit_plans.append(kwargs["plan"])
        return SimpleNamespace(id=self.audit_id)

    def write_event(self, **kwargs: Any) -> SimpleNamespace:
        self.calls.append("event")
        self.event_plans.append(kwargs["plan"])
        return SimpleNamespace(id=self.event_id)

    def complete(self, **kwargs: Any) -> None:
        self.calls.append("complete")
        self.complete_kwargs.append(kwargs)

    def commit(self) -> None:
        self.calls.append("commit")
        self.commits += 1

    def rollback(self) -> None:
        self.calls.append("rollback")
        self.rollbacks += 1

    def readback(self, **_: Any) -> Any:
        self.calls.append("readback")
        return self.appointment

    def dependencies(self) -> CheckInDependencies:
        return CheckInDependencies(
            claim=self.claim,
            load_locked_appointment=self.load_locked_appointment,
            load_current_actor=self.load_current_actor,
            load_waiting_area=self.load_waiting_area,
            verify_evidence=self.verify_evidence,
            stage_effect=self.stage_effect,
            write_audit=self.write_audit,
            write_event=self.write_event,
            complete=self.complete,
            commit=self.commit,
            rollback=self.rollback,
            readback=self.readback,
        )


def _body(trace: _AdapterTrace) -> AppointmentCheckInProposalConfirmationIn:
    command = AppointmentCheckInCommand(
        appointment_id=trace.appointment_id,
        waiting_area_id=None,
        waiting_area_id_supplied=False,
    )
    freshness = check_in_proposal_freshness_id(
        command,
        check_in_state_payload(trace.appointment),
    )
    proposal = AppointmentCheckInProposalOut(
        safe=True,
        requires_confirmation=True,
        autonomy_tier="execute_with_report",
        summary="Authored-synthetic structural check-in rehearsal",
        command=command,
        warnings=[],
        blocks=[],
        check_in_proposal_freshness_id=freshness,
        signed_confirmation_evidence=trace.evidence,
        signed_confirmation_evidence_required=True,
    )
    return AppointmentCheckInProposalConfirmationIn(
        confirmed=True,
        check_in_proposal=proposal,
        confirmed_warnings=[],
        check_in_proposal_freshness_id=freshness,
        signed_confirmation_evidence=trace.evidence,
        signed_confirmation_evidence_required=True,
    )


def _run_adapter_once(
    candidate: gate.CandidatePayload,
    utility: dict[str, int],
) -> dict[str, Any]:
    structural_digest = gate.canonical_candidate_sha256(candidate)
    trace = _AdapterTrace(
        structural_digest=structural_digest,
        minute_span=utility["relative_minute_span"],
    )
    result = compose_product_check_in(
        _body(trace),
        target_appointment_id=trace.appointment_id,
        server_practice_id=trace.practice_id,
        authenticated_actor=trace.actor,
        raw_idempotency_key=trace.idempotency_key,
        now=trace.now,
        dependencies=trace.dependencies(),
    )
    expected_calls = [
        "claim",
        "lock",
        "reauthorize",
        "verify",
        "effect",
        "audit",
        "event",
        "complete",
        "commit",
        "readback",
    ]
    if trace.calls != expected_calls:
        _reject("adapter_call_order_mismatch")
    if (
        result.kind != "confirmed_write"
        or result.outcome != "confirmed_write"
        or result.response_status_code != 200
        or result.committed is not True
        or result.reason is not None
        or trace.commits != 1
        or trace.rollbacks != 0
        or len(trace.effect_plans) != 1
        or len(trace.audit_plans) != 1
        or len(trace.event_plans) != 1
        or len(trace.complete_kwargs) != 1
    ):
        _reject("adapter_result_mismatch")
    effect = trace.effect_plans[0]
    audit = trace.audit_plans[0]
    event = trace.event_plans[0]
    response = dict(result.response_body or {})
    receipt = response.get("receipt")
    if (
        effect.status_after != AppointmentStatus.Arrived.value
        or effect.waiting_area_id_after is not None
        or audit.status_before != AppointmentStatus.Booked.value
        or audit.status_after != AppointmentStatus.Arrived.value
        or audit.waiting_area_id_before is not None
        or audit.waiting_area_id_after is not None
        or audit.audit_evidence != CHECK_IN_AUDIT_EVIDENCE
        or event.event_type != CHECK_IN_EVENT_TYPE
        or event.schema_version != CHECK_IN_EVENT_SCHEMA_VERSION
        or event.payload.get("status_before") != AppointmentStatus.Booked.value
        or event.payload.get("status_after") != AppointmentStatus.Arrived.value
        or event.payload.get("waiting_area_id_before") is not None
        or event.payload.get("waiting_area_id_after") is not None
        or response.get("autonomy_tier") != "confirmed_write"
        or not isinstance(receipt, dict)
        or receipt.get("schema_version") != CHECK_IN_RECEIPT_SCHEMA_VERSION
        or receipt.get("status") != AppointmentStatus.Arrived.value
        or receipt.get("waiting_area_id") is not None
    ):
        _reject("adapter_contract_assertion_mismatch")
    if (
        trace.claim_kwargs.get("practice_id") != trace.practice_id
        or trace.claim_kwargs.get("actor_user_id") != str(trace.actor_id)
        or trace.claim_kwargs.get("actor_role") != UserRole.Receptionist.value
        or trace.claim_kwargs.get("operation_id") != CHECK_IN_OPERATION_ID
        or trace.claim_kwargs.get("route_family") != CHECK_IN_ROUTE_FAMILY
        or trace.verify_kwargs.get("evidence") != trace.evidence
        or trace.verify_kwargs.get("expected_practice_id") != str(trace.practice_id)
        or trace.verify_kwargs.get("expected_actor_user_id") != str(trace.actor_id)
        or trace.verify_kwargs.get("expected_status_before")
        != AppointmentStatus.Booked.value
    ):
        _reject("adapter_authority_or_evidence_assertion_mismatch")
    serialized = json.dumps(response, sort_keys=True)
    for forbidden in (
        trace.evidence,
        trace.idempotency_key,
        "patient_id",
        "patient_name",
        "phone_number",
        "appointment_reason_text",
        "appointment_note",
    ):
        if forbidden in serialized:
            _reject("adapter_response_not_patient_free")
    return {
        "invocations": 1,
        "call_order": expected_calls,
        "authenticated_receptionist_reauthorised": True,
        "practice_scope_exact": True,
        "idempotency_claimed_and_completed": True,
        "signed_evidence_verified": True,
        "freshness_revalidated": True,
        "status_before": "Booked",
        "status_after": "Arrived",
        "waiting_area_preserved_none": True,
        "audit_count": 1,
        "event_count": 1,
        "event_type": CHECK_IN_EVENT_TYPE,
        "event_schema_version": CHECK_IN_EVENT_SCHEMA_VERSION,
        "commit_count": 1,
        "readback_matched": True,
        "receipt_schema_version": CHECK_IN_RECEIPT_SCHEMA_VERSION,
        "response_status_code": 200,
        "response_patient_free": True,
        "synthetic_identifiers_or_keys_persisted": False,
    }


def _terminal(
    *,
    decision: Literal[
        "blocked",
        "revision_required",
        "consumed_for_exact_declared_local_adapter_test_only",
    ],
    candidate_source: str,
    reason_codes: list[str],
    fixture_sha256_expected: str,
    digest_match: bool,
    same_bytes_parsed: bool,
    utility: dict[str, int] | None = None,
    adapter: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "raisa.historical_derived_check_in_adapter_test_consumption_result.v1",
        "evidence_label": EVIDENCE_LABEL,
        "decision": decision,
        "reason_codes": reason_codes,
        "candidate_source": candidate_source,
        "bindings": {
            "plan_source": PLAN_SOURCE,
            "clockwork_source": CLOCKWORK_SOURCE,
            "clockwork_closeout_source": CLOCKWORK_CLOSEOUT_SOURCE,
            "first_use_source": FIRST_USE_SOURCE,
            "candidate_gate_source": CANDIDATE_GATE_SOURCE,
            "original_adapter_source": ORIGINAL_ADAPTER_SOURCE,
            "current_adapter_source": CURRENT_ADAPTER_SOURCE,
            "current_adapter_blob": CURRENT_ADAPTER_BLOB,
            "subgate_contract_sha256": SUBGATE_CONTRACT_SHA256,
            "successor_contract_sha256": SUCCESSOR_CONTRACT_SHA256,
        },
        "consumption": {
            "fixture_sha256_expected": fixture_sha256_expected,
            "fixture_digest_match": digest_match,
            "digest_verified_before_parse": digest_match,
            "parsed_from_same_in_memory_bytes": same_bytes_parsed,
            "logical_fixture_read_count": 1,
            "fixture_retry_authorized": False,
            "historical_archive_reads": 0,
        },
        "structural_utility": utility,
        "adapter_test": adapter
        or {
            "invocations": 0,
            "synthetic_identifiers_or_keys_persisted": False,
        },
        "privacy": {
            "fixture_rows_persisted": False,
            "structural_slot_values_persisted": False,
            "source_text_identity_contact_note_emitted": False,
            "filename_path_date_or_timestamp_emitted": False,
            "token_key_or_mapping_emitted": False,
            "product_patient_appointment_or_clinical_data_used": False,
        },
        "authority": {
            "fixture_is_command_authority": False,
            "provider_or_model_calls": 0,
            "network_or_external_release": False,
            "database_route_client_runtime_or_configuration": False,
            "ordinary_practice": False,
            "production_deployment_release_pages_or_protected_refs": False,
            "authority_non_transitive": True,
        },
        "claim_ceiling": CLAIM_CEILING,
    }


def _safe_reason(error: Exception) -> str:
    if isinstance(error, ConsumptionError):
        candidate = str(error)
        if re.fullmatch(r"[a-z0-9_]+", candidate):
            return candidate
    return "internal_local_consumption_failure"


def consume(
    candidate_source: str,
    *,
    paths: ConsumptionPaths = DEFAULT_PATHS,
    contract: ConsumptionContract = DEFAULT_CONTRACT,
) -> dict[str, Any]:
    """Consume the sole fixture-read lease and run exactly one adapter test."""

    _validate_public_bindings(candidate_source, paths, require_control_absent=False)
    control = _read_public_json(paths.control)
    if control != _control(
        state="prepared",
        candidate_source=candidate_source,
        logical_read_count=0,
    ):
        _reject("prepared_control_mismatch_or_consumed")
    consuming = _control(
        state="consuming",
        candidate_source=candidate_source,
        logical_read_count=1,
    )
    _replace_json(paths.control, consuming)

    digest_match = False
    same_bytes_parsed = False
    utility: dict[str, int] | None = None
    adapter: dict[str, Any] | None = None
    try:
        with paths.fixture.open("rb") as handle:
            fixture_bytes = handle.read()
        if len(fixture_bytes) > contract.maximum_fixture_bytes:
            _reject("fixture_size_ceiling_exceeded_after_read")
        digest_match = _sha256_bytes(fixture_bytes) == contract.fixture_sha256
        if not digest_match:
            _reject("fixture_digest_mismatch")
        try:
            candidate = gate.CandidatePayload.model_validate_json(fixture_bytes)
        except ValueError as error:
            raise ConsumptionError("candidate_schema_invalid") from error
        same_bytes_parsed = True
        if gate.canonical_candidate_sha256(candidate) != contract.fixture_sha256:
            _reject("canonical_candidate_digest_mismatch")
        utility = gate.structural_utility(candidate).model_dump(mode="json")
        utility.pop("schema_version", None)
        if utility != contract.utility():
            _reject("structural_utility_mismatch")
        adapter = _run_adapter_once(candidate, utility)
        result = _terminal(
            decision=SUCCESS_DECISION,
            candidate_source=candidate_source,
            reason_codes=[],
            fixture_sha256_expected=contract.fixture_sha256,
            digest_match=True,
            same_bytes_parsed=True,
            utility=utility,
            adapter=adapter,
        )
    except Exception as error:
        reason = _safe_reason(error)
        decision: Literal["blocked", "revision_required"] = (
            "revision_required"
            if reason
            in {
                "fixture_digest_mismatch",
                "candidate_schema_invalid",
                "canonical_candidate_digest_mismatch",
                "structural_utility_mismatch",
            }
            else "blocked"
        )
        result = _terminal(
            decision=decision,
            candidate_source=candidate_source,
            reason_codes=[reason],
            fixture_sha256_expected=contract.fixture_sha256,
            digest_match=digest_match,
            same_bytes_parsed=same_bytes_parsed,
            utility=utility,
            adapter=adapter,
        )

    _exclusive_json(paths.result, result)
    result_digest = _sha256_bytes(paths.result.read_bytes())
    final_state: Literal["complete", "failed_closed"] = (
        "complete" if result["decision"] == SUCCESS_DECISION else "failed_closed"
    )
    _replace_json(
        paths.control,
        _control(
            state=final_state,
            candidate_source=candidate_source,
            logical_read_count=1,
            decision=str(result["decision"]),
            result_sha256=result_digest,
        ),
    )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    phase = parser.add_mutually_exclusive_group(required=True)
    phase.add_argument("--prepare", action="store_true")
    phase.add_argument("--consume", action="store_true")
    parser.add_argument("--candidate-source", required=True)
    arguments = parser.parse_args(argv)
    try:
        if arguments.prepare:
            result = prepare(arguments.candidate_source)
        else:
            result = consume(arguments.candidate_source)
    except Exception as error:
        print(
            json.dumps(
                {
                    "schema_version": "raisa.historical_derived_check_in_adapter_consumption_failure.v1",
                    "decision": "blocked",
                    "reason_codes": [_safe_reason(error)],
                    "fixture_retry_authorized": False,
                    "historical_archive_reads": 0,
                    "provider_or_model_calls": 0,
                    "source_value_emitted": False,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("decision", result.get("status")) in {SUCCESS_DECISION, "prepared"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
