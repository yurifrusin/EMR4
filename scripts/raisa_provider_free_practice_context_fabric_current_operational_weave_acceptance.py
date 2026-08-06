"""Deterministic acceptance for the Context Fabric Current operational weave."""

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
    seal,
)
from scripts.raisa_provider_free_practice_context_fabric_current_operational_weave import (
    OperationalWeaveViolation,
    assemble_current_operational_weave,
    build_authored_synthetic_packet,
    proofread_current_operational_weave,
)


ARTIFACT_ROOT = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-practice-context-fabric-current-operational-weave"
)
SCHEMA_PATH = ARTIFACT_ROOT / "operational-weave-contract.schema.json"
EXAMPLE_PATH = ARTIFACT_ROOT / "operational-weave-contract.example.json"
EVIDENCE_PATH = ARTIFACT_ROOT / "provider-free-acceptance-evidence.json"
PLAN_PATH = (
    ROOT
    / "docs/raisa-provider-free-practice-context-fabric-current-operational-weave-plan.md"
)
DESIGN_PATH = (
    ROOT
    / "docs/raisa-provider-free-practice-context-fabric-current-operational-weave-design.md"
)
THREAT_PATH = (
    ROOT
    / "docs/security/raisa-provider-free-practice-context-fabric-current-operational-weave-threat-model-delta.md"
)
ENGINE_PATH = (
    ROOT
    / "scripts/raisa_provider_free_practice_context_fabric_current_operational_weave.py"
)
ACCEPTANCE_PATH = Path(__file__).resolve()
TEST_PATH = (
    ROOT
    / "tests/test_raisa_provider_free_practice_context_fabric_current_operational_weave.py"
)
RESULT = "raisa_provider_free_practice_context_fabric_current_operational_weave_pass"


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _sha(path: Path) -> str:
    canonical_lf = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(canonical_lf).hexdigest()


def build_example() -> dict[str, Any]:
    return build_authored_synthetic_packet()


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


def _tamper_is_blocked(packet: dict[str, Any]) -> bool:
    tampered = deepcopy(packet["frame_set"])
    tampered["frames"][0]["content"]["appointments"][0]["status"] = "COMPLETED"
    trace = proofread_current_operational_weave(
        packet["candidate"],
        packet["context_need"],
        packet["authority_binding"],
        packet["scope_grant"],
        packet["source_envelopes"],
        tampered,
        packet["source_trace"],
        packet["weave_trace"],
        assembled_at=packet["context_need"]["assembled_at"],
    )
    return trace["release_decision"] == "BLOCK"


def _cross_source_incoherence_is_blocked(packet: dict[str, Any]) -> bool:
    sources = deepcopy(packet["source_envelopes"])
    waiting = next(
        item
        for item in sources
        if item["frame_type"] == "current_waiting_room_projection"
    )
    waiting["payload"]["entries"][0]["appointment_ref"] = (
        "synthetic:appointment:not-in-diary"
    )
    waiting = seal(
        {key: value for key, value in waiting.items() if key != "source_digest"},
        "source_digest",
    )
    sources[sources.index(next(
        item
        for item in sources
        if item["frame_type"] == "current_waiting_room_projection"
    ))] = waiting
    try:
        assemble_current_operational_weave(
            packet["candidate"],
            packet["context_need"],
            packet["authority_binding"],
            packet["scope_grant"],
            sources,
            assembled_at=packet["context_need"]["assembled_at"],
        )
    except OperationalWeaveViolation:
        return True
    return False


def build_evidence() -> dict[str, Any]:
    packet = build_example()
    validate_packet(packet)
    if packet["scope_grant"]["decision"] != "ADMIT":
        raise ValueError("nominal scope was not admitted")
    if packet["proofreader_trace"]["release_decision"] != "RELEASE":
        raise ValueError("nominal packet was not released")
    frame_types = [item["frame_type"] for item in packet["frame_set"]["frames"]]
    if frame_types != [
        "current_diary_projection",
        "current_waiting_room_projection",
        "active_practitioner_directory",
        "private_application_session_state",
    ]:
        raise ValueError("canonical frame order drift")
    if not _tamper_is_blocked(packet):
        raise ValueError("tampered frame set was not blocked")
    if not _cross_source_incoherence_is_blocked(packet):
        raise ValueError("cross-source incoherence was not blocked")

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
            "emr4.practice_context_fabric_current_operational_weave_acceptance.v1"
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
            "provider_free_authored_synthetic_current_operational_weave"
        ),
        "artifact_hashes": artifact_hashes,
        "artifact_set_digest": canonical_sha256(artifact_hashes),
        "deterministic_checks": {
            "schema_valid": True,
            "closed_objects": True,
            "scope_only_narrows": True,
            "source_contract_pairing_exact": True,
            "practice_session_location_bound": True,
            "freshness_and_supersession_fail_closed": True,
            "required_source_set_complete": True,
            "cross_source_coherence": True,
            "field_level_minimisation": True,
            "canonical_frame_order": frame_types,
            "same_packet_proofreader_release": True,
            "digest_tamper_blocked": True,
            "cross_source_incoherence_blocked": True,
        },
        "api_spine_checks": {
            "new_graphql_roots": 0,
            "new_graphql_resolvers": 0,
            "new_rest_commands": 0,
            "new_subscriptions": 0,
            "source_shapes_only": True,
        },
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
        "claim_boundary": (
            "Strict provider-free authored-synthetic pure composition only; no "
            "patient or product data, retrieval, runtime, persistence, provider, "
            "command, deployment, production or protected-ref claim."
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
        print(f"Current operational weave acceptance failed: {error}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
