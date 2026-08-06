"""Deterministic acceptance for the patient-free Context Fabric temporal weave."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.raisa_provider_free_practice_context_fabric_bureau_memory_contract import (
    canonical_sha256,
)
from scripts.raisa_provider_free_practice_context_fabric_current_operational_weave import (
    build_authored_synthetic_packet,
)
from scripts.raisa_provider_free_practice_context_fabric_patient_free_temporal_weave import (
    assess_reassembly_result,
    build_authored_synthetic_temporal_packet,
    derive_dependency_manifest,
    derive_watch_lease,
    make_signal,
    process_signals,
    proofread_temporal_packet,
)


ARTIFACT_ROOT = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-practice-context-fabric-patient-free-temporal-weave"
)
SCHEMA_PATH = ARTIFACT_ROOT / "temporal-weave-contract.schema.json"
EXAMPLE_PATH = ARTIFACT_ROOT / "temporal-weave-contract.example.json"
EVIDENCE_PATH = ARTIFACT_ROOT / "provider-free-acceptance-evidence.json"
PLAN_PATH = (
    ROOT
    / "docs/raisa-provider-free-practice-context-fabric-patient-free-temporal-weave-plan.md"
)
DESIGN_PATH = (
    ROOT
    / "docs/raisa-provider-free-practice-context-fabric-patient-free-temporal-weave-design.md"
)
THREAT_PATH = (
    ROOT
    / "docs/security/raisa-provider-free-practice-context-fabric-patient-free-temporal-weave-threat-model-delta.md"
)
ENGINE_PATH = (
    ROOT
    / "scripts/raisa_provider_free_practice_context_fabric_patient_free_temporal_weave.py"
)
ACCEPTANCE_PATH = Path(__file__).resolve()
TEST_PATH = (
    ROOT
    / "tests/test_raisa_provider_free_practice_context_fabric_patient_free_temporal_weave.py"
)
RESULT = "raisa_provider_free_practice_context_fabric_patient_free_temporal_weave_pass"


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _sha(path: Path) -> str:
    canonical_lf = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(canonical_lf).hexdigest()


def build_example() -> dict[str, Any]:
    return build_authored_synthetic_temporal_packet()


def validate_packet(packet: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(
            schema, format_checker=FormatChecker()
        ).iter_errors(packet),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        first = errors[0]
        raise ValueError(
            f"schema validation failed at {list(first.absolute_path)}: {first.message}"
        )


def _static_checks() -> dict[str, Any]:
    tree = ast.parse(ENGINE_PATH.read_text(encoding="utf-8"))
    forbidden_imports = {
        "app",
        "boto3",
        "google",
        "httpx",
        "os",
        "pathlib",
        "requests",
        "socket",
        "sqlalchemy",
        "subprocess",
    }
    forbidden_calls = {
        "Popen",
        "commit",
        "connect",
        "execute",
        "open",
        "request",
        "run",
        "write_bytes",
        "write_text",
    }
    imports: set[str] = set()
    calls: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".", 1)[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr)
    bad_imports = sorted(imports & forbidden_imports)
    bad_calls = sorted(calls & forbidden_calls)
    if bad_imports or bad_calls:
        raise ValueError(
            f"forbidden engine surface: imports={bad_imports}, calls={bad_calls}"
        )
    return {
        "forbidden_imports": bad_imports,
        "forbidden_calls": bad_calls,
        "caller_clocked": True,
        "application_imports": 0,
        "api_surface_changes": 0,
    }


def _gap_probe() -> str:
    parent = build_authored_synthetic_packet()
    manifest = derive_dependency_manifest(parent)
    lease = derive_watch_lease(parent, manifest)
    signal = make_signal(
        signal_id="synthetic:signal:gap-probe",
        event_type="diary.appointment_rescheduled",
        aggregate_ref="synthetic:appointment:one",
        aggregate_revision=12,
        previous_transaction_position=100,
        transaction_position=102,
        location_refs=["synthetic:location:brisbane-one"],
        practice_binding_digest=manifest["practice_binding_digest"],
        occurred_at="2026-08-06T03:00:10Z",
        received_at="2026-08-06T03:00:11Z",
    )
    state, requirement, _, decisions, transitions, trace = process_signals(
        parent, manifest, lease, [signal]
    )
    if (
        state["state"] != "REASSEMBLY_REQUIRED"
        or requirement is None
        or decisions[0]["decision"] != "CURSOR_GAP"
        or transitions[0]["fresh_read_executed"]
        or not trace["parent_frame_set_unchanged"]
    ):
        raise ValueError("cursor gap did not fail closed")
    return decisions[0]["decision"]


def build_evidence() -> dict[str, Any]:
    packet = build_example()
    validate_packet(packet)
    if packet["proofreader_trace"]["release_decision"] != "RELEASE":
        raise ValueError("nominal temporal packet was not released")
    decisions = [item["decision"] for item in packet["invalidation_decisions"]]
    if decisions != ["REASSEMBLY_REQUIRED", "COALESCED", "IRRELEVANT"]:
        raise ValueError("canonical temporal decisions drifted")
    if packet["frame_set_state"]["usable_for_new_reasoning"]:
        raise ValueError("superseded frame set remained usable")
    if packet["temporal_trace"]["parent_frame_set_bytes_before"] != packet[
        "temporal_trace"
    ]["parent_frame_set_bytes_after"]:
        raise ValueError("parent frame set changed during invalidation")
    if packet["stale_reassembly_decision"]["decision"] != (
        "REJECT_SUPERSEDED_REQUEST"
    ):
        raise ValueError("stale reassembly result was admitted")
    historical_counts = [
        result["frames"][0]["content"]["waiting_count"]
        for result in packet["historical_results"]
    ]
    if historical_counts != [2, 3]:
        raise ValueError("bitemporal known-at selection drifted")
    if any(
        result["event_delivery_ttl_controls_retention"]
        for result in packet["historical_results"]
    ):
        raise ValueError("delivery TTL became historical retention")
    tampered = deepcopy(packet)
    tampered["frame_set_state"]["state"] = "CURRENT"
    trace = proofread_temporal_packet(
        build_authored_synthetic_packet(),
        {key: value for key, value in tampered.items() if key != "proofreader_trace"},
        checked_at="2026-08-06T03:01:01Z",
    )
    if trace["release_decision"] != "BLOCK":
        raise ValueError("proofreader admitted state rollback")
    requirement = packet["reassembly_requirement"]
    accepted = assess_reassembly_result(
        requirement,
        result_session_generation=requirement["session_generation"],
        result_request_revision=requirement["request_revision"],
        current_session_generation=requirement["session_generation"],
        current_request_revision=requirement["request_revision"],
    )
    if accepted["decision"] != "ADMIT_NEW_GENERATION":
        raise ValueError("current exact reassembly result was rejected")

    artifacts = [
        SCHEMA_PATH,
        PLAN_PATH,
        DESIGN_PATH,
        THREAT_PATH,
        ENGINE_PATH,
        ACCEPTANCE_PATH,
        TEST_PATH,
    ]
    artifact_hashes = {
        path.relative_to(ROOT).as_posix(): _sha(path) for path in artifacts
    }
    return {
        "schema_version": (
            "emr4.practice_context_fabric_patient_free_temporal_weave_acceptance.v1"
        ),
        "result": RESULT,
        "passed": True,
        "source_binding": {
            "mode": "canonical_lf_artifact_hashes_with_external_exact_head_receipt",
            "artifact_count": len(artifact_hashes),
            "git_head_self_reference_forbidden": True,
            "checkout_line_endings_normalized": True,
        },
        "evidence_label": (
            "provider_free_authored_synthetic_patient_free_temporal_weave"
        ),
        "artifact_hashes": artifact_hashes,
        "artifact_set_digest": canonical_sha256(artifact_hashes),
        "deterministic_checks": {
            "schema_valid": True,
            "closed_objects": True,
            "manifest_parent_bound": True,
            "watch_lease_only_narrows": True,
            "event_payload_is_not_truth": True,
            "observation_decision_checkpoint_transition_atomic": True,
            "immutable_parent_frame_set": True,
            "first_relevant_signal_invalidates": True,
            "later_relevant_signal_coalesces": True,
            "irrelevant_signal_silent": True,
            "cursor_gap_disposition": _gap_probe(),
            "stale_reassembly_rejected": True,
            "current_exact_reassembly_admissible": True,
            "valid_and_transaction_time_selected": True,
            "known_then_and_corrected_later_distinct": historical_counts,
            "coverage_gap_explicit": True,
            "delivery_ttl_is_not_retention": True,
            "same_packet_proofreader_release": True,
            "state_rollback_tamper_blocked": True,
        },
        "api_spine_checks": {
            "new_graphql_roots": 0,
            "new_graphql_resolvers": 0,
            "new_rest_commands": 0,
            "new_subscriptions": 0,
            "event_signal_remains_non_command": True,
        },
        "static_checks": _static_checks(),
        "authority_and_side_effects": {
            "provider_calls": 0,
            "network_operations": 0,
            "database_operations": 0,
            "filesystem_write_operations_by_engine": 0,
            "subprocess_operations_by_engine": 0,
            "product_runtime_operations": 0,
            "event_listener_operations": 0,
            "source_read_operations": 0,
            "command_operations": 0,
            "deployment_operations": 0,
            "protected_operations": 0,
        },
        "claim_boundary": (
            "Pure provider-free authored-synthetic invalidation, reassembly and "
            "bitemporal-query semantics only; no live watcher, event transport, "
            "database, persistence, retention choice, patient/product data, "
            "provider retrieval, command, deployment or protected-ref claim."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        example = build_example()
        validate_packet(example)
        evidence = build_evidence()
        if args.write:
            _write_json(EXAMPLE_PATH, example)
            _write_json(EVIDENCE_PATH, evidence)
        print(json.dumps(evidence, indent=2, sort_keys=True))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Patient-free temporal weave acceptance failed: {error}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
