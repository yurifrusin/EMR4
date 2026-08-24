"""Provider-free authored-synthetic temporal composition rehearsal for check-in."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from uuid import UUID

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from app.models.appointments import AppointmentStatus
from app.models.tenancy import UserRole
from app.schemas.appointments import (
    AppointmentCheckInCommand,
    AppointmentCheckInProposalConfirmationIn,
    AppointmentCheckInProposalOut,
)
from app.services.appointment_check_in_product_adapter import (
    CheckInDependencies,
    check_in_proposal_freshness_id,
    check_in_state_payload,
    compose_product_check_in,
)


SCHEMA_VERSION = "raisa.authored_synthetic_time_ordered_check_in_context_scenario_contract.v1"
EVIDENCE_SCHEMA_VERSION = (
    "raisa.authored_synthetic_time_ordered_check_in_context_branch_composition_evidence.v1"
)
EFFICACY_SCHEMA_VERSION = (
    "raisa.authored_synthetic_time_ordered_check_in_context_branch_composition_efficacy.v1"
)
OPERATION_ID = (
    "raisa-provider-free-authored-synthetic-time-ordered-canonical-check-in-context-"
    "branch-composition-rehearsal"
)
PLANNING_SOURCE = "78bf34d7db6ed001f7f50eeb1c7a554ccb458b11"
DECISION = "accepted_provider_free_authored_synthetic_pairwise_composition_rehearsal"
RECORDED_AT = "2026-08-24T16:12:00.0000000+10:00"

BASE = f"orchestration/continuity/{OPERATION_ID}"
CONTRACT_PATH = f"{BASE}/scenario-contract.json"
EVIDENCE_PATH = f"{BASE}/evidence.json"
REPORT_PATH = f"{BASE}/report.md"
EFFICACY_PATH = f"{BASE}/efficacy-reading.json"
AXIS_CONTRACT_PATH = (
    "orchestration/continuity/raisa-provider-free-read-only-historical-derived-"
    "check-in-context-adapter-test-utility-gap-review/"
    "authored-synthetic-successor-axis-contract.json"
)
ADAPTER_PATH = "app/services/appointment_check_in_product_adapter.py"
ADAPTER_TEST_PATH = "tests/test_raisa_provider_free_unmounted_canonical_check_in_product_adapter.py"

SOURCE_AXIS = (
    "eligible_none",
    "eligible_assign_valid",
    "eligible_preserve_valid",
    "intervening_state_change_rejected",
    "intervening_area_topology_change_rejected",
)
AUTHORITY_AXIS = (
    "unchanged_valid",
    "actor_revoked",
    "evidence_invalidated",
    "proposal_stale_after_intervening_update",
)
OUTCOME_AXIS = (
    "first_execution",
    "exact_replay",
    "conflict_or_in_progress",
    "precommit_failure",
    "commit_outcome_unknown",
    "committed_readback_unavailable",
)
AUTHORITY_MATRIX = (
    (0, 0, 0, 1, 2, 3),
    (0, 0, 1, 0, 3, 2),
    (1, 1, 2, 3, 0, 0),
    (2, 2, 0, 0, 1, 3),
    (3, 3, 3, 2, 0, 1),
)
WITNESS_CELLS = {
    "eligible_none": (0, 0),
    "eligible_assign_valid": (1, 3),
    "eligible_preserve_valid": (2, 4),
    "intervening_state_change_rejected": (3, 3),
    "intervening_area_topology_change_rejected": (4, 4),
    "unchanged_valid": (0, 0),
    "actor_revoked": (2, 0),
    "evidence_invalidated": (0, 4),
    "proposal_stale_after_intervening_update": (2, 3),
    "first_execution": (0, 0),
    "exact_replay": (0, 1),
    "conflict": (0, 2),
    "in_progress": (1, 2),
    "precommit_failure": (1, 3),
    "commit_outcome_unknown": (2, 4),
    "committed_readback_unavailable": (2, 5),
}
PHASE_ORDER = (
    "create_authored_synthetic_initial_state",
    "freeze_confirmation_and_freshness",
    "apply_declared_intervening_changes",
    "invoke_unchanged_unmounted_adapter",
    "compare_typed_result_callback_boundary_and_readback",
    "emit_patient_free_structural_evidence",
)
PRECEDENCE = (
    "exact_replay_or_idempotency_stop",
    "locked_appointment_source_state",
    "current_actor_reauthorization",
    "proposal_freshness",
    "signed_evidence",
    "waiting_area_topology",
    "precommit_composition",
    "commit_outcome",
    "committed_readback",
)
EVIDENCE_RULES = {
    "authored_synthetic_only": True,
    "masked_axes_reported_separately": True,
    "patient_shaped_or_secret_values_forbidden": True,
    "historical_occurrence_or_frequency_claim_forbidden": True,
    "durable_database_claim_forbidden": True,
}
CLOSED_BOUNDARIES = {
    "historical_fixture_control_archive_or_local_data_access": False,
    "product_adapter_route_schema_database_client_runtime_or_configuration_change": False,
    "provider_model_network_or_external_release": False,
    "ordinary_practice_activation": False,
    "production_deployment_release_pages_or_protected_ref_movement": False,
}
EXACT_BINDINGS = {
    "planning_baseline": "d9114b3e9a72fa94acc0a7ab3657f17043c6be0a",
    "accepted_predecessor_review_source": "0f6c091935f172351972f349db8cc5c1ec72d5dc",
    "successor_axis_contract_sha256": (
        "dc74a5373a670aca52f804436e33be70a10d60ac96dd46508a58b09fd2ca778f"
    ),
    "adapter_git_blob": "6955dec2e31e14c0ae4847acba22f9fb0087715b",
    "accepted_adapter_test_git_blob": "97bcfc3725f4df9495333779c75c41d798eeae87",
    "protected_ref_commit": "2e34bdad732fdab32fbf778280b3d3c70d66d602",
}
PAIRWISE_PROOF = {
    "scenario_count": 30,
    "full_cross_product_count": 120,
    "required_cross_family_pair_count": 74,
    "lower_bound_basis": (
        "every_5_value_source_axis_member_must_pair_with_every_6_value_outcome_"
        "axis_member"
    ),
    "every_source_outcome_pair_appears_exactly_once": True,
    "every_matrix_row_contains_all_authority_values": True,
    "every_matrix_column_contains_all_authority_values": True,
    "removing_any_scenario_loses_its_unique_source_outcome_pair": True,
}
TOP_LEVEL_KEYS = {
    "schema_version",
    "operation_id",
    "recorded_at",
    "status",
    "exact_bindings",
    "axis_families",
    "authority_axis_matrix_by_source_row_and_outcome_column",
    "pairwise_proof",
    "unmasked_witness_cells",
    "scenario_phase_order",
    "adapter_precedence",
    "evidence_rules",
    "closed_boundaries",
    "claim_ceiling",
}

PRACTICE_ID = UUID("10000000-0000-0000-0000-000000000101")
ACTOR_ID = UUID("20000000-0000-0000-0000-000000000101")
APPOINTMENT_ID = UUID("30000000-0000-0000-0000-000000000101")
LOCATION_ID = UUID("40000000-0000-0000-0000-000000000101")
AREA_ID = UUID("50000000-0000-0000-0000-000000000101")
COMMAND_ID = UUID("60000000-0000-0000-0000-000000000101")
AUDIT_ID = UUID("70000000-0000-0000-0000-000000000101")
EVENT_ID = UUID("80000000-0000-0000-0000-000000000101")
NOW = datetime(2026, 8, 24, 6, 0, tzinfo=timezone.utc)
OPAQUE_EVIDENCE = "opaque-authored-synthetic-temporal-check-in-evidence"
RAW_IDEMPOTENCY_KEY = "authored-synthetic-temporal-check-in-key"
FORBIDDEN_RELEASE_VALUES = (
    OPAQUE_EVIDENCE,
    RAW_IDEMPOTENCY_KEY,
    str(APPOINTMENT_ID),
    str(ACTOR_ID),
    str(PRACTICE_ID),
    "patient_id",
    "patient_name",
    "notes",
)


class RehearsalError(RuntimeError):
    """The frozen scenario contract or one observed adapter result changed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RehearsalError(message)


