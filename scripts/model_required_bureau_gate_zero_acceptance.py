"""Provider-free deterministic acceptance for the Gate-zero Bureau contract."""

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
ARTIFACT_ROOT = (
    ROOT / "orchestration/continuity/model-required-bureau-gate-zero"
)
CONTRACT_PATH = ARTIFACT_ROOT / "shared-contract.json"
CONTRACT_SCHEMA_PATH = ARTIFACT_ROOT / "shared-contract.schema.json"
DESIGN_PATH = ROOT / "docs/emr4-model-required-bureau-gate-zero-shared-contract.md"
THREAT_PATH = (
    ROOT
    / "docs/security/emr4-model-required-bureau-gate-zero-threat-model-delta.md"
)
DEFAULT_OUTPUT = ARTIFACT_ROOT / "provider-free-acceptance-evidence.json"
EXPECTED_SOURCE_HEAD = "50dab5d66fc1401344fc47d7aa5ebd336b75e960"
EXPECTED_RESULT = (
    "model_required_bureau_gate_zero_provider_free_deterministic_acceptance_pass"
)

SCHEMA_EXAMPLES = {
    "labeled_context_frame": (
        ARTIFACT_ROOT / "labeled-context-frame.schema.json",
        ARTIFACT_ROOT / "labeled-context-frame.example.json",
    ),
    "typed_candidate": (
        ARTIFACT_ROOT / "typed-candidate.schema.json",
        ARTIFACT_ROOT / "typed-candidate.example.json",
    ),
    "typed_denial_receipt": (
        ARTIFACT_ROOT / "typed-denial-receipt.schema.json",
        ARTIFACT_ROOT / "typed-denial-receipt.example.json",
    ),
    "one_attempt_cell_manifest": (
        ARTIFACT_ROOT / "one-attempt-cell-manifest.schema.json",
        ARTIFACT_ROOT / "one-attempt-cell-manifest.example.json",
    ),
    "teardown_residue_receipt": (
        ARTIFACT_ROOT / "teardown-residue-receipt.schema.json",
        ARTIFACT_ROOT / "teardown-residue-receipt.example.json",
    ),
}


class DuplicateKeyError(ValueError):
    """Raised before schema validation when hostile JSON repeats a key."""


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return payload


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validator(schema_path: Path) -> Draft202012Validator:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def validate_instance(schema_path: Path, instance: dict[str, Any]) -> None:
    errors = sorted(validator(schema_path).iter_errors(instance), key=str)
    if errors:
        raise ValueError(f"{schema_path.name}: {errors[0].message}")


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(key)
        result[key] = value
    return result


def parse_candidate_bytes(data: bytes) -> tuple[dict[str, Any] | None, str | None]:
    contract = load_json(CONTRACT_PATH)
    if len(data) > contract["cell_contract"]["quotas"]["output_bytes_max"]:
        return None, "BYTE_BUDGET_EXCEEDED"
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return None, "INVALID_UTF8"
    try:
        payload = json.loads(text, object_pairs_hook=_reject_duplicate_pairs)
    except DuplicateKeyError:
        return None, "DUPLICATE_KEY"
    except json.JSONDecodeError:
        return None, "SCHEMA_REJECTED"
    if not isinstance(payload, dict):
        return None, "SCHEMA_REJECTED"
    errors = list(
        validator(SCHEMA_EXAMPLES["typed_candidate"][0]).iter_errors(payload)
    )
    if errors:
        return None, "SCHEMA_REJECTED"
    return payload, None


def authority_index(ceiling: str) -> int:
    order = load_json(CONTRACT_PATH)["label_algebra"]["authority_ceiling_order"]
    try:
        return order.index(ceiling)
    except ValueError as error:
        raise ValueError(f"unknown authority ceiling: {ceiling}") from error


