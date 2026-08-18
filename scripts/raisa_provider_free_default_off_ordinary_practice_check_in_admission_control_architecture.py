"""Validate the source-bound default-off check-in admission-control architecture."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterator

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture"
)
CONTRACT_PATH = CONTRACT_DIR / "contract.json"
SCHEMA_PATH = CONTRACT_DIR / "contract.schema.json"

EXPECTED_SOURCE_HEAD = "062f5fb12eb82eab6ec570abea56ad1bd9a7b304"
EXPECTED_READINESS_SOURCE = "27101faa86b5aa3850e90bc4ded8600e5f8d7dc9"
EXPECTED_ROUTE_SOURCE = "c82c3a741053a9c8da260aa62e1a968af22bb54e"
EXPECTED_CONTRACT_DIGEST = "51ba39390b56672e982a6dd85b4dfb939c31d19a7962ce7124cf076760134bfb"
EXPECTED_SOURCES = {
    "app/config.py": "f0cafc21a88babd0d60d6ce30067a30d23b4030ad5dd4d26bb841096c62c1f2e",
    "app/routers/appointments.py": "8443bc1d045672f05567a5cb6443a882dfda4946791412c231ce475995f71d08",
    "app/services/appointment_check_in_product_adapter.py": "ef6abdfef1b99737c527790be007ab07296bbc0422197858a5ae561012230570",
    "docs/api-spine/openapi/appointment-commands.yaml": "0dfbce13f3d8933d0cd2355fb41e70612c1550e75c452b95c1528576ac1c8622",
    "orchestration/api_spine_adr.md": "d0fa77aec371d634284f81bf1fd6cfd49bb5a52fbe14003a17c5e35dcaf0283e",
    "orchestration/api_spine_programme.md": "5532f9ccc0efc326d34bc0d33f9f650d3f5322f8f4b22271fc8970b0dad31946",
    "docs/raisa-provider-free-read-only-ordinary-practice-canonical-check-in-admission-readiness-review-plan.md": "3bffad89188d3f700e769d4d39301b8f440d763b21d0e4b7c64fe67354ed78ba",
    "orchestration/continuity/raisa-provider-free-read-only-ordinary-practice-canonical-check-in-admission-readiness-review/admission-readiness-review-report.md": "81a4a92e4f1f7e539282a646d59474420309f2f93785fe2c007e413ef26c297f",
    "docs/raisa-provider-free-read-only-ordinary-practice-canonical-check-in-admission-readiness-review-closeout.md": "335c82727662a408305e18954bc2927d724e8e312182af5b1ca0d4b32d32d3e8",
    "orchestration/agent_inbox/codex/raisa-ordinary-practice-check-in-admission-readiness-review-sol-acceptance.md": "584756f6723e0e699c4dd9ffc7d504b3d7b5cea8dd1f735c63e3e13aef31af53",
    "docs/ariadne-transactional-closeout-control-plane-consolidation-efficacy-rehearsal-closeout.md": "e577f20e1b164be1abce990f915bd792eb4e158051f48c5c1d629825cd93a78f",
}

EXPECTED_STATES = [
    {"state": "prepared", "admits": False, "terminal": False},
    {"state": "active", "admits": True, "terminal": False},
    {"state": "suspended", "admits": False, "terminal": False},
    {"state": "withdrawn", "admits": False, "terminal": True},
]
EXPECTED_ALLOWED_TRANSITIONS = [
    "absent->prepared",
    "prepared->active",
    "prepared->withdrawn",
    "active->suspended",
    "active->withdrawn",
    "suspended->withdrawn",
]
EXPECTED_FORBIDDEN_TRANSITIONS = [
    "absent->active",
    "active->prepared",
    "suspended->active",
    "withdrawn->active",
    "withdrawn->prepared",
    "rollback->active",
    "kill_switch_engaged->clear",
]
EXPECTED_DECISION_STEPS = [
    "validate_snapshot_shape_signature_resolution_freshness_and_uniqueness",
    "deny_unless_existing_feature_flag_exact_true",
    "deny_if_global_kill_switch_engaged",
    "compute_synthetic_and_ordinary_lane_matches_independently",
    "deny_if_both_lanes_match",
    "preserve_unchanged_synthetic_result_when_only_synthetic_matches",
    "require_one_exact_active_ordinary_record_when_only_ordinary_matches",
    "require_all_current_operational_evidence_for_ordinary",
    "return_typed_decision_without_command_capability",
]
EXPECTED_OPERATIONS = [
    "prepareAppointmentCheckInAdmission",
    "activateAppointmentCheckInAdmission",
    "suspendAppointmentCheckInAdmission",
    "withdrawAppointmentCheckInAdmission",
    "engageAppointmentCheckInGlobalKillSwitch",
]
EXPECTED_COMMAND_REQUIREMENTS = [
    "authenticated_current_human",
    "separate_check_in_admission_operator_role",
    "server_owned_practice_scope",
    "server_owned_environment_scope",
    "correlation_id",
    "idempotency_key_bound_to_complete_request_digest",
    "expected_record_version",
    "expected_snapshot_generation",
    "closed_reason_code",
    "authority_git_object_full_40",
    "authority_git_object_resolved",
    "freshness",
    "append_only_audit",
    "bounded_patient_free_receipt",
]
EXPECTED_EVIDENCE_GATES = [
    "tenant_runtime_role",
    "rollback_and_unknown_commit",
    "environment_and_secret_posture",
]
EXPECTED_METRICS = [
    "emr4_check_in_admission_decisions_total",
    "emr4_check_in_admission_snapshot_age_seconds",
    "emr4_check_in_admission_kill_switch",
    "emr4_check_in_unknown_commit_total",
    "emr4_check_in_control_commands_total",
]
EXPECTED_ALERTS = [
    "check_in_kill_switch_engaged",
    "check_in_admission_snapshot_invalid_or_stale",
    "check_in_unknown_commit",
    "check_in_active_record_rejected",
    "check_in_control_audit_failure",
    "check_in_rollback_failure",
]
FORBIDDEN_TELEMETRY_FIELDS = {
    "practice_id",
    "appointment_id",
    "patient_id",
    "practitioner_id",
    "user_id",
    "actor_id",
    "correlation_id",
    "idempotency_key",
    "command_id",
    "record_id",
    "evidence_digest",
    "token",
    "free_text",
    "request_body",
    "response_body",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_contract() -> dict[str, Any]:
    return _load(CONTRACT_PATH)


def load_schema() -> dict[str, Any]:
    return _load(SCHEMA_PATH)


def _canonical_json_digest(value: dict[str, Any]) -> str:
    material = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def _canonical_source_digest(path: Path) -> str:
    text = path.read_bytes().decode("utf-8", errors="strict")
    text = text.replace("\r\n", "\n")
    if "\r" in text:
        raise ValueError("bare CR is forbidden")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def source_errors(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    bindings = {row["path"]: row["sha256"] for row in packet["source_bindings"]}
    if bindings != EXPECTED_SOURCES:
        errors.append("source_bindings_mismatch")
        return errors
    for relative_path, expected_digest in EXPECTED_SOURCES.items():
        source = ROOT / relative_path
        if not source.is_file():
            errors.append(f"source_missing:{relative_path}")
            continue
        try:
            actual_digest = _canonical_source_digest(source)
        except (UnicodeDecodeError, ValueError):
            errors.append(f"source_not_canonical_utf8_lf:{relative_path}")
            continue
        if actual_digest != expected_digest:
            errors.append(f"source_hash_mismatch:{relative_path}")
    return errors


def _operation_ids(packet: dict[str, Any]) -> list[str]:
    return [row["operation_id"] for row in packet["control_plane"]["operations"]]


def semantic_errors(
    packet: dict[str, Any],
    *,
    verify_source_files: bool = False,
) -> list[str]:
    errors: list[str] = []
    if packet.get("source_head") != EXPECTED_SOURCE_HEAD:
        errors.append("source_head_mismatch")
    if packet.get("accepted_readiness_source") != EXPECTED_READINESS_SOURCE:
        errors.append("readiness_source_mismatch")
    if packet.get("accepted_route_source") != EXPECTED_ROUTE_SOURCE:
        errors.append("route_source_mismatch")
    if _canonical_json_digest(packet) != EXPECTED_CONTRACT_DIGEST:
        errors.append("contract_digest_mismatch")
    if verify_source_files:
        errors.extend(source_errors(packet))

    posture = packet["current_posture"]
    if posture != {
        "feature_setting": "rayleen_a5_check_in_enabled",
        "feature_default": False,
        "synthetic_allowlist_setting": "rayleen_a5_check_in_synthetic_practice_ids",
        "synthetic_allowlist_default": [],
        "ordinary_admission_setting_present": False,
        "ordinary_admission_records_present": False,
        "current_gate_order": [
            "feature_enabled_exact_true",
            "authenticated_practice_in_exact_authored_synthetic_allowlist",
        ],
        "proposal_operation_id": "proposeAppointmentCheckIn",
        "confirmation_operation_id": "confirmAppointmentCheckInProposal",
        "product_source_changed": False,
        "configuration_changed": False,
        "openapi_changed": False,
        "practice_enabled": False,
    }:
        errors.append("current_posture_mismatch")

    lanes = packet["admission_lanes"]
    if (
        lanes["synthetic"]["ordinary_authority"]
        or lanes["synthetic"]["may_infer_ordinary_record"]
        or lanes["ordinary"]["caller_claim_allowed"]
        or lanes["ordinary"]["synthetic_receipt_substitution_allowed"]
        or lanes["ordinary"]["default_when_absent"] != "denied"
        or lanes["both_lanes_match"] != "deny_lane_ambiguity"
        or lanes["neither_lane_matches"] != "deny_no_admission"
        or lanes["cross_lane_fallback"]
    ):
        errors.append("lane_separation_or_default_denial_open")

    state_machine = packet["ordinary_state_machine"]
    if state_machine["states"] != EXPECTED_STATES:
        errors.append("state_set_mismatch")
    if state_machine["allowed_transitions"] != EXPECTED_ALLOWED_TRANSITIONS:
        errors.append("allowed_transition_mismatch")
    if state_machine["forbidden_transitions"] != EXPECTED_FORBIDDEN_TRANSITIONS:
        errors.append("forbidden_transition_mismatch")
    if (
        state_machine["resume_transition_present"]
        or not state_machine["reactivation_requires_new_record"]
        or state_machine["activation_authority_granted"]
    ):
        errors.append("unsafe_reactivation_or_authority")

    evaluator = packet["decision_evaluator"]
    if evaluator["ordered_steps"] != EXPECTED_DECISION_STEPS:
        errors.append("decision_order_mismatch")
    if not evaluator["kill_switch_dominates_synthetic"]:
        errors.append("kill_switch_not_dominant_for_synthetic")
    if not evaluator["kill_switch_dominates_ordinary"]:
        errors.append("kill_switch_not_dominant_for_ordinary")
    if evaluator["unknown_or_extra_state"] != "deny":
        errors.append("unknown_state_not_denied")
    if evaluator["multiple_current_records_behavior"] != "deny":
        errors.append("multiple_records_not_denied")
    if any(
        evaluator[field]
        for field in (
            "executes_check_in",
            "creates_confirmation_evidence",
            "changes_authentication_or_role",
        )
    ):
        errors.append("evaluator_has_command_capability")

    spine = packet["api_spine"]
    if (
        spine["state_change_transport"] != "rest_openapi_only"
        or spine["graphql_posture"] != "read_only_posture_projection_only"
        or spine["async_event_posture"] != "observation_only_never_authority"
        or spine["current_manifest_changed"]
        or spine["candidate_control_operations_unmounted"] != EXPECTED_OPERATIONS
        or spine["model_or_agent_write_authority"]
        or spine["committed_event_write_authority"]
    ):
        errors.append("api_spine_boundary_mismatch")

    control = packet["control_plane"]
    if _operation_ids(packet) != EXPECTED_OPERATIONS:
        errors.append("control_operation_order_mismatch")
    if control["command_requirements"] != EXPECTED_COMMAND_REQUIREMENTS:
        errors.append("command_requirements_mismatch")
    if control["authority_git_object_pattern"] != "^[0-9a-f]{40}$":
        errors.append("git_object_pattern_mismatch")
    if re.fullmatch(control["authority_git_object_pattern"], EXPECTED_SOURCE_HEAD) is None:
        errors.append("full_git_object_pattern_does_not_match")
    if re.fullmatch(control["authority_git_object_pattern"], EXPECTED_SOURCE_HEAD[:7]):
        errors.append("abbreviated_git_object_matches")
    if (
        control["abbreviated_git_object_allowed"]
        or not control["human_authority_required"]
        or control["receptionist_role_is_activation_authority"]
        or control["model_authority_allowed"]
        or any(row["authorized_now"] for row in control["operations"])
    ):
        errors.append("control_authority_open")

    switch = packet["global_kill_switch"]
    if switch != {
        "default_state": "clear",
        "engage_transition": "clear->engaged",
        "clear_in_place_allowed": False,
        "engaged_effect": "deny_both_lanes",
        "monotonic_within_generation": True,
        "new_generation_required_to_clear": True,
        "automatic_clear_allowed": False,
    }:
        errors.append("kill_switch_mismatch")

    rollback = packet["rollback"]
    if (
        rollback["operation_id"] != "withdrawAppointmentCheckInAdmission"
        or not rollback["disable_only"]
        or rollback["terminal_state"] != "withdrawn"
        or rollback["restore_active_version_allowed"]
        or rollback["retry_after_unknown_commit_allowed"]
        or not rollback["readback_required_after_unknown_commit"]
        or not rollback["audit_required"]
    ):
        errors.append("rollback_not_disable_only")

    evidence = packet["operational_evidence"]
    if [row["gate_id"] for row in evidence["gates"]] != EXPECTED_EVIDENCE_GATES:
        errors.append("operational_evidence_gate_mismatch")
    if (
        not evidence["required_for_active"]
        or evidence["authored_synthetic_substitution_allowed"]
        or evidence["missing_invalid_stale_or_wrong_generation"] != "deny"
        or "full_40_character_resolved_git_object"
        not in evidence["artifact_requirements"]
    ):
        errors.append("operational_evidence_not_mandatory")

    observability = packet["observability"]
    if [row["name"] for row in observability["metric_families"]] != EXPECTED_METRICS:
        errors.append("metric_family_mismatch")
    if [row["alert_id"] for row in observability["alerts"]] != EXPECTED_ALERTS:
        errors.append("alert_set_mismatch")
    if not FORBIDDEN_TELEMETRY_FIELDS.issubset(
        set(observability["forbidden_labels_and_values"])
    ):
        errors.append("forbidden_telemetry_fields_missing")
    if any(
        row["automatic_control_action"] or row["contains_identifier"]
        for row in observability["alerts"]
    ):
        errors.append("alert_control_or_identifier_open")
    if any(
        observability[field]
        for field in (
            "raw_request_or_response_allowed",
            "audit_record_used_as_metric",
            "telemetry_feedback_to_admission",
            "automatic_retry_or_control_action",
        )
    ):
        errors.append("observability_feedback_or_data_open")

    clockwork = packet["clockwork_boundary"]
    if (
        clockwork["full_git_oid_pattern"] != "^[0-9a-f]{40}$"
        or clockwork["manual_git_abbreviation_accepted"]
        or clockwork["ariadne_deepseek_shared_clock_status"] != "accepted_shadow_only"
        or clockwork["deepseek_broker_binding"]
        != "protocol_conformance_only_no_product_or_activation_authority"
        or clockwork["live_clockwork_adoption_authorized"]
        or clockwork["existing_control_retirement_authorized"]
    ):
        errors.append("clockwork_authority_or_git_shape_open")

    if any(packet["closed_boundaries"].values()):
        errors.append("closed_boundary_open")
    successor = packet["successor"]
    if (
        successor["ordinary_enablement_authorized"]
        or successor["operational_evidence_gaps_closed"]
        or successor["operation_id"]
        != "raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-check-in-admission-control-kernel-rehearsal"
    ):
        errors.append("successor_scope_open")
    return errors


def validate_contract(
    packet: dict[str, Any],
    *,
    verify_source_files: bool = False,
) -> list[str]:
    errors: list[str] = []
    schema = load_schema()
    for error in Draft202012Validator(schema).iter_errors(packet):
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        errors.append(f"schema:{location}:{error.validator}")
    if errors:
        return sorted(set(errors))
    errors.extend(semantic_errors(packet, verify_source_files=verify_source_files))
    return sorted(set(errors))


def _scalar_paths(value: Any, prefix: tuple[Any, ...] = ()) -> Iterator[tuple[Any, ...]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _scalar_paths(child, (*prefix, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _scalar_paths(child, (*prefix, index))
    elif isinstance(value, (str, bool, int, float)) or value is None:
        yield prefix


def _mutate_scalar(value: Any) -> Any:
    if isinstance(value, bool):
        return not value
    if isinstance(value, str):
        return value + "__hostile"
    if isinstance(value, int):
        return value + 1
    if isinstance(value, float):
        return value + 1.0
    return "hostile_not_null"


def _get_at_path(value: Any, path: tuple[Any, ...]) -> Any:
    cursor = value
    for part in path:
        cursor = cursor[part]
    return cursor


def _set_at_path(value: Any, path: tuple[Any, ...], replacement: Any) -> None:
    cursor = value
    for part in path[:-1]:
        cursor = cursor[part]
    cursor[path[-1]] = replacement


def hostile_mutations(packet: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    mutations: list[tuple[str, dict[str, Any]]] = []
    for index, path in enumerate(_scalar_paths(packet)):
        candidate = copy.deepcopy(packet)
        _set_at_path(candidate, path, _mutate_scalar(_get_at_path(candidate, path)))
        label = "/".join(str(part) for part in path)
        mutations.append((f"scalar_{index:03d}:{label}", candidate))

    for key in (
        "current_posture",
        "admission_lanes",
        "ordinary_state_machine",
        "decision_evaluator",
        "api_spine",
        "control_plane",
        "global_kill_switch",
        "rollback",
        "operational_evidence",
        "observability",
        "clockwork_boundary",
        "closed_boundaries",
        "successor",
    ):
        candidate = copy.deepcopy(packet)
        candidate[key]["unexpected_hostile_field"] = True
        mutations.append((f"extra_field:{key}", candidate))
    return mutations


def build_report(packet: dict[str, Any] | None = None) -> dict[str, Any]:
    packet = load_contract() if packet is None else packet
    errors = validate_contract(packet, verify_source_files=True)
    mutants = hostile_mutations(packet)
    escaped = [
        name for name, mutant in mutants if not validate_contract(mutant)
    ]
    if escaped:
        errors.append("hostile_mutation_escaped:" + ",".join(escaped))
    return {
        "schema_version": "emr4.check-in-admission-control-architecture-report.v1",
        "status": "passed" if not errors else "failed",
        "reasons": sorted(set(errors)),
        "source_head": packet["source_head"],
        "source_binding_count": len(packet["source_bindings"]),
        "state_count": len(packet["ordinary_state_machine"]["states"]),
        "allowed_transition_count": len(
            packet["ordinary_state_machine"]["allowed_transitions"]
        ),
        "control_operation_count": len(packet["control_plane"]["operations"]),
        "operational_evidence_gate_count": len(
            packet["operational_evidence"]["gates"]
        ),
        "metric_family_count": len(packet["observability"]["metric_families"]),
        "alert_count": len(packet["observability"]["alerts"]),
        "hostile_mutation_count": len(mutants),
        "hostile_mutation_escape_count": len(escaped),
        "ordinary_practice_enabled": packet["closed_boundaries"][
            "ordinary_practice_enabled"
        ],
        "application_or_configuration_changed": (
            packet["closed_boundaries"]["product_code_changed"]
            or packet["closed_boundaries"]["configuration_changed"]
        ),
        "provider_or_network_used": packet["closed_boundaries"][
            "provider_or_network_used"
        ],
        "live_clockwork_adopted": packet["closed_boundaries"][
            "live_clockwork_adopted"
        ],
    }


def main() -> int:
    report = build_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
