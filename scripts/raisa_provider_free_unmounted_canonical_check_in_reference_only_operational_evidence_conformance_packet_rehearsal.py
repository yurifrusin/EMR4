"""Run the provider-free canonical check-in reference-only conformance packet."""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
from typing import Any

import yaml

from app.services.appointment_check_in_environment_evidence_gate import (
    EnvironmentEvidenceGateReading,
    evaluate_check_in_environment_evidence_gate,
)
from app.services.appointment_check_in_environment_manifest import (
    ManifestNormalizationResult,
    normalize_check_in_environment_manifest,
)
from app.services.appointment_check_in_operational_evidence import (
    OperationalEvidenceInputNormalizationResult,
    normalize_check_in_operational_evidence_inputs,
)
from orchestration_harness.check_in_admission_control import (
    AdmissionRequest,
    AdmissionSnapshot,
    AdmissionState,
    KillSwitchState,
    OrdinaryAdmissionRecord,
    evaluate_admission,
)
from orchestration_harness.check_in_environment_evidence_admission import (
    evaluate_admission_with_environment_evidence,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTINUITY_DIR = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-canonical-check-in-reference-only-"
    "operational-evidence-conformance-packet-rehearsal"
)
PACKET_PATH = CONTINUITY_DIR / "reference-only-packet.json"
FULL_GIT_OBJECT = re.compile(r"^[0-9a-f]{40}$")
RESULT = (
    "raisa_provider_free_unmounted_canonical_check_in_reference_only_"
    "operational_evidence_conformance_packet_rehearsal_pass"
)

EXPECTED_HOSTILE_REASONS = (
    ("manifest_absent", "manifest_absent", "ordinary_evidence_missing"),
    ("manifest_ambiguous", "manifest_ambiguous", "ordinary_evidence_missing"),
    ("manifest_secret_material", "manifest_invalid", "ordinary_evidence_missing"),
    ("evidence_boolean_claim", "role_evidence_invalid", "ordinary_evidence_missing"),
    ("manifest_stale", "manifest_stale", "ordinary_evidence_missing"),
    ("wrong_environment", "environment_mismatch", "ordinary_evidence_missing"),
    ("wrong_role", "role_binding_missing", "ordinary_evidence_missing"),
    ("self_verified_role", "role_evidence_invalid", "ordinary_evidence_missing"),
    (
        "duplicate_evidence_reference",
        "rotation_evidence_invalid",
        "ordinary_evidence_missing",
    ),
    ("rotation_key_mismatch", "secret_reference_invalid", "ordinary_evidence_missing"),
    (
        "break_glass_engaged",
        "break_glass_not_inactive",
        "ordinary_evidence_missing",
    ),
    (
        "snapshot_binding_mismatch",
        "evidence_gate_satisfied",
        "ordinary_evidence_missing",
    ),
)


class RehearsalFailure(ValueError):
    """Raised when the accepted components do not produce the frozen reading."""


def _load_packet() -> tuple[dict[str, Any], bytes]:
    raw = PACKET_PATH.read_bytes()
    value = json.loads(raw.decode("utf-8"))
    if type(value) is not dict:
        raise RehearsalFailure("packet_root_invalid")
    return value, raw


def _packet_digest(packet: dict[str, Any], raw: bytes | None) -> str:
    payload = (
        raw
        if raw is not None
        else (json.dumps(packet, sort_keys=True, separators=(",", ":")) + "\n").encode(
            "utf-8"
        )
    )
    return hashlib.sha256(payload).hexdigest()


def _manifest_bytes(manifest: dict[str, Any]) -> bytes:
    return yaml.safe_dump(
        manifest,
        allow_unicode=True,
        sort_keys=False,
    ).encode("utf-8")


def _normalize_manifest(manifest: dict[str, Any]) -> ManifestNormalizationResult:
    return normalize_check_in_environment_manifest(_manifest_bytes(manifest))


def _normalize_evidence(
    evidence: dict[str, Any],
) -> OperationalEvidenceInputNormalizationResult:
    return normalize_check_in_operational_evidence_inputs(evidence)


def _evaluation_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise RehearsalFailure("evaluation_time_invalid")
    return parsed