def join_labels(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """Deterministic mirror of the frozen conservative label join."""

    left_expiry = datetime.fromisoformat(left["expires_at"].replace("Z", "+00:00"))
    right_expiry = datetime.fromisoformat(right["expires_at"].replace("Z", "+00:00"))
    left_observed = datetime.fromisoformat(
        left["observed_at"].replace("Z", "+00:00")
    )
    right_observed = datetime.fromisoformat(
        right["observed_at"].replace("Z", "+00:00")
    )
    ceilings = (left["authority_ceiling"], right["authority_ceiling"])
    return {
        "source_ids": sorted(set(left["source_ids"]) | set(right["source_ids"])),
        "transformation_trace": list(
            dict.fromkeys(
                left["transformation_trace"]
                + right["transformation_trace"]
                + ["label_join:conservative.v1"]
            )
        ),
        "integrity_principals": sorted(
            set(left["integrity_principals"])
            & set(right["integrity_principals"])
        ),
        "confidentiality_readers": sorted(
            set(left["confidentiality_readers"])
            & set(right["confidentiality_readers"])
        ),
        "observed_at": max(left_observed, right_observed)
        .isoformat()
        .replace("+00:00", "Z"),
        "expires_at": min(left_expiry, right_expiry)
        .isoformat()
        .replace("+00:00", "Z"),
        "freshness_state": (
            "stale"
            if "stale" in {left["freshness_state"], right["freshness_state"]}
            else "fresh"
        ),
        "authority_ceiling": min(ceilings, key=authority_index),
    }


def mediate_sink(label: dict[str, Any], sink_id: str) -> str | None:
    contract = load_json(CONTRACT_PATH)
    sinks = {item["id"]: item for item in contract["sink_registry"]}
    if sink_id not in sinks:
        return "SCHEMA_REJECTED"
    sink = sinks[sink_id]
    if sink["freshness_required"] and label["freshness_state"] != "fresh":
        return "CONTEXT_STALE"
    if sink["required_reader"] not in label["confidentiality_readers"]:
        return "READER_NOT_AUTHORIZED"
    if not set(sink["required_integrity_any"]) & set(
        label["integrity_principals"]
    ):
        return "INTEGRITY_INSUFFICIENT"
    if authority_index(label["authority_ceiling"]) > authority_index(
        sink["maximum_authority_ceiling"]
    ):
        return "AUTHORITY_CEILING_EXCEEDED"
    return None


def provider_outage_receipt(domain: str = "davida") -> dict[str, Any]:
    receipt = load_json(SCHEMA_EXAMPLES["typed_denial_receipt"][1])
    receipt.update(
        {
            "domain": domain,
            "reason_code": "PROVIDER_REQUIRED_UNAVAILABLE",
            "failed_sink": "provider_input",
            "field_path": "$",
            "source_ids": [],
            "failed_rules": ["MODEL_REQUIRED_NO_ADMITTED_PROVIDER_RESULT"],
            "provider_call_count": 0,
        }
    )
    validate_instance(SCHEMA_EXAMPLES["typed_denial_receipt"][0], receipt)
    return receipt


def _validate_contract() -> dict[str, Any]:
    contract = load_json(CONTRACT_PATH)
    validate_instance(CONTRACT_SCHEMA_PATH, contract)

    planes = contract["planes"]
    if [item["order"] for item in planes] != [1, 2, 3, 4]:
        raise ValueError("four-plane order drift")
    expected_plane_ids = ["cognitive", "proof", "authority", "execution_verification"]
    if [item["id"] for item in planes] != expected_plane_ids:
        raise ValueError("four-plane identity drift")
    principals = [item["principal"] for item in planes]
    if len(principals) != len(set(principals)):
        raise ValueError("plane principals are not distinct")
    if [item["effect_authority"] for item in planes] != [False, False, False, True]:
        raise ValueError("effect authority escaped the execution plane")
    if dict(zip(expected_plane_ids, principals, strict=True)) != {
        "cognitive": "cognitive_cell_generation",
        "proof": "deterministic_proofreader",
        "authority": "backend_authority_service",
        "execution_verification": "single_purpose_command_handler",
    }:
        raise ValueError("plane principal association drift")

    expected_domains = ["bernie", "rayleen", "davida", "controlled_recovery_update"]
    domains = contract["domains"]
    if [item["id"] for item in domains] != expected_domains:
        raise ValueError("domain order or identity drift")
    kinds = [kind for item in domains for kind in item["candidate_kinds"]]
    if len(kinds) != len(set(kinds)):
        raise ValueError("candidate kind crosses a Bureau domain")
    if {item["id"]: item["candidate_kinds"] for item in domains} != {
        "bernie": ["appointment_projection", "appointment_proposal"],
        "rayleen": [
            "waiting_room_projection",
            "arrival_status_or_area_proposal",
        ],
        "davida": [
            "practice_administration_advisory",
            "practice_administration_proposal",
        ],
        "controlled_recovery_update": [
            "technical_diagnosis",
            "recovery_plan",
            "update_proposal",
        ],
    }:
        raise ValueError("domain candidate-kind association drift")

    sources = contract["source_registry"]
    if len({item["id"] for item in sources}) != len(sources):
        raise ValueError("duplicate source registry entry")
    if {item["id"]: item["integrity_principal"] for item in sources} != {
        "authorized_backend_read": "backend_truth",
        "committed_event_hint": "event_hint_only",
        "authored_synthetic_fixture": "authored_synthetic",
        "provider_model_candidate": "untrusted_model",
    }:
        raise ValueError("source integrity association drift")
    sinks = contract["sink_registry"]
    if len({item["id"] for item in sinks}) != len(sinks):
        raise ValueError("duplicate sink registry entry")
    sink_map = {item["id"]: item for item in sinks}
    if {
        sink_id: (
            sink["maximum_authority_ceiling"],
            tuple(sink["required_integrity_any"]),
            sink["required_reader"],
            sink["separate_material_gate"],
        )
        for sink_id, sink in sink_map.items()
    } != {
        "provider_input": (
            "data_only",
            ("backend_truth", "authored_synthetic"),
            "admitted_provider_request",
            True,
        ),
        "projection_release": (
            "projection_candidate",
            ("deterministic_proofreader",),
            "authorized_surface",
            False,
        ),
        "proposal_release": (
            "proposal_candidate",
            ("deterministic_proofreader",),
            "authorized_surface",
            False,
        ),
        "diagnosis_release": (
            "diagnosis_candidate",
            ("deterministic_proofreader",),
            "authorized_operator",
            False,
        ),
        "recovery_plan_release": (
            "recovery_plan_candidate",
            ("deterministic_proofreader",),
            "authorized_operator",
            False,
        ),
        "command_argument": (
            "command_argument",
            ("backend_authority_service",),
            "single_purpose_command_handler",
            True,
        ),
        "effect": (
            "effect",
            ("single_purpose_command_handler",),
            "deterministic_readback",
            True,
        ),
    }:
        raise ValueError("sink rule association drift")

    cell = contract["cell_contract"]
    if set(cell["cell_visible_bridges"]) & set(cell["forbidden_bridges"]):
        raise ValueError("forbidden cell bridge admitted")
    if cell["input_count"] != 1 or cell["candidate_output_count"] != 1:
        raise ValueError("cell is not one input/one output")

    authority = contract["authority"]
    forbidden_true = [
        key
        for key, value in authority.items()
        if key.endswith("_authorized") and value is not False
    ]
    if forbidden_true:
        raise ValueError(f"Gate-zero authority widened: {forbidden_true}")

    return {
        "source_head": contract["source_head"],
        "plane_count": len(planes),
        "distinct_plane_principal_count": len(set(principals)),
        "domain_count": len(domains),
        "candidate_kind_count": len(kinds),
        "source_rule_count": len(sources),
        "sink_rule_count": len(sinks),
        "forbidden_bridge_count": len(cell["forbidden_bridges"]),
        "blocked_boundary_count": len(contract["blocked_boundaries"]),
    }


def _validate_schema_examples() -> dict[str, Any]:
    for schema_path, example_path in SCHEMA_EXAMPLES.values():
        validate_instance(schema_path, load_json(example_path))
    return {
        "closed_schema_count": 1 + len(SCHEMA_EXAMPLES),
        "canonical_example_count": len(SCHEMA_EXAMPLES),
        "schema_ids": {
            name: load_json(schema_path)["$id"]
            for name, (schema_path, _) in SCHEMA_EXAMPLES.items()
        },
    }


def _validate_hostile_parser() -> dict[str, Any]:
    candidate = load_json(SCHEMA_EXAMPLES["typed_candidate"][1])
    nominal = json.dumps(candidate, separators=(",", ":"), sort_keys=True).encode()
    parsed, reason = parse_candidate_bytes(nominal)
    if reason is not None or parsed != candidate:
        raise ValueError("nominal candidate failed hostile parser")

    duplicate = b'{"schema_version":"a","schema_version":"b"}'
    _, duplicate_reason = parse_candidate_bytes(duplicate)
    _, utf8_reason = parse_candidate_bytes(b"\xff")
    quota = load_json(CONTRACT_PATH)["cell_contract"]["quotas"]["output_bytes_max"]
    _, budget_reason = parse_candidate_bytes(b"x" * (quota + 1))
    trailing = nominal + b"\n{}"
    _, trailing_reason = parse_candidate_bytes(trailing)
    if [duplicate_reason, utf8_reason, budget_reason, trailing_reason] != [
        "DUPLICATE_KEY",
        "INVALID_UTF8",
        "BYTE_BUDGET_EXCEEDED",
        "SCHEMA_REJECTED",
    ]:
        raise ValueError("hostile parser reason-code drift")
    return {
        "nominal_candidate_admitted_to_schema_validation": True,
        "hostile_cases": 4,
        "duplicate_key_reason": duplicate_reason,
        "invalid_utf8_reason": utf8_reason,
        "byte_budget_reason": budget_reason,
        "trailing_bytes_reason": trailing_reason,
    }


def _label_fixture(**changes: Any) -> dict[str, Any]:
    label = deepcopy(
        load_json(SCHEMA_EXAMPLES["typed_candidate"][1])["payload"]["summary"][
            "label"
        ]
    )
    label.update(
        {
            "integrity_principals": ["deterministic_proofreader"],
            "confidentiality_readers": ["authorized_surface"],
            "authority_ceiling": "proposal_candidate",
        }
    )
    label.update(changes)
    return label


def _validate_label_and_sink_rules() -> dict[str, Any]:
    admitted = _label_fixture()
    if mediate_sink(admitted, "proposal_release") is not None:
        raise ValueError("nominal proposal label was denied")
    cases = {
        "stale": mediate_sink(
            _label_fixture(freshness_state="stale"), "proposal_release"
        ),
        "reader": mediate_sink(
            _label_fixture(confidentiality_readers=["authorized_operator"]),
            "proposal_release",
        ),
        "integrity": mediate_sink(
            _label_fixture(integrity_principals=["untrusted_model"]),
            "proposal_release",
        ),
        "ceiling": mediate_sink(
            _label_fixture(authority_ceiling="effect"), "proposal_release"
        ),
    }
    if cases != {
        "stale": "CONTEXT_STALE",
        "reader": "READER_NOT_AUTHORIZED",
        "integrity": "INTEGRITY_INSUFFICIENT",
        "ceiling": "AUTHORITY_CEILING_EXCEEDED",
    }:
        raise ValueError(f"sink denial drift: {cases}")

    restrictive = _label_fixture(
        source_ids=["authorized_backend_read:one"],
        integrity_principals=["deterministic_proofreader", "backend_truth"],
        confidentiality_readers=["authorized_surface", "authorized_operator"],
        expires_at="2026-08-04T02:03:00Z",
        authority_ceiling="projection_candidate",
    )
    joined = join_labels(admitted, restrictive)
    if joined["integrity_principals"] != ["deterministic_proofreader"]:
        raise ValueError("integrity join widened trust")
    if joined["confidentiality_readers"] != ["authorized_surface"]:
        raise ValueError("reader join widened access")
    if joined["expires_at"] != "2026-08-04T02:03:00Z":
        raise ValueError("expiry join did not choose earliest")
    if joined["authority_ceiling"] != "projection_candidate":
        raise ValueError("authority join did not choose minimum")

    return {
        "nominal_sink_admissions": 1,
        "typed_sink_denials": cases,
        "join_dimensions_checked": 5,
    }


def _validate_outage() -> dict[str, Any]:
    contract = load_json(CONTRACT_PATH)
    admission = contract["provider_admission"]
    receipt = provider_outage_receipt()
    if admission["gate_zero_provider_call_authorized"]:
        raise ValueError("Gate zero unexpectedly authorizes a provider call")
    if receipt["candidate_released"] or receipt["provider_call_count"]:
        raise ValueError("provider outage released a candidate or call")
    return {
        "model_required_for_agentic_claim": admission[
            "model_required_for_agentic_claim"
        ],
        "reason_code": receipt["reason_code"],
        "provider_call_count": 0,
        "candidate_release_count": 0,
        "agentic_completion_claim_count": 0,
    }


def _validate_documents() -> dict[str, Any]:
    combined = " ".join(
        " ".join(path.read_text(encoding="utf-8").lower().split())
        for path in (DESIGN_PATH, THREAT_PATH)
    )
    required = (
        "model-required cognition; deterministic authority",
        "no provider call",
        "one-attempt",
        "duplicate keys",
        "typed denial receipt",
        "no silent",
        "deterministic readback",
        "docs/branding/",
        "provider_free_gate_zero_architecture_contract",
    )
    missing = [phrase for phrase in required if phrase not in combined]
    if missing:
        raise ValueError(f"Gate-zero documents missing claims: {missing}")
    forbidden = (
        "production ready",
        "prompt injection is eliminated",
        "provider runtime is authorized",
        "patient data is authorized",
    )
    overclaims = [phrase for phrase in forbidden if phrase in combined]
    if overclaims:
        raise ValueError(f"Gate-zero overclaim present: {overclaims}")
    return {
        "document_count": 2,
        "required_claim_count": len(required),
        "overclaim_count": 0,
    }


def build_evidence() -> dict[str, Any]:
    contract = _validate_contract()
    if contract["source_head"] != EXPECTED_SOURCE_HEAD:
        raise ValueError("Gate-zero source-head binding drift")
    schemas = _validate_schema_examples()
    parser = _validate_hostile_parser()
    labels = _validate_label_and_sink_rules()
    outage = _validate_outage()
    documents = _validate_documents()
    artifact_paths = [
        CONTRACT_PATH,
        CONTRACT_SCHEMA_PATH,
        DESIGN_PATH,
        THREAT_PATH,
        *[
            path
            for pair in SCHEMA_EXAMPLES.values()
            for path in pair
        ],
    ]
    return {
        "schema_version": "emr4.model_required_bureau_gate_zero_acceptance.v1",
        "passed": True,
        "result": EXPECTED_RESULT,
        "source_head": EXPECTED_SOURCE_HEAD,
        "contract": contract,
        "schemas": schemas,
        "hostile_parser": parser,
        "label_and_sink_mediation": labels,
        "provider_outage": outage,
        "documents": documents,
        "artifact_hashes": {
            path.relative_to(ROOT).as_posix(): f"sha256:{sha256_path(path)}"
            for path in sorted(artifact_paths)
        },
        "authority_and_side_effects": {
            "provider_calls": 0,
            "external_prompt_transmissions": 0,
            "product_data_reads": 0,
            "patient_or_clinical_data_accesses": 0,
            "runtime_wirings": 0,
            "commands_or_writes": 0,
            "actuator_calls": 0,
            "deployments": 0,
            "production_changes": 0,
            "releases": 0,
            "pages_rebuilds": 0,
            "protected_ref_movements": 0,
            "protected_evidence_accesses": 0,
        },
        "claim_boundary": (
            "Architecture, closed schema prototypes and provider-free deterministic "
            "failure evidence only; no occupied model, live product or runtime claim."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    evidence = build_evidence()
    if not args.check:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(evidence, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
