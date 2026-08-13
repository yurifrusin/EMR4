from __future__ import annotations

from scripts.raisa_channel_neutral_patient_interaction_foundation_acceptance import (
    ASSURANCE_ORDER,
    CHANNELS,
    CONTRACT_PATH,
    EXAMPLES_PATH,
    MESSAGE_DEFS,
    SCHEMA_PATH,
    _load,
    build_report,
    hostile_mutations,
    validate_contract,
    validate_examples,
    validate_hostile_mutations,
)


def _packet() -> tuple[dict, dict, dict]:
    return _load(CONTRACT_PATH), _load(SCHEMA_PATH), _load(EXAMPLES_PATH)


def test_canonical_foundation_packet_passes_without_runtime_or_data() -> None:
    report = build_report()

    assert report["status"] == "passed"
    assert report["canonical_error_count"] == 0
    assert report["runtime_started"] is False
    assert report["provider_calls"] == 0
    assert report["external_patient_clients"] == 0
    assert report["product_or_patient_data"] is False
    assert report["database_or_source_access"] is False
    assert report["command_or_write"] is False


def test_contract_and_all_eight_message_schemas_are_closed_and_valid() -> None:
    contract, schema, examples = _packet()

    assert schema["additionalProperties"] is False
    assert set(examples["messages"]) == set(MESSAGE_DEFS)
    assert all(
        schema["$defs"][definition]["additionalProperties"] is False
        for definition in MESSAGE_DEFS.values()
    )
    assert validate_contract(contract, schema) == []
    assert validate_examples(examples, contract, schema) == []


def test_patient_record_proofing_authentication_and_authority_are_distinct() -> None:
    contract, _, examples = _packet()
    identity = contract["identity_model"]
    binding = examples["messages"]["patient_identity_binding"]

    assert identity["record_matching_is_identity_proofing"] is False
    assert identity["identity_proofing_is_authentication"] is False
    assert identity["authentication_is_authorization"] is False
    assert identity["channel_recognition_is_identity_proofing"] is False
    assert identity["patient_and_proxy_share_credentials"] is False
    assert identity["enabled_proofing_methods"] == []
    assert {
        "individual_healthcare_identifier",
        "medicare_number",
        "date_of_birth",
        "telephone_number",
        "email_address",
        "appointment_details",
    } <= set(identity["record_identifiers_forbidden_as_authenticators"])
    assert binding["knowledge_attributes_used_as_authenticator"] is False
    assert binding["channel_address_is_identity"] is False
    assert binding["command_authority"] is False


def test_passkey_first_policy_is_inclusive_and_recovery_aware() -> None:
    contract, _, examples = _packet()
    auth = contract["authentication_policy"]
    binding = examples["messages"]["patient_identity_binding"]

    assert auth["posture"] == "passkey_first_not_passkey_only"
    assert auth["preferred_authenticator"] == "phishing_resistant_passkey"
    assert auth["multiple_authenticators_supported"] is True
    assert auth["encourage_two_independent_authenticators"] is True
    assert len(binding["authenticator_binding_refs"]) == 2
    assert auth["password_vault_required"] is False
    assert auth["physical_security_key_required"] is False
    assert auth["device_biometric_ingested_by_emr4"] is False
    assert auth["synced_passkey_treated_as_infallible"] is False
    assert auth["email_is_out_of_band_authenticator"] is False
    assert auth["sms_or_voice_is_phishing_resistant"] is False
    assert auth["knowledge_based_authentication_permitted"] is False
    assert auth["fallback_may_silently_raise_assurance"] is False


def test_assurance_ladder_is_default_deny_and_recovery_is_restrictive() -> None:
    contract, _, _ = _packet()
    assurance = contract["assurance_policy"]

    assert assurance["default_decision"] == "deny"
    assert assurance["order"] == ASSURANCE_ORDER
    assert [item["rank"] for item in assurance["levels"]] == [0, 1, 2, 3, 4]
    assert assurance["adapter_or_model_may_raise_assurance"] is False
    assert assurance["stronger_action_requires_current_or_stronger_assurance"] is True
    assert assurance["recovery_restricted_is_not_a_stronger_authentication_level"] is True
    recovery_level = assurance["levels"][-1]
    assert recovery_level["level"] == "recovery_restricted"
    assert {
        "view_patient_booking_state",
        "propose_booking",
        "confirm_command",
        "manage_proxy_grant",
    } <= set(recovery_level["must_not"])


def test_all_channels_are_future_closed_renderers_without_authority() -> None:
    contract, _, examples = _packet()
    policy = contract["channel_policy"]

    assert policy["universal_fallback"] == "plain_text_plus_expiring_thin_web_handoff"
    assert policy["channel_content_is_untrusted"] is True
    assert policy["channel_address_is_not_identity"] is True
    assert policy["channel_receipt_is_not_command_receipt"] is True
    assert [adapter["channel"] for adapter in policy["adapters"]] == CHANNELS
    for adapter in policy["adapters"]:
        assert adapter["status"] == "future_closed"
        assert adapter["identity_proof"] is False
        assert adapter["command_authority"] is False
    envelope = examples["messages"]["patient_interaction_envelope"]
    assert envelope["untrusted_input"] is True
    assert envelope["assurance_ceiling"] == "recognized_channel"
    assert envelope["provider_memory_authority"] is False
    assert envelope["contains_command_receipt"] is False


