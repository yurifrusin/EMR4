"""Exercise the inert authored-synthetic shadow-comparison rehearsal."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator

from scripts.raisa_provider_free_unmounted_default_off_shadow_comparison_architecture import (
    EXPECTED_PROJECTION_FIELDS,
    EXPECTED_RECORD_FIELDS,
    admission_decision,
    load_contract as load_architecture_contract,
)
from scripts.raisa_provider_free_unmounted_pure_route_adapter_differential_rehearsal import (
    adapt_envelope,
    load_contract as load_adapter_contract,
    semantic_projection,
)


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal"
)
EVIDENCE_PATH = (
    EVIDENCE_DIR / "provider-free-authored-synthetic-shadow-comparison-evidence.json"
)
SCHEMA_PATH = (
    EVIDENCE_DIR
    / "provider-free-authored-synthetic-shadow-comparison-evidence.schema.json"
)

EXPECTED_SOURCE_HEAD = "fb899b26966c1a171528306ae5ab49b80bacc947"
EXPECTED_SOURCE_BINDINGS = {
    "orchestration/continuity/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture/contract.json": "bbef6febf7046521dbc7112d25cfa7984c4acaa3a059872abd0bf183aecc2c81",
    "docs/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture-plan.md": "e1199e1902fa776c8b965567d4b6ba1aae10fbb13ba45e6c9a93073a3d6971bc",
    "docs/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture.md": "04aeb534c025ad48f498cfe89e09ccbb62b04da14f3331827fe82e384cf8c97e",
    "docs/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture-closeout.md": "639490e15e6ccfec146cc5b48c22bf167b66c1cd24b4fcdfe071f67636baf2ae",
    "orchestration/agent_inbox/codex/raisa-default-off-shadow-comparison-architecture-sol-acceptance.md": "fbc47ae99c3e9dcf629a5af772d95aa131b5082cc04f5e5f2621f330b7feece0",
    "orchestration/continuity/raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal/contract.json": "050ddc373b5ca7f1f00207122da653fd9bb5dae01c7b313a88fa529e6b640ddc",
    "scripts/raisa_provider_free_unmounted_pure_route_adapter_differential_rehearsal.py": "bfe9d352c6c8cfd717e0edaee9b42279da4d53d18162d3a155c771ce4e398939",
    "orchestration/api_spine_adr.md": "d0fa77aec371d634284f81bf1fd6cfd49bb5a52fbe14003a17c5e35dcaf0283e",
}
ARCHITECTURE_GENERATION_DIGEST = "syn-hmac-sha256-architecture-generation-001"
CONFIGURATION_DIGEST = "syn-hmac-sha256-shadow-configuration-001"
RECORDED_AT = "2026-08-12T00:00:00Z"
EXPECTED_GAPS = [
    "backend_precondition_missing",
    "confirmation_evidence_missing",
    "idempotency_identity_missing",
]
EXPECTED_SEMANTIC_DIGESTS = {
    "raw_compat_create": "4f9e3e15feace896f83fa1868a44cafc968145c8716d89274cded93b4c387f1f",
    "raw_compat_update": "ba9af26c4c49cb6614963bf98983d0ef1f11df1ab220d5f74da5d48d630d5347",
    "raw_compat_status": "fc2612db4256da953090aa76e4ba9cc0f0a6a9b80c2ab8960a3b403fb704829b",
    "raw_compat_delete": "5ad4cd47e5b5b67e2dd9e3d1233ebd8a6ef584eca0c3a55c696ec16ea2f5b42d",
}
ROUTE_FACTS = {
    "raw_compat_create": (
        "create",
        "confirmAppointmentCreateProposal",
        None,
        "syn-hmac-sha256-conflict-create-001",
        "practice_schedule_domain",
    ),
    "raw_compat_update": (
        "update",
        "confirmAppointmentUpdateProposal",
        "syn-hmac-sha256-target-update-001",
        "syn-hmac-sha256-conflict-update-001",
        "appointment_and_schedule_domain",
    ),
    "raw_compat_status": (
        "status",
        "confirmAppointmentStatusProposal",
        "syn-hmac-sha256-target-status-001",
        None,
        "appointment_status_target",
    ),
    "raw_compat_delete": (
        "delete",
        "confirmAppointmentDeleteProposal",
        "syn-hmac-sha256-target-delete-001",
        None,
        "appointment_delete_target",
    ),
}


def _controls(
    generation_status: str | None = "current",
    global_state: str | None = "enabled",
    practice_state: str | None = "enabled",
    route_allowed: bool | None = True,
    externally_disabled: bool | None = False,
) -> dict[str, Any]:
    return {
        "generation_status": generation_status,
        "global_state": global_state,
        "practice_state": practice_state,
        "route_allowed": route_allowed,
        "externally_disabled": externally_disabled,
    }


SCENARIO_SPECS = [
    {
        "scenario_id": "shd-001-global-default-denied",
        "case_kind": "disabled",
        "route_adapter_id": "raw_compat_create",
        "controls": _controls(global_state="disabled"),
        "projection_profile": "raw_current",
        "comparison_mode": "expected_current_gaps",
        "fault": "none",
    },
    {
        "scenario_id": "shd-002-practice-default-denied",
        "case_kind": "disabled",
        "route_adapter_id": "raw_compat_update",
        "controls": _controls(practice_state="disabled"),
        "projection_profile": "raw_current",
        "comparison_mode": "expected_current_gaps",
        "fault": "none",
    },
    {
        "scenario_id": "shd-003-route-default-denied",
        "case_kind": "disabled",
        "route_adapter_id": "raw_compat_status",
        "controls": _controls(route_allowed=False),
        "projection_profile": "raw_current",
        "comparison_mode": "expected_current_gaps",
        "fault": "none",
    },
    {
        "scenario_id": "shd-004-stale-generation-denied",
        "case_kind": "disabled",
        "route_adapter_id": "raw_compat_delete",
        "controls": _controls(generation_status="stale"),
        "projection_profile": "raw_current",
        "comparison_mode": "expected_current_gaps",
        "fault": "none",
    },
    {
        "scenario_id": "shd-005-missing-generation-denied",
        "case_kind": "disabled",
        "route_adapter_id": "raw_compat_create",
        "controls": _controls(generation_status=None),
        "projection_profile": "raw_current",
        "comparison_mode": "expected_current_gaps",
        "fault": "none",
    },
    {
        "scenario_id": "shd-006-external-disable-denied",
        "case_kind": "disabled",
        "route_adapter_id": "raw_compat_update",
        "controls": _controls(externally_disabled=True),
        "projection_profile": "raw_current",
        "comparison_mode": "expected_current_gaps",
        "fault": "none",
    },
    *[
        {
            "scenario_id": f"shd-{number:03d}-expected-current-gaps-{family}",
            "case_kind": "admitted_expected_gap",
            "route_adapter_id": route_id,
            "controls": _controls(),
            "projection_profile": "raw_current",
            "comparison_mode": "expected_current_gaps",
            "fault": "none",
        }
        for number, (route_id, (family, *_)) in enumerate(
            ROUTE_FACTS.items(), start=7
        )
    ],
    {
        "scenario_id": "shd-011-unexpected-gap-set",
        "case_kind": "unexpected_gap",
        "route_adapter_id": "raw_compat_update",
        "controls": _controls(),
        "projection_profile": "raw_precondition_only",
        "comparison_mode": "expected_current_gaps",
        "fault": "none",
    },
    {
        "scenario_id": "shd-012-unexpected-candidate",
        "case_kind": "unexpected_candidate",
        "route_adapter_id": "raw_compat_create",
        "controls": _controls(),
        "projection_profile": "raw_future_complete",
        "comparison_mode": "expected_current_gaps",
        "fault": "none",
    },
    {
        "scenario_id": "shd-013-candidate-equivalent",
        "case_kind": "candidate_equivalent",
        "route_adapter_id": "raw_compat_status",
        "controls": _controls(),
        "projection_profile": "raw_future_complete",
        "comparison_mode": "semantic_expectation",
        "fault": "none",
    },
    {
        "scenario_id": "shd-014-candidate-divergent",
        "case_kind": "candidate_divergent",
        "route_adapter_id": "raw_compat_delete",
        "controls": _controls(),
        "projection_profile": "raw_future_divergent",
        "comparison_mode": "semantic_expectation",
        "fault": "none",
    },
    {
        "scenario_id": "shd-015-observer-failure",
        "case_kind": "observer_failure",
        "route_adapter_id": "raw_compat_update",
        "controls": _controls(),
        "projection_profile": "raw_current",
        "comparison_mode": "expected_current_gaps",
        "fault": "observer_failure",
    },
    {
        "scenario_id": "shd-016-timeout-drop",
        "case_kind": "timeout",
        "route_adapter_id": "raw_compat_status",
        "controls": _controls(),
        "projection_profile": "raw_current",
        "comparison_mode": "expected_current_gaps",
        "fault": "timeout",
    },
    {
        "scenario_id": "shd-017-overflow-drop",
        "case_kind": "overflow",
        "route_adapter_id": "raw_compat_delete",
        "controls": _controls(),
        "projection_profile": "raw_current",
        "comparison_mode": "expected_current_gaps",
        "fault": "overflow",
    },
    {
        "scenario_id": "shd-018-sink-failure-drop",
        "case_kind": "sink_failure",
        "route_adapter_id": "raw_compat_create",
        "controls": _controls(),
        "projection_profile": "raw_current",
        "comparison_mode": "expected_current_gaps",
        "fault": "sink_failure",
    },
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def _canonical_digest(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def load_evidence() -> dict[str, Any]:
    return _load(EVIDENCE_PATH)


def load_schema() -> dict[str, Any]:
    return _load(SCHEMA_PATH)


def build_sealed_primary(route_adapter_id: str) -> dict[str, Any]:
    family = ROUTE_FACTS[route_adapter_id][0]
    return {
        "http_status": 200,
        "response_body": {
            "synthetic_receipt": f"syn-primary-receipt-{family}-001",
            "authority": "authored_synthetic_non_product",
        },
        "response_headers": [
            ["content-type", "application/json"],
            ["x-emr4-synthetic", "sealed-primary-v1"],
        ],
        "transaction_disposition": "syn-transaction-committed",
        "mutation_audit_disposition": "syn-audit-appended",
    }


def build_projection(route_adapter_id: str, profile: str) -> dict[str, Any]:
    family, operation, target, conflict, target_shape = ROUTE_FACTS[route_adapter_id]
    complete = profile in {"raw_future_complete", "raw_future_divergent"}
    precondition = complete or profile == "raw_precondition_only"
    command_digest = f"syn-hmac-sha256-command-{family}-001"
    if profile == "raw_future_divergent":
        command_digest = f"syn-hmac-sha256-command-{family}-divergent"
    projection = {
        "schema_version": "emr4.shadow-route-projection.v1",
        "architecture_generation_digest": ARCHITECTURE_GENERATION_DIGEST,
        "route_adapter_id": route_adapter_id,
        "canonical_operation_id": operation,
        "practice_scope_digest": "syn-hmac-sha256-practice-001",
        "actor_digest": "syn-hmac-sha256-actor-reception-001",
        "actor_role": "reception",
        "session_digest": "syn-hmac-sha256-session-001",
        "purpose": "appointment_mutation_shadow_comparison",
        "target_shape": target_shape,
        "target_digest": target,
        "conflict_domain_digest": conflict,
        "command_digest": command_digest,
        "precondition_present": precondition,
        "precondition_version": "syn-precondition-v1" if precondition else None,
        "precondition_digest": (
            f"syn-hmac-sha256-precondition-{family}-001" if precondition else None
        ),
        "confirmation_present": complete,
        "confirmation_mode": (
            "destructive_explicit"
            if complete and family == "delete"
            else "explicit_staff_confirmation" if complete else None
        ),
        "confirmation_reference_digest": (
            f"syn-hmac-sha256-confirmation-{family}-001" if complete else None
        ),
        "idempotency_present": complete,
        "idempotency_key_digest": (
            f"syn-hmac-sha256-idempotency-{family}-001" if complete else None
        ),
        "canonicalization_version": "syn-canonical-json-v1" if complete else None,
        "correlation_digest": f"syn-hmac-sha256-correlation-{family}-001",
        "request_shape_digest": f"syn-hmac-sha256-request-shape-{family}-001",
    }
    if list(projection) != EXPECTED_PROJECTION_FIELDS:
        raise ValueError("projection_field_order_or_set_mismatch")
    return projection


def projection_to_raw_envelope(projection: dict[str, Any]) -> dict[str, Any]:
    envelope = {
        "request_context": {
            "practice_id": projection["practice_scope_digest"],
            "actor_id": projection["actor_digest"],
            "actor_role": projection["actor_role"],
            "session_id": projection["session_digest"],
            "purpose": projection["purpose"],
        },
        "mutation": {
            "target_appointment_id": projection["target_digest"],
            "conflict_domain_id": projection["conflict_domain_digest"],
            "command_digest": projection["command_digest"],
        },
        "correlation_id": projection["correlation_digest"],
    }
    if projection["precondition_present"]:
        envelope["conditional_controls"] = {
            "precondition_version": projection["precondition_version"],
            "precondition_digest": projection["precondition_digest"],
        }
    if projection["confirmation_present"]:
        envelope["confirmation_evidence"] = {
            "confirmation_mode": projection["confirmation_mode"],
            "confirmation_reference": projection["confirmation_reference_digest"],
        }
    if projection["idempotency_present"]:
        envelope["command_identity"] = {
            "idempotency_key_digest": projection["idempotency_key_digest"],
            "canonicalization_version": projection["canonicalization_version"],
        }
    return envelope


def expected_semantic_candidate(route_adapter_id: str) -> dict[str, Any]:
    family, operation, target, conflict, _ = ROUTE_FACTS[route_adapter_id]
    return {
        "schema_version": "emr4.conditional-appointment-command.v1",
        "canonical_operation_id": operation,
        "practice_id": "syn-hmac-sha256-practice-001",
        "actor_id": "syn-hmac-sha256-actor-reception-001",
        "actor_role": "reception",
        "session_id": "syn-hmac-sha256-session-001",
        "purpose": "appointment_mutation_shadow_comparison",
        "target_appointment_id": target,
        "conflict_domain_id": conflict,
        "command_digest": f"syn-hmac-sha256-command-{family}-001",
        "precondition_version": "syn-precondition-v1",
        "precondition_digest": f"syn-hmac-sha256-precondition-{family}-001",
        "confirmation_mode": (
            "destructive_explicit"
            if family == "delete"
            else "explicit_staff_confirmation"
        ),
        "confirmation_reference": f"syn-hmac-sha256-confirmation-{family}-001",
        "idempotency_key_digest": f"syn-hmac-sha256-idempotency-{family}-001",
        "canonicalization_version": "syn-canonical-json-v1",
        "correlation_id": f"syn-hmac-sha256-correlation-{family}-001",
    }


def build_record(
    projection: dict[str, Any],
    *,
    adapter_result: str,
    gap_codes: list[str],
    mismatch_field_codes: list[str],
    comparison_class: str,
    timing_category: str,
) -> dict[str, Any]:
    record = {
        "schema_version": "emr4.shadow-comparison-record.v1",
        "architecture_generation_digest": projection["architecture_generation_digest"],
        "configuration_digest": CONFIGURATION_DIGEST,
        "route_adapter_id": projection["route_adapter_id"],
        "canonical_operation_id": projection["canonical_operation_id"],
        "practice_scope_digest": projection["practice_scope_digest"],
        "correlation_digest": projection["correlation_digest"],
        "request_shape_digest": projection["request_shape_digest"],
        "adapter_result": adapter_result,
        "gap_codes": sorted(gap_codes),
        "mismatch_field_codes": sorted(mismatch_field_codes),
        "comparison_class": comparison_class,
        "timing_category": timing_category,
        "overflow_category": "not_overflowed",
        "recorded_at": RECORDED_AT,
    }
    if list(record) != EXPECTED_RECORD_FIELDS:
        raise ValueError("record_field_order_or_set_mismatch")
    return record


def evaluate_scenario(spec: dict[str, Any]) -> dict[str, Any]:
    route_adapter_id = spec["route_adapter_id"]
    primary = build_sealed_primary(route_adapter_id)
    before = _canonical_bytes(primary)
    before_digest = hashlib.sha256(before).hexdigest()
    controls = spec["controls"]
    admission = admission_decision(**controls)

    adapter_called = False
    adapter_result = "not_observed"
    gaps: list[str] = []
    mismatches: list[str] = []
    comparison_class: str | None = None
    record_candidates: list[dict[str, Any]] = []
    emitted_records: list[dict[str, Any]] = []

    if admission == "disabled_no_observation":
        disposition = "disabled_no_observation"
        comparison_class = "disabled_no_observation"
    elif spec["fault"] == "timeout":
        disposition = "timeout_dropped"
    elif spec["fault"] == "overflow":
        disposition = "overflow_dropped"
    else:
        projection = build_projection(route_adapter_id, spec["projection_profile"])
        if spec["fault"] == "observer_failure":
            adapter_result = "observer_failed"
            comparison_class = "observer_failed"
            record_candidates.append(
                build_record(
                    projection,
                    adapter_result=adapter_result,
                    gap_codes=[],
                    mismatch_field_codes=[],
                    comparison_class=comparison_class,
                    timing_category="observer_failed_before_comparison",
                )
            )
        else:
            adapter_called = True
            adapter_packet = load_adapter_contract()
            adapted = adapt_envelope(
                adapter_packet,
                route_adapter_id,
                projection_to_raw_envelope(projection),
            )
            adapter_result = adapted["adapter_result"]
            gaps = list(adapted["reason_codes"])
            if adapted["runtime_execution_authorized"] is not False:
                raise ValueError("adapter_runtime_authority_open")
            if adapted["command_outcome"] is not None or adapted["effect_performed"]:
                raise ValueError("adapter_command_or_effect_open")
            if adapter_result == "adapter_rejected":
                comparison_class = (
                    "expected_current_gap_match"
                    if gaps == EXPECTED_GAPS
                    else "unexpected_gap_set"
                )
            elif spec["comparison_mode"] == "expected_current_gaps":
                comparison_class = "unexpected_candidate_mapped"
            else:
                candidate = adapted["kernel_candidate"]
                if candidate is None:
                    raise ValueError("candidate_missing_after_mapping")
                actual = semantic_projection(adapter_packet, candidate)
                expected = expected_semantic_candidate(route_adapter_id)
                expected_digest = EXPECTED_SEMANTIC_DIGESTS[route_adapter_id]
                if _canonical_digest(expected) != expected_digest:
                    raise ValueError("independent_semantic_expectation_digest_mismatch")
                mismatches = sorted(
                    key for key in expected if actual.get(key) != expected[key]
                )
                if set(actual) != set(expected):
                    mismatches = sorted(
                        set(mismatches) | (set(actual) ^ set(expected))
                    )
                comparison_class = (
                    "candidate_projection_equivalent"
                    if _canonical_digest(actual) == expected_digest and not mismatches
                    else "candidate_projection_divergent"
                )
            record_candidates.append(
                build_record(
                    projection,
                    adapter_result=adapter_result,
                    gap_codes=gaps,
                    mismatch_field_codes=mismatches,
                    comparison_class=comparison_class,
                    timing_category="within_budget",
                )
            )

        if spec["fault"] == "sink_failure":
            disposition = "sink_failure_dropped"
        else:
            emitted_records = list(record_candidates)
            disposition = "record_emitted"

    after = _canonical_bytes(primary)
    after_digest = hashlib.sha256(after).hexdigest()
    return {
        "admission_decision": admission,
        "adapter_called": adapter_called,
        "adapter_result": adapter_result,
        "gap_codes": sorted(gaps),
        "mismatch_field_codes": sorted(mismatches),
        "comparison_class": comparison_class,
        "observation_disposition": disposition,
        "retry_count": 0,
        "command_outcome": None,
        "primary_before_sha256": before_digest,
        "primary_after_sha256": after_digest,
        "primary_bytes_equal": before == after,
        "record_candidate_count": len(record_candidates),
        "diagnostic_record_count": len(emitted_records),
        "diagnostic_records": emitted_records,
    }


def build_evidence() -> dict[str, Any]:
    scenarios = [
        {**copy.deepcopy(spec), "observed": evaluate_scenario(spec)}
        for spec in SCENARIO_SPECS
    ]
    observed = [row["observed"] for row in scenarios]
    records = [
        record
        for result in observed
        for record in result["diagnostic_records"]
    ]
    evidence = {
        "schema_version": "emr4.authored-synthetic-shadow-comparison-evidence.v1",
        "artifact_kind": "provider_free_unmounted_authored_synthetic_rehearsal",
        "status": "passed",
        "source_head": EXPECTED_SOURCE_HEAD,
        "source_bindings": [
            {"path": path, "sha256": digest}
            for path, digest in EXPECTED_SOURCE_BINDINGS.items()
        ],
        "architecture_binding": {
            "architecture_schema_version": "emr4.default-off-shadow-comparison-architecture.v1",
            "architecture_generation_digest": ARCHITECTURE_GENERATION_DIGEST,
            "configuration_digest": CONFIGURATION_DIGEST,
            "parent_posture": "current_raw_not_kernel_eligible",
            "observer_runtime_created": False,
        },
        "evidence_label": "provider_free_unmounted_authored_synthetic",
        "semantic_expectation_digests": copy.deepcopy(EXPECTED_SEMANTIC_DIGESTS),
        "scenario_results": scenarios,
        "summary": {
            "scenario_count": len(scenarios),
            "disabled_count": sum(
                row["admission_decision"] == "disabled_no_observation"
                for row in observed
            ),
            "admitted_count": sum(
                row["admission_decision"] == "shadow_observation_admitted"
                for row in observed
            ),
            "adapter_call_count": sum(row["adapter_called"] for row in observed),
            "primary_byte_equal_count": sum(
                row["primary_bytes_equal"] for row in observed
            ),
            "record_candidate_count": sum(
                row["record_candidate_count"] for row in observed
            ),
            "diagnostic_record_count": len(records),
            "maximum_records_per_scenario": max(
                row["diagnostic_record_count"] for row in observed
            ),
            "observer_failure_count": sum(
                row["comparison_class"] == "observer_failed" for row in observed
            ),
            "timeout_drop_count": sum(
                row["observation_disposition"] == "timeout_dropped"
                for row in observed
            ),
            "overflow_drop_count": sum(
                row["observation_disposition"] == "overflow_dropped"
                for row in observed
            ),
            "sink_failure_drop_count": sum(
                row["observation_disposition"] == "sink_failure_dropped"
                for row in observed
            ),
            "command_outcome_count": sum(
                row["command_outcome"] is not None for row in observed
            ),
        },
        "claim_boundary": {
            "application_route_imported_or_executed": False,
            "observer_runtime_created": False,
            "database_or_source_accessed": False,
            "event_or_watcher_consumed": False,
            "provider_or_network_used": False,
            "product_or_patient_data_used": False,
            "kernel_or_command_invoked": False,
            "command_or_write_performed": False,
            "deployment_or_release_performed": False,
            "protected_ref_moved": False,
        },
        "effect_boundary": {
            "runtime_hook_or_feature_flag": False,
            "thread_process_queue_or_sink": False,
            "persistence_retention_or_aggregation": False,
            "response_or_header_change": False,
            "transaction_or_audit_change": False,
            "retry_or_latency_feedback": False,
            "kernel_eligibility_or_command_outcome": False,
            "client_behavior_change": False,
        },
        "next_safe_descendant": "separately_reviewed_default_off_runtime_instrumentation_plan",
    }
    return evidence


def semantic_errors(
    packet: dict[str, Any], *, verify_source_files: bool = False
) -> list[str]:
    errors: list[str] = []
    if packet != build_evidence():
        errors.append("evidence_replay_mismatch")
    if packet.get("source_head") != EXPECTED_SOURCE_HEAD:
        errors.append("source_head_mismatch")
    bindings = {
        row["path"]: row["sha256"] for row in packet.get("source_bindings", [])
    }
    if bindings != EXPECTED_SOURCE_BINDINGS:
        errors.append("source_bindings_mismatch")
    if verify_source_files:
        for path, digest in EXPECTED_SOURCE_BINDINGS.items():
            source = ROOT / path
            if not source.is_file() or _file_hash(source) != digest:
                errors.append(f"source_file_hash_mismatch:{path}")
    architecture = load_architecture_contract()
    if architecture["projection"]["allowed_fields"] != EXPECTED_PROJECTION_FIELDS:
        errors.append("parent_projection_fields_changed")
    if architecture["diagnostic_record"]["allowed_fields"] != EXPECTED_RECORD_FIELDS:
        errors.append("parent_record_fields_changed")
    if architecture["observer"]["expected_current_gap_codes"] != EXPECTED_GAPS:
        errors.append("parent_gap_codes_changed")
    try:
        rows = packet["scenario_results"]
        if len(rows) != 18 or len({row["scenario_id"] for row in rows}) != 18:
            errors.append("scenario_population_mismatch")
        for row in rows:
            observed = row["observed"]
            if not observed["primary_bytes_equal"]:
                errors.append(f"primary_result_changed:{row['scenario_id']}")
            if observed["diagnostic_record_count"] > 1:
                errors.append(f"record_bound_exceeded:{row['scenario_id']}")
            for record in observed["diagnostic_records"]:
                if list(record) != EXPECTED_RECORD_FIELDS:
                    errors.append(f"record_fields_changed:{row['scenario_id']}")
                if "command_outcome" in record:
                    errors.append(f"command_outcome_in_record:{row['scenario_id']}")
        summary = packet["summary"]
        expected_summary = {
            "scenario_count": 18,
            "disabled_count": 6,
            "admitted_count": 12,
            "adapter_call_count": 9,
            "primary_byte_equal_count": 18,
            "record_candidate_count": 10,
            "diagnostic_record_count": 9,
            "maximum_records_per_scenario": 1,
            "observer_failure_count": 1,
            "timeout_drop_count": 1,
            "overflow_drop_count": 1,
            "sink_failure_drop_count": 1,
            "command_outcome_count": 0,
        }
        if summary != expected_summary:
            errors.append("summary_mismatch")
        if any(packet["claim_boundary"].values()):
            errors.append("claim_boundary_open")
        if any(packet["effect_boundary"].values()):
            errors.append("effect_boundary_open")
    except (KeyError, TypeError, ValueError) as error:
        errors.append(f"semantic_shape_error:{type(error).__name__}")
    return sorted(set(errors))


def validate_evidence(
    packet: dict[str, Any], *, verify_source_files: bool = False
) -> list[str]:
    schema = load_schema()
    Draft202012Validator.check_schema(schema)
    schema_errors = sorted(
        f"schema:{error.json_path}:{error.message}"
        for error in Draft202012Validator(schema).iter_errors(packet)
    )
    try:
        semantic = semantic_errors(packet, verify_source_files=verify_source_files)
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        semantic = [f"semantic_validation_failed:{type(error).__name__}"]
    return sorted(set(schema_errors + semantic))


def hostile_mutations(packet: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    changes: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("schema_version", lambda p: p.__setitem__("schema_version", "v0")),
        ("artifact_kind", lambda p: p.__setitem__("artifact_kind", "runtime")),
        ("status", lambda p: p.__setitem__("status", "partial")),
        ("source_head", lambda p: p.__setitem__("source_head", "0" * 40)),
        ("source_hash", lambda p: p["source_bindings"][0].__setitem__("sha256", "0" * 64)),
        ("source_removed", lambda p: p["source_bindings"].pop()),
        ("architecture_schema", lambda p: p["architecture_binding"].__setitem__("architecture_schema_version", "v0")),
        ("architecture_generation", lambda p: p["architecture_binding"].__setitem__("architecture_generation_digest", "syn-wrong")),
        ("configuration", lambda p: p["architecture_binding"].__setitem__("configuration_digest", "syn-wrong")),
        ("parent_posture", lambda p: p["architecture_binding"].__setitem__("parent_posture", "kernel_eligible")),
        ("runtime_created", lambda p: p["architecture_binding"].__setitem__("observer_runtime_created", True)),
        ("evidence_label", lambda p: p.__setitem__("evidence_label", "live")),
        ("semantic_digest", lambda p: p["semantic_expectation_digests"].__setitem__("raw_compat_create", "0" * 64)),
        ("scenario_removed", lambda p: p["scenario_results"].pop()),
        ("scenario_duplicate", lambda p: p["scenario_results"].__setitem__(17, copy.deepcopy(p["scenario_results"][16]))),
        ("scenario_id", lambda p: p["scenario_results"][0].__setitem__("scenario_id", "wrong")),
        ("case_kind", lambda p: p["scenario_results"][0].__setitem__("case_kind", "timeout")),
        ("route", lambda p: p["scenario_results"][6].__setitem__("route_adapter_id", "raw_compat_delete")),
        ("generation", lambda p: p["scenario_results"][4]["controls"].__setitem__("generation_status", "current")),
        ("global", lambda p: p["scenario_results"][0]["controls"].__setitem__("global_state", "enabled")),
        ("practice", lambda p: p["scenario_results"][1]["controls"].__setitem__("practice_state", "enabled")),
        ("route_allowed", lambda p: p["scenario_results"][2]["controls"].__setitem__("route_allowed", True)),
        ("external_disable", lambda p: p["scenario_results"][5]["controls"].__setitem__("externally_disabled", False)),
        ("projection_profile", lambda p: p["scenario_results"][10].__setitem__("projection_profile", "raw_future_complete")),
        ("comparison_mode", lambda p: p["scenario_results"][12].__setitem__("comparison_mode", "expected_current_gaps")),
        ("fault", lambda p: p["scenario_results"][15].__setitem__("fault", "none")),
        ("admission", lambda p: p["scenario_results"][6]["observed"].__setitem__("admission_decision", "disabled_no_observation")),
        ("adapter_called", lambda p: p["scenario_results"][0]["observed"].__setitem__("adapter_called", True)),
        ("adapter_result", lambda p: p["scenario_results"][6]["observed"].__setitem__("adapter_result", "candidate_mapped")),
        ("gap_codes", lambda p: p["scenario_results"][6]["observed"]["gap_codes"].pop()),
        ("mismatch_codes", lambda p: p["scenario_results"][13]["observed"]["mismatch_field_codes"].clear()),
        ("comparison", lambda p: p["scenario_results"][12]["observed"].__setitem__("comparison_class", "candidate_projection_divergent")),
        ("disposition", lambda p: p["scenario_results"][15]["observed"].__setitem__("observation_disposition", "record_emitted")),
        ("retry", lambda p: p["scenario_results"][6]["observed"].__setitem__("retry_count", 1)),
        ("command_outcome", lambda p: p["scenario_results"][6]["observed"].__setitem__("command_outcome", "committed")),
        ("primary_before", lambda p: p["scenario_results"][6]["observed"].__setitem__("primary_before_sha256", "0" * 64)),
        ("primary_after", lambda p: p["scenario_results"][6]["observed"].__setitem__("primary_after_sha256", "0" * 64)),
        ("primary_equal", lambda p: p["scenario_results"][6]["observed"].__setitem__("primary_bytes_equal", False)),
        ("record_candidate_count", lambda p: p["scenario_results"][17]["observed"].__setitem__("record_candidate_count", 2)),
        ("record_count", lambda p: p["scenario_results"][6]["observed"].__setitem__("diagnostic_record_count", 2)),
        ("record_removed", lambda p: p["scenario_results"][6]["observed"]["diagnostic_records"].clear()),
        ("record_extra_field", lambda p: p["scenario_results"][6]["observed"]["diagnostic_records"][0].__setitem__("command_outcome", "committed")),
        ("record_route", lambda p: p["scenario_results"][6]["observed"]["diagnostic_records"][0].__setitem__("route_adapter_id", "raw_compat_delete")),
        ("record_class", lambda p: p["scenario_results"][6]["observed"]["diagnostic_records"][0].__setitem__("comparison_class", "observer_failed")),
        ("summary_count", lambda p: p["summary"].__setitem__("scenario_count", 17)),
        ("claim_route", lambda p: p["claim_boundary"].__setitem__("application_route_imported_or_executed", True)),
        ("claim_provider", lambda p: p["claim_boundary"].__setitem__("provider_or_network_used", True)),
        ("claim_command", lambda p: p["claim_boundary"].__setitem__("command_or_write_performed", True)),
        ("effect_sink", lambda p: p["effect_boundary"].__setitem__("thread_process_queue_or_sink", True)),
        ("effect_response", lambda p: p["effect_boundary"].__setitem__("response_or_header_change", True)),
        ("next_descendant", lambda p: p.__setitem__("next_safe_descendant", "runtime_enabled")),
    ]
    mutants: list[tuple[str, dict[str, Any]]] = []
    for name, change in changes:
        candidate = copy.deepcopy(packet)
        change(candidate)
        mutants.append((name, candidate))
    return mutants


def build_report(packet: dict[str, Any] | None = None) -> dict[str, Any]:
    packet = load_evidence() if packet is None else packet
    errors = validate_evidence(packet, verify_source_files=True)
    mutants = hostile_mutations(packet)
    escaped = [name for name, mutant in mutants if not validate_evidence(mutant)]
    if escaped:
        errors.append("hostile_mutation_escaped:" + ",".join(escaped))
    return {
        "schema_version": "emr4.authored-synthetic-shadow-comparison-report.v1",
        "status": "passed" if not errors else "failed",
        "reasons": sorted(set(errors)),
        "source_head": packet.get("source_head"),
        "scenario_count": packet.get("summary", {}).get("scenario_count"),
        "disabled_count": packet.get("summary", {}).get("disabled_count"),
        "admitted_count": packet.get("summary", {}).get("admitted_count"),
        "primary_byte_equal_count": packet.get("summary", {}).get("primary_byte_equal_count"),
        "diagnostic_record_count": packet.get("summary", {}).get("diagnostic_record_count"),
        "maximum_records_per_scenario": packet.get("summary", {}).get("maximum_records_per_scenario"),
        "hostile_mutation_count": len(mutants),
        "hostile_mutation_escape_count": len(escaped),
        "application_route_imported_or_executed": False,
        "observer_runtime_created": False,
        "provider_call_count": 0,
        "command_or_write_performed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Exercise the inert authored-synthetic shadow comparison."
    )
    parser.add_argument(
        "--write-evidence",
        action="store_true",
        help="Write the deterministic authored-synthetic evidence fixture.",
    )
    args = parser.parse_args(argv)
    if args.write_evidence:
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        EVIDENCE_PATH.write_text(
            json.dumps(build_evidence(), indent=2, sort_keys=False) + "\n",
            encoding="utf-8",
        )
        return 0
    report = build_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
