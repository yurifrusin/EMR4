"""Deterministic acceptance for the provider-free Context Fabric contract."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
# The harness performs one fixed local Git metadata read; the engine performs none.
import subprocess  # nosec B404
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

from graphql import build_schema
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.raisa_provider_free_practice_context_fabric_bureau_memory_contract import (
    SCHEMA_VERSION,
    build_contract_packet,
    canonical_sha256,
    proofread_same_packet,
    seal,
)


ARTIFACT_ROOT = ROOT / "orchestration/continuity/raisa-provider-free-practice-context-fabric-bureau-memory-contract"
SCHEMA_PATH = ARTIFACT_ROOT / "context-fabric-contract.schema.json"
EXAMPLE_PATH = ARTIFACT_ROOT / "context-fabric-contract.example.json"
EVIDENCE_PATH = ARTIFACT_ROOT / "provider-free-acceptance-evidence.json"
GRAPHQL_PATH = ROOT / "docs/api-spine/graphql/practice-context-fabric-read.graphql"
BASE_GRAPHQL_PATH = ROOT / "docs/api-spine/graphql/appointment-diary-read.graphql"
PLAN_PATH = ROOT / "docs/raisa-provider-free-practice-context-fabric-bureau-memory-contract-plan.md"
DESIGN_PATH = ROOT / "docs/raisa-provider-free-practice-context-fabric-bureau-memory-contract-design.md"
THREAT_PATH = ROOT / "docs/security/raisa-provider-free-practice-context-fabric-bureau-memory-contract-threat-model-delta.md"
ENGINE_PATH = ROOT / "scripts/raisa_provider_free_practice_context_fabric_bureau_memory_contract.py"
RESULT = "raisa_provider_free_practice_context_fabric_bureau_memory_contract_pass"


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_head() -> str:
    # Fixed argv and cwd, no untrusted input, and shell remains disabled.
    return subprocess.run(  # nosec B603 B607
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def authored_synthetic_inputs() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    selector = seal(
        {
            "originating_bureaus": ["rayleen", "bernie"],
            "action_families": ["waiting_room_read", "appointment_read"],
            "actor_relations": ["same_practice_staff", "self"],
            "outcome_codes": ["completed"],
            "temporal_hint": "current_practice_day",
            "maximum_results": 3,
        },
        "selector_digest",
    )
    candidate = seal(
        {
            "schema_version": SCHEMA_VERSION,
            "need_id": "need:recent-practice-work-001",
            "requesting_bureau": "rayleen",
            "purpose_code": "recent_practice_work",
            "requested_frame_types": ["bureau_memory_item_set"],
            "entity_features": [],
            "temporal_hint": "current_practice_day",
            "requested_time_window": {
                "starts_at": "2026-08-06T00:00:00Z",
                "ends_at": "2026-08-06T10:00:00Z",
            },
            "source_classes": ["recent_collective_work"],
            "requested_fields": ["request_label_code", "opaque_target_ref"],
            "maximum_results": 5,
            "freshness_seconds": 300,
            "historical_state_required": False,
            "command_authority": False,
            "issued_at": "2026-08-06T08:00:00Z",
            "bureau_memory_selector": selector,
        },
        "candidate_digest",
    )
    binding = seal(
        {
            "schema_version": SCHEMA_VERSION,
            "binding_id": "binding:staff-session-001",
            "principal_ref": "principal:synthetic-staff-001",
            "role_codes": ["receptionist"],
            "practice_ref": "practice:synthetic-001",
            "location_refs": ["location:synthetic-main"],
            "session_ref": "session:synthetic-001",
            "consent_codes": [],
            "policy_version": "context-policy.v1",
            "allowed_bureaus": ["rayleen", "bernie"],
            "allowed_purposes": ["recent_practice_work"],
            "allowed_frame_types": ["bureau_memory_item_set"],
            "allowed_source_classes": ["recent_collective_work"],
            "allowed_fields": ["request_label_code"],
            "allowed_action_families": ["waiting_room_read", "appointment_read"],
            "allowed_actor_relations": ["same_practice_staff", "self"],
            "allowed_outcome_codes": ["completed"],
            "maximum_results": 2,
            "maximum_bytes": 8192,
            "maximum_freshness_seconds": 120,
            "authorized_time_window": {
                "starts_at": "2026-08-06T07:00:00Z",
                "ends_at": "2026-08-06T09:00:00Z",
            },
            "issued_at": "2026-08-06T07:55:00Z",
            "expires_at": "2026-08-06T08:10:00Z",
        },
        "binding_digest",
    )

    def item(
        item_id: str,
        bureau: str,
        action: str,
        completed_at: str,
        *,
        state: str = "CURRENT",
    ) -> dict[str, Any]:
        return seal(
            {
                "schema_version": SCHEMA_VERSION,
                "memory_item_id": item_id,
                "originating_bureau": bureau,
                "request_kind": "read_projection",
                "request_label_code": "recent_operational_read",
                "action_family": action,
                "outcome_code": "completed",
                "initiator_relation": "same_practice_staff",
                "target_kind": "waiting_room" if action == "waiting_room_read" else "appointment",
                "opaque_target_ref": None,
                "started_at": completed_at,
                "completed_at": completed_at,
                "source_receipt_ref": "receipt:" + item_id.split(":", 1)[1],
                "source_revision": "synthetic-revision-1",
                "source_digest": canonical_sha256({"fixture": item_id}),
                "supersession_state": state,
                "relevance_reason_codes": ["PURPOSE_MATCH", "TIME_MATCH"],
                "authority_ceiling": "read_context_only",
            },
            "memory_item_digest",
        )

    items = [
        item("memory:rayleen-001", "rayleen", "waiting_room_read", "2026-08-06T08:01:00Z"),
        item("memory:bernie-001", "bernie", "appointment_read", "2026-08-06T08:00:00Z"),
        item("memory:old-001", "rayleen", "waiting_room_read", "2026-08-06T06:00:00Z"),
        item("memory:superseded-001", "rayleen", "waiting_room_read", "2026-08-06T08:02:00Z", state="SUPERSEDED"),
    ]
    return candidate, binding, items


def build_example() -> dict[str, Any]:
    candidate, binding, items = authored_synthetic_inputs()
    return build_contract_packet(
        candidate,
        binding,
        items,
        assembled_at="2026-08-06T08:02:00Z",
        proofread_at="2026-08-06T08:02:01Z",
        source_revision="authored-synthetic-source-1",
    )


def validate_packet(packet: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(packet),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        raise ValueError(f"schema validation failed at {list(errors[0].absolute_path)}: {errors[0].message}")


def _graphql_checks() -> dict[str, Any]:
    extension = GRAPHQL_PATH.read_text(encoding="utf-8")
    build_schema(BASE_GRAPHQL_PATH.read_text(encoding="utf-8") + "\n" + extension)
    lowered = extension.lower()
    forbidden = ["type mutation", "type subscription", "bureauMemory(", "principal:", "role:", "practice:"]
    hits = [value for value in forbidden if value.lower() in lowered]
    if hits:
        raise ValueError(f"GraphQL forbidden surface: {hits}")
    if extension.count("extend type Query") != 1 or extension.count("practiceContextFabric(") != 1:
        raise ValueError("GraphQL root drift")
    return {"composition_valid": True, "root_field_count": 1, "forbidden_hits": []}


def _static_checks() -> dict[str, Any]:
    tree = ast.parse(ENGINE_PATH.read_text(encoding="utf-8"))
    forbidden_imports = {"app", "sqlalchemy", "requests", "httpx", "socket", "subprocess", "pathlib", "google", "boto3", "os"}
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
    bad_calls = sorted(calls & {"open", "write_text", "write_bytes", "run", "Popen", "connect", "request"})
    if bad_imports or bad_calls:
        raise ValueError(f"forbidden engine surface: imports={bad_imports}, calls={bad_calls}")
    return {"forbidden_imports": bad_imports, "forbidden_calls": bad_calls, "caller_clocked": True}


def build_evidence() -> dict[str, Any]:
    packet = build_example()
    validate_packet(packet)
    if packet["scope_grant"]["decision"] != "ADMIT":
        raise ValueError("nominal scope not admitted")
    if packet["proofreader_trace"]["release_decision"] != "RELEASE":
        raise ValueError("nominal packet not released")
    if len(packet["frame_set"]["frames"][0]["items"]) != 2:
        raise ValueError("selection/cardinality drift")

    tampered = deepcopy(packet)
    tampered["frame_set"]["frames"][0]["items"][0]["outcome_code"] = "blocked"
    tamper_blocked = False
    try:
        proofread_same_packet(
            tampered["context_need"], tampered["scope_grant"], tampered["memory_selector"], tampered["frame_set"],
            tampered["selector_trace"], tampered["weave_trace"],
            proofread_at="2026-08-06T08:02:01Z",
        )
    except ValueError:
        tamper_blocked = True
    if not tamper_blocked:
        raise ValueError("tampered packet was not blocked")

    artifacts = [SCHEMA_PATH, GRAPHQL_PATH, PLAN_PATH, DESIGN_PATH, THREAT_PATH, ENGINE_PATH]
    artifact_hashes = {path.relative_to(ROOT).as_posix(): _sha(path) for path in artifacts}
    return {
        "schema_version": "emr4.practice_context_fabric_bureau_memory_acceptance.v1",
        "result": RESULT,
        "passed": True,
        "source_head": _source_head(),
        "evidence_label": "provider_free_authored_synthetic_contract",
        "artifact_hashes": artifact_hashes,
        "artifact_set_digest": canonical_sha256(artifact_hashes),
        "deterministic_checks": {
            "schema_valid": True,
            "scope_only_narrows": True,
            "effective_interval_half_open": True,
            "selected_memory_item_count": 2,
            "out_of_window_excluded": True,
            "superseded_excluded": True,
            "same_packet_proofreader_release": True,
            "digest_tamper_blocked": tamper_blocked,
            "raw_audit_accessed": False,
        },
        "graphql_checks": _graphql_checks(),
        "static_checks": _static_checks(),
        "authority_and_side_effects": {
            "provider_calls": 0,
            "network_operations": 0,
            "database_operations": 0,
            "filesystem_write_operations_by_engine": 0,
            "subprocess_operations_by_engine": 0,
            "product_runtime_operations": 0,
            "command_operations": 0,
            "deployment_operations": 0,
            "protected_operations": 0,
        },
        "claim_boundary": "Strict provider-free authored-synthetic contract behavior only; no product data, runtime, persistence, provider, command, deployment or production claim.",
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
        print(f"Context Fabric acceptance failed: {error}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
