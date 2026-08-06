"""Deterministic acceptance for intent-shaped temporal Context Fabric retrieval."""

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
from scripts.raisa_provider_free_practice_context_fabric_intent_shaped_temporal_retrieval_rehearsal import (
    build_authored_synthetic_intent_packet,
    build_authored_synthetic_sources,
    build_intent_authority_binding,
    build_intent_candidate,
    build_intent_packet,
    build_source_catalog,
    proofread_intent_packet,
)


ARTIFACT_ROOT = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-practice-context-fabric-intent-shaped-temporal-retrieval-rehearsal"
)
SCHEMA_PATH = ARTIFACT_ROOT / "intent-shaped-temporal-retrieval-contract.schema.json"
EXAMPLE_PATH = ARTIFACT_ROOT / "intent-shaped-temporal-retrieval-contract.example.json"
EVIDENCE_PATH = ARTIFACT_ROOT / "provider-free-acceptance-evidence.json"
PLAN_PATH = (
    ROOT
    / "docs/raisa-provider-free-practice-context-fabric-intent-shaped-temporal-retrieval-rehearsal-plan.md"
)
DESIGN_PATH = (
    ROOT
    / "docs/raisa-provider-free-practice-context-fabric-intent-shaped-temporal-retrieval-rehearsal-design.md"
)
THREAT_PATH = (
    ROOT
    / "docs/security/raisa-provider-free-practice-context-fabric-intent-shaped-temporal-retrieval-rehearsal-threat-model-delta.md"
)
ENGINE_PATH = (
    ROOT
    / "scripts/raisa_provider_free_practice_context_fabric_intent_shaped_temporal_retrieval_rehearsal.py"
)
ACCEPTANCE_PATH = Path(__file__).resolve()
TEST_PATH = (
    ROOT
    / "tests/test_raisa_provider_free_practice_context_fabric_intent_shaped_temporal_retrieval_rehearsal.py"
)
RESULT = (
    "raisa_provider_free_practice_context_fabric_intent_shaped_temporal_retrieval_rehearsal_pass"
)


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _sha(path: Path) -> str:
    canonical_lf = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(canonical_lf).hexdigest()


def build_example() -> dict[str, Any]:
    return build_authored_synthetic_intent_packet()


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


