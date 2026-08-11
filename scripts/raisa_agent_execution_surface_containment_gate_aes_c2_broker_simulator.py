"""Pure provider-free AES-C2 broker simulator over authored-synthetic objects.

This module proves the smallest broker-owned dispatch step beneath the accepted
AES-C0 authority contract and the AES-C1 admission result.  AES-C2 may call
exactly one fixed pure inert adapter function in-process after a fresh exact
AES-C1 ``allow``.  It never starts a broker or work-cell process, mounts a real
adapter, performs external I/O, or creates provider, product, data, credential,
tool or command authority.

The evidence label is
``authored_synthetic_provider_free_in_process_inert_simulation``.  All values are
newly authored synthetic.  An adapter invocation here means one ordinary pure
Python function call, never a runtime service, executable tool, provider tool or
product adapter.
"""

from __future__ import annotations

import argparse
import copy
from datetime import datetime
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.raisa_agent_execution_surface_containment_gate_aes_c0_acceptance import (
    validate_instance,
    _forbidden_keys,
)
from scripts.raisa_agent_execution_surface_containment_gate_aes_c1_admission import (
    AES_C0_SCHEMA,
    CONTRACT_PATH as AES_C1_CONTRACT_PATH,
    SCHEMA_PATH as AES_C1_SCHEMA_PATH,
    SCENARIOS_PATH as AES_C1_SCENARIOS_PATH,
    EVIDENCE_PATH as AES_C1_EVIDENCE_PATH,
    _load,
    digest_of,
    evaluate_attempt,
    validate_attempt as validate_c1_attempt,
)

BASE = (
    ROOT
    / "orchestration/continuity/"
    "raisa-agent-execution-surface-containment-gate-aes-c2"
)
CONTRACT_PATH = BASE / "broker-simulator-contract.json"
SCHEMA_PATH = BASE / "broker-simulator-contract.schema.json"
SCENARIOS_PATH = BASE / "authored-synthetic-broker-simulator-scenarios.json"
EVIDENCE_PATH = BASE / "provider-free-broker-simulator-evidence.json"
C1_SCRIPT_PATH = (
    ROOT / "scripts/raisa_agent_execution_surface_containment_gate_aes_c1_admission.py"
)

WRONG_DIGEST = "sha256:" + "9" * 64
ADAPTER_ARTIFACT_DIGEST = "sha256:" + "f" * 64

# Exact inherited AES-C1 artifact identities frozen by the C2 plan.
INHERITED_ARTIFACT_DIGESTS: dict[str, str] = {
    AES_C1_CONTRACT_PATH.relative_to(ROOT).as_posix(): (
        "sha256:241f081b1c3346ef50e80eb495c9bfb6ea3b99f67956b439c7c7638962069f90"
    ),
    AES_C1_SCHEMA_PATH.relative_to(ROOT).as_posix(): (
        "sha256:2e6c5b83d379f5b6f900fa0a26a8733b6fe09496ff8e1c52d5ed40123603e9b6"
    ),
    AES_C1_SCENARIOS_PATH.relative_to(ROOT).as_posix(): (
        "sha256:e6e427efa32fb27387598042f0d1b1f19c4472b09288f7c8d3ed321a7309945c"
    ),
    AES_C1_EVIDENCE_PATH.relative_to(ROOT).as_posix(): (
        "sha256:f7d1a2f60ef4b6f46242cfff7a12b36b6e20405a07ad788854c877851a0bbd4c"
    ),
    C1_SCRIPT_PATH.relative_to(ROOT).as_posix(): (
        "sha256:4407646c98dee84e8ef4210b0e06aa500178b5a2e2094ca02003b43fbf0acda6"
    ),
}

STATUS_VOCABULARY: list[str] = ["simulated", "not_dispatched", "stop"]
REASON_VOCABULARY: list[str] = [
    "simulated_inert_adapter",
    "admission_not_allow",
    "registry_not_exact",
    "adapter_identity_mismatch",
    "supply_chain_identity_mismatch",
    "credential_custody_violation",
    "control_state_changed",
    "external_kill_switch",
    "invocation_contract_mismatch",
    "adapter_result_invalid",
    "budget_commit_mismatch",
    "generation_terminal",
]
DISPATCH_PRECEDENCE: list[str] = [
    "1_reject_malformed_or_open_contract_attempt_registry_result_or_evidence",
    "2_stop_on_inherited_aes_c1_artifact_or_simulator_contract_digest_mismatch",
    "3_recompute_and_run_exact_aes_c1_admission_over_broker_side_attempt",
    "4_return_not_dispatched_when_aes_c1_returns_deny_or_stop",
    "5_stop_unless_registry_is_exactly_one_frozen_definition_and_identity_equals_admitted_operation",
    "6_stop_if_work_cell_view_contains_forbidden_custody_or_identity_field",
    "7_recheck_generation_manifest_authority_revocation_and_external_kill_before_dispatch",
    "8_verify_and_commit_exact_aes_c1_budget_after_digest_and_cumulative_counts_before_invocation",
    "9_build_invocation_entirely_from_registry_and_admitted_candidate_digest_and_allowlisted_fields",
    "10_compare_broker_private_synthetic_custody_binding_without_copying_handle_or_value",
    "11_call_single_fixed_pure_adapter_function_at_most_once",
    "12_validate_exact_adapter_result_before_returning_minimized_evidence",
    "13_make_any_stop_or_exhausted_generation_terminal_for_following_attempt",
]

# The one closed declarative adapter definition.  It deliberately contains no
# URL, host, port, path, SQL, executable, command route, tool definition,
# cleanup target, environment variable or provider identifier.
IMPLEMENTATION_DEFINITION: dict[str, Any] = {
    "schema_version": "emr4.aes_c2.adapter_definition.v1",
    "implementation_id": "aes-c2-pure-inert-render-v1",
    "kind": "pure_inert_render",
    "input_fields": [
        "invocation-id",
        "operation-id",
        "candidate-digest",
        "synthetic-input-alpha",
        "synthetic-input-beta",
    ],
    "result_fields": ["result-code", "invocation-digest", "result-digest"],
    "effect_class": "none",
    "external_io": False,
    "command_authority": False,
    "contains_provider_identifier": False,
    "contains_url_host_port_path_sql_executable_command_tool": False,
}
IMPLEMENTATION_DEFINITION_DIGEST: str = digest_of(IMPLEMENTATION_DEFINITION)

# The exact single immutable registry entry.
BROKER_REGISTRY_ENTRY: dict[str, Any] = {
    "schema_version": "emr4.aes_c2.broker_registry_entry.v1",
    "entry_id": "registry-synthetic-inert-001",
    "capability_class": "inert_tool_adapter",
    "capability_id": "capability-synthetic-inert",
    "adapter_id": "synthetic-inert-adapter",
    "operation_id": "render-inert-adapter",
    "destination_id": "synthetic-inert-destination",
    "method": "POST",
    "media_type": "application/json",
    "source_class": "authored_synthetic",
    "implementation_id": "aes-c2-pure-inert-render-v1",
    "effect_class": "none",
    "external_io": False,
    "command_authority": False,
    "adapter_artifact_digest": ADAPTER_ARTIFACT_DIGEST,
    "implementation_definition_digest": IMPLEMENTATION_DEFINITION_DIGEST,
}

