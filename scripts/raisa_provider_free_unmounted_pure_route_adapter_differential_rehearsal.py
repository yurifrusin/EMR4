"""Validate and exercise the inert pure route-adapter differential contract."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal"
)
CONTRACT_PATH = CONTRACT_DIR / "contract.json"
SCHEMA_PATH = CONTRACT_DIR / "contract.schema.json"
PARENT_CONTRACT_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface"
    / "contract.json"
)

EXPECTED_SOURCE_HEAD = "a433eb68b5c40dd61fb4b6cf23c9af09cb0270ef"
EXPECTED_SOURCES = {
    "orchestration/continuity/raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface/contract.json": "4fd0062641fd8181cc4920e8b9708f379e4d9b8d6ab48c2092654ddb0f0b911d",
    "docs/raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface-plan.md": "3321764f4ea663b96c348167dbdb186c4af9c020d905104d0341b8fa7ba6ddd5",
    "docs/raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface-design.md": "73c3c6ca7c254b6c38000b16d829b1a5d731977d22a3b18c0ad379b584437292",
    "docs/raisa-provider-free-unmounted-conditional-command-admission-rehearsal-design.md": "ed84a15d101b3bc6cb616b6955d4054dc42d8e9827118f319ba9e4d72ebbea53",
    "orchestration/api_spine_adr.md": "d0fa77aec371d634284f81bf1fd6cfd49bb5a52fbe14003a17c5e35dcaf0283e",
}
EXPECTED_REQUIRED_FIELDS = [
    "schema_version",
    "canonical_operation_id",
    "route_adapter_id",
    "practice_id",
    "actor_id",
    "actor_role",
    "session_id",
    "purpose",
    "target_appointment_id",
    "conflict_domain_id",
    "command_digest",
    "precondition_version",
    "precondition_digest",
    "confirmation_mode",
    "confirmation_reference",
    "idempotency_key_digest",
    "canonicalization_version",
    "correlation_id",
]
EXPECTED_OUTCOMES = [
    "committed",
    "idempotent_replay",
    "stale_precondition",
    "schedule_conflict",
    "authority_revoked",
    "confirmation_required",
    "validation_rejected",
    "idempotency_conflict",
]
EXPECTED_PRECEDENCE = [
    "closed_structure_and_binding_admission",
    "current_authority_before_receipt_disclosure",
    "separate_confirmation_validation",
    "idempotency_replay_or_conflict",
    "source_and_conflict_domain_freshness",
    "current_schedule_and_domain_invariants",
    "atomic_mutation_audit_receipt_and_readback",
]
EXPECTED_LOCK_ORDER = [
    "practice",
    "schedule_domain",
    "appointment",
    "idempotency_record",
]
EXPECTED_GAP_CODES = [
    "backend_precondition_missing",
    "confirmation_evidence_missing",
    "idempotency_identity_missing",
]
EXPECTED_ADAPTERS = {
    "proposal_confirm_create": (
        "appointment_create",
        "confirm",
        "POST",
        "/api/v1/appointments/proposals/create/confirm",
        "confirmAppointmentCreateProposal",
        "preferred_confirm_ingress",
    ),
    "proposal_confirm_create_bernie": (
        "appointment_create",
        "confirm",
        "POST",
        "/api/v1/appointments/proposals/create/confirm-bernie",
        "confirmAppointmentCreateProposal",
        "preferred_confirm_ingress_variant",
    ),
    "proposal_confirm_update": (
        "appointment_update",
        "confirm",
        "POST",
        "/api/v1/appointments/proposals/update/confirm",
        "confirmAppointmentUpdateProposal",
        "preferred_confirm_ingress",
    ),
    "proposal_confirm_status": (
        "appointment_status",
        "confirm",
        "POST",
        "/api/v1/appointments/proposals/status-confirm",
        "confirmAppointmentStatusProposal",
        "preferred_confirm_ingress",
    ),
    "proposal_confirm_delete": (
        "appointment_delete",
        "confirm",
        "POST",
        "/api/v1/appointments/proposals/delete-confirm",
        "confirmAppointmentDeleteProposal",
        "preferred_confirm_ingress",
    ),
    "raw_compat_create": (
        "appointment_create",
        "raw",
        "POST",
        "/api/v1/appointments",
        "confirmAppointmentCreateProposal",
        "current_raw_not_kernel_eligible",
    ),
    "raw_compat_update": (
        "appointment_update",
        "raw",
        "PUT",
        "/api/v1/appointments/{appointment_id}",
        "confirmAppointmentUpdateProposal",
        "current_raw_not_kernel_eligible",
    ),
    "raw_compat_status": (
        "appointment_status",
        "raw",
        "PATCH",
        "/api/v1/appointments/{appointment_id}/status",
        "confirmAppointmentStatusProposal",
        "current_raw_not_kernel_eligible",
    ),
    "raw_compat_delete": (
        "appointment_delete",
        "raw",
        "DELETE",
        "/api/v1/appointments/{appointment_id}",
        "confirmAppointmentDeleteProposal",
        "current_raw_not_kernel_eligible",
    ),
}
EXPECTED_FAMILY_LOCKS = {
    "appointment_create": ["practice", "schedule_domain", "idempotency_record"],
    "appointment_update": EXPECTED_LOCK_ORDER,
    "appointment_status": ["practice", "appointment", "idempotency_record"],
    "appointment_delete": ["practice", "appointment", "idempotency_record"],
}
EXPECTED_SCENARIO_IDS = {f"rad-{number:03d}-" for number in range(1, 14)}

CONFIRM_TOP_LEVEL = {
    "principal",
    "command",
    "proposal_evidence",
    "confirmation",
    "idempotency",
    "correlation_id",
}
RAW_REQUIRED_TOP_LEVEL = {"request_context", "mutation", "correlation_id"}
RAW_OPTIONAL_TOP_LEVEL = {
    "conditional_controls",
    "confirmation_evidence",
    "command_identity",
}
NESTED_KEYS = {
    "principal": {"practice_id", "actor_id", "actor_role", "session_id", "purpose"},
    "request_context": {
        "practice_id",
        "actor_id",
        "actor_role",
        "session_id",
        "purpose",
    },
    "command": {
        "target_appointment_id",
        "conflict_domain_id",
        "command_digest",
    },
    "mutation": {
        "target_appointment_id",
        "conflict_domain_id",
        "command_digest",
    },
    "proposal_evidence": {"precondition_version", "precondition_digest"},
    "conditional_controls": {"precondition_version", "precondition_digest"},
    "confirmation": {"confirmation_mode", "confirmation_reference"},
    "confirmation_evidence": {"confirmation_mode", "confirmation_reference"},
    "idempotency": {"idempotency_key_digest", "canonicalization_version"},
    "command_identity": {"idempotency_key_digest", "canonicalization_version"},
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_contract() -> dict[str, Any]:
    return _load(CONTRACT_PATH)


def load_schema() -> dict[str, Any]:
    return _load(SCHEMA_PATH)


def _adapter_specs(packet: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["adapter_id"]: row for row in packet["adapter_specs"]}


def _intents(packet: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["intent_id"]: row for row in packet["authored_synthetic_intents"]}


def build_envelope(profile: str, intent: dict[str, Any]) -> dict[str, Any]:
    principal = {
        key: intent[key]
        for key in ("practice_id", "actor_id", "actor_role", "session_id", "purpose")
    }
    command = {
        key: intent[key]
        for key in (
            "target_appointment_id",
            "conflict_domain_id",
            "command_digest",
        )
    }
    precondition = {
        key: intent[key]
        for key in ("precondition_version", "precondition_digest")
    }
    confirmation = {
        key: intent[key]
        for key in ("confirmation_mode", "confirmation_reference")
    }
    idempotency = {
        key: intent[key]
        for key in ("idempotency_key_digest", "canonicalization_version")
    }
    if profile == "confirm_complete":
        return {
            "principal": principal,
            "command": command,
            "proposal_evidence": precondition,
            "confirmation": confirmation,
            "idempotency": idempotency,
            "correlation_id": intent["correlation_id"],
        }
    if profile == "raw_current":
        return {
            "request_context": principal,
            "mutation": command,
            "correlation_id": intent["correlation_id"],
        }
    if profile == "raw_future_complete":
        return {
            "request_context": principal,
            "mutation": command,
            "conditional_controls": precondition,
            "confirmation_evidence": confirmation,
            "command_identity": idempotency,
            "correlation_id": intent["correlation_id"],
        }
    raise ValueError(f"unknown envelope profile: {profile}")


def _deep_get(envelope: dict[str, Any], dotted_path: str) -> Any:
    value: Any = envelope
    for component in dotted_path.split("."):
        if not isinstance(value, dict) or component not in value:
            return None
        value = value[component]
    return value


def _structure_errors(envelope: dict[str, Any], input_shape: str) -> list[str]:
    if any(field in envelope for field in ("canonical_operation_id", "route_adapter_id")):
        return ["caller_authority_field_forbidden"]
    top_level = set(envelope)
    if input_shape == "confirm_envelope":
        if top_level != CONFIRM_TOP_LEVEL:
            return ["input_structure_invalid"]
    elif input_shape == "raw_envelope":
        if not RAW_REQUIRED_TOP_LEVEL <= top_level:
            return ["input_structure_invalid"]
        if not top_level <= RAW_REQUIRED_TOP_LEVEL | RAW_OPTIONAL_TOP_LEVEL:
            return ["input_structure_invalid"]
    else:
        return ["input_shape_unknown"]
    for section, expected_keys in NESTED_KEYS.items():
        if section in envelope:
            value = envelope[section]
            if not isinstance(value, dict) or set(value) != expected_keys:
                return ["input_structure_invalid"]
    return []


def adapt_envelope(
    packet: dict[str, Any], adapter_id: str, envelope: dict[str, Any]
) -> dict[str, Any]:
    spec = _adapter_specs(packet).get(adapter_id)
    if spec is None:
        return _rejection(["adapter_identity_unknown"])
    input_shape = "confirm_envelope" if spec["ingress_kind"] == "confirm" else "raw_envelope"
    structure_errors = _structure_errors(envelope, input_shape)
    if structure_errors:
        return _rejection(structure_errors)

    gaps: list[str] = []
    if input_shape == "raw_envelope":
        if "conditional_controls" not in envelope:
            gaps.append("backend_precondition_missing")
        if "confirmation_evidence" not in envelope:
            gaps.append("confirmation_evidence_missing")
        if "command_identity" not in envelope:
            gaps.append("idempotency_identity_missing")
    if gaps:
        return _rejection(sorted(gaps))

    field_map = packet["field_maps"][input_shape]
    candidate = {
        "schema_version": packet["kernel_binding"]["candidate_schema_version"],
        "canonical_operation_id": spec["canonical_operation_id"],
        "route_adapter_id": spec["adapter_id"],
    }
    candidate.update(
        {field: _deep_get(envelope, path) for field, path in field_map.items()}
    )
    if set(candidate) != set(packet["kernel_binding"]["required_fields"]):
        return _rejection(["kernel_candidate_shape_invalid"])
    if any(
        candidate[field] is None
        for field in EXPECTED_REQUIRED_FIELDS
        if field not in {"target_appointment_id", "conflict_domain_id"}
    ):
        return _rejection(["kernel_candidate_value_missing"])

    target = candidate["target_appointment_id"]
    conflict_domain = candidate["conflict_domain_id"]
    family = spec["family_id"]
    if family == "appointment_create":
        if target is not None or conflict_domain is None:
            return _rejection(["target_or_conflict_shape_invalid"])
    elif family == "appointment_update":
        if target is None or conflict_domain is None:
            return _rejection(["target_or_conflict_shape_invalid"])
    elif target is None or conflict_domain is not None:
        return _rejection(["target_or_conflict_shape_invalid"])

    return {
        "adapter_result": "candidate_mapped",
        "reason_codes": [],
        "kernel_candidate": candidate,
        "lock_plan": list(spec["lock_plan"]),
        "runtime_execution_authorized": False,
        "command_outcome": None,
        "effect_performed": False,
    }


def _rejection(reason_codes: list[str]) -> dict[str, Any]:
    return {
        "adapter_result": "adapter_rejected",
        "reason_codes": sorted(set(reason_codes)),
        "kernel_candidate": None,
        "lock_plan": None,
        "runtime_execution_authorized": False,
        "command_outcome": None,
        "effect_performed": False,
    }


def evaluate_scenario(
    packet: dict[str, Any], scenario: dict[str, Any]
) -> dict[str, Any]:
    intent = _intents(packet).get(scenario["intent_id"])
    if intent is None:
        return _rejection(["intent_identity_unknown"])
    envelope = build_envelope(scenario["envelope_profile"], intent)
    return adapt_envelope(packet, scenario["adapter_id"], envelope)


def semantic_projection(packet: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    excluded = set(packet["kernel_binding"]["provenance_only_fields"])
    return {key: value for key, value in candidate.items() if key not in excluded}


def semantic_errors(packet: dict[str, Any], *, verify_source_files: bool = False) -> list[str]:
    errors: list[str] = []
    if packet["source_head"] != EXPECTED_SOURCE_HEAD:
        errors.append("source_head_mismatch")
    bindings = {row["path"]: row["sha256"] for row in packet["source_bindings"]}
    if bindings != EXPECTED_SOURCES:
        errors.append("source_bindings_mismatch")
    if verify_source_files:
        for path, expected_hash in EXPECTED_SOURCES.items():
            source = ROOT / path
            if not source.is_file() or _file_hash(source) != expected_hash:
                errors.append(f"source_file_hash_mismatch:{path}")

    parent = _load(PARENT_CONTRACT_PATH)
    kernel = packet["kernel_binding"]
    if kernel["required_fields"] != EXPECTED_REQUIRED_FIELDS:
        errors.append("kernel_required_fields_mismatch")
    if kernel["required_fields"] != parent["kernel_interface"]["required_fields"]:
        errors.append("parent_required_fields_mismatch")
    if kernel["outcomes_preserved_but_not_evaluated"] != EXPECTED_OUTCOMES:
        errors.append("outcome_vocabulary_mismatch")
    if kernel["outcomes_preserved_but_not_evaluated"] != parent["kernel_interface"]["outcomes"]:
        errors.append("parent_outcome_vocabulary_mismatch")
    if kernel["precedence_preserved_but_not_evaluated"] != EXPECTED_PRECEDENCE:
        errors.append("precedence_mismatch")
    if kernel["canonical_lock_order"] != EXPECTED_LOCK_ORDER:
        errors.append("canonical_lock_order_mismatch")
    if kernel["provenance_only_fields"] != ["route_adapter_id"]:
        errors.append("provenance_exception_mismatch")
    if kernel["runtime_execution_authorized"] or kernel["command_outcome_emitted"]:
        errors.append("kernel_effect_boundary_open")

    profiles = packet["envelope_profiles"]
    if profiles["confirm_complete"]["input_shape"] != "confirm_envelope":
        errors.append("confirm_complete_input_shape_mismatch")
    if profiles["raw_current"]["input_shape"] != "raw_envelope":
        errors.append("raw_current_input_shape_mismatch")
    if profiles["raw_future_complete"]["input_shape"] != "raw_envelope":
        errors.append("raw_future_complete_input_shape_mismatch")
    if profiles["raw_current"]["missing_control_codes"] != EXPECTED_GAP_CODES:
        errors.append("raw_current_gap_contract_mismatch")
    if profiles["confirm_complete"]["missing_control_codes"]:
        errors.append("confirm_complete_declares_gap")
    if profiles["raw_future_complete"]["missing_control_codes"]:
        errors.append("raw_future_complete_declares_gap")
    if packet["forbidden_caller_fields"] != [
        "canonical_operation_id",
        "route_adapter_id",
    ]:
        errors.append("forbidden_caller_fields_mismatch")

    specs = _adapter_specs(packet)
    if len(specs) != len(packet["adapter_specs"]):
        errors.append("adapter_id_duplicate")
    observed_specs = {
        adapter_id: (
            spec["family_id"],
            spec["ingress_kind"],
            spec["method"],
            spec["path"],
            spec["canonical_operation_id"],
            spec["parent_route_posture"],
        )
        for adapter_id, spec in specs.items()
    }
    if observed_specs != EXPECTED_ADAPTERS:
        errors.append("adapter_census_or_binding_mismatch")
    for spec in packet["adapter_specs"]:
        if spec["lock_plan"] != EXPECTED_FAMILY_LOCKS.get(spec["family_id"]):
            errors.append(f"adapter_lock_plan_mismatch:{spec['adapter_id']}")
        expected_shape = (
            "null_appointment_target"
            if spec["family_id"] == "appointment_create"
            else "existing_appointment_target"
        )
        if spec["target_shape"] != expected_shape:
            errors.append(f"adapter_target_shape_mismatch:{spec['adapter_id']}")

    intents = _intents(packet)
    if len(intents) != len(packet["authored_synthetic_intents"]):
        errors.append("intent_id_duplicate")
    if {row["family_id"] for row in packet["authored_synthetic_intents"]} != set(
        EXPECTED_FAMILY_LOCKS
    ):
        errors.append("intent_family_census_mismatch")
    for intent in packet["authored_synthetic_intents"]:
        family = intent["family_id"]
        if not intent["intent_id"].startswith("syn-"):
            errors.append(f"intent_not_synthetic:{intent['intent_id']}")
        if family == "appointment_create":
            if intent["target_appointment_id"] is not None or intent["conflict_domain_id"] is None:
                errors.append("create_intent_shape_mismatch")
        elif family == "appointment_update":
            if intent["target_appointment_id"] is None or intent["conflict_domain_id"] is None:
                errors.append("update_intent_shape_mismatch")
        elif intent["target_appointment_id"] is None or intent["conflict_domain_id"] is not None:
            errors.append(f"single_target_intent_shape_mismatch:{family}")
        if family == "appointment_delete" and intent["confirmation_mode"] != "staff_destructive_explicit":
            errors.append("delete_confirmation_not_destructive")

    scenarios = packet["scenario_matrix"]
    scenario_ids = [row["scenario_id"] for row in scenarios]
    if len(scenario_ids) != len(set(scenario_ids)):
        errors.append("scenario_id_duplicate")
    if {scenario_id[:8] for scenario_id in scenario_ids} != EXPECTED_SCENARIO_IDS:
        errors.append("scenario_census_mismatch")
    profile_counts = {
        profile: sum(row["envelope_profile"] == profile for row in scenarios)
        for profile in profiles
    }
    if profile_counts != {
        "confirm_complete": 5,
        "raw_current": 4,
        "raw_future_complete": 4,
    }:
        errors.append("scenario_profile_census_mismatch")

    results: dict[str, dict[str, Any]] = {}
    for scenario in scenarios:
        spec = specs.get(scenario["adapter_id"])
        intent = intents.get(scenario["intent_id"])
        if spec is None or intent is None:
            errors.append(f"scenario_reference_unknown:{scenario['scenario_id']}")
            continue
        if spec["family_id"] != intent["family_id"]:
            errors.append(f"scenario_family_mismatch:{scenario['scenario_id']}")
        if scenario["envelope_profile"] == "confirm_complete" and spec["ingress_kind"] != "confirm":
            errors.append(f"confirm_profile_adapter_mismatch:{scenario['scenario_id']}")
        if scenario["envelope_profile"].startswith("raw_") and spec["ingress_kind"] != "raw":
            errors.append(f"raw_profile_adapter_mismatch:{scenario['scenario_id']}")
        try:
            result = evaluate_scenario(packet, scenario)
        except (KeyError, TypeError, ValueError):
            errors.append(f"scenario_evaluation_failed:{scenario['scenario_id']}")
            continue
        results[scenario["scenario_id"]] = result
        if result["adapter_result"] != scenario["expected_adapter_result"]:
            errors.append(f"scenario_result_mismatch:{scenario['scenario_id']}")
        if result["reason_codes"] != sorted(scenario["expected_gap_codes"]):
            errors.append(f"scenario_gap_mismatch:{scenario['scenario_id']}")
        if result["runtime_execution_authorized"] or result["effect_performed"]:
            errors.append(f"scenario_effect_boundary_open:{scenario['scenario_id']}")
        if result["command_outcome"] is not None:
            errors.append(f"scenario_command_outcome_emitted:{scenario['scenario_id']}")
        if result["adapter_result"] == "adapter_rejected" and result["kernel_candidate"] is not None:
            errors.append(f"rejected_scenario_has_candidate:{scenario['scenario_id']}")
        if result["adapter_result"] == "candidate_mapped":
            candidate = result["kernel_candidate"]
            if candidate is None or list(candidate) != EXPECTED_REQUIRED_FIELDS:
                errors.append(f"candidate_field_order_mismatch:{scenario['scenario_id']}")
            if result["lock_plan"] != spec["lock_plan"]:
                errors.append(f"scenario_lock_plan_mismatch:{scenario['scenario_id']}")

    groups = packet["differential_groups"]
    if {row["family_id"] for row in groups} != set(EXPECTED_FAMILY_LOCKS):
        errors.append("differential_family_census_mismatch")
    for group in groups:
        if group["excluded_fields"] != ["route_adapter_id"]:
            errors.append(f"differential_exclusion_mismatch:{group['family_id']}")
            continue
        candidates: list[dict[str, Any]] = []
        for scenario_id in group["scenario_ids"]:
            result = results.get(scenario_id)
            if result is None or result["kernel_candidate"] is None:
                errors.append(f"differential_candidate_missing:{group['family_id']}")
                continue
            candidates.append(result["kernel_candidate"])
        if candidates:
            projections = [semantic_projection(packet, item) for item in candidates]
            if any(projection != projections[0] for projection in projections[1:]):
                errors.append(f"differential_semantics_mismatch:{group['family_id']}")
            provenances = {candidate["route_adapter_id"] for candidate in candidates}
            if len(provenances) != len(candidates):
                errors.append(f"differential_provenance_not_distinct:{group['family_id']}")

    if any(packet["claim_boundary"].values()):
        errors.append("claim_boundary_not_zero")
    if any(packet["effect_boundary"].values()):
        errors.append("effect_boundary_not_zero")
    return sorted(set(errors))


def validate_contract(
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
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("source_head", lambda p: p.__setitem__("source_head", "0" * 40)),
        ("source_hash", lambda p: p["source_bindings"][0].__setitem__("sha256", "0" * 64)),
        ("source_removed", lambda p: p["source_bindings"].pop()),
        ("route_behavior", lambda p: p["claim_boundary"].__setitem__("route_behavior_changed", True)),
        ("application_import", lambda p: p["claim_boundary"].__setitem__("application_route_imported", True)),
        ("database_access", lambda p: p["claim_boundary"].__setitem__("database_or_source_accessed", True)),
        ("provider_access", lambda p: p["claim_boundary"].__setitem__("provider_or_network_used", True)),
        ("kernel_execution", lambda p: p["claim_boundary"].__setitem__("kernel_command_executed", True)),
        ("write", lambda p: p["claim_boundary"].__setitem__("command_or_write_performed", True)),
        ("required_field_removed", lambda p: p["kernel_binding"]["required_fields"].pop()),
        ("required_field_added", lambda p: p["kernel_binding"]["required_fields"].append("ambient_authority")),
        ("provenance_exception_added", lambda p: p["kernel_binding"]["provenance_only_fields"].append("confirmation_reference")),
        ("outcome_removed", lambda p: p["kernel_binding"]["outcomes_preserved_but_not_evaluated"].pop()),
        ("outcome_reordered", lambda p: p["kernel_binding"]["outcomes_preserved_but_not_evaluated"].reverse()),
        ("precedence_swapped", lambda p: p["kernel_binding"]["precedence_preserved_but_not_evaluated"].__setitem__(slice(1, 3), ["separate_confirmation_validation", "current_authority_before_receipt_disclosure"])),
        ("lock_order_swapped", lambda p: p["kernel_binding"].__setitem__("canonical_lock_order", ["practice", "appointment", "schedule_domain", "idempotency_record"])),
        ("runtime_authorized", lambda p: p["kernel_binding"].__setitem__("runtime_execution_authorized", True)),
        ("outcome_emitted", lambda p: p["kernel_binding"].__setitem__("command_outcome_emitted", True)),
        ("raw_gap_removed", lambda p: p["envelope_profiles"]["raw_current"]["missing_control_codes"].pop()),
        ("raw_shape_confirm", lambda p: p["envelope_profiles"]["raw_current"].__setitem__("input_shape", "confirm_envelope")),
        ("field_map_rewritten", lambda p: p["field_maps"]["raw_envelope"].__setitem__("confirmation_reference", "request_context.actor_id")),
        ("caller_field_allowed", lambda p: p["forbidden_caller_fields"].pop()),
        ("adapter_removed", lambda p: p["adapter_specs"].pop()),
        ("adapter_duplicate", lambda p: p["adapter_specs"].__setitem__(8, copy.deepcopy(p["adapter_specs"][7]))),
        ("adapter_path", lambda p: p["adapter_specs"][0].__setitem__("path", "/api/v1/appointments")),
        ("adapter_operation", lambda p: p["adapter_specs"][0].__setitem__("canonical_operation_id", "confirmAppointmentDeleteProposal")),
        ("adapter_family", lambda p: p["adapter_specs"][0].__setitem__("family_id", "appointment_delete")),
        ("adapter_target", lambda p: p["adapter_specs"][0].__setitem__("target_shape", "existing_appointment_target")),
        ("adapter_lock", lambda p: p["adapter_specs"][2]["lock_plan"].reverse()),
        ("raw_posture", lambda p: p["adapter_specs"][5].__setitem__("parent_route_posture", "preferred_confirm_ingress")),
        ("intent_removed", lambda p: p["authored_synthetic_intents"].pop()),
        ("create_target", lambda p: p["authored_synthetic_intents"][0].__setitem__("target_appointment_id", "syn-appointment-create-001")),
        ("status_conflict", lambda p: p["authored_synthetic_intents"][2].__setitem__("conflict_domain_id", "syn-conflict")),
        ("delete_confirmation", lambda p: p["authored_synthetic_intents"][3].__setitem__("confirmation_mode", "staff_explicit")),
        ("scenario_removed", lambda p: p["scenario_matrix"].pop()),
        ("scenario_duplicate", lambda p: p["scenario_matrix"][12].__setitem__("scenario_id", p["scenario_matrix"][11]["scenario_id"])),
        ("current_raw_mapped", lambda p: p["scenario_matrix"][5].__setitem__("expected_adapter_result", "candidate_mapped")),
        ("current_raw_gap", lambda p: p["scenario_matrix"][5]["expected_gap_codes"].pop()),
        ("confirm_uses_raw", lambda p: p["scenario_matrix"][0].__setitem__("envelope_profile", "raw_future_complete")),
        ("unknown_adapter", lambda p: p["scenario_matrix"][0].__setitem__("adapter_id", "unknown_adapter")),
        ("intent_family_crossed", lambda p: p["scenario_matrix"][0].__setitem__("intent_id", "syn-intent-delete-001")),
        ("differential_exclusion", lambda p: p["differential_groups"][0]["excluded_fields"].append("confirmation_reference")),
        ("differential_member", lambda p: p["differential_groups"][1]["scenario_ids"].__setitem__(1, "rad-013-delete-raw-future-complete")),
        ("effect_runtime", lambda p: p["effect_boundary"].__setitem__("runtime_adapter", True)),
        ("effect_command", lambda p: p["effect_boundary"].__setitem__("command_or_mutation", True)),
    ]
    results: list[tuple[str, dict[str, Any]]] = []
    for name, mutate in mutations:
        candidate = copy.deepcopy(packet)
        mutate(candidate)
        results.append((name, candidate))
    return results


def build_report(packet: dict[str, Any] | None = None) -> dict[str, Any]:
    packet = load_contract() if packet is None else packet
    errors = validate_contract(packet, verify_source_files=True)
    results = [evaluate_scenario(packet, row) for row in packet["scenario_matrix"]]
    mutants = hostile_mutations(packet)
    escaped = [name for name, mutant in mutants if not validate_contract(mutant)]
    if escaped:
        errors.append("hostile_mutation_escaped:" + ",".join(escaped))
    return {
        "schema_version": "emr4.pure-route-adapter-differential-rehearsal-report.v1",
        "status": "passed" if not errors else "failed",
        "reasons": sorted(set(errors)),
        "source_head": packet["source_head"],
        "adapter_count": len(packet["adapter_specs"]),
        "confirm_adapter_count": sum(row["ingress_kind"] == "confirm" for row in packet["adapter_specs"]),
        "raw_adapter_count": sum(row["ingress_kind"] == "raw" for row in packet["adapter_specs"]),
        "scenario_count": len(packet["scenario_matrix"]),
        "mapped_candidate_count": sum(row["adapter_result"] == "candidate_mapped" for row in results),
        "rejected_current_raw_count": sum(row["adapter_result"] == "adapter_rejected" for row in results),
        "differential_group_count": len(packet["differential_groups"]),
        "hostile_mutation_count": len(mutants),
        "hostile_mutation_escape_count": len(escaped),
        "runtime_execution_authorized": False,
        "command_or_write_performed": False,
    }


def main() -> int:
    report = build_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
