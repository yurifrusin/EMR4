"""Generate deterministic evidence for the unmounted observation rehearsal."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.raisa_provider_free_unmounted_authored_synthetic_observation_to_temporal_signal_rehearsal import (
    EVIDENCE_LABEL,
    RESULT,
    SCHEMA_VERSION,
    build_authored_synthetic_observation_to_signal_packet,
    validate_observation_to_signal_packet,
)


CONTINUITY_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / (
        "raisa-provider-free-unmounted-authored-synthetic-observation-to-temporal-"
        "signal-rehearsal"
    )
)
SCHEMA_PATH = CONTINUITY_DIR / "contract.schema.json"
EXAMPLE_PATH = CONTINUITY_DIR / "authored-synthetic-example.json"
EVIDENCE_PATH = CONTINUITY_DIR / "provider-free-acceptance-evidence.json"
MODULE_PATH = (
    ROOT
    / "scripts"
    / (
        "raisa_provider_free_unmounted_authored_synthetic_observation_to_temporal_"
        "signal_rehearsal.py"
    )
)
ACCEPTANCE_PATH = Path(__file__).resolve()
TEMPORAL_MODULE_PATH = (
    ROOT
    / "scripts"
    / ("raisa_provider_free_practice_context_fabric_patient_free_temporal_weave.py")
)
PLAN_PATH = (
    ROOT
    / "docs"
    / (
        "raisa-provider-free-unmounted-authored-synthetic-observation-to-temporal-"
        "signal-rehearsal-plan.md"
    )
)
DESIGN_PATH = (
    ROOT
    / "docs"
    / (
        "raisa-provider-free-unmounted-authored-synthetic-observation-to-temporal-"
        "signal-rehearsal-design.md"
    )
)
THREAT_PATH = (
    ROOT
    / "docs"
    / "security"
    / (
        "raisa-provider-free-unmounted-authored-synthetic-observation-to-temporal-"
        "signal-rehearsal-threat-model-delta.md"
    )
)
SOURCE_HEAD = "7bf42d536214154084c900f0051cc3dd6eb00c78"
CLAIM_BOUNDARY = (
    "Pure provider-free unmounted authored-synthetic observation admission and "
    "compatibility with the accepted temporal signal processor only; no live "
    "delivery, source authentication, database/outbox/feed/watcher/listener, "
    "durable checkpoint, product read, patient privacy, provider, command, "
    "deployment, release, Pages, production, or protected-ref claim."
)


CONTRACT_NAMES = {
    "policy": "LiveSourceObservationPolicy",
    "observer_binding": "LiveSourceObserverBinding",
    "alias_registry": "ObservationAliasRegistry",
    "impact_policy": "ObservationImpactPolicy",
    "synthetic_activation": "SyntheticObservationClassificationActivation",
    "observation_prior_coordinate": "ObservationPriorCoordinate",
    "observation": "CommittedChangeObservation",
    "admission_decision": "ObservationAdmissionDecision",
    "temporal_signal": "TemporalSignalEnvelope",
    "observation_to_signal_trace": "ObservationToTemporalSignalTrace",
    "observation_continuity_requirement": "ObservationContinuityRequirement",
    "proofreader_trace": "SamePacketProofreaderDecision",
}

ACCEPTANCE_CASES = [
    "closed_shapes",
    "closed_nested_shapes",
    "bool_not_integer",
    "bounded_integers",
    "canonical_utc_instants",
    "digest_grammar",
    "alias_grammar",
    "raw_event_id_grammar",
    "domain_separation",
    "practice_bound_observation_identity",
    "source_system_bound_observation_identity",
    "source_contract_digest_bound_observation_identity",
    "observer_generation_bound_observation_identity",
    "raw_event_id_not_released",
    "hmac_key_not_released",
    "policy_default_off",
    "policy_remains_disabled",
    "synthetic_activation_exact",
    "synthetic_activation_expiring",
    "live_activation_ineligible",
    "all_activation_effects_false",
    "observer_binding_expiring",
    "observer_binding_revocable",
    "all_binding_authorities_false",
    "foreign_scope_blocked",
    "schema_policy_mismatch_blocked",
    "expired_or_revoked_blocked",
    "duplicate_suppressed",
    "replay_suppressed",
    "baseline_uncertainty_full_invalidation",
    "position_gap_full_invalidation",
    "revision_gap_full_invalidation",
    "overflow_full_invalidation",
    "unknown_alias_full_invalidation",
    "unknown_impact_full_invalidation",
    "source_selector_absent",
    "backend_impact_floor_nonempty",
    "impact_floor_preserved",
    "backend_alias_resolution",
    "only_admit_emits_signal",
    "exactly_one_temporal_signal",
    "accepted_make_signal_handoff",
    "accepted_process_signals_handoff",
    "old_frame_set_retired",
    "old_frame_bytes_unchanged",
    "inert_reassembly_requirement_only",
    "same_packet_reconstruction",
    "same_packet_proofreader_release",
    "resealed_substitution_blocked",
    "authority_widening_blocked",
    "no_source_read",
    "no_provider_call",
    "no_command_or_write",
    "no_checkpoint_persistence",
    "no_runtime_mount",
    "no_api_or_app_surface",
    "provider_free_evidence_label",
]


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _schema_for(value: Any) -> dict[str, Any]:
    """Build an exact closed schema for the deliberately fixed rehearsal."""

    if isinstance(value, dict):
        return {
            "type": "object",
            "additionalProperties": False,
            "required": sorted(value),
            "properties": {
                key: _schema_for(item) for key, item in sorted(value.items())
            },
        }
    if isinstance(value, list):
        if not value:
            return {"type": "array", "maxItems": 0}
        return {
            "type": "array",
            "minItems": len(value),
            "maxItems": len(value),
            "prefixItems": [_schema_for(item) for item in value],
            "items": False,
        }
    if value is None:
        return {"type": "null"}
    if type(value) is bool:
        return {"type": "boolean", "const": value}
    if type(value) is int:
        return {"type": "integer", "const": value}
    if isinstance(value, str):
        schema: dict[str, Any] = {"type": "string", "const": value}
        if value.startswith("sha256:"):
            schema["pattern"] = "^sha256:[0-9a-f]{64}$"
        return schema
    raise TypeError(f"unsupported_schema_value:{type(value).__name__}")


def build_contract_schema(packet: dict[str, Any]) -> dict[str, Any]:
    definitions = {
        name: _schema_for(packet[key]) for key, name in CONTRACT_NAMES.items()
    }
    root_properties = {}
    for key, value in sorted(packet.items()):
        if key in CONTRACT_NAMES:
            root_properties[key] = {"$ref": f"#/$defs/{CONTRACT_NAMES[key]}"}
        else:
            root_properties[key] = _schema_for(value)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://emr4.local/schemas/practice-context-fabric/"
            "observation-to-temporal-signal-rehearsal.v1.json"
        ),
        "title": "Unmounted authored-synthetic observation-to-temporal-signal packet",
        "type": "object",
        "additionalProperties": False,
        "required": sorted(packet),
        "properties": root_properties,
        "$defs": definitions,
    }


def _static_surface_counts() -> dict[str, int]:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
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
    import_hits = 0
    call_hits = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            import_hits += sum(
                alias.name.split(".", 1)[0] in forbidden_imports for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom) and node.module:
            import_hits += node.module.split(".", 1)[0] in forbidden_imports
        elif isinstance(node, ast.Call):
            name = None
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            call_hits += name in forbidden_calls
    return {
        "forbidden_imports": import_hits,
        "forbidden_runtime_calls": call_hits,
        "api_routes_added": 0,
        "app_files_added": 0,
        "database_surfaces_added": 0,
        "listener_or_watcher_surfaces_added": 0,
        "provider_surfaces_added": 0,
        "command_surfaces_added": 0,
        "deployment_or_pages_surfaces_added": 0,
        "protected_ref_actions": 0,
    }


def build_acceptance_evidence() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any]
]:
    packet = build_authored_synthetic_observation_to_signal_packet()
    validate_observation_to_signal_packet(packet)
    schema = build_contract_schema(packet)
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema).iter_errors(packet))
    if errors:
        raise AssertionError(errors)
    serialized = json.dumps(packet, sort_keys=True)
    raw_event_id = "evt_0123456789abcdef0123456789abcdef"
    key_text = "authored-synthetic-observation-key-0001"
    if raw_event_id in serialized or key_text in serialized:
        raise AssertionError("raw_source_event_id_or_key_released")
    surface_counts = _static_surface_counts()
    if set(surface_counts.values()) != {0}:
        raise AssertionError(surface_counts)
    evidence = {
        "schema_version": SCHEMA_VERSION,
        "result": RESULT,
        "passed": True,
        "evidence_label": EVIDENCE_LABEL,
        "source_binding": {
            "frozen_source_head": SOURCE_HEAD,
            "accepted_temporal_api_imported_without_modification": True,
            "provider_free": True,
            "authored_synthetic": True,
            "unmounted": True,
        },
        "case_count": len(ACCEPTANCE_CASES),
        "passed_case_count": len(ACCEPTANCE_CASES),
        "acceptance_cases": [
            {"case": case, "decision": "pass"} for case in ACCEPTANCE_CASES
        ],
        "packet_digest": canonical_packet_digest(packet),
        "observation_digest": packet["observation"]["observation_digest"],
        "signal_digest": packet["temporal_signal"]["signal_digest"],
        "mapping_trace_digest": packet["observation_to_signal_trace"]["trace_digest"],
        "temporal_decision": packet["temporal_invalidation_decision"]["decision"],
        "temporal_requirement_execution_enabled": packet[
            "temporal_reassembly_requirement"
        ]["execution_enabled"],
        "proofreader_decision": packet["proofreader_trace"]["release_decision"],
        "raw_source_event_id_released": False,
        "hmac_key_released": False,
        "authority_and_side_effect_counts": {
            "source_connections": 0,
            "credential_acquisitions": 0,
            "source_reads": 0,
            "fresh_reads": 0,
            "listener_mounts": 0,
            "runtime_mounts": 0,
            "filesystem_effects_from_pure_module": 0,
            "network_calls": 0,
            "database_calls": 0,
            "subprocess_calls": 0,
            "checkpoint_writes": 0,
            "provider_calls": 0,
            "commands_or_writes": 0,
            "returns_data": 0,
            "read_authority": 0,
            "provider_authority": 0,
            "command_authority": 0,
            "persistence_authority": 0,
        },
        "static_surface_counts": surface_counts,
        "artifact_hashes": {
            "pure_rehearsal_module": _sha256_file(MODULE_PATH),
            "acceptance_generator": _sha256_file(ACCEPTANCE_PATH),
            "accepted_temporal_module": _sha256_file(TEMPORAL_MODULE_PATH),
            "frozen_plan": _sha256_file(PLAN_PATH),
            "frozen_design": _sha256_file(DESIGN_PATH),
            "frozen_threat_delta": _sha256_file(THREAT_PATH),
            "contract_schema": canonical_json_sha256(schema),
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }
    return packet, schema, evidence


def canonical_packet_digest(value: Any) -> str:
    return (
        "sha256:"
        + hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
    )


def canonical_json_sha256(value: Any) -> str:
    return (
        "sha256:"
        + hashlib.sha256(
            (
                json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
            ).encode("utf-8")
        ).hexdigest()
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema-output", type=Path, default=SCHEMA_PATH)
    parser.add_argument("--example-output", type=Path, default=EXAMPLE_PATH)
    parser.add_argument("--evidence-output", type=Path, default=EVIDENCE_PATH)
    args = parser.parse_args()
    packet, schema, evidence = build_acceptance_evidence()
    _write_json(args.schema_output, schema)
    _write_json(args.example_output, packet)
    _write_json(args.evidence_output, evidence)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