def _admission_inputs(
    packet: dict[str, Any],
    *,
    manifest_digest: str,
) -> tuple[AdmissionSnapshot, AdmissionRequest]:
    admission = packet["admission"]
    snapshot_value = admission["snapshot"]
    record_value = snapshot_value["ordinary_record"]
    record = OrdinaryAdmissionRecord(
        state=AdmissionState(record_value["state"]),
        practice_id=record_value["practice_id"],
        environment=record_value["environment"],
        operation_family=record_value["operation_family"],
        record_version=record_value["record_version"],
        snapshot_generation=record_value["snapshot_generation"],
        operational_evidence_valid=record_value["operational_evidence_valid"],
    )
    snapshot = AdmissionSnapshot(
        schema_version=snapshot_value["schema_version"],
        signature_valid=snapshot_value["signature_valid"],
        authority_git_object=snapshot_value["authority_git_object"],
        authority_git_object_resolved=snapshot_value["authority_git_object_resolved"],
        fresh=snapshot_value["fresh"],
        environment=snapshot_value["environment"],
        snapshot_generation=snapshot_value["snapshot_generation"],
        snapshot_digest=snapshot_value["snapshot_digest"],
        current_record_count=snapshot_value["current_record_count"],
        kill_switch=KillSwitchState(snapshot_value["kill_switch"]),
        ordinary_record=record,
        environment_evidence_identifier=snapshot_value[
            "environment_evidence_identifier"
        ],
        environment_evidence_manifest_digest=manifest_digest,
    )
    request_value = admission["request"]
    request = AdmissionRequest(
        feature_enabled=request_value["feature_enabled"],
        authored_synthetic_admitted=request_value["authored_synthetic_admitted"],
        practice_id=request_value["practice_id"],
        environment=request_value["environment"],
        operation_family=request_value["operation_family"],
    )
    return snapshot, request


def _decision_reading(
    packet: dict[str, Any],
    gate_reading: EnvironmentEvidenceGateReading,
    *,
    manifest_digest: str,
) -> dict[str, Any]:
    snapshot, request = _admission_inputs(packet, manifest_digest=manifest_digest)
    base = evaluate_admission(snapshot, request)
    composed = evaluate_admission_with_environment_evidence(
        snapshot,
        request,
        gate_reading,
    )
    return {
        "base_admission_reason": base.reason_code.value,
        "decision": composed.decision.value,
        "lane": composed.lane.value,
        "reason": composed.reason_code.value,
        "admission_released": composed.admitted,
        "ordinary_admission_released": (
            composed.admitted and composed.lane.value == "ordinary_practice"
        ),
    }


def _canonical_reading(packet: dict[str, Any]) -> tuple[dict[str, Any], str]:
    manifest_result = _normalize_manifest(deepcopy(packet["manifest"]))
    evidence_result = _normalize_evidence(deepcopy(packet["operational_evidence"]))
    gate = evaluate_check_in_environment_evidence_gate(
        (manifest_result,),
        evidence_result,
        evaluation_time=_evaluation_time(packet["evaluation_time"]),
    )
    if manifest_result.manifest_digest is None:
        raise RehearsalFailure("canonical_manifest_digest_absent")
    decision = _decision_reading(
        packet,
        gate,
        manifest_digest=manifest_result.manifest_digest,
    )
    return (
        {
            "manifest_reason": manifest_result.reason_code,
            "evidence_input_reason": evidence_result.reason_code,
            "evidence_gate_reason": gate.reason_code,
            **decision,
        },
        manifest_result.manifest_digest,
    )


