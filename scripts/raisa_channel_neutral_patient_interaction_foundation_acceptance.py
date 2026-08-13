from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-channel-neutral-patient-interaction-foundation"
)
CONTRACT_PATH = ARTIFACT_ROOT / "foundation-contract.json"
SCHEMA_PATH = ARTIFACT_ROOT / "foundation-contract.schema.json"
EXAMPLES_PATH = ARTIFACT_ROOT / "authored-synthetic-contract-examples.json"
DEFAULT_EVIDENCE_PATH = ARTIFACT_ROOT / "provider-free-acceptance-evidence.json"

MESSAGE_DEFS = {
    "patient_identity_binding": "PatientIdentityBinding",
    "identity_assurance_decision": "IdentityAssuranceDecision",
    "patient_interaction_envelope": "PatientInteractionEnvelope",
    "patient_diary_projection": "PatientDiaryProjection",
    "patient_selection": "PatientSelection",
    "patient_confirmation_challenge": "PatientConfirmationChallenge",
    "patient_command_outcome": "PatientCommandOutcome",
    "patient_recovery_case": "PatientRecoveryCase",
}

IDENTITY_OBJECTS = [
    "identity_subject",
    "practice_patient_link",
    "channel_binding",
    "authenticator_binding",
    "proxy_grant",
]
IDENTITY_FLAGS = {
    "record_matching_is_identity_proofing": False,
    "identity_proofing_is_authentication": False,
    "authentication_is_authorization": False,
    "channel_recognition_is_identity_proofing": False,
    "patient_and_proxy_share_credentials": False,
    "cross_practice_link_implies_authority": False,
}
AUTHENTICATION_FIELDS = {
    "posture": "passkey_first_not_passkey_only",
    "preferred_authenticator": "phishing_resistant_passkey",
    "multiple_authenticators_supported": True,
    "encourage_two_independent_authenticators": True,
    "password_vault_required": False,
    "physical_security_key_required": False,
    "device_biometric_ingested_by_emr4": False,
    "synced_passkey_treated_as_infallible": False,
    "email_is_out_of_band_authenticator": False,
    "sms_or_voice_is_phishing_resistant": False,
    "knowledge_based_authentication_permitted": False,
    "fallback_may_silently_raise_assurance": False,
    "authenticator_binding_requires_current_assurance": True,
    "authenticator_change_requires_independent_notification": True,
    "provider_choice_settled": False,
}
ASSURANCE_ORDER = [
    "public",
    "recognized_channel",
    "verified_patient",
    "stepped_up",
    "recovery_restricted",
]
ASSURANCE_FIELDS = {
    "default_decision": "deny",
    "adapter_or_model_may_raise_assurance": False,
    "stronger_action_requires_current_or_stronger_assurance": True,
    "recovery_restricted_is_not_a_stronger_authentication_level": True,
    "non_enumerating_failure_required": True,
}
CHANNELS = ["sms", "email", "thin_web", "whatsapp", "voice", "delegated_assistant"]
CHANNEL_FIELDS = {
    "universal_fallback": "plain_text_plus_expiring_thin_web_handoff",
    "channel_content_is_untrusted": True,
    "channel_address_is_not_identity": True,
    "channel_receipt_is_not_command_receipt": True,
}
INTERACTION_FIELDS = {
    "backend_owns_typed_session_state": True,
    "provider_or_channel_memory_is_authority": False,
    "context_fabric_access_is_direct_from_channel": False,
    "context_need_is_closed_candidate": True,
    "context_frame_set_is_minimized_expiring_read_only": True,
    "projection_is_current_truth": False,
    "projection_is_reservation": False,
    "selection_is_proposal_only": True,
    "stale_projection_requires_reassembly": True,
    "candidate_refs_are_opaque_and_expiring": True,
    "plain_text_fallback_required": True,
    "clinical_reason_in_async_projection": False,
    "direct_identifier_in_transport_event": False,
}
COMMAND_FIELDS = {
    "command_plane": "rest_openapi_single_purpose",
    "graphql_mutation": False,
    "channel_or_model_direct_command": False,
    "confirmation_challenge_is_command_authority": False,
    "server_selects_command_family": True,
    "current_principal_recheck_required": True,
    "current_practice_and_proxy_scope_recheck_required": True,
    "current_assurance_recheck_required": True,
    "current_proposal_and_source_recheck_required": True,
    "idempotency_required": True,
    "audit_required": True,
    "atomic_receipt_required": True,
    "exact_replay_required": True,
    "transport_deduplication_is_command_idempotency": False,
    "event_or_delivery_receipt_is_command_receipt": False,
    "race_loser_gets_refreshed_projection": True,
}
RECOVERY_FIELDS = {
    "ordinary_command_authority_while_recovery_unresolved": False,
    "health_or_demographic_knowledge_as_proof": False,
    "single_channel_possession_is_sufficient_for_high_assurance_recovery": False,
    "independent_notification_required": True,
    "prior_session_revocation_required": True,
    "compromised_authenticator_revocation_required": True,
    "sensitive_change_cooling_off_required": True,
    "recovery_evidence_reusable_as_command_confirmation": False,
    "recovery_may_create_proxy_grant": False,
    "human_assisted_exception_path_required": True,
    "recovery_events_audited": True,
}
DELEGATION_FIELDS = {
    "patient_parent_guardian_carer_are_distinct_principals": True,
    "proxy_grant_is_practice_patient_action_scoped": True,
    "proxy_grant_is_expiring_and_revocable": True,
    "shared_patient_credential": False,
    "delegated_assistant_status": "future_closed",
    "client_registration_required": True,
    "oauth_oidc_authorization_code_pkce_required": True,
    "audience_restricted": True,
    "sender_constrained_where_supported": True,
    "minimum_scopes_only": True,
    "per_command_confirmation_policy_required": True,
    "patient_emr_credential_disclosed_to_client": False,
    "generic_command_tunnel": False,
    "revocation_required": True,
}
PRIVACY_FIELDS = {
    "data_minimization_required": True,
    "anti_enumeration_required": True,
    "rate_limiting_required_before_runtime": True,
    "privacy_impact_assessment_required_before_runtime": True,
    "generic_external_errors_required": True,
    "sensitive_values_forbidden_in_contract_evidence": True,
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _mutated_value(value: Any) -> Any:
    if isinstance(value, bool):
        return not value
    if isinstance(value, str):
        return f"{value}-mutated"
    if isinstance(value, int):
        return value + 10
    if isinstance(value, list):
        return list(reversed(value)) if len(value) > 1 else [*value, "mutated"]
    raise TypeError(f"Unsupported mutation value: {type(value)!r}")


def _expect_fields(
    errors: list[str], section: str, value: dict[str, Any], expected: dict[str, Any]
) -> None:
    for key, required in expected.items():
        if value.get(key) != required:
            errors.append(f"{section}.{key}_must_equal_{required!r}")


def validate_contract(
    contract: dict[str, Any], schema: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    try:
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(contract)
    except Exception as exc:  # deterministic error code only
        errors.append(f"schema_or_contract_invalid:{type(exc).__name__}")
        return errors

    if set(contract["authority_boundary"].values()) != {False}:
        errors.append("authority_boundary_must_be_all_false")

    identity = contract["identity_model"]
    if identity.get("objects") != IDENTITY_OBJECTS:
        errors.append("identity_objects_must_remain_exact_and_ordered")
    _expect_fields(errors, "identity_model", identity, IDENTITY_FLAGS)
    forbidden_authenticators = {
        "individual_healthcare_identifier",
        "medicare_number",
        "date_of_birth",
        "address",
        "telephone_number",
        "email_address",
        "appointment_details",
    }
    if set(identity.get("record_identifiers_forbidden_as_authenticators", [])) != forbidden_authenticators:
        errors.append("record_identifiers_must_all_remain_forbidden_as_authenticators")
    if identity.get("enabled_proofing_methods") != []:
        errors.append("proofing_runtime_must_remain_disabled")

    _expect_fields(
        errors,
        "authentication_policy",
        contract["authentication_policy"],
        AUTHENTICATION_FIELDS,
    )

    assurance = contract["assurance_policy"]
    _expect_fields(errors, "assurance_policy", assurance, ASSURANCE_FIELDS)
    if assurance.get("order") != ASSURANCE_ORDER:
        errors.append("assurance_order_must_remain_exact")
    levels = assurance.get("levels", [])
    if [item.get("level") for item in levels] != ASSURANCE_ORDER:
        errors.append("assurance_levels_must_match_order")
    if [item.get("rank") for item in levels] != [0, 1, 2, 3, 4]:
        errors.append("assurance_ranks_must_remain_monotonic")
    if "confirm_command" not in levels[-1].get("must_not", []):
        errors.append("recovery_restricted_must_forbid_commands")

    channel_policy = contract["channel_policy"]
    _expect_fields(errors, "channel_policy", channel_policy, CHANNEL_FIELDS)
    adapters = channel_policy.get("adapters", [])
    if [adapter.get("channel") for adapter in adapters] != CHANNELS:
        errors.append("channel_matrix_must_remain_exact_and_ordered")
    for adapter in adapters:
        channel = adapter.get("channel", "unknown")
        if adapter.get("status") != "future_closed":
            errors.append(f"channel_{channel}_must_remain_future_closed")
        if adapter.get("identity_proof") is not False:
            errors.append(f"channel_{channel}_must_not_prove_identity")
        if adapter.get("command_authority") is not False:
            errors.append(f"channel_{channel}_must_not_hold_command_authority")
        if not adapter.get("may_render") or not adapter.get("may_collect"):
            errors.append(f"channel_{channel}_capability_intersection_missing")

    _expect_fields(
        errors,
        "interaction_policy",
        contract["interaction_policy"],
        INTERACTION_FIELDS,
    )
    _expect_fields(
        errors,
        "command_convergence",
        contract["command_convergence"],
        COMMAND_FIELDS,
    )
    _expect_fields(
        errors,
        "recovery_policy",
        contract["recovery_policy"],
        RECOVERY_FIELDS,
    )
    _expect_fields(
        errors,
        "delegation_policy",
        contract["delegation_policy"],
        DELEGATION_FIELDS,
    )
    _expect_fields(
        errors,
        "privacy_and_audit_policy",
        contract["privacy_and_audit_policy"],
        PRIVACY_FIELDS,
    )

    forbidden_evidence = set(contract["privacy_and_audit_policy"].get("forbidden_evidence_fields", []))
    if not {
        "patient_identifier",
        "phone_number",
        "email_address",
        "message_body",
        "authenticator",
        "credential",
        "access_token",
        "recovery_secret",
        "provider_output",
    } <= forbidden_evidence:
        errors.append("sensitive_evidence_forbidden_fields_incomplete")

    registry = contract.get("schema_registry", [])
    if {item.get("message_type") for item in registry} != set(MESSAGE_DEFS.values()):
        errors.append("schema_registry_must_name_exact_eight_messages")

    next_descendant = contract["next_descendant"]
    expected_next = {
        "id": "bounded-visible-native-diary-status-confirm-wiring",
        "staff_surface_only": True,
        "external_patient_client": False,
        "real_identity": False,
        "channel_connector": False,
        "provider_call": False,
        "product_or_patient_data": False,
        "requires_fresh_frozen_plan": True,
    }
    if next_descendant != expected_next:
        errors.append("next_descendant_must_remain_staff_only_and_closed")
    return errors


def _message_validator(schema: dict[str, Any], definition: str) -> Draft202012Validator:
    packet = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$ref": f"#/$defs/{definition}",
        "$defs": schema["$defs"],
    }
    return Draft202012Validator(packet, format_checker=FormatChecker())


def validate_examples(
    examples: dict[str, Any], contract: dict[str, Any], schema: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    if set(examples) != {
        "schema_version",
        "evidence_mode",
        "contains_sensitive_values",
        "messages",
    }:
        errors.append("example_packet_keys_must_be_closed")
    if examples.get("schema_version") != "emr4.patient_interaction_foundation.examples.v1":
        errors.append("example_packet_schema_version_invalid")
    if examples.get("evidence_mode") != "authored_synthetic_provider_free":
        errors.append("example_packet_evidence_mode_invalid")
    if examples.get("contains_sensitive_values") is not False:
        errors.append("example_packet_must_not_contain_sensitive_values")

    messages = examples.get("messages", {})
    if set(messages) != set(MESSAGE_DEFS):
        errors.append("example_packet_must_contain_exact_eight_messages")
        return errors
    for key, definition in MESSAGE_DEFS.items():
        message_errors = list(_message_validator(schema, definition).iter_errors(messages[key]))
        if message_errors:
            errors.append(f"message_{key}_invalid:{message_errors[0].validator}")

    binding = messages["patient_identity_binding"]
    assurance = messages["identity_assurance_decision"]
    envelope = messages["patient_interaction_envelope"]
    projection = messages["patient_diary_projection"]
    selection = messages["patient_selection"]
    challenge = messages["patient_confirmation_challenge"]
    outcome = messages["patient_command_outcome"]
    recovery = messages["patient_recovery_case"]

    if len(binding["authenticator_binding_refs"]) < 2:
        errors.append("example_binding_must_show_two_authenticators")
    if envelope["assurance_ceiling"] not in {"public", "recognized_channel"}:
        errors.append("channel_envelope_assurance_ceiling_too_high")
    if _iso(projection["assembled_at"]) >= _iso(projection["expires_at"]):
        errors.append("projection_must_expire_after_assembly")
    if selection["projection_id"] != projection["projection_id"]:
        errors.append("selection_projection_binding_mismatch")
    if selection["candidate_set_id"] != projection["candidate_set_id"]:
        errors.append("selection_candidate_set_binding_mismatch")
    if selection["candidate_ref"] not in {
        item["candidate_ref"] for item in projection["candidates"]
    }:
        errors.append("selection_candidate_not_in_projection")
    if _iso(selection["selected_at"]) >= _iso(selection["projection_expires_at"]):
        errors.append("example_selection_must_precede_projection_expiry")
    if challenge["source_revision_digest"] != projection["source_revision_digest"]:
        errors.append("challenge_source_revision_binding_mismatch")
    if challenge["identity_subject_ref"] != binding["identity_subject_ref"]:
        errors.append("challenge_subject_binding_mismatch")
    if challenge["practice_ref"] != binding["practice_ref"]:
        errors.append("challenge_practice_binding_mismatch")
    if challenge["patient_record_ref"] != binding["patient_record_ref"]:
        errors.append("challenge_patient_binding_mismatch")
    if assurance["observed_level"] != challenge["observed_assurance"]:
        errors.append("challenge_assurance_decision_mismatch")
    if _iso(challenge["issued_at"]) >= _iso(challenge["expires_at"]):
        errors.append("challenge_must_expire_after_issue")
    if outcome["challenge_id"] != challenge["challenge_id"]:
        errors.append("outcome_challenge_binding_mismatch")
    if outcome["outcome"] in {"committed", "replay"} and outcome["effect_committed"] is not True:
        errors.append("successful_outcome_must_record_committed_effect")
    if outcome["outcome"] in {"blocked", "stale", "expired", "unavailable"} and outcome["effect_committed"] is not False:
        errors.append("unsuccessful_outcome_must_not_record_committed_effect")
    if recovery["current_assurance"] != "recovery_restricted":
        errors.append("recovery_case_must_remain_restricted")

    forbidden_keys = set(contract["privacy_and_audit_policy"]["forbidden_evidence_fields"])

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                if key in forbidden_keys:
                    errors.append(f"forbidden_example_field:{key}")
                walk(nested)
        elif isinstance(value, list):
            for nested in value:
                walk(nested)

    walk(examples)
    return errors


def hostile_mutations() -> list[tuple[str, dict[str, Any], dict[str, Any]]]:
    contract = _load(CONTRACT_PATH)
    examples = _load(EXAMPLES_PATH)
    mutations: list[tuple[str, dict[str, Any], dict[str, Any]]] = []

    def add_contract_field(section: str, key: str) -> None:
        changed = copy.deepcopy(contract)
        changed[section][key] = _mutated_value(changed[section][key])
        mutations.append((f"contract:{section}.{key}", changed, copy.deepcopy(examples)))

    for key in contract["authority_boundary"]:
        add_contract_field("authority_boundary", key)
    for key in IDENTITY_FLAGS:
        add_contract_field("identity_model", key)
    for key in AUTHENTICATION_FIELDS:
        add_contract_field("authentication_policy", key)
    for key in ASSURANCE_FIELDS:
        add_contract_field("assurance_policy", key)
    for key in CHANNEL_FIELDS:
        add_contract_field("channel_policy", key)
    for key in INTERACTION_FIELDS:
        add_contract_field("interaction_policy", key)
    for key in COMMAND_FIELDS:
        add_contract_field("command_convergence", key)
    for key in RECOVERY_FIELDS:
        add_contract_field("recovery_policy", key)
    for key in DELEGATION_FIELDS:
        add_contract_field("delegation_policy", key)
    for key in PRIVACY_FIELDS:
        add_contract_field("privacy_and_audit_policy", key)

    changed = copy.deepcopy(contract)
    changed["identity_model"]["objects"] = list(reversed(IDENTITY_OBJECTS))
    mutations.append(("contract:identity_model.objects_order", changed, copy.deepcopy(examples)))
    changed = copy.deepcopy(contract)
    changed["identity_model"]["record_identifiers_forbidden_as_authenticators"].pop()
    mutations.append(("contract:identity_model.identifier_removed", changed, copy.deepcopy(examples)))
    changed = copy.deepcopy(contract)
    changed["identity_model"]["enabled_proofing_methods"] = ["practice_attended"]
    mutations.append(("contract:identity_model.runtime_proofing_enabled", changed, copy.deepcopy(examples)))
    changed = copy.deepcopy(contract)
    changed["assurance_policy"]["order"] = list(reversed(ASSURANCE_ORDER))
    mutations.append(("contract:assurance_policy.order", changed, copy.deepcopy(examples)))
    changed = copy.deepcopy(contract)
    changed["assurance_policy"]["levels"][-1]["must_not"].remove("confirm_command")
    mutations.append(("contract:assurance_policy.recovery_command", changed, copy.deepcopy(examples)))

    for index, channel in enumerate(CHANNELS):
        for key, value in (
            ("status", "runtime_enabled"),
            ("identity_proof", True),
            ("command_authority", True),
        ):
            changed = copy.deepcopy(contract)
            changed["channel_policy"]["adapters"][index][key] = value
            mutations.append((f"contract:channel.{channel}.{key}", changed, copy.deepcopy(examples)))

    for message_key in MESSAGE_DEFS:
        changed_examples = copy.deepcopy(examples)
        changed_examples["messages"][message_key]["unexpected_authority"] = True
        mutations.append((f"message:{message_key}.unexpected", copy.deepcopy(contract), changed_examples))
        changed_examples = copy.deepcopy(examples)
        del changed_examples["messages"][message_key]["schema_version"]
        mutations.append((f"message:{message_key}.missing_schema_version", copy.deepcopy(contract), changed_examples))

    return mutations


def validate_hostile_mutations(
    schema: dict[str, Any],
) -> tuple[list[str], list[str]]:
    rejected: list[str] = []
    admitted: list[str] = []
    for label, contract, examples in hostile_mutations():
        errors = validate_contract(contract, schema)
        errors.extend(validate_examples(examples, contract, schema))
        (rejected if errors else admitted).append(label)
    return rejected, admitted


def build_report() -> dict[str, Any]:
    contract = _load(CONTRACT_PATH)
    schema = _load(SCHEMA_PATH)
    examples = _load(EXAMPLES_PATH)
    canonical_errors = validate_contract(contract, schema)
    canonical_errors.extend(validate_examples(examples, contract, schema))
    rejected, admitted = validate_hostile_mutations(schema)
    contract_digest = hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest()
    status = "passed" if not canonical_errors and not admitted and len(rejected) >= 60 else "failed"
    return {
        "schema_version": "emr4.patient_interaction_foundation.acceptance_evidence.v1",
        "result": "raisa_channel_neutral_patient_interaction_foundation_pass" if status == "passed" else "raisa_channel_neutral_patient_interaction_foundation_failed",
        "status": status,
        "evidence_mode": "authored_synthetic_provider_free",
        "recorded_at": "2026-08-13T04:40:00Z",
        "canonical_contract_digest": f"sha256:{contract_digest}",
        "canonical_error_count": len(canonical_errors),
        "message_type_count": len(MESSAGE_DEFS),
        "assurance_level_count": len(ASSURANCE_ORDER),
        "channel_count": len(CHANNELS),
        "scenario_count": 12,
        "hostile_mutation_count": len(rejected) + len(admitted),
        "hostile_rejection_count": len(rejected),
        "hostile_admission_count": len(admitted),
        "contains_sensitive_values": False,
        "runtime_started": False,
        "provider_calls": 0,
        "external_patient_clients": 0,
        "product_or_patient_data": False,
        "database_or_source_access": False,
        "command_or_write": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the provider-free patient interaction foundation."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_EVIDENCE_PATH)
    args = parser.parse_args()
    report = build_report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