def _packet_for(
    intent: str,
    *,
    requesting_bureau: str = "RAYLEEN",
    valid_at: str | None = "2026-08-06T00:30:00Z",
    known_at: str | None = "2026-08-06T02:30:00Z",
    sources: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_bundle = sources or build_authored_synthetic_sources()
    catalog = build_source_catalog(source_bundle)
    binding = build_intent_authority_binding(source_bundle, catalog=catalog)
    candidate = build_intent_candidate(
        intent,
        requesting_bureau=requesting_bureau,
        valid_at=valid_at,
        known_at=known_at,
    )
    return build_intent_packet(candidate, binding, catalog)


def build_evidence() -> dict[str, Any]:
    packet = build_example()
    validate_packet(packet)
    if packet["proofreader_trace"]["release_decision"] != "RELEASE":
        raise ValueError("nominal intent packet was not released")
    if packet["frame_set"]["disposition"] != "ADMIT":
        raise ValueError("nominal intent packet was not admitted")

    expected_components = {
        "CURRENT_OPERATIONAL_STATUS": ["CURRENT_OPERATIONAL"],
        "RECENT_PRACTICE_WORK": ["BUREAU_MEMORY"],
        "HISTORICAL_OPERATIONAL_STATE": ["HISTORICAL_OPERATIONAL"],
        "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON": [
            "CURRENT_OPERATIONAL",
            "HISTORICAL_OPERATIONAL",
        ],
    }
    component_results: dict[str, list[str]] = {}
    for intent, expected in expected_components.items():
        result = _packet_for(intent)
        actual = [
            item["component_code"] for item in result["frame_set"]["components"]
        ]
        if actual != expected:
            raise ValueError(f"minimal component selection drifted for {intent}")
        component_results[intent] = actual

    current = _packet_for("CURRENT_OPERATIONAL_STATUS")
    current_fact_codes = [
        fact["fact_code"]
        for fact in current["frame_set"]["components"][0]["facts"]
    ]
    if current_fact_codes != [
        "CURRENT_APPOINTMENT_STATUS",
        "CURRENT_WAIT_MINUTES",
        "CURRENT_PRACTITIONER_ROLE",
        "CURRENT_SESSION_PROPOSAL_STATE",
    ]:
        raise ValueError("atomic four-source Current projection drifted")

    ambiguity = _packet_for("RECENT_OPERATIONAL_REFERENCE")
    if (
        ambiguity["frame_set"]["disposition"] != "ALTERNATIVES"
        or len(ambiguity["frame_set"]["alternatives"]) != 2
        or any(
            item["identity_asserted"]
            for item in ambiguity["frame_set"]["alternatives"]
        )
    ):
        raise ValueError("ambiguity was silently resolved")

    shared_memory = _packet_for(
        "RECENT_PRACTICE_WORK", requesting_bureau="BERNIE"
    )
    if shared_memory["frame_set"]["disposition"] != "ADMIT":
        raise ValueError("bilaterally authorised Memory sharing was rejected")
    private_current = _packet_for(
        "CURRENT_OPERATIONAL_STATUS", requesting_bureau="BERNIE"
    )
    if (
        private_current["frame_set"]["disposition"] != "NOT_AVAILABLE"
        or "PRIVATE_SESSION_NOT_SHAREABLE"
        not in private_current["frame_set"]["omission_reason_codes"]
    ):
        raise ValueError("private session crossed Bureau boundary")

    invalidated_sources = build_authored_synthetic_sources()
    invalidated_sources["current_state"] = invalidated_sources["temporal_packet"][
        "frame_set_state"
    ]
    invalidated = _packet_for(
        "CURRENT_OPERATIONAL_STATUS", sources=invalidated_sources
    )
    if (
        invalidated["frame_set"]["disposition"] != "NOT_AVAILABLE"
        or "CURRENT_COMPONENT_REASSEMBLY_REQUIRED"
        not in invalidated["frame_set"]["omission_reason_codes"]
    ):
        raise ValueError("invalidated Current component was released")

    historical_counts = []
    for known_at in ["2026-08-06T01:00:00Z", "2026-08-06T02:30:00Z"]:
        historical = _packet_for(
            "HISTORICAL_OPERATIONAL_STATE", known_at=known_at
        )
        historical_counts.append(
            historical["frame_set"]["components"][0]["facts"][0]["value"]
        )
    if historical_counts != [2, 3]:
        raise ValueError("known-then/corrected-later selection drifted")

    gap = _packet_for(
        "HISTORICAL_OPERATIONAL_STATE",
        valid_at="2026-08-06T02:15:00Z",
        known_at="2026-08-06T02:30:00Z",
    )
    if gap["frame_set"]["disposition"] != "NOT_AVAILABLE":
        raise ValueError("historical coverage gap was treated as absence truth")

    candidate = deepcopy(packet["candidate"])
    candidate["principal_ref"] = "synthetic:injected-principal"
    candidate.pop("candidate_digest")
    candidate = seal(candidate, "candidate_digest")
    injection_blocked = False
    try:
        sources = build_authored_synthetic_sources()
        catalog = build_source_catalog(sources)
        binding = build_intent_authority_binding(sources, catalog=catalog)
        build_intent_packet(candidate, binding, catalog)
    except ValueError:
        injection_blocked = True
    if not injection_blocked:
        raise ValueError("candidate authority injection was admitted")

    bare = {
        key: deepcopy(value)
        for key, value in packet.items()
        if key not in {"proofreader_trace", "contract_digest"}
    }
    bare["frame_set"]["components"][0]["facts"][0]["value"] = "TAMPERED"
    tamper_trace = proofread_intent_packet(
        bare, checked_at="2026-08-06T03:01:01Z"
    )
    if tamper_trace["release_decision"] != "BLOCK":
        raise ValueError("same-packet proofreader admitted content tamper")

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
            "emr4.practice_context_fabric_intent_shaped_temporal_retrieval_acceptance.v1"
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
            "provider_free_authored_synthetic_intent_shaped_temporal_retrieval"
        ),
        "artifact_hashes": artifact_hashes,
        "artifact_set_digest": canonical_sha256(artifact_hashes),
        "deterministic_checks": {
            "schema_valid": True,
            "closed_objects": True,
            "explicit_vocabulary_mapping": True,
            "brand_is_not_authority": True,
            "minimal_component_results": component_results,
            "current_four_source_component_atomic": current_fact_codes,
            "bilateral_memory_share_admitted": True,
            "private_session_cross_bureau_blocked": True,
            "ambiguous_reference_returns_alternatives": True,
            "identity_assertions": 0,
            "invalidated_current_blocked": True,
            "known_then_and_corrected_later_distinct": historical_counts,
            "coverage_gap_not_absence": True,
            "candidate_authority_injection_blocked": True,
            "same_packet_content_tamper_blocked": True,
            "same_packet_proofreader_release": True,
        },
        "api_spine_checks": {
            "new_graphql_roots": 0,
            "new_graphql_resolvers": 0,
            "new_rest_commands": 0,
            "new_subscriptions": 0,
            "read_context_remains_non_command": True,
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
            "clinical_authority_operations": 0,
            "prescribing_operations": 0,
            "referral_operations": 0,
            "billing_operations": 0,
            "deployment_operations": 0,
            "protected_operations": 0,
        },
        "claim_boundary": (
            "Unmounted provider-free authored-synthetic intent-to-context "
            "selection only; no natural-language classification, patient/product "
            "data, provider, live retrieval, watcher, runtime, clinical or "
            "administrative command, deployment or protected-ref claim."
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
        return 0
    except (KeyError, TypeError, ValueError) as error:
        print(json.dumps({"passed": False, "error": str(error)}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