def _hostile_reading(
    packet: dict[str, Any],
    case_id: str,
    *,
    canonical_manifest_digest: str,
) -> dict[str, Any]:
    manifest = deepcopy(packet["manifest"])
    evidence = deepcopy(packet["operational_evidence"])
    evaluation_time = packet["evaluation_time"]
    manifest_results: tuple[ManifestNormalizationResult, ...]

    if case_id == "manifest_absent":
        manifest_results = ()
        manifest_reason = "not_selected"
    elif case_id == "manifest_ambiguous":
        normalized = _normalize_manifest(manifest)
        manifest_results = (normalized, normalized)
        manifest_reason = normalized.reason_code
    elif case_id == "manifest_secret_material":
        manifest["secret_references"][0]["secret_value"] = (
            "synthetic-forbidden-marker"
        )
        normalized = _normalize_manifest(manifest)
        manifest_results = (normalized,)
        manifest_reason = normalized.reason_code
    else:
        if case_id == "manifest_stale":
            evaluation_time = "2026-11-01T00:00:00Z"
        elif case_id == "wrong_environment":
            evidence["role_attestation"]["environment_identifier"] = (
                "env:wrong-reference"
            )
        elif case_id == "wrong_role":
            evidence["role_attestation"]["database_role_identifier"] = (
                "other_runtime"
            )
        elif case_id == "self_verified_role":
            evidence["role_attestation"]["independent_verifier_reference"] = (
                evidence["role_attestation"]["evidence_reference"]
            )
        elif case_id == "duplicate_evidence_reference":
            duplicate = manifest["rotation_evidence"][0]["evidence_reference"]
            manifest["secret_references"][1]["rotation_evidence_reference"] = duplicate
            manifest["rotation_evidence"][1]["evidence_reference"] = duplicate
            evidence["rotation_custody_attestations"][1][
                "evidence_reference"
            ] = duplicate
        elif case_id == "rotation_key_mismatch":
            evidence["rotation_custody_attestations"][1]["key_id"] = "other-key"
        elif case_id == "break_glass_engaged":
            manifest["break_glass"]["state"] = "engaged_deny"
            evidence["break_glass_evidence"]["state"] = "engaged_deny"
        elif case_id == "snapshot_binding_mismatch":
            pass
        elif case_id != "evidence_boolean_claim":
            raise RehearsalFailure(f"unknown_hostile_case:{case_id}")
        normalized = _normalize_manifest(manifest)
        manifest_results = (normalized,)
        manifest_reason = normalized.reason_code

    if case_id == "evidence_boolean_claim":
        evidence["role_attestation"]["ownership_observation"] = True
    evidence_result = _normalize_evidence(evidence)
    gate = evaluate_check_in_environment_evidence_gate(
        manifest_results,
        evidence_result,
        evaluation_time=_evaluation_time(evaluation_time),
    )
    selected_digest = canonical_manifest_digest
    if (
        len(manifest_results) == 1
        and manifest_results[0].manifest_digest is not None
    ):
        selected_digest = manifest_results[0].manifest_digest
    if case_id == "snapshot_binding_mismatch":
        selected_digest = "f" * 64
    decision = _decision_reading(
        packet,
        gate,
        manifest_digest=selected_digest,
    )
    return {
        "id": case_id,
        "manifest_reason": manifest_reason,
        "evidence_input_reason": evidence_result.reason_code,
        "evidence_gate_reason": gate.reason_code,
        **decision,
        "external_fact_count": 0,
    }


def _validate_reading(reading: dict[str, Any]) -> None:
    canonical = reading["canonical_path"]
    expected_canonical = {
        "manifest_reason": "manifest_normalized",
        "evidence_input_reason": "evidence_inputs_normalized",
        "evidence_gate_reason": "evidence_gate_satisfied",
        "base_admission_reason": "ordinary_activation_closed",
        "decision": "denied",
        "lane": "ordinary_practice",
        "reason": "ordinary_activation_closed",
        "admission_released": False,
        "ordinary_admission_released": False,
    }
    if canonical != expected_canonical:
        raise RehearsalFailure("canonical_path_mismatch")

    actual_hostile = tuple(
        (case["id"], case["evidence_gate_reason"], case["reason"])
        for case in reading["hostile_cases"]
    )
    if actual_hostile != EXPECTED_HOSTILE_REASONS:
        raise RehearsalFailure("hostile_matrix_mismatch")
    if any(
        case["admission_released"]
        or case["ordinary_admission_released"]
        or case["external_fact_count"] != 0
        or case["base_admission_reason"] != "ordinary_activation_closed"
        for case in reading["hostile_cases"]
    ):
        raise RehearsalFailure("hostile_case_released_authority")
    if reading["readiness"] != {
        "blocking_gap": 0,
        "operational_evidence_gap": 1,
        "repository_prerequisites_remaining": 0,
        "satisfied": 11,
        "verdict": "not_ready_for_ordinary_practice_admission",
    }:
        raise RehearsalFailure("readiness_mismatch")
    if len(reading["external_facts"]) != 6 or any(
        item["status"] != "absent" for item in reading["external_facts"]
    ):
        raise RehearsalFailure("external_fact_boundary_mismatch")
    if len(reading["human_choices"]) != 5 or any(
        item["status"] != "unselected" for item in reading["human_choices"]
    ):
        raise RehearsalFailure("human_choice_boundary_mismatch")