def _canonical_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    require(b"\r" not in raw.replace(b"\r\n", b""), f"bare CR: {path}")
    return raw.replace(b"\r\n", b"\n")


def _sha256(path: Path) -> str:
    return hashlib.sha256(_canonical_bytes(path)).hexdigest()


def _git_blob(root: Path, relative: str) -> str:
    result = subprocess.run(
        ["git", "hash-object", "--", relative],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _git_ancestor(root: Path, object_id: str) -> bool:
    return (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", object_id, "HEAD"],
            cwd=root,
            check=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )


def load_contract(root: Path) -> dict[str, Any]:
    path = (root / CONTRACT_PATH).resolve()
    require(path.is_relative_to(root.resolve()), "contract escapes repository")
    value = json.loads(_canonical_bytes(path).decode("utf-8"))
    require(isinstance(value, dict), "contract must be an object")
    return value


def pairwise_sets(matrix: tuple[tuple[int, ...], ...] = AUTHORITY_MATRIX) -> dict[str, set[tuple[int, int]]]:
    pairs = {"source_authority": set(), "source_outcome": set(), "authority_outcome": set()}
    for source_index, row in enumerate(matrix):
        for outcome_index, authority_index in enumerate(row):
            pairs["source_authority"].add((source_index, authority_index))
            pairs["source_outcome"].add((source_index, outcome_index))
            pairs["authority_outcome"].add((authority_index, outcome_index))
    return pairs


def validate_contract(contract: dict[str, Any], root: Path, *, check_git: bool = True) -> None:
    require(set(contract) == TOP_LEVEL_KEYS, "top-level keys changed")
    require(contract["schema_version"] == SCHEMA_VERSION, "schema version changed")
    require(contract["operation_id"] == OPERATION_ID, "operation changed")
    require(contract["status"] == "frozen_minimum_pairwise_provider_free_rehearsal", "status changed")
    require(contract["exact_bindings"] == EXACT_BINDINGS, "exact bindings changed")
    for label in ("planning_baseline", "accepted_predecessor_review_source", "protected_ref_commit"):
        object_id = contract["exact_bindings"][label]
        require(re.fullmatch(r"[0-9a-f]{40}", object_id) is not None, f"bad full Git ID: {label}")
        if check_git and label != "protected_ref_commit":
            require(_git_ancestor(root, object_id), f"non-ancestor Git ID: {label}")
    if check_git:
        require(_git_ancestor(root, PLANNING_SOURCE), "planning source is not an ancestor")
        require(_sha256(root / AXIS_CONTRACT_PATH) == EXACT_BINDINGS["successor_axis_contract_sha256"], "axis contract changed")
        require(_git_blob(root, ADAPTER_PATH) == EXACT_BINDINGS["adapter_git_blob"], "adapter blob changed")
        require(_git_blob(root, ADAPTER_TEST_PATH) == EXACT_BINDINGS["accepted_adapter_test_git_blob"], "adapter test blob changed")

    axes = contract["axis_families"]
    require(
        axes
        == {
            "source_and_waiting_area_transition": list(SOURCE_AXIS),
            "authority_evidence_and_freshness_transition": list(AUTHORITY_AXIS),
            "idempotency_and_outcome_transition": list(OUTCOME_AXIS),
        },
        "axis families changed",
    )
    matrix = tuple(tuple(row) for row in contract["authority_axis_matrix_by_source_row_and_outcome_column"])
    require(matrix == AUTHORITY_MATRIX, "authority matrix changed")
    pairs = pairwise_sets(matrix)
    require(len(pairs["source_authority"]) == 20, "source-authority coverage changed")
    require(len(pairs["source_outcome"]) == 30, "source-outcome coverage changed")
    require(len(pairs["authority_outcome"]) == 24, "authority-outcome coverage changed")
    require(contract["pairwise_proof"] == PAIRWISE_PROOF, "pairwise proof changed")
    require(
        {key: tuple(value) for key, value in contract["unmasked_witness_cells"].items()} == WITNESS_CELLS,
        "witness cells changed",
    )
    require(tuple(contract["scenario_phase_order"]) == PHASE_ORDER, "phase order changed")
    require(tuple(contract["adapter_precedence"]) == PRECEDENCE, "precedence changed")
    require(contract["evidence_rules"] == EVIDENCE_RULES, "evidence rules changed")
    require(contract["closed_boundaries"] == CLOSED_BOUNDARIES, "closed boundaries changed")
    require(
        contract["claim_ceiling"]
        == "minimum_pairwise_authored_synthetic_in_memory_adapter_composition_and_precedence_only",
        "claim ceiling changed",
    )


class SyntheticDependencies:
    def __init__(self, *, appointment: Any, current_actor: Any, areas: dict[UUID, Any]) -> None:
        self.appointment = appointment
        self.current_actor = current_actor
        self.areas = areas
        self.claim_kind = "started"
        self.replay_body: dict[str, Any] | None = None
        self.verify_result: tuple[bool, str, dict[str, Any] | None] = (
            True,
            "signed_evidence_verified",
            {},
        )
        self.fail_at: str | None = None
        self.calls: list[str] = []
        self.commits = 0
        self.rollbacks = 0
        self._snapshot: tuple[Any, Any] | None = None

    def _fail(self, stage: str) -> None:
        if self.fail_at == stage:
            raise RuntimeError(f"injected {stage} failure")

    def claim(self, **_kwargs: Any) -> SimpleNamespace:
        self.calls.append("claim")
        return SimpleNamespace(
            kind=self.claim_kind,
            record=SimpleNamespace(id=COMMAND_ID),
            response_status_code=200,
            response_body_json=copy.deepcopy(self.replay_body),
        )

    def load_locked_appointment(self, **_kwargs: Any) -> Any:
        self.calls.append("lock")
        return self.appointment

    def load_current_actor(self, **_kwargs: Any) -> Any:
        self.calls.append("reauthorize")
        return self.current_actor

    def load_waiting_area(self, **kwargs: Any) -> Any:
        self.calls.append("waiting_area")
        return self.areas.get(kwargs["waiting_area_id"])

    def verify_evidence(self, _evidence: str, **_kwargs: Any) -> Any:
        self.calls.append("verify")
        return self.verify_result

    def stage_effect(self, **kwargs: Any) -> None:
        self.calls.append("effect")
        self._snapshot = (self.appointment.status, self.appointment.waiting_area_id)
        plan = kwargs["plan"]
        self.appointment.status = AppointmentStatus.Arrived
        self.appointment.waiting_area_id = plan.waiting_area_id_after

    def write_audit(self, **_kwargs: Any) -> SimpleNamespace:
        self.calls.append("audit")
        self._fail("audit")
        return SimpleNamespace(id=AUDIT_ID)

    def write_event(self, **_kwargs: Any) -> SimpleNamespace:
        self.calls.append("event")
        return SimpleNamespace(id=EVENT_ID)

    def complete(self, **_kwargs: Any) -> None:
        self.calls.append("complete")

    def commit(self) -> None:
        self.calls.append("commit")
        self._fail("commit")
        self.commits += 1

    def rollback(self) -> None:
        self.calls.append("rollback")
        self.rollbacks += 1
        if self._snapshot is not None:
            self.appointment.status, self.appointment.waiting_area_id = self._snapshot

    def readback(self, **_kwargs: Any) -> Any:
        self.calls.append("readback")
        self._fail("readback")
        return self.appointment

    def bundle(self) -> CheckInDependencies:
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


def _actor(*, active: bool = True) -> SimpleNamespace:
    return SimpleNamespace(
        id=ACTOR_ID,
        practice_id=PRACTICE_ID,
        role=UserRole.Receptionist,
        is_active=active,
    )


def _source_fixture(source: str) -> tuple[Any, dict[UUID, Any], UUID | None, bool]:
    preserve = source == "eligible_preserve_valid"
    assign = source in {
        "eligible_assign_valid",
        "intervening_area_topology_change_rejected",
    }
    appointment = SimpleNamespace(
        id=APPOINTMENT_ID,
        practice_id=PRACTICE_ID,
        status=AppointmentStatus.Confirmed if preserve else AppointmentStatus.Booked,
        waiting_area_id=AREA_ID if preserve else None,
        location_id=LOCATION_ID,
    )
    areas = {
        AREA_ID: SimpleNamespace(
            id=AREA_ID,
            practice_id=PRACTICE_ID,
            location_id=LOCATION_ID,
            is_active=True,
        )
    } if preserve or assign else {}
    return appointment, areas, AREA_ID if assign else None, assign


def _body(appointment: Any, *, supplied_area: UUID | None, supplied: bool) -> AppointmentCheckInProposalConfirmationIn:
    command = AppointmentCheckInCommand(
        appointment_id=APPOINTMENT_ID,
        waiting_area_id=supplied_area,
        waiting_area_id_supplied=supplied,
    )
    freshness = check_in_proposal_freshness_id(command, check_in_state_payload(appointment))
    proposal = AppointmentCheckInProposalOut(
        safe=True,
        requires_confirmation=True,
        autonomy_tier="execute_with_report",
        summary="Authored-synthetic time-ordered check-in",
        command=command,
        warnings=[],
        blocks=[],
        check_in_proposal_freshness_id=freshness,
        signed_confirmation_evidence=OPAQUE_EVIDENCE,
        signed_confirmation_evidence_required=True,
    )
    return AppointmentCheckInProposalConfirmationIn(
        confirmed=True,
        check_in_proposal=proposal,
        confirmed_warnings=[],
        check_in_proposal_freshness_id=freshness,
        signed_confirmation_evidence=OPAQUE_EVIDENCE,
        signed_confirmation_evidence_required=True,
    )


def _invoke(deps: SyntheticDependencies, body: AppointmentCheckInProposalConfirmationIn):
    return compose_product_check_in(
        body,
        target_appointment_id=APPOINTMENT_ID,
        server_practice_id=PRACTICE_ID,
        authenticated_actor=_actor(),
        raw_idempotency_key=RAW_IDEMPOTENCY_KEY,
        now=NOW,
        dependencies=deps.bundle(),
    )


def _replay_seed(source: str) -> dict[str, Any]:
    appointment, areas, supplied_area, supplied = _source_fixture(source)
    deps = SyntheticDependencies(appointment=appointment, current_actor=_actor(), areas=areas)
    result = _invoke(deps, _body(appointment, supplied_area=supplied_area, supplied=supplied))
    require(result.kind == "confirmed_write" and result.committed is True, "replay seed failed")
    return copy.deepcopy(result.response_body)


def _apply_intervening_changes(
    source: str,
    authority: str,
    deps: SyntheticDependencies,
) -> list[str]:
    changes: list[str] = []
    if authority == "actor_revoked":
        deps.current_actor.is_active = False
        changes.append("current_receptionist_revoked")
    elif authority == "evidence_invalidated":
        deps.verify_result = (False, "signed_evidence_expired", None)
        changes.append("signed_evidence_invalidated")
    elif authority == "proposal_stale_after_intervening_update":
        deps.appointment.status = (
            AppointmentStatus.Booked
            if deps.appointment.status == AppointmentStatus.Confirmed
            else AppointmentStatus.Confirmed
        )
        changes.append("eligible_appointment_state_changed_after_proposal")

    if source == "intervening_state_change_rejected":
        deps.appointment.status = AppointmentStatus.Cancelled
        changes.append("appointment_changed_to_ineligible_source_state")
    elif source == "intervening_area_topology_change_rejected":
        deps.areas[AREA_ID].is_active = False
        changes.append("assigned_waiting_area_became_inactive")
    if not changes:
        changes.append("no_intervening_change")
    return changes


def _claim_variant(source_index: int, outcome: str) -> str:
    if outcome == "exact_replay":
        return "replay"
    if outcome == "conflict_or_in_progress":
        return "conflict" if source_index % 2 == 0 else "in_progress"
    return "started"


def _expected_result(source: str, authority: str, outcome: str, claim_variant: str) -> dict[str, Any]:
    if claim_variant == "replay":
        return {"kind": "replay", "outcome": "replay", "reason": None, "committed": True}
    if claim_variant == "conflict":
        return {"kind": "stopped", "outcome": "idempotency_conflict", "reason": "idempotency_key_conflict", "committed": False}
    if claim_variant == "in_progress":
        return {"kind": "stopped", "outcome": "in_progress", "reason": "command_in_progress", "committed": False}
    if source == "intervening_state_change_rejected":
        return {"kind": "stopped", "outcome": "validation_rejected", "reason": "invalid_source_status", "committed": False}
    if authority == "actor_revoked":
        return {"kind": "stopped", "outcome": "authority_revoked", "reason": "current_authority_revoked", "committed": False}
    if authority == "proposal_stale_after_intervening_update":
        return {"kind": "stopped", "outcome": "stale_precondition", "reason": "stale_check_in_proposal_freshness_id", "committed": False}
    if authority == "evidence_invalidated":
        return {"kind": "stopped", "outcome": "confirmation_required", "reason": "signed_evidence_expired", "committed": False}
    if source == "intervening_area_topology_change_rejected":
        return {"kind": "stopped", "outcome": "validation_rejected", "reason": "waiting_area_not_active", "committed": False}
    if outcome == "precommit_failure":
        return {"kind": "stopped", "outcome": "retry_required", "reason": "precommit_composition_failed", "committed": False}
    if outcome == "commit_outcome_unknown":
        return {"kind": "stopped", "outcome": "outcome_unknown", "reason": "commit_outcome_unknown", "committed": None}
    if outcome == "committed_readback_unavailable":
        return {"kind": "stopped", "outcome": "outcome_unknown", "reason": "committed_readback_unavailable", "committed": None}
    return {"kind": "confirmed_write", "outcome": "confirmed_write", "reason": None, "committed": True}


def _expected_calls(source: str, authority: str, outcome: str, claim_variant: str) -> list[str]:
    calls = ["claim"]
    if claim_variant == "replay":
        return calls
    if claim_variant in {"conflict", "in_progress"}:
        return calls + ["rollback"]
    calls.append("lock")
    if source == "intervening_state_change_rejected":
        return calls + ["rollback"]
    calls.append("reauthorize")
    if authority == "actor_revoked":
        return calls + ["rollback"]
    if authority == "proposal_stale_after_intervening_update":
        return calls + ["rollback"]
    calls.append("verify")
    if authority == "evidence_invalidated":
        return calls + ["rollback"]
    if source in {
        "eligible_assign_valid",
        "eligible_preserve_valid",
        "intervening_area_topology_change_rejected",
    }:
        calls.append("waiting_area")
    if source == "intervening_area_topology_change_rejected":
        return calls + ["rollback"]
    calls.extend(["effect", "audit"])
    if outcome == "precommit_failure":
        return calls + ["rollback"]
    calls.extend(["event", "complete", "commit"])
    if outcome == "commit_outcome_unknown":
        return calls
    calls.append("readback")
    return calls


def _readback_disposition(expected: dict[str, Any], outcome: str) -> str:
    if expected["kind"] == "replay":
        return "exact_replay_without_lock_or_readback"
    if expected["reason"] == "precommit_composition_failed":
        return "rolled_back_to_transaction_entry"
    if expected["reason"] == "commit_outcome_unknown":
        return "commit_outcome_unknown_without_readback"
    if expected["reason"] == "committed_readback_unavailable":
        return "committed_readback_unavailable_no_false_success"
    if expected["kind"] == "confirmed_write" and outcome == "first_execution":
        return "matching_committed_readback"
    return "not_reached_after_fail_closed_stop"


def run_scenario(source_index: int, outcome_index: int) -> dict[str, Any]:
    source = SOURCE_AXIS[source_index]
    outcome = OUTCOME_AXIS[outcome_index]
    authority = AUTHORITY_AXIS[AUTHORITY_MATRIX[source_index][outcome_index]]
    appointment, areas, supplied_area, supplied = _source_fixture(source)
    initial_status = appointment.status.value
    initial_area_mode = "preserve" if appointment.waiting_area_id else ("assign" if supplied else "none")
    body = _body(appointment, supplied_area=supplied_area, supplied=supplied)
    deps = SyntheticDependencies(appointment=appointment, current_actor=_actor(), areas=areas)
    changes = _apply_intervening_changes(source, authority, deps)
    claim_variant = _claim_variant(source_index, outcome)
    deps.claim_kind = claim_variant
    replay_seed_created = False
    if claim_variant == "replay":
        deps.replay_body = _replay_seed(source)
        replay_seed_created = True
    elif outcome == "precommit_failure":
        deps.fail_at = "audit"
    elif outcome == "commit_outcome_unknown":
        deps.fail_at = "commit"
    elif outcome == "committed_readback_unavailable":
        deps.fail_at = "readback"

    expected = _expected_result(source, authority, outcome, claim_variant)
    expected_calls = _expected_calls(source, authority, outcome, claim_variant)
    transaction_entry = (deps.appointment.status, deps.appointment.waiting_area_id)
    result = _invoke(deps, body)
    observed = {
        "kind": result.kind,
        "outcome": result.outcome,
        "reason": result.reason,
        "committed": result.committed,
    }
    require(observed == expected, f"typed result changed for {source_index}:{outcome_index}")
    require(deps.calls == expected_calls, f"callback order changed for {source_index}:{outcome_index}")
    if expected["reason"] == "precommit_composition_failed":
        require(
            (deps.appointment.status, deps.appointment.waiting_area_id) == transaction_entry,
            "precommit rollback did not restore transaction entry",
        )
        require(deps.rollbacks == 1 and deps.commits == 0, "precommit counters changed")
    if expected["reason"] in {"commit_outcome_unknown", "committed_readback_unavailable"}:
        require(result.response_body.get("receipt") is None, "unknown outcome released receipt")
        require(deps.rollbacks == 0, "postcommit uncertainty rolled back")
    if expected["kind"] == "confirmed_write":
        require(deps.appointment.status == AppointmentStatus.Arrived, "success readback changed")
        require(deps.commits == 1 and deps.rollbacks == 0, "success counters changed")

    return {
        "scenario_id": f"s{source_index + 1:02d}-o{outcome_index + 1:02d}",
        "cell": [source_index, outcome_index],
        "axes": {
            "source_and_waiting_area_transition": source,
            "authority_evidence_and_freshness_transition": authority,
            "idempotency_and_outcome_transition": outcome,
            "idempotency_submode": claim_variant,
        },
        "initial_state": {
            "status": initial_status,
            "waiting_area_mode": initial_area_mode,
        },
        "intervening_changes": changes,
        "replay_seed_created_through_same_adapter": replay_seed_created,
        "expected_adapter_result": expected,
        "observed_adapter_result": observed,
        "callback_sequence": list(deps.calls),
        "readback_disposition": _readback_disposition(expected, outcome),
    }


def _witness_checks(scenarios: list[dict[str, Any]]) -> dict[str, bool]:
    by_cell = {tuple(item["cell"]): item for item in scenarios}
    checks: dict[str, bool] = {}
    for name, cell in WITNESS_CELLS.items():
        item = by_cell[cell]
        axes = item["axes"]
        observed = item["observed_adapter_result"]
        if name == "eligible_none":
            passed = observed["kind"] == "confirmed_write" and "waiting_area" not in item["callback_sequence"]
        elif name == "eligible_assign_valid":
            passed = item["initial_state"]["waiting_area_mode"] == "assign" and "effect" in item["callback_sequence"]
        elif name == "eligible_preserve_valid":
            passed = item["initial_state"]["waiting_area_mode"] == "preserve" and observed["reason"] == "commit_outcome_unknown"
        elif name == "intervening_state_change_rejected":
            passed = observed["reason"] == "invalid_source_status"
        elif name == "intervening_area_topology_change_rejected":
            passed = observed["reason"] == "waiting_area_not_active"
        elif name == "unchanged_valid":
            passed = observed["kind"] == "confirmed_write"
        elif name == "actor_revoked":
            passed = observed["reason"] == "current_authority_revoked"
        elif name == "evidence_invalidated":
            passed = observed["reason"] == "signed_evidence_expired"
        elif name == "proposal_stale_after_intervening_update":
            passed = observed["reason"] == "stale_check_in_proposal_freshness_id"
        elif name in {"conflict", "in_progress"}:
            passed = axes["idempotency_submode"] == name and observed["outcome"] in {"idempotency_conflict", "in_progress"}
        elif name == "first_execution":
            passed = observed["kind"] == "confirmed_write"
        elif name == "exact_replay":
            passed = observed["kind"] == "replay" and item["callback_sequence"] == ["claim"]
        elif name == "precommit_failure":
            passed = observed["reason"] == "precommit_composition_failed" and item["readback_disposition"] == "rolled_back_to_transaction_entry"
        elif name == "commit_outcome_unknown":
            passed = observed["reason"] == "commit_outcome_unknown" and observed["committed"] is None
        else:
            passed = observed["reason"] == "committed_readback_unavailable" and observed["committed"] is None
        checks[name] = passed
    require(all(checks.values()), "one or more unmasked witnesses changed")
    return checks


def hostile_contract_mutations(contract: dict[str, Any]) -> list[dict[str, Any]]:
    mutations: list[dict[str, Any]] = []
    for key in sorted(TOP_LEVEL_KEYS):
        value = copy.deepcopy(contract)
        value.pop(key)
        mutations.append(value)
    for source_index in range(5):
        for outcome_index in range(6):
            value = copy.deepcopy(contract)
            current = value["authority_axis_matrix_by_source_row_and_outcome_column"][source_index][outcome_index]
            value["authority_axis_matrix_by_source_row_and_outcome_column"][source_index][outcome_index] = (current + 1) % 4
            mutations.append(value)
    for family in contract["axis_families"]:
        value = copy.deepcopy(contract)
        value["axis_families"][family][0] = "free_form"
        mutations.append(value)
    for key in contract["unmasked_witness_cells"]:
        value = copy.deepcopy(contract)
        value["unmasked_witness_cells"][key] = [4, 5]
        mutations.append(value)
    for key in ("planning_baseline", "accepted_predecessor_review_source", "protected_ref_commit"):
        value = copy.deepcopy(contract)
        value["exact_bindings"][key] = value["exact_bindings"][key][:7]
        mutations.append(value)
    for field in ("scenario_count", "required_cross_family_pair_count"):
        value = copy.deepcopy(contract)
        value["pairwise_proof"][field] += 1
        mutations.append(value)
    for field in ("scenario_phase_order", "adapter_precedence"):
        value = copy.deepcopy(contract)
        value[field] = list(reversed(value[field]))
        mutations.append(value)
    for field in ("evidence_rules", "closed_boundaries"):
        value = copy.deepcopy(contract)
        first = next(iter(value[field]))
        value[field][first] = not value[field][first]
        mutations.append(value)
    return mutations


def run_rehearsal(root: Path) -> dict[str, Any]:
    contract = load_contract(root)
    validate_contract(contract, root)
    rejected = 0
    for mutation in hostile_contract_mutations(contract):
        try:
            validate_contract(mutation, root, check_git=False)
        except RehearsalError:
            rejected += 1
    require(rejected == len(hostile_contract_mutations(contract)), "hostile mutation escaped")

    scenarios = [
        run_scenario(source_index, outcome_index)
        for source_index in range(len(SOURCE_AXIS))
        for outcome_index in range(len(OUTCOME_AXIS))
    ]
    require(len(scenarios) == 30, "scenario count changed")
    pairs = pairwise_sets()
    witnesses = _witness_checks(scenarios)
    conflict_modes = Counter(
        item["axes"]["idempotency_submode"]
        for item in scenarios
        if item["axes"]["idempotency_and_outcome_transition"] == "conflict_or_in_progress"
    )
    require(conflict_modes["conflict"] == 3 and conflict_modes["in_progress"] == 2, "idempotency submode coverage changed")
    result_counts = Counter(item["observed_adapter_result"]["outcome"] for item in scenarios)
    reason_counts = Counter(
        item["observed_adapter_result"]["reason"] or "none"
        for item in scenarios
    )
    evidence = {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "operation_id": OPERATION_ID,
        "recorded_at": RECORDED_AT,
        "planning_source": PLANNING_SOURCE,
        "decision": DECISION,
        "contract_sha256": _sha256(root / CONTRACT_PATH),
        "exact_bindings": EXACT_BINDINGS,
        "pairwise_coverage": {
            "scenario_count": len(scenarios),
            "full_cross_product_count": 120,
            "source_authority_pairs": len(pairs["source_authority"]),
            "source_outcome_pairs": len(pairs["source_outcome"]),
            "authority_outcome_pairs": len(pairs["authority_outcome"]),
            "required_cross_family_pair_count": sum(len(value) for value in pairs.values()),
            "minimum_by_unique_source_outcome_pairs": True,
        },
        "unmasked_witnesses": witnesses,
        "idempotency_submode_counts": dict(sorted(conflict_modes.items())),
        "result_outcome_counts": dict(sorted(result_counts.items())),
        "result_reason_counts": dict(sorted(reason_counts.items())),
        "hostile_contract_mutations_rejected": rejected,
        "scenario_results": scenarios,
        "closed_boundaries": {
            "historical_or_local_data_accessed": False,
            "provider_model_or_network_used": False,
            "product_adapter_route_schema_database_client_runtime_or_configuration_changed": False,
            "ordinary_practice_activated": False,
            "production_deployment_release_pages_or_protected_ref_moved": False,
        },
        "claim_ceiling": "minimum_pairwise_authored_synthetic_in_memory_adapter_composition_and_precedence_only",
    }
    serialized = json.dumps(evidence, sort_keys=True)
    for forbidden in FORBIDDEN_RELEASE_VALUES:
        require(forbidden not in serialized, f"forbidden release value: {forbidden}")
    return evidence


def build_efficacy_reading(evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": EFFICACY_SCHEMA_VERSION,
        "recorded_at": RECORDED_AT,
        "planning_source": PLANNING_SOURCE,
        "decision": "effective_minimum_pairwise_time_ordered_adapter_precedence_evidence",
        "utility": {
            "scenario_count": evidence["pairwise_coverage"]["scenario_count"],
            "cross_family_pairs_covered": evidence["pairwise_coverage"]["required_cross_family_pair_count"],
            "full_cross_product_avoided_cases": 90,
            "all_unmasked_witnesses_passed": all(evidence["unmasked_witnesses"].values()),
            "new_check_in_business_rules": 0,
            "product_files_changed": 0,
            "historical_data_reads": 0,
        },
        "recommendation": "review_the_temporal_composition_evidence_for_the_narrowest_adapter_or_operational_gap_without_reopening_historical_data",
    }


def render_report(evidence: dict[str, Any]) -> str:
    coverage = evidence["pairwise_coverage"]
    outcomes = "\n".join(
        f"- `{key}`: {value}"
        for key, value in evidence["result_outcome_counts"].items()
    )
    return f"""# Authored-synthetic time-ordered canonical check-in context branch composition — report

Date: 2026-08-24

Timestamp: {RECORDED_AT} (Australia/Brisbane)

Decision: `{DECISION}`

## Result

The unchanged unmounted adapter passed exactly {coverage['scenario_count']} authored-synthetic
time-ordered scenarios. They cover all {coverage['required_cross_family_pair_count']} required
cross-family pairs at the mathematical 30-case lower bound; a 120-case full
cross-product would add 90 cases without adding a new pair.

Every frozen source/waiting-area, authority/evidence/freshness and
idempotency/outcome value has an unmasked witness. Exact replay stopped before
lock, both conflict and in-progress stopped at the claim boundary, precommit
failure restored transaction-entry state, and commit/readback uncertainty
released no false success.

## Typed outcomes

{outcomes}

The counts describe this deliberately constructed matrix, not historical or
real-practice frequency.

## Claim boundary

This is provider-free in-memory contract evidence for the existing adapter's
composition and fail-closed precedence. It added zero business rules and
changed zero product files. It did not read the historical diary trove or any
`local_data`, invoke a provider/model/network, mount a route, use a database,
activate ordinary practice or open production, deployment, release, Pages or
protected-ref authority.
"""


def release(root: Path, evidence: dict[str, Any]) -> None:
    outputs = {
        EVIDENCE_PATH: json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        EFFICACY_PATH: json.dumps(build_efficacy_reading(evidence), indent=2, sort_keys=True) + "\n",
        REPORT_PATH: render_report(evidence),
    }
    for relative, content in outputs.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--release", action="store_true")
    args = parser.parse_args(argv)
    try:
        evidence = run_rehearsal(args.root.resolve())
        if args.release:
            release(args.root.resolve(), evidence)
        print(json.dumps(evidence, sort_keys=True))
        return 0
    except (OSError, ValueError, RehearsalError, subprocess.SubprocessError) as exc:
        print(json.dumps({"decision": "revision_required", "reason": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())