# The broker-private authored-synthetic noncredential custody fixture.  It is
# not a token, password, key, identity, secret or usable credential.  Only its
# SHA-256 binding is ever compared; the handle and value stay in this private
# source scope and never reach any work-cell, request, result, evidence,
# exception or returned simulator surface.
SYNTHETIC_FIXTURE_HANDLE = "synthetic-noncredential-fixture:inert-custody-handle-v1"
SYNTHETIC_FIXTURE_VALUE = "synthetic-noncredential-fixture:inert-custody-value-v1"
SYNTHETIC_FIXTURE_VALUE_DIGEST = digest_of(SYNTHETIC_FIXTURE_VALUE)

SYNTHETIC_CUSTODY_BINDING: dict[str, Any] = {
    "schema_version": "emr4.aes_c2.synthetic_custody_binding.v1",
    "fixture_value_digest": SYNTHETIC_FIXTURE_VALUE_DIGEST,
    "real_credential": False,
}

BROKER_REGISTRY: dict[str, Any] = {
    "schema_version": "emr4.aes_c2.broker_registry.v1",
    "entries": [copy.deepcopy(BROKER_REGISTRY_ENTRY)],
    "synthetic_custody_binding": copy.deepcopy(SYNTHETIC_CUSTODY_BINDING),
}

# Two allowlisted authored-synthetic invocation inputs.  Candidate content can
# never select or replace these.
ALLOWED_INPUT_ALPHA = "authored-synthetic-inert-input-alpha"
ALLOWED_INPUT_BETA = "authored-synthetic-inert-input-beta"

# Fields that the work cell must never receive, directly or nested.
WORK_CELL_FORBIDDEN_FIELDS: list[str] = [
    "lease",
    "capability_lease",
    "registry",
    "broker_registry",
    "capability",
    "capability_id",
    "capability_class",
    "operation",
    "operation_id",
    "adapter",
    "adapter_id",
    "destination",
    "destination_id",
    "method",
    "media_type",
    "executable",
    "credential",
    "credential_reference",
    "filesystem_path",
    "path",
    "url",
    "sql",
    "tool",
    "tool_definition",
    "command_route",
    "cleanup_target",
    "policy",
    "policy_amendment",
]

ZERO_RUNTIME_BOUNDARY: dict[str, Any] = {
    "runtime_started": False,
    "provider_calls": 0,
    "real_adapters_executed": 0,
    "network_operations": 0,
    "database_operations": 0,
    "source_operations": 0,
    "filesystem_operations": 0,
    "executable_or_tool_operations": 0,
    "command_operations": 0,
    "real_credentials_used": False,
    "product_or_patient_data": False,
}

SYNTHETIC_CUSTODY_POLICY: dict[str, Any] = {
    "fixture_value_prefix": "synthetic-noncredential-fixture:",
    "real_credential": False,
    "fixture_is_broker_private": True,
    "fixture_never_emitted": True,
    "digest_only_comparison": True,
    "no_cross_generation_transfer": True,
}

DIGEST_RULES: dict[str, Any] = {
    "implementation_definition_digest_rule": {
        "algorithm": "sha256",
        "canonicalization": "json_utf8_sorted_keys_compact_separators",
        "digested_object": "implementation_definition",
        "compared_with": "broker_registry.entries[0].implementation_definition_digest",
    },
    "invocation_digest_rule": {
        "algorithm": "sha256",
        "canonicalization": "json_utf8_sorted_keys_compact_separators",
        "digested_object": "broker_invocation",
    },
    "adapter_result_digest_rule": {
        "algorithm": "sha256",
        "canonicalization": "json_utf8_sorted_keys_compact_separators",
        "digested_object": "adapter_result_payload",
    },
    "adapter_artifact_identity_rule": {
        "algorithm": "sha256",
        "canonicalization": "inherited_c1_manifest_and_current_generation_identity",
        "expected": ADAPTER_ARTIFACT_DIGEST,
        "compared_with": "broker_registry.entries[0].adapter_artifact_digest",
        "no_equality_or_preimage_with_implementation_definition_digest": True,
    },
}

ADAPTER_INVOCATION_CONTRACT: dict[str, Any] = {
    "schema_version": "emr4.aes_c2.broker_invocation.v1",
    "fields": [
        "schema_version",
        "invocation_id",
        "operation_id",
        "candidate_digest",
        "synthetic_input_alpha",
        "synthetic_input_beta",
    ],
    "operation_identity_broker_resolved": True,
    "candidate_content_selects_no_identity": True,
}

ADAPTER_RESULT_CONTRACT: dict[str, Any] = {
    "schema_version": "emr4.aes_c2.adapter_result.v1",
    "fields": [
        "schema_version",
        "result_id",
        "result_code",
        "invocation_digest",
        "result_digest",
        "command_authority",
        "effect_class",
        "contains_sensitive_values",
    ],
    "command_authority": False,
    "effect_class": "none",
    "contains_sensitive_values": False,
}

# Authoritative 26-scenario catalogue: scenario_id -> (status, reasons, calls).
SCENARIO_EXPECTATIONS: dict[str, tuple[str, list[str], int]] = {
    "exact-inert-dispatch-simulated": ("simulated", ["simulated_inert_adapter"], 1),
    "exact-inert-second-within-budget-simulated": (
        "simulated", ["simulated_inert_adapter"], 1),
    "admission-deny-not-dispatched": ("not_dispatched", ["admission_not_allow"], 0),
    "admission-stop-not-dispatched": ("not_dispatched", ["admission_not_allow"], 0),
    "proofreader-deny-not-dispatched": ("not_dispatched", ["admission_not_allow"], 0),
    "candidate-selector-not-dispatched": ("not_dispatched", ["admission_not_allow"], 0),
    "registry-missing-stop": ("stop", ["registry_not_exact"], 0),
    "registry-extra-entry-stop": ("stop", ["registry_not_exact"], 0),
    "registry-capability-mismatch-stop": ("stop", ["registry_not_exact"], 0),
    "registry-adapter-mismatch-stop": ("stop", ["adapter_identity_mismatch"], 0),
    "registry-destination-mismatch-stop": ("stop", ["adapter_identity_mismatch"], 0),
    "registry-method-mismatch-stop": ("stop", ["adapter_identity_mismatch"], 0),
    "registry-media-type-mismatch-stop": ("stop", ["adapter_identity_mismatch"], 0),
    "registry-operation-mismatch-stop": ("stop", ["adapter_identity_mismatch"], 0),
    "registry-implementation-digest-mismatch-stop": (
        "stop", ["adapter_identity_mismatch"], 0),
    "registry-custody-binding-mismatch-stop": (
        "stop", ["credential_custody_violation"], 0),
    "adapter-artifact-digest-mismatch-stop": (
        "stop", ["supply_chain_identity_mismatch"], 0),
    "work-cell-custody-exposure-stop": ("stop", ["credential_custody_violation"], 0),
    "generation-superseded-before-dispatch-stop": (
        "stop", ["control_state_changed"], 0),
    "authority-changed-before-dispatch-stop": ("stop", ["control_state_changed"], 0),
    "revocation-before-dispatch-stop": ("stop", ["control_state_changed"], 0),
    "external-kill-before-dispatch-stop": ("stop", ["external_kill_switch"], 0),
    "invocation-candidate-digest-mismatch-stop": (
        "stop", ["invocation_contract_mismatch"], 0),
    "adapter-result-contract-mismatch-stop": (
        "stop", ["adapter_result_invalid"], 1),
    "budget-commit-mismatch-stop": ("stop", ["budget_commit_mismatch"], 0),
    "repeat-after-terminal-stop": ("stop", ["generation_terminal"], 0),
}