def test_projection_and_selection_are_expiring_non_reserving_proposals() -> None:
    contract, _, examples = _packet()
    interaction = contract["interaction_policy"]
    projection = examples["messages"]["patient_diary_projection"]
    selection = examples["messages"]["patient_selection"]

    assert interaction["backend_owns_typed_session_state"] is True
    assert interaction["provider_or_channel_memory_is_authority"] is False
    assert interaction["context_fabric_access_is_direct_from_channel"] is False
    assert interaction["context_frame_set_is_minimized_expiring_read_only"] is True
    assert interaction["projection_is_current_truth"] is False
    assert interaction["projection_is_reservation"] is False
    assert projection["minimum_disclosure"] is True
    assert projection["contains_clinical_reason"] is False
    assert projection["current_truth"] is False
    assert projection["reservation_created"] is False
    assert all(candidate["reserved"] is False for candidate in projection["candidates"])
    assert selection["proposal_only"] is True
    assert selection["reservation_created"] is False
    assert selection["current_source_recheck_required"] is True


def test_confirmation_converges_on_existing_backend_command_boundary() -> None:
    contract, _, examples = _packet()
    command = contract["command_convergence"]
    challenge = examples["messages"]["patient_confirmation_challenge"]
    outcome = examples["messages"]["patient_command_outcome"]

    assert command["command_plane"] == "rest_openapi_single_purpose"
    assert command["graphql_mutation"] is False
    assert command["channel_or_model_direct_command"] is False
    assert command["confirmation_challenge_is_command_authority"] is False
    assert command["server_selects_command_family"] is True
    assert command["current_principal_recheck_required"] is True
    assert command["current_practice_and_proxy_scope_recheck_required"] is True
    assert command["current_assurance_recheck_required"] is True
    assert command["current_proposal_and_source_recheck_required"] is True
    assert command["idempotency_required"] is True
    assert command["audit_required"] is True
    assert command["atomic_receipt_required"] is True
    assert command["exact_replay_required"] is True
    assert command["transport_deduplication_is_command_idempotency"] is False
    assert command["event_or_delivery_receipt_is_command_receipt"] is False
    assert challenge["single_use"] is True
    assert challenge["reusable_credential"] is False
    assert challenge["command_authority"] is False
    assert outcome["transport_receipt_is_command_receipt"] is False
    assert outcome["current_principal_checked"] is True
    assert outcome["current_source_checked"] is True


def test_recovery_and_delegation_do_not_create_hidden_authority() -> None:
    contract, _, examples = _packet()
    recovery_policy = contract["recovery_policy"]
    delegation = contract["delegation_policy"]
    recovery = examples["messages"]["patient_recovery_case"]

    assert recovery_policy["ordinary_command_authority_while_recovery_unresolved"] is False
    assert recovery_policy["health_or_demographic_knowledge_as_proof"] is False
    assert recovery_policy["single_channel_possession_is_sufficient_for_high_assurance_recovery"] is False
    assert recovery_policy["independent_notification_required"] is True
    assert recovery_policy["prior_session_revocation_required"] is True
    assert recovery_policy["compromised_authenticator_revocation_required"] is True
    assert recovery_policy["sensitive_change_cooling_off_required"] is True
    assert recovery_policy["recovery_evidence_reusable_as_command_confirmation"] is False
    assert recovery_policy["recovery_may_create_proxy_grant"] is False
    assert recovery["ordinary_command_authority"] is False
    assert recovery["may_confirm_booking"] is False
    assert recovery["may_create_proxy_grant"] is False
    assert delegation["patient_parent_guardian_carer_are_distinct_principals"] is True
    assert delegation["proxy_grant_is_practice_patient_action_scoped"] is True
    assert delegation["shared_patient_credential"] is False
    assert delegation["delegated_assistant_status"] == "future_closed"
    assert delegation["patient_emr_credential_disclosed_to_client"] is False
    assert delegation["generic_command_tunnel"] is False


def test_all_hostile_mutations_fail_closed_and_evidence_is_minimized() -> None:
    contract, schema, _ = _packet()
    rejected, admitted = validate_hostile_mutations(schema)
    report = build_report()

    assert len(hostile_mutations()) == 143
    assert len(rejected) == 143
    assert admitted == []
    assert report["hostile_rejection_count"] == 143
    assert report["contains_sensitive_values"] is False
    assert {
        "patient_identifier",
        "phone_number",
        "email_address",
        "message_body",
        "authenticator",
        "credential",
        "recovery_secret",
        "provider_output",
    } <= set(contract["privacy_and_audit_policy"]["forbidden_evidence_fields"])


def test_next_descendant_is_staff_only_visible_diary_work() -> None:
    contract, _, _ = _packet()

    assert contract["next_descendant"] == {
        "id": "bounded-visible-native-diary-status-confirm-wiring",
        "staff_surface_only": True,
        "external_patient_client": False,
        "real_identity": False,
        "channel_connector": False,
        "provider_call": False,
        "product_or_patient_data": False,
        "requires_fresh_frozen_plan": True,
    }