def run_rehearsal(
    *,
    candidate_source: str,
    packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return one deterministic evidence reading without writing or side effects."""

    if FULL_GIT_OBJECT.fullmatch(candidate_source) is None:
        raise RehearsalFailure("candidate_source_not_full_git_object")
    raw: bytes | None = None
    if packet is None:
        loaded, raw = _load_packet()
        packet = loaded
    elif type(packet) is not dict:
        raise RehearsalFailure("packet_root_invalid")
    original = deepcopy(packet)
    digest_before = _packet_digest(packet, raw)
    canonical, manifest_digest = _canonical_reading(packet)
    hostile_cases = [
        _hostile_reading(
            packet,
            case_id,
            canonical_manifest_digest=manifest_digest,
        )
        for case_id, _gate_reason, _admission_reason in EXPECTED_HOSTILE_REASONS
    ]
    digest_after = _packet_digest(packet, PACKET_PATH.read_bytes() if raw else None)
    unchanged = packet == original and digest_before == digest_after
    reading = {
        "schema_version": "raisa.check_in_reference_only_conformance_evidence.v1",
        "result": RESULT,
        "candidate_source": candidate_source,
        "packet": {
            "classification": packet["classification"],
            "sha256": digest_before,
            "unchanged": unchanged,
            "operational_fact_status": packet["operational_fact_status"],
            "secret_material_count": 0,
            "resolved_reference_count": 0,
            "external_fact_count": 0,
        },
        "canonical_path": canonical,
        "hostile_cases": hostile_cases,
        "counts": {
            "hostile_cases": len(hostile_cases),
            "admission_releases": 0,
            "ordinary_admission_releases": 0,
            "provider_calls": 0,
            "product_data_records": 0,
            "external_facts_established": 0,
            "human_choices_selected": 0,
        },
        "readiness": {
            "satisfied": packet["readiness"]["satisfied"],
            "blocking_gap": packet["readiness"]["blocking_gap"],
            "operational_evidence_gap": packet["readiness"][
                "operational_evidence_gap"
            ],
            "verdict": packet["readiness"]["verdict"],
            "repository_prerequisites_remaining": packet["readiness"][
                "repository_prerequisites_remaining_after_pass"
            ],
        },
        "external_facts": [
            {"id": item, "status": "absent"}
            for item in packet["external_fact_ids"]
        ],
        "human_choices": [
            {"id": item, "status": "unselected"}
            for item in packet["human_choice_ids"]
        ],
        "api_spine": {
            "boundary": "declarative_manifest_and_default_off_admission_reading",
            "graphql_mutation_added": False,
            "rest_command_added_or_changed": False,
            "runtime_authority_added": False,
        },
        "effects": {
            "feature_flag_changed": False,
            "authored_synthetic_allowlist_changed": False,
            "ordinary_practice_enabled": False,
            "admission_record_activated": False,
            "generic_status_arrived_changed": False,
            "waiting_area_changed": False,
            "product_source_changed": False,
            "deployment_or_release": False,
            "protected_ref_changed": False,
        },
    }
    if not unchanged:
        raise RehearsalFailure("packet_mutated")
    _validate_reading(reading)
    return reading


def render_report(reading: dict[str, Any]) -> str:
    """Render the deterministic evidence as a concise Markdown report."""

    lines = [
        "# Canonical check-in reference-only conformance packet report",
        "",
        f"Result: `{reading['result']}`",
        "",
        "The authored-synthetic packet normalized and satisfied the evidence gate,",
        "then remained denied at `ordinary_activation_closed`. It established no",
        "operational fact and released no ordinary-practice admission.",
        "",
        "| Hostile case | Evidence-gate reason | Admission reason |",
        "|---|---|---|",
    ]
    lines.extend(
        f"| `{case['id']}` | `{case['evidence_gate_reason']}` | `{case['reason']}` |"
        for case in reading["hostile_cases"]
    )
    lines.extend(
        [
            "",
            "Readiness remains exactly 11 satisfied / 0 blocking / 1 operational",
            "evidence gap. Six external facts remain absent and five human choices",
            "remain unselected. No API, route, product, provider, runtime, deployment",
            "or protected-ref surface changed.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-source", required=True)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    args = parser.parse_args()
    try:
        reading = run_rehearsal(candidate_source=args.candidate_source)
    except (OSError, UnicodeError, json.JSONDecodeError, RehearsalFailure) as error:
        print(json.dumps({"result": "failed_closed", "reason": str(error)}))
        return 2
    if args.format == "json":
        print(json.dumps(reading, indent=2, sort_keys=True))
    else:
        print(render_report(reading), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