def _set_path(value: dict[str, Any], path: tuple[Any, ...], replacement: Any) -> None:
    target: Any = value
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = replacement


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _c1_attempt(scenario_id: str) -> dict[str, Any]:
    packet = _load(AES_C1_SCENARIOS_PATH)
    for scenario in packet["scenarios"]:
        if scenario["scenario_id"] == scenario_id:
            return copy.deepcopy(scenario)
    raise ValueError(f"missing AES-C1 scenario: {scenario_id}")


def _canonical_post_admission_state(
    admission_attempt: dict[str, Any],
) -> dict[str, Any]:
    manifest = admission_attempt["generation_manifest"]
    return {
        "schema_version": "emr4.aes_c2.post_admission_control_state.v1",
        "generation_id": manifest["generation_id"],
        "manifest_id": manifest["manifest_id"],
        "manifest_digest": manifest["manifest_digest"],
        "authority_binding_digest": manifest["authority_binding_digest"],
        "revocation_record": None,
        "external_kill_switch_active": False,
    }


def _canonical_expected_budget_commit(
    admission_attempt: dict[str, Any],
) -> dict[str, Any]:
    c1 = evaluate_attempt(admission_attempt)
    return {
        "schema_version": "emr4.aes_c2.budget_commit.v1",
        "budget_after_digest": c1["broker_decision"]["budget_after_digest"],
        "cumulative_counts": dict(c1["after_observed"]),
        "terminal_state": c1["after_terminal_state"],
        "next_operation_permitted": c1["after_next_operation_permitted"],
    }


def _build_invocation(
    attempt: dict[str, Any], admitted_candidate_digest: str
) -> dict[str, Any]:
    return {
        "schema_version": "emr4.aes_c2.broker_invocation.v1",
        "invocation_id": f"invocation-{attempt['scenario_id']}",
        "operation_id": BROKER_REGISTRY_ENTRY["operation_id"],
        "candidate_digest": admitted_candidate_digest,
        "synthetic_input_alpha": ALLOWED_INPUT_ALPHA,
        "synthetic_input_beta": ALLOWED_INPUT_BETA,
    }


def _sample_revocation(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "emr4.aes_c0.revocation_record.v1",
        "revocation_id": "revocation-synthetic-002",
        "generation_id": manifest["generation_id"],
        "manifest_digest": manifest["manifest_digest"],
        "initiated_by": "external_operator",
        "reason_code": "external_stop",
        "effective_at": "2026-08-11T00:00:00Z",
        "all_leases_revoked": True,
        "all_aliases_invalidated": True,
        "all_tokens_invalidated": True,
        "all_writable_caches_quarantined": True,
        "all_further_calls_blocked": True,
        "conversation_clear_is_cleanup": False,
        "model_influenced_revocation": False,
        "evidence_digest": (
            "sha256:4444444444444444444444444444444444444444444444444444444444444444"
        ),
    }

# ---------------------------------------------------------------------------
# Pure adapter
# ---------------------------------------------------------------------------

def _pure_inert_render(
    invocation: dict[str, Any], _fixture_value: str
) -> dict[str, Any]:
    """The single fixed pure inert adapter function.

    It treats every input as an opaque value and never parses, selects or
    executes anything.  The synthetic custody fixture is passed only to prove
    the broker-custody rehearsal shape and is never emitted into the result.
    """
    invocation_digest = digest_of(invocation)
    result_payload = {
        "result_code": "inert-render-ok",
        "invocation_digest": invocation_digest,
    }
    result_digest = digest_of(result_payload)
    return {
        "schema_version": "emr4.aes_c2.adapter_result.v1",
        "result_id": f"result-{invocation.get('invocation_id', 'unknown')}",
        "result_code": "inert-render-ok",
        "invocation_digest": invocation_digest,
        "result_digest": result_digest,
        "command_authority": False,
        "effect_class": "none",
        "contains_sensitive_values": False,
    }


def _dispatch_adapter(
    attempt: dict[str, Any],
    invocation: dict[str, Any],
    fixture_value: str,
) -> dict[str, Any]:
    """Call the single pure adapter at most once.

    The optional ``adapter_result_override`` is the deterministic malformed-
    result seam used only by the frozen ``adapter-result-contract-mismatch-stop``
    scenario.  The adapter is still called once; the override is the observed
    result that must fail closed.
    """
    override = attempt.get("adapter_result_override")
    if override is not None:
        return copy.deepcopy(override)
    return _pure_inert_render(invocation, fixture_value)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_attempt(attempt: dict[str, Any]) -> list[str]:
    schema = _load(SCHEMA_PATH)
    errors = list(
        validate_instance(
            attempt,
            schema["$defs"]["BrokerSimulationAttempt"],
            root_schema=schema,
            path="$",
        )
    )
    admission_attempt = attempt.get("broker_admission_attempt")
    if isinstance(admission_attempt, dict):
        errors.extend(validate_c1_attempt(admission_attempt))
    view = attempt.get("work_cell_view")
    if isinstance(view, dict) and isinstance(admission_attempt, dict):
        if view.get("candidate") != admission_attempt.get("candidate"):
            errors.append("$.work_cell_view.candidate:cross_record_mismatch")
        if view.get("proofreader_result") != admission_attempt.get(
            "proofreader_result"
        ):
            errors.append("$.work_cell_view.proofreader_result:cross_record_mismatch")
    control = attempt.get("post_admission_control_state")
    if isinstance(control, dict):
        revocation = control.get("revocation_record")
        if revocation is not None:
            if not isinstance(revocation, dict):
                errors.append("$.post_admission_control_state.revocation_record:type")
            else:
                errors.extend(
                    validate_instance(
                        revocation,
                        AES_C0_SCHEMA["$defs"]["RevocationRecord"],
                        root_schema=AES_C0_SCHEMA,
                        path="$.post_admission_control_state.revocation_record",
                    )
                )
    return sorted(set(errors))

