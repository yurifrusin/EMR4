"""Provider-free deterministic acceptance for Bureau successor lanes."""

from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "orchestration/continuity/model-required-bureau-provider-free-successor-lanes"
CONTRACT = ARTIFACT_ROOT / "successor-lanes-contract.json"
CONTRACT_SCHEMA = ARTIFACT_ROOT / "successor-lanes-contract.schema.json"
DESIGN = ROOT / "docs/emr4-model-required-bureau-provider-free-successor-lanes.md"
THREAT = ROOT / "docs/security/emr4-model-required-bureau-provider-free-successor-lanes-threat-model-delta.md"
DEFAULT_OUTPUT = ARTIFACT_ROOT / "provider-free-acceptance-evidence.json"
EXPECTED_HEAD = "ef6d0e20d4fabaa922d95ce96853bacda7b50603"
EXPECTED_RESULT = "model_required_bureau_provider_free_successor_lanes_pass"
SCHEMA_EXAMPLES = {
    "waiting_room": (ARTIFACT_ROOT / "waiting-room-context-frame.schema.json", ARTIFACT_ROOT / "waiting-room-context-frame.example.json"),
    "technical_anatomy": (ARTIFACT_ROOT / "technical-anatomy-frame.schema.json", ARTIFACT_ROOT / "technical-anatomy-frame.example.json"),
    "technical_diagnosis": (ARTIFACT_ROOT / "technical-diagnosis-candidate.schema.json", ARTIFACT_ROOT / "technical-diagnosis-candidate.example.json"),
    "update_provenance_delta": (ARTIFACT_ROOT / "update-provenance-delta.schema.json", ARTIFACT_ROOT / "update-provenance-delta.example.json"),
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must be an object")
    return value


def validate(schema_path: Path, instance: dict[str, Any]) -> None:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(instance),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        raise ValueError(f"{schema_path.name}: {errors[0].message}")


def language_decision(domain: str, case: dict[str, Any]) -> str:
    if case["authority_shape"] in {"direct_confirmation", "administration"}:
        return "refuse"
    if case["policy_signal"] in {
        "clinical_content", "cross_scope", "inactive_resource", "bulk",
        "negated", "delegated_confirmation",
    }:
        return "refuse"
    if case["context_state"] == "stale":
        return "refuse"
    if case["context_state"] == "conflict" or case["identity_state"] == "ambiguous":
        return "clarify"
    if case["policy_signal"] == "correction" or case["candidate_intent"] == "clarify":
        return "clarify"
    if case["candidate_intent"].endswith("_proposal"):
        return "admit_proposal"
    if domain == "rayleen":
        return "admit_projection"
    if case["candidate_intent"] == "dry_run":
        return "admit_dry_run"
    if case["candidate_intent"] == "refuse":
        return "refuse"
    return "admit_read"


def proofread_diagnosis(
    anatomy: dict[str, Any], candidate: dict[str, Any], *, now: str = "2026-08-04T08:00:30Z"
) -> str | None:
    try:
        validate(SCHEMA_EXAMPLES["technical_diagnosis"][0], candidate)
    except ValueError:
        return "SCHEMA_REJECTED"
    if candidate["anatomy_frame_id"] != anatomy["frame_id"]:
        return "CROSS_ENVIRONMENT_REFERENCE"
    if candidate["anatomy_version"] != anatomy["anatomy_version"]:
        return "STALE_ANATOMY_VERSION"
    current = datetime.fromisoformat(now.replace("Z", "+00:00"))
    expiry = datetime.fromisoformat(anatomy["expires_at"].replace("Z", "+00:00"))
    if current >= expiry:
        return "STALE_ANATOMY_VERSION"
    observation_ids = {item["observation_id"] for item in anatomy["observations"]}
    for hypothesis in candidate["hypotheses"]:
        if not set(hypothesis["evidence_links"]) <= observation_ids:
            return "UNKNOWN_EVIDENCE"
        if hypothesis["support_state"] == "partially_supported" and not candidate["missing_evidence"]:
            return "UNSUPPORTED_HYPOTHESIS"
    runbooks = {item["runbook_id"] for item in anatomy["signed_runbook_catalog"]}
    if candidate["candidate_runbook_id"] not in runbooks | {None}:
        return "UNKNOWN_RUNBOOK"
    forbidden = ("shell", "sql", "powershell", "cmd.exe", "http://", "https://", "kubectl", "successfully recovered")
    text = json.dumps(candidate, sort_keys=True).lower()
    if any(token in text for token in forbidden):
        return "EXECUTABLE_INSTRUCTION"
    return None


def _validate_contract() -> dict[str, Any]:
    contract = load_json(CONTRACT)
    validate(CONTRACT_SCHEMA, contract)
    if contract["source_head"] != EXPECTED_HEAD:
        raise ValueError("source HEAD drift")
    rayleen = contract["rayleen"]
    davida = contract["davida"]
    if rayleen["action_grammar_reuse"] != {
        "check_in_proposal": "diary.check_in",
        "status_proposal": "diary.status_change",
        "waiting_area_move_proposal": "diary.waiting_area_move",
    }:
        raise ValueError("Rayleen private-action drift")
    if set(davida["resources"]) != {"active_practitioner", "active_location"}:
        raise ValueError("Davida initial resource boundary drift")
    decisions: dict[str, dict[str, int]] = {}
    for lane in (rayleen, davida):
        counts: dict[str, int] = {}
        for case in lane["cases"]:
            actual = language_decision(lane["domain"], case)
            if actual != case["expected_decision"]:
                raise ValueError(f"{case['id']} expected {case['expected_decision']} got {actual}")
            counts[actual] = counts.get(actual, 0) + 1
        decisions[lane["domain"]] = counts
    recovery = contract["controlled_recovery"]
    required_kinds = {
        "service_version", "component_version", "deployment_manifest_reference",
        "database_schema_head", "dependency_state", "health_signal", "capacity_signal",
        "sanitized_error_class", "backup_verification", "configuration_drift",
        "signed_runbook_catalog_reference",
    }
    if set(recovery["observation_kinds"]) != required_kinds:
        raise ValueError("C1 observation vocabulary drift")
    update = contract["update_supply_chain"]
    class_map = {item["id"]: item["future_command_family"] for item in update["classes"]}
    if len(class_map) != 4 or len(set(class_map.values())) != 4 or update["generic_update_command"]:
        raise ValueError("D1 update-class separation failed")
    return {
        "rayleen_case_count": len(rayleen["cases"]),
        "davida_case_count": len(davida["cases"]),
        "language_decisions": decisions,
        "c1_observation_kind_count": len(required_kinds),
        "c1_vocabulary_frozen": recovery["c1_vocabulary_frozen"],
        "d1_update_class_count": len(class_map),
        "distinct_future_command_family_count": len(set(class_map.values())),
    }


def _validate_examples() -> dict[str, Any]:
    for schema_path, example_path in SCHEMA_EXAMPLES.values():
        validate(schema_path, load_json(example_path))
    waiting = load_json(SCHEMA_EXAMPLES["waiting_room"][1])
    fact = waiting["backend_facts"][0]
    if fact["label"]["authority_ceiling"] != "data_only":
        raise ValueError("waiting-room fact authority widened")
    arrived = datetime.fromisoformat(fact["arrived_at"].replace("Z", "+00:00"))
    generated = datetime.fromisoformat(waiting["generated_at"].replace("Z", "+00:00"))
    expected_minutes = int((generated - arrived).total_seconds() // 60)
    if waiting["derived_signals"][0]["value"] != expected_minutes:
        raise ValueError("elapsed wait was not deterministically derived")
    anatomy = load_json(SCHEMA_EXAMPLES["technical_anatomy"][1])
    candidate = load_json(SCHEMA_EXAMPLES["technical_diagnosis"][1])
    if proofread_diagnosis(anatomy, candidate) is not None:
        raise ValueError("nominal technical diagnosis was denied")
    update = load_json(SCHEMA_EXAMPLES["update_provenance_delta"][1])
    if update["activation_authorized"]:
        raise ValueError("update activation escaped D2")
    return {
        "closed_schema_count": 1 + len(SCHEMA_EXAMPLES),
        "canonical_example_count": len(SCHEMA_EXAMPLES),
        "waiting_room_fact_count": len(waiting["backend_facts"]),
        "deterministic_elapsed_wait_minutes": expected_minutes,
        "diagnosis_proofreader_nominal": "admit_read_only_candidate",
        "update_activation_count": 0,
    }


def _validate_diagnosis_denials() -> dict[str, str]:
    anatomy = load_json(SCHEMA_EXAMPLES["technical_anatomy"][1])
    candidate = load_json(SCHEMA_EXAMPLES["technical_diagnosis"][1])
    cases: dict[str, str] = {}
    changed = deepcopy(candidate); changed["hypotheses"][0]["evidence_links"] = ["missing"]
    cases["unknown_evidence"] = proofread_diagnosis(anatomy, changed) or ""
    changed = deepcopy(candidate); changed["anatomy_version"] = "other"
    cases["stale_version"] = proofread_diagnosis(anatomy, changed) or ""
    changed = deepcopy(candidate); changed["candidate_runbook_id"] = "unknown-runbook"
    cases["unknown_runbook"] = proofread_diagnosis(anatomy, changed) or ""
    changed = deepcopy(candidate); changed["operator_explanation"] = "Run shell command now"
    cases["executable"] = proofread_diagnosis(anatomy, changed) or ""
    cases["expired"] = proofread_diagnosis(anatomy, candidate, now="2026-08-04T08:05:00Z") or ""
    expected = {
        "unknown_evidence":"UNKNOWN_EVIDENCE", "stale_version":"STALE_ANATOMY_VERSION",
        "unknown_runbook":"UNKNOWN_RUNBOOK", "executable":"EXECUTABLE_INSTRUCTION",
        "expired":"STALE_ANATOMY_VERSION",
    }
    if cases != expected:
        raise ValueError(f"diagnosis denial drift: {cases}")
    return cases


def _validate_documents() -> dict[str, Any]:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in (DESIGN, THREAT))
    required = (
        "provid" + "er-free and non-executing", "graphql is scoped read/context only",
        "no generic update command", "docs/branding/", "provider_free_successor_lane_architecture_and_proof",
        "cannot convert `propose` into `confirm`", "no actuator exists",
    )
    missing = [phrase for phrase in required if phrase not in text]
    if missing:
        raise ValueError(f"document boundary missing: {missing}")
    return {"document_count": 2, "required_boundary_count": len(required)}


def build_evidence() -> dict[str, Any]:
    contract = _validate_contract()
    examples = _validate_examples()
    denials = _validate_diagnosis_denials()
    documents = _validate_documents()
    artifacts = [CONTRACT, CONTRACT_SCHEMA, DESIGN, THREAT]
    artifacts.extend(path for pair in SCHEMA_EXAMPLES.values() for path in pair)
    authority = load_json(CONTRACT)["authority"]
    if set(authority.values()) != {0}:
        raise ValueError("side-effect accounting is not zero")
    return {
        "schema_version":"emr4.model_required_bureau_successor_lanes_acceptance.v1",
        "passed":True,"result":EXPECTED_RESULT,"source_head":EXPECTED_HEAD,
        "contract":contract,"schemas_and_examples":examples,
        "diagnosis_denials":denials,"documents":documents,
        "authority_and_side_effects":authority,
        "artifact_hashes":{str(path.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest() for path in artifacts},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    evidence = build_evidence()
    if args.check:
        existing = load_json(args.output)
        if existing != evidence:
            raise SystemExit("acceptance evidence is stale")
    else:
        args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "result": EXPECTED_RESULT, "source_head": EXPECTED_HEAD}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