def validate_contract(contract: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors = list(validate_instance(contract, schema, root_schema=schema))
    if contract.get("schema_version") != "emr4.aes_c2.broker_simulator_contract.v1":
        errors.append("schema_version:not_exact")
    if contract.get("contract_id") != "raisa-agent-execution-surface-containment-gate-aes-c2":
        errors.append("contract_id:not_exact")
    if (
        contract.get("status")
        != "frozen_for_authored_synthetic_provider_free_in_process_simulation"
    ):
        errors.append("status:not_exact")
    if (
        contract.get("evidence_mode")
        != "authored_synthetic_provider_free_in_process_inert_simulation"
    ):
        errors.append("evidence_mode:not_exact")
    if contract.get("inherited_artifact_digests") != INHERITED_ARTIFACT_DIGESTS:
        errors.append("inherited_artifact_digests:not_exact")
    if contract.get("status_vocabulary") != STATUS_VOCABULARY:
        errors.append("status_vocabulary:not_exact")
    if contract.get("reason_vocabulary") != REASON_VOCABULARY:
        errors.append("reason_vocabulary:not_exact")
    if contract.get("dispatch_precedence") != DISPATCH_PRECEDENCE:
        errors.append("dispatch_precedence:not_exact")
    if contract.get("implementation_definition") != IMPLEMENTATION_DEFINITION:
        errors.append("implementation_definition:not_exact")
    if contract.get("broker_registry") != BROKER_REGISTRY:
        errors.append("broker_registry:not_exact")
    if contract.get("synthetic_custody_policy") != SYNTHETIC_CUSTODY_POLICY:
        errors.append("synthetic_custody_policy:not_exact")
    if contract.get("work_cell_forbidden_fields") != WORK_CELL_FORBIDDEN_FIELDS:
        errors.append("work_cell_forbidden_fields:not_exact")
    if contract.get("digest_rules") != DIGEST_RULES:
        errors.append("digest_rules:not_exact")
    if contract.get("adapter_invocation_contract") != ADAPTER_INVOCATION_CONTRACT:
        errors.append("adapter_invocation_contract:not_exact")
    if contract.get("adapter_result_contract") != ADAPTER_RESULT_CONTRACT:
        errors.append("adapter_result_contract:not_exact")
    if contract.get("zero_runtime_boundary") != ZERO_RUNTIME_BOUNDARY:
        errors.append("zero_runtime_boundary:not_exact")
    registry = contract.get("scenario_registry", [])
    if len(registry) != len(SCENARIO_EXPECTATIONS):
        errors.append("scenario_registry:count")
    registry_ids = [entry.get("scenario_id") for entry in registry]
    if len(set(registry_ids)) != len(registry_ids):
        errors.append("scenario_registry:duplicates")
    if set(registry_ids) != set(SCENARIO_EXPECTATIONS):
        errors.append("scenario_registry:ids_not_exact")
    for entry in registry:
        scenario_id = entry.get("scenario_id")
        if scenario_id not in SCENARIO_EXPECTATIONS:
            continue
        status, reasons, calls = SCENARIO_EXPECTATIONS[scenario_id]
        if entry.get("status") != status:
            errors.append(f"scenario_registry:{scenario_id}:status")
        if entry.get("reason_codes") != reasons:
            errors.append(f"scenario_registry:{scenario_id}:reason_codes")
        if entry.get("expected_invocations") != calls:
            errors.append(f"scenario_registry:{scenario_id}:invocations")
    boundary = contract.get("zero_runtime_boundary", {})
    for key in (
        "runtime_started",
        "provider_calls",
        "real_adapters_executed",
        "network_operations",
        "database_operations",
        "source_operations",
        "filesystem_operations",
        "executable_or_tool_operations",
        "command_operations",
    ):
        if boundary.get(key) is not False and boundary.get(key) != 0:
            errors.append(f"zero_runtime_boundary:{key}:opening_detected")
    if boundary.get("real_credentials_used") is not False:
        errors.append("zero_runtime_boundary:real_credentials_used")
    if boundary.get("product_or_patient_data") is not False:
        errors.append("zero_runtime_boundary:product_or_patient_data")
    return sorted(set(errors))


def validate_scenario_packet(
    packet: dict[str, Any], schema: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    if (
        packet.get("schema_version")
        != "emr4.aes_c2.authored_synthetic_broker_simulator_scenarios.v1"
    ):
        errors.append("scenarios:schema_version")
    if (
        packet.get("evidence_mode")
        != "authored_synthetic_provider_free_in_process_inert_simulation"
    ):
        errors.append("scenarios:evidence_mode")
    scenarios = packet.get("scenarios", [])
    if not isinstance(scenarios, list) or len(scenarios) != len(SCENARIO_EXPECTATIONS):
        errors.append("scenarios:count")
        return sorted(set(errors))
    ids = [scenario.get("scenario_id") for scenario in scenarios]
    if len(set(ids)) != len(ids):
        errors.append("scenarios:duplicate_ids")
    if set(ids) != set(SCENARIO_EXPECTATIONS):
        errors.append("scenarios:undeclared_ids")
    for attempt in scenarios:
        errors.extend(validate_attempt(attempt))
    return sorted(set(errors))

# ---------------------------------------------------------------------------
# Ordered fail-closed simulation
# ---------------------------------------------------------------------------

def _registry_stop_reason(
    registry: dict[str, Any], admission_attempt: dict[str, Any]
) -> str | None:
    entries = registry.get("entries")
    if not isinstance(entries, list) or len(entries) != 1:
        return "registry_not_exact"
    entry = entries[0]
    if not isinstance(entry, dict):
        return "registry_not_exact"
    frozen = BROKER_REGISTRY_ENTRY
    if set(entry) != set(frozen):
        return "registry_not_exact"
    for key in frozen:
        if entry[key] != frozen[key]:
            if key in (
                "capability_id",
                "adapter_id",
                "operation_id",
                "destination_id",
                "method",
                "media_type",
                "implementation_definition_digest",
            ):
                return "adapter_identity_mismatch"
            if key == "adapter_artifact_digest":
                return "supply_chain_identity_mismatch"
            return "registry_not_exact"
    # Every identity must equal the admitted broker-observed operation.
    observed_op = admission_attempt.get("broker_observed_operation", {})
    for key in (
        "capability_id",
        "adapter_id",
        "operation_id",
        "destination_id",
        "method",
        "media_type",
    ):
        if entry[key] != observed_op.get(key):
            return "adapter_identity_mismatch"
    return None


def _control_state_reason(
    attempt: dict[str, Any], admission_attempt: dict[str, Any]
) -> str | None:
    cs = attempt["post_admission_control_state"]
    manifest = admission_attempt["generation_manifest"]
    if cs["external_kill_switch_active"]:
        return "external_kill_switch"
    if cs["revocation_record"] is not None:
        return "control_state_changed"
    if cs["generation_id"] != manifest["generation_id"]:
        return "control_state_changed"
    if cs["manifest_id"] != manifest["manifest_id"]:
        return "control_state_changed"
    if cs["manifest_digest"] != manifest["manifest_digest"]:
        return "control_state_changed"
    if cs["authority_binding_digest"] != manifest["authority_binding_digest"]:
        return "control_state_changed"
    return None


def _invocation_errors(
    invocation: dict[str, Any], admitted_candidate_digest: str
) -> list[str]:
    schema = _load(SCHEMA_PATH)
    errors = list(
        validate_instance(
            invocation,
            schema["$defs"]["BrokerInvocation"],
            root_schema=schema,
            path="$.broker_invocation",
        )
    )
    if invocation.get("candidate_digest") != admitted_candidate_digest:
        errors.append("broker_invocation:candidate_digest_mismatch")
    if invocation.get("operation_id") != BROKER_REGISTRY_ENTRY["operation_id"]:
        errors.append("broker_invocation:operation_identity_mismatch")
    if (
        invocation.get("synthetic_input_alpha") != ALLOWED_INPUT_ALPHA
        or invocation.get("synthetic_input_beta") != ALLOWED_INPUT_BETA
    ):
        errors.append("broker_invocation:allowlisted_input_mismatch")
    return errors


def _adapter_result_errors(
    adapter_result: dict[str, Any], invocation: dict[str, Any]
) -> list[str]:
    schema = _load(SCHEMA_PATH)
    errors = list(
        validate_instance(
            adapter_result,
            schema["$defs"]["AdapterResult"],
            root_schema=schema,
            path="$.adapter_result",
        )
    )
    invocation_digest = digest_of(invocation)
    if adapter_result.get("invocation_digest") != invocation_digest:
        errors.append("adapter_result:invocation_digest_mismatch")
    result_payload = {
        "result_code": adapter_result.get("result_code"),
        "invocation_digest": adapter_result.get("invocation_digest"),
    }
    if adapter_result.get("result_digest") != digest_of(result_payload):
        errors.append("adapter_result:result_digest_mismatch")
    return errors


def _build_result(
    attempt: dict[str, Any],
    c1: dict[str, Any],
    status: str,
    reason: str,
    invocation_count: int,
    released: bool,
    invocation_digest: str | None = None,
    result_digest: str | None = None,
) -> dict[str, Any]:
    scenario_id = attempt["scenario_id"]
    budget_after_digest = c1["broker_decision"]["budget_after_digest"] if c1 else None
    return {
        "schema_version": "emr4.aes_c2.broker_simulation_result.v1",
        "result_id": f"simulation-result-{scenario_id}",
        "scenario_id": scenario_id,
        "status": status,
        "reason_codes": [reason],
        "admission_decision": c1["decision"] if c1 else "stop",
        "admission_reason_codes": c1["reason_codes"] if c1 else [],
        "simulated_invocation_count": invocation_count,
        "released_simulated_result": released,
        "adapter_artifact_identity_digest": ADAPTER_ARTIFACT_DIGEST,
        "implementation_definition_digest": IMPLEMENTATION_DEFINITION_DIGEST,
        "budget_after_digest": budget_after_digest,
        "invocation_digest": invocation_digest,
        "result_digest": result_digest,
        "boundary_assertions": {
            "work_cell_received_lease_or_registry": False,
            "work_cell_received_credential_fixture": False,
            "candidate_selected_operation_identity": False,
            "command_authority": False,
            "real_runtime_or_external_effect": False,
        },
        "contains_sensitive_values": False,
    }

def evaluate_simulation_attempt(attempt: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one closed BrokerSimulationAttempt with fixed fail-closed order."""
    admission_attempt = attempt["broker_admission_attempt"]

    # Step 3: recompute exact AES-C1 admission over the broker-side attempt.
    c1 = evaluate_attempt(admission_attempt)

    # Step 4: not_dispatched when AES-C1 returns deny or stop.
    if c1["decision"] != "allow":
        return _build_result(
            attempt, c1, "not_dispatched", "admission_not_allow", 0, False
        )

    # Step 5: registry exact one-entry and identity equality.
    registry = attempt["broker_registry"]
    reg_reason = _registry_stop_reason(registry, admission_attempt)
    if reg_reason is not None:
        return _build_result(attempt, c1, "stop", reg_reason, 0, False)

    # Step 6: work-cell view forbidden custody/identity fields.
    forbidden = _forbidden_keys(
        attempt["work_cell_view"], set(WORK_CELL_FORBIDDEN_FIELDS)
    )
    if forbidden:
        return _build_result(
            attempt, c1, "stop", "credential_custody_violation", 0, False
        )

    # Step 7: control-state recheck at the dispatch instant.
    control_reason = _control_state_reason(attempt, admission_attempt)
    if control_reason is not None:
        return _build_result(attempt, c1, "stop", control_reason, 0, False)

    # Step 8: exact AES-C1 budget-after digest and cumulative counts; terminal
    # state stops before invocation.
    commit = attempt["expected_budget_commit"]
    if commit["budget_after_digest"] != c1["broker_decision"]["budget_after_digest"]:
        return _build_result(attempt, c1, "stop", "budget_commit_mismatch", 0, False)
    if commit["cumulative_counts"] != c1["after_observed"]:
        return _build_result(attempt, c1, "stop", "budget_commit_mismatch", 0, False)
    if commit["terminal_state"] != c1["after_terminal_state"]:
        return _build_result(attempt, c1, "stop", "budget_commit_mismatch", 0, False)
    if commit["next_operation_permitted"] != c1["after_next_operation_permitted"]:
        return _build_result(attempt, c1, "stop", "budget_commit_mismatch", 0, False)
    if admission_attempt["budget_state"]["next_operation_permitted"] is False:
        return _build_result(attempt, c1, "stop", "generation_terminal", 0, False)

    # Step 9: build the closed invocation from the registry plus admitted
    # candidate digest and the two allowlisted authored-synthetic values.
    admitted_candidate_digest = c1["broker_decision"]["candidate_digest"]
    invocation = attempt.get("invocation_override")
    if invocation is None:
        invocation = _build_invocation(attempt, admitted_candidate_digest)
    if _invocation_errors(invocation, admitted_candidate_digest):
        return _build_result(
            attempt, c1, "stop", "invocation_contract_mismatch", 0, False
        )

    # Step 10: compare the broker-private synthetic custody binding digest only.
    if (
        registry["synthetic_custody_binding"]["fixture_value_digest"]
        != SYNTHETIC_FIXTURE_VALUE_DIGEST
    ):
        return _build_result(
            attempt, c1, "stop", "credential_custody_violation", 0, False
        )

    # Step 11: call the single fixed pure adapter function at most once.
    adapter_result = _dispatch_adapter(attempt, invocation, SYNTHETIC_FIXTURE_VALUE)
    invocation_count = 1
    invocation_digest = digest_of(invocation)

    # Step 12: validate the exact adapter result before releasing anything.
    result_errors = _adapter_result_errors(adapter_result, invocation)
    if result_errors:
        return _build_result(
            attempt, c1, "stop", "adapter_result_invalid", invocation_count, False
        )
    return _build_result(
        attempt,
        c1,
        "simulated",
        "simulated_inert_adapter",
        invocation_count,
        True,
        invocation_digest,
        adapter_result["result_digest"],
    )

# ---------------------------------------------------------------------------
# Authored-synthetic scenario authoring
# ---------------------------------------------------------------------------

def _base_attempt(scenario_id: str) -> dict[str, Any]:
    c1 = _c1_attempt("exact-inert-intersection-allow")
    return {
        "schema_version": "emr4.aes_c2.broker_simulation_attempt.v1",
        "attempt_id": f"simulation-{scenario_id}",
        "scenario_id": scenario_id,
        "work_cell_view": {
            "schema_version": "emr4.aes_c2.work_cell_view.v1",
            "candidate": copy.deepcopy(c1["candidate"]),
            "proofreader_result": copy.deepcopy(c1["proofreader_result"]),
        },
        "broker_admission_attempt": c1,
        "post_admission_control_state": _canonical_post_admission_state(c1),
        "broker_registry": copy.deepcopy(BROKER_REGISTRY),
        "expected_budget_commit": _canonical_expected_budget_commit(c1),
        "invocation_override": None,
        "adapter_result_override": None,
    }


def _adopt_c1(scenario_id: str) -> Callable[[dict[str, Any]], None]:
    def mutate(attempt: dict[str, Any]) -> None:
        c1 = _c1_attempt(scenario_id)
        attempt["broker_admission_attempt"] = c1
        attempt["work_cell_view"]["candidate"] = copy.deepcopy(c1["candidate"])
        attempt["work_cell_view"]["proofreader_result"] = copy.deepcopy(
            c1["proofreader_result"]
        )
        attempt["post_admission_control_state"] = _canonical_post_admission_state(c1)
        attempt["expected_budget_commit"] = _canonical_expected_budget_commit(c1)
    return mutate


def _build_scenarios() -> list[dict[str, Any]]:
    attempts: list[dict[str, Any]] = []

    def add(
        scenario_id: str, mutate: Callable[[dict[str, Any]], None]
    ) -> None:
        attempt = _base_attempt(scenario_id)
        mutate(attempt)
        attempts.append(attempt)

    # 1-2: simulated success scenarios.
    add("exact-inert-dispatch-simulated", lambda a: None)
    add("exact-inert-second-within-budget-simulated", _adopt_c1(
        "exact-inert-second-within-budget-allow"))

    # 3-6: AES-C1 deny/stop -> not_dispatched.
    add("admission-deny-not-dispatched", _adopt_c1("grant-missing-deny"))
    add("admission-stop-not-dispatched", _adopt_c1("external-kill-switch-stop"))
    add("proofreader-deny-not-dispatched", _adopt_c1("proofreader-not-admitted-deny"))
    add("candidate-selector-not-dispatched", _adopt_c1(
        "candidate-operation-identity-deny"))

    # 7-8: registry count.
    add("registry-missing-stop", lambda a: a["broker_registry"]["entries"].clear())
    add("registry-extra-entry-stop", lambda a: a["broker_registry"]["entries"].append(
        copy.deepcopy(BROKER_REGISTRY_ENTRY)))

    # 9-17: registry field mismatches.
    add("registry-capability-mismatch-stop", lambda a: _set_path(
        a, ("broker_registry", "entries", 0, "capability_class"),
        "authoritative_read"))
    add("registry-adapter-mismatch-stop", lambda a: _set_path(
        a, ("broker_registry", "entries", 0, "adapter_id"),
        "synthetic-other-adapter"))
    add("registry-destination-mismatch-stop", lambda a: _set_path(
        a, ("broker_registry", "entries", 0, "destination_id"),
        "synthetic-other-destination"))
    add("registry-method-mismatch-stop", lambda a: _set_path(
        a, ("broker_registry", "entries", 0, "method"), "GET"))
    add("registry-media-type-mismatch-stop", lambda a: _set_path(
        a, ("broker_registry", "entries", 0, "media_type"), "text/plain"))
    add("registry-operation-mismatch-stop", lambda a: _set_path(
        a, ("broker_registry", "entries", 0, "operation_id"),
        "render-other-operation"))
    add("registry-implementation-digest-mismatch-stop", lambda a: _set_path(
        a, ("broker_registry", "entries", 0, "implementation_definition_digest"),
        WRONG_DIGEST))
    add("registry-custody-binding-mismatch-stop", lambda a: _set_path(
        a, ("broker_registry", "synthetic_custody_binding", "fixture_value_digest"),
        WRONG_DIGEST))
    add("adapter-artifact-digest-mismatch-stop", lambda a: _set_path(
        a, ("broker_registry", "entries", 0, "adapter_artifact_digest"),
        WRONG_DIGEST))

    # 18: work-cell custody exposure (declared hostile field in the view).
    def sc18(a: dict[str, Any]) -> None:
        a["work_cell_view"]["credential_reference"] = "attacker-placed-custody-marker"
    add("work-cell-custody-exposure-stop", sc18)

    # 19-22: control-state changes after admission.
    add("generation-superseded-before-dispatch-stop", lambda a: _set_path(
        a, ("post_admission_control_state", "generation_id"),
        "generation-synthetic-002"))
    add("authority-changed-before-dispatch-stop", lambda a: _set_path(
        a, ("post_admission_control_state", "authority_binding_digest"),
        WRONG_DIGEST))
    add("revocation-before-dispatch-stop", lambda a: _set_path(
        a, ("post_admission_control_state", "revocation_record"),
        _sample_revocation(a["broker_admission_attempt"]["generation_manifest"])))
    add("external-kill-before-dispatch-stop", lambda a: _set_path(
        a, ("post_admission_control_state", "external_kill_switch_active"), True))

    # 23: invocation candidate-digest mismatch.
    def sc23(a: dict[str, Any]) -> None:
        a["invocation_override"] = _build_invocation(a, WRONG_DIGEST)
    add("invocation-candidate-digest-mismatch-stop", sc23)

    # 24: malformed adapter result (the adapter is still called once).
    def sc24(a: dict[str, Any]) -> None:
        a["adapter_result_override"] = {
            "schema_version": "emr4.aes_c2.adapter_result.v1",
            "result_id": "result-adapter-result-contract-mismatch-stop",
            "result_code": "inert-render-ok",
            "invocation_digest": WRONG_DIGEST,
            "result_digest": WRONG_DIGEST,
            "command_authority": True,
            "effect_class": "none",
            "contains_sensitive_values": False,
        }
    add("adapter-result-contract-mismatch-stop", sc24)

    # 25: budget commit mismatch.
    add("budget-commit-mismatch-stop", lambda a: _set_path(
        a, ("expected_budget_commit", "budget_after_digest"), WRONG_DIGEST))

    # 26: following attempt after a terminal/exhausted generation.
    def sc26(a: dict[str, Any]) -> None:
        c1 = _c1_attempt("exact-inert-second-within-budget-allow")
        c1["budget_state"]["next_operation_permitted"] = False
        c1["budget_state"]["terminal_state"] = "exhausted"
        a["broker_admission_attempt"] = c1
        a["work_cell_view"]["candidate"] = copy.deepcopy(c1["candidate"])
        a["work_cell_view"]["proofreader_result"] = copy.deepcopy(
            c1["proofreader_result"]
        )
        a["post_admission_control_state"] = _canonical_post_admission_state(c1)
        a["expected_budget_commit"] = _canonical_expected_budget_commit(c1)
    add("repeat-after-terminal-stop", sc26)

    return attempts


def generate_scenarios() -> dict[str, Any]:
    attempts = _build_scenarios()
    return {
        "schema_version": "emr4.aes_c2.authored_synthetic_broker_simulator_scenarios.v1",
        "evidence_mode": "authored_synthetic_provider_free_in_process_inert_simulation",
        "scenarios": attempts,
    }

# ---------------------------------------------------------------------------
# Hostile mutations
# ---------------------------------------------------------------------------

def _hostile_mutations() -> list[tuple[str, Callable[[dict[str, Any]], None]]]:
    return [
        ("additional_top_level_key", lambda a: _set_path(a, ("forged_field",), "forged")),
        ("missing_required_key", lambda a: a.__delitem__("expected_budget_commit")),
        ("wrong_type_scenario_id", lambda a: _set_path(a, ("scenario_id",), 7)),
        ("additional_work_cell_key", lambda a: _set_path(
            a, ("work_cell_view", "forged_benign_key"), "forged")),
        ("work_cell_capability_field", lambda a: _set_path(
            a, ("work_cell_view", "capability_id"), "capability-forged")),
        ("work_cell_adapter_field", lambda a: _set_path(
            a, ("work_cell_view", "adapter_id"), "adapter-forged")),
        ("work_cell_destination_field", lambda a: _set_path(
            a, ("work_cell_view", "destination_id"), "destination-forged")),
        ("work_cell_method_field", lambda a: _set_path(
            a, ("work_cell_view", "method"), "GET")),
        ("work_cell_executable_field", lambda a: _set_path(
            a, ("work_cell_view", "executable"), "forged.exe")),
        ("work_cell_credential_field", lambda a: _set_path(
            a, ("work_cell_view", "credential"), "forged-credential")),
        ("work_cell_command_route_field", lambda a: _set_path(
            a, ("work_cell_view", "command_route"), "forged/route")),
        ("second_registry_entry", lambda a: a["broker_registry"]["entries"].append(
            copy.deepcopy(BROKER_REGISTRY_ENTRY))),
        ("registry_url_field", lambda a: _set_path(
            a, ("broker_registry", "entries", 0, "url"), "https://forged.invalid")),
        ("registry_filesystem_path_field", lambda a: _set_path(
            a, ("broker_registry", "entries", 0, "filesystem_path"), "/tmp/forged")),
        ("registry_sql_field", lambda a: _set_path(
            a, ("broker_registry", "entries", 0, "sql"), "SELECT 1")),
        ("registry_executable_selector_field", lambda a: _set_path(
            a, ("broker_registry", "entries", 0, "executable"), "forged.exe")),
        ("adapter_result_sensitive_field", lambda a: _set_path(
            a, ("adapter_result_override", "contains_sensitive_values"), True)),
        ("adapter_result_command_authority_field", lambda a: _set_path(
            a, ("adapter_result_override", "command_authority"), True)),
    ]


def validate_hostile_mutations() -> tuple[list[str], list[str]]:
    """Apply independent hostile mutations; zero may reach simulated release."""
    base = _base_attempt("hostile-mutation-base")
    rejected: list[str] = []
    admitted: list[str] = []
    for name, mutate in _hostile_mutations():
        candidate = copy.deepcopy(base)
        try:
            mutate(candidate)
        except (KeyError, TypeError):
            rejected.append(name)
            continue
        errors = validate_attempt(candidate)
        if errors:
            rejected.append(name)
            continue
        result = evaluate_simulation_attempt(candidate)
        if result["status"] == "simulated" and result["released_simulated_result"]:
            admitted.append(name)
        else:
            rejected.append(name)
    return rejected, admitted

def _hostile_contract_mutations() -> list[tuple[str, Callable[[dict[str, Any]], None]]]:
    inherited_key = next(iter(INHERITED_ARTIFACT_DIGESTS))
    return [
        ("contract_inherited_digest_value_changed", lambda c: _set_path(
            c, ("inherited_artifact_digests", inherited_key), WRONG_DIGEST)),
        ("contract_inherited_digests_extra", lambda c: _set_path(
            c, ("inherited_artifact_digests", "forged/path.json"),
            "sha256:" + "0" * 64)),
        ("contract_registry_adapter_changed", lambda c: _set_path(
            c, ("broker_registry", "entries", 0, "adapter_id"),
            "synthetic-other-adapter")),
        ("contract_registry_second_entry", lambda c: c["broker_registry"][
            "entries"].append(copy.deepcopy(BROKER_REGISTRY_ENTRY))),
        ("contract_implementation_definition_extra", lambda c: _set_path(
            c, ("implementation_definition", "forged_rule"), "forged")),
        ("contract_status_vocabulary_changed", lambda c: c["status_vocabulary"].__setitem__(
            0, "forged_status")),
        ("contract_reason_vocabulary_changed", lambda c: c["reason_vocabulary"].__setitem__(
            0, "forged_reason")),
        ("contract_dispatch_precedence_changed", lambda c: c["dispatch_precedence"].__setitem__(
            0, "0_forged_precedence")),
        ("contract_custody_policy_extra", lambda c: _set_path(
            c, ("synthetic_custody_policy", "forged_policy"), True)),
        ("contract_work_cell_forbidden_fields_changed", lambda c: c[
            "work_cell_forbidden_fields"].append("forged-field")),
        ("contract_digest_rules_extra", lambda c: _set_path(
            c, ("digest_rules", "forged_rule"), {"forged": True})),
        ("contract_invocation_contract_extra", lambda c: _set_path(
            c, ("adapter_invocation_contract", "forged_rule"), "forged")),
        ("contract_result_contract_extra", lambda c: _set_path(
            c, ("adapter_result_contract", "forged_rule"), "forged")),
        ("contract_zero_runtime_opened", lambda c: _set_path(
            c, ("zero_runtime_boundary", "runtime_started"), True)),
    ]


def validate_hostile_contract_mutations() -> tuple[list[str], list[str]]:
    contract = _load(CONTRACT_PATH)
    schema = _load(SCHEMA_PATH)
    rejected: list[str] = []
    admitted: list[str] = []
    for name, mutate in _hostile_contract_mutations():
        candidate = copy.deepcopy(contract)
        mutate(candidate)
        errors = validate_contract(candidate, schema)
        if errors:
            rejected.append(name)
        else:
            admitted.append(name)
    return rejected, admitted

# ---------------------------------------------------------------------------
# Evidence and static boundary checks
# ---------------------------------------------------------------------------

def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture_occurs(value: Any) -> bool:
    if isinstance(value, str):
        return SYNTHETIC_FIXTURE_HANDLE in value or SYNTHETIC_FIXTURE_VALUE in value
    if isinstance(value, dict):
        return any(_fixture_occurs(v) for v in value.values())
    if isinstance(value, list):
        return any(_fixture_occurs(v) for v in value)
    return False


def static_boundary_check() -> list[str]:
    """Prove no external-effect import or callable-selection path in this source."""
    import ast

    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    errors: list[str] = []

    banned_names = {
        "eval": "eval",
        "exec": "exec",
        "__import__": "dynamic_import",
        "importlib": "dynamic_import",
        "open": "filesystem_open",
        "subprocess": "subprocess",
        "os": "os_process",
        "socket": "socket",
        "http": "http_client",
        "urllib": "http_client",
        "requests": "http_client",
        "sqlite3": "database_client",
        "psycopg": "database_client",
        "getenv": "environment_read",
        "environ": "environment_read",
        "load": "deserialization_engine",
    }
    # The only permitted filesystem ``open`` is the deterministic minimized
    # evidence writer ``_write_lf``; reading committed fixture JSON is done
    # through the shared ``_load`` helper, never a bare ``open``.
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node

    def _enclosing_function(node):
        parent = node.parent if hasattr(node, "parent") else None
        while parent is not None:
            if isinstance(parent, ast.FunctionDef):
                return parent.name
            parent = parent.parent if hasattr(parent, "parent") else None
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in banned_names:
                if func.id == "open" and _enclosing_function(node) == "_write_lf":
                    continue
                errors.append(f"call:{banned_names[func.id]}:{func.id}")
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in banned_names:
                    errors.append(f"import:{banned_names[root]}:{alias.name}")
        if isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in banned_names:
                errors.append(f"import:{banned_names[root]}:{node.module}")

    callable_names = {
        n.id
        for n in ast.walk(tree)
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)
    }
    if "_pure_inert_render" not in callable_names:
        errors.append("static_boundary:pure_adapter_not_referenced")
    for banned in ("eval", "exec", "__import__", "importlib", "getattr"):
        if banned in callable_names:
            errors.append(f"static_boundary:dynamic_callable:{banned}")
    return sorted(set(errors))


def _fixture_leaks(results: list[dict[str, Any]], report: dict[str, Any]) -> list[str]:
    leaks: list[str] = []
    for result in results:
        if _fixture_occurs(result):
            leaks.append(result["scenario_id"])
    if _fixture_occurs(report):
        leaks.append("report")
    return sorted(set(leaks))

def build_report() -> dict[str, Any]:
    contract = _load(CONTRACT_PATH)
    schema = _load(SCHEMA_PATH)
    packet = _load(SCENARIOS_PATH)

    reasons: list[str] = []
    reasons.extend(validate_contract(contract, schema))
    reasons.extend(validate_scenario_packet(packet, schema))
    reasons.extend(static_boundary_check())

    for rel, expected in INHERITED_ARTIFACT_DIGESTS.items():
        if _digest(ROOT / rel) != expected:
            reasons.append(f"inherited_artifact_digest_mismatch:{rel}")

    scenario_results: list[dict[str, Any]] = []
    simulated_count = 0
    not_dispatched_count = 0
    stop_count = 0
    invocation_total = 0
    for attempt in packet["scenarios"]:
        scenario_id = attempt["scenario_id"]
        result = evaluate_simulation_attempt(attempt)
        expected_status, expected_reasons, expected_calls = SCENARIO_EXPECTATIONS[
            scenario_id
        ]
        if result["status"] != expected_status:
            reasons.append(f"scenario:{scenario_id}:status")
        if result["reason_codes"] != expected_reasons:
            reasons.append(f"scenario:{scenario_id}:reason_codes")
        if result["simulated_invocation_count"] != expected_calls:
            reasons.append(f"scenario:{scenario_id}:invocations")
        if result["released_simulated_result"] != (expected_status == "simulated"):
            reasons.append(f"scenario:{scenario_id}:released")
        if result["status"] == "simulated":
            simulated_count += 1
        elif result["status"] == "not_dispatched":
            not_dispatched_count += 1
        else:
            stop_count += 1
        invocation_total += result["simulated_invocation_count"]
        scenario_results.append(result)

    rejected, admitted = validate_hostile_mutations()
    if admitted:
        reasons.append("hostile_mutations_admitted:" + ",".join(admitted))
    contract_rejected, contract_admitted = validate_hostile_contract_mutations()
    if contract_admitted:
        reasons.append(
            "contract_hostile_mutations_admitted:" + ",".join(contract_admitted)
        )

    report: dict[str, Any] = {
        "schema_version": "emr4.aes_c2.broker_simulator_report.v1",
        "status": "passed" if not reasons else "revision_required",
        "evidence_mode": "authored_synthetic_provider_free_in_process_inert_simulation",
        "runtime_started": False,
        "provider_calls": 0,
        "real_adapters_executed": 0,
        "network_operations": 0,
        "database_operations": 0,
        "source_operations": 0,
        "filesystem_operations": 0,
        "executable_or_tool_operations": 0,
        "command_operations": 0,
        "real_credentials_used": False,
        "product_or_patient_data": False,
        "simulated_inert_invocation_count": invocation_total,
        "inherited_artifact_digests": dict(INHERITED_ARTIFACT_DIGESTS),
        "adapter_artifact_identity_digest": ADAPTER_ARTIFACT_DIGEST,
        "implementation_definition_digest": IMPLEMENTATION_DEFINITION_DIGEST,
        "scenario_count": len(scenario_results),
        "simulated_count": simulated_count,
        "not_dispatched_count": not_dispatched_count,
        "stop_count": stop_count,
        "scenario_results": scenario_results,
        "mutation_count": len(_hostile_mutations()),
        "mutation_rejected_count": len(rejected),
        "mutation_admitted": admitted,
        "contract_mutation_count": len(_hostile_contract_mutations()),
        "contract_mutation_rejected_count": len(contract_rejected),
        "contract_mutation_admitted": contract_admitted,
        "reasons": sorted(set(reasons)),
        "artifact_digests": {
            CONTRACT_PATH.relative_to(ROOT).as_posix(): _digest(CONTRACT_PATH),
            SCHEMA_PATH.relative_to(ROOT).as_posix(): _digest(SCHEMA_PATH),
            SCENARIOS_PATH.relative_to(ROOT).as_posix(): _digest(SCENARIOS_PATH),
        },
    }
    leaks = _fixture_leaks(scenario_results, report)
    if leaks:
        report["reasons"] = sorted(
            set(report["reasons"]) | {f"fixture_leak:{leak}" for leak in leaks}
        )
        report["status"] = "revision_required"
    return report


def _write_lf(path: Path, content: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)

def _contract_payload() -> dict[str, Any]:
    scenario_registry = [
        {
            "scenario_id": scenario_id,
            "status": status,
            "reason_codes": reasons,
            "expected_invocations": calls,
        }
        for scenario_id, (status, reasons, calls) in sorted(SCENARIO_EXPECTATIONS.items())
    ]
    return {
        "schema_version": "emr4.aes_c2.broker_simulator_contract.v1",
        "contract_id": "raisa-agent-execution-surface-containment-gate-aes-c2",
        "status": "frozen_for_authored_synthetic_provider_free_in_process_simulation",
        "evidence_mode": "authored_synthetic_provider_free_in_process_inert_simulation",
        "inherited_artifact_digests": dict(INHERITED_ARTIFACT_DIGESTS),
        "status_vocabulary": list(STATUS_VOCABULARY),
        "reason_vocabulary": list(REASON_VOCABULARY),
        "dispatch_precedence": list(DISPATCH_PRECEDENCE),
        "implementation_definition": copy.deepcopy(IMPLEMENTATION_DEFINITION),
        "broker_registry": copy.deepcopy(BROKER_REGISTRY),
        "synthetic_custody_policy": copy.deepcopy(SYNTHETIC_CUSTODY_POLICY),
        "work_cell_forbidden_fields": list(WORK_CELL_FORBIDDEN_FIELDS),
        "digest_rules": copy.deepcopy(DIGEST_RULES),
        "adapter_invocation_contract": copy.deepcopy(ADAPTER_INVOCATION_CONTRACT),
        "adapter_result_contract": copy.deepcopy(ADAPTER_RESULT_CONTRACT),
        "zero_runtime_boundary": copy.deepcopy(ZERO_RUNTIME_BOUNDARY),
        "scenario_registry": scenario_registry,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--generate-scenarios",
        action="store_true",
        help="Regenerate the authored-synthetic broker-simulator scenario packet.",
    )
    parser.add_argument(
        "--generate-contract",
        action="store_true",
        help="Regenerate the closed broker-simulator contract.",
    )
    args = parser.parse_args()
    if args.generate_contract:
        contract = _contract_payload()
        _write_lf(CONTRACT_PATH, json.dumps(contract, indent=2, sort_keys=True) + "\n")
        print("wrote", CONTRACT_PATH.relative_to(ROOT).as_posix())
        return 0
    if args.generate_scenarios:
        packet = generate_scenarios()
        _write_lf(
            SCENARIOS_PATH,
            json.dumps(packet, indent=2, sort_keys=True) + "\n",
        )
        print(
            "wrote",
            SCENARIOS_PATH.relative_to(ROOT).as_posix(),
            "with",
            len(packet["scenarios"]),
            "scenarios",
        )
        return 0
    report = build_report()
    _write_lf(EVIDENCE_PATH, json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
