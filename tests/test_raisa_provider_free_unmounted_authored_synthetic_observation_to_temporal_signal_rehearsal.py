from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts.raisa_provider_free_practice_context_fabric_bureau_memory_contract import (
    canonical_sha256,
    seal,
)
from scripts.raisa_provider_free_practice_context_fabric_current_operational_weave import (
    build_authored_synthetic_packet,
)
from scripts.raisa_provider_free_practice_context_fabric_patient_free_temporal_weave import (
    derive_dependency_manifest,
)
from scripts.raisa_provider_free_unmounted_authored_synthetic_observation_to_temporal_signal_rehearsal import (
    ACTIVATION_MODE,
    ADMISSION_DECISIONS,
    ADMISSION_REASON_CODES,
    EVIDENCE_LABEL,
    MANDATORY_FRAME_FLOOR,
    MAX_SAFE_INTEGER,
    ObservationToSignalViolation,
    RESULT,
    SOURCE_CONTRACT_ID,
    SOURCE_SYSTEM_ID,
    admit_synthetic_committed_change,
    build_authored_synthetic_observation_to_signal_packet,
    build_authored_synthetic_source_input,
    build_live_source_observation_policy,
    build_live_source_observer_binding,
    build_observation_alias_registry,
    build_observation_impact_policy,
    build_observation_prior_coordinate,
    build_synthetic_observation_classification_activation,
    derive_observation_id,
    map_observation_to_temporal_signal,
    proofread_observation_to_signal_packet,
    validate_observation_to_signal_packet,
)
from scripts.raisa_provider_free_unmounted_authored_synthetic_observation_to_temporal_signal_rehearsal_acceptance import (
    ACCEPTANCE_CASES,
    CONTINUITY_DIR,
    MODULE_PATH,
    build_acceptance_evidence,
)


KEY = b"authored-synthetic-observation-key-0001"
RAW_ID = "evt_0123456789abcdef0123456789abcdef"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _reseal(value: dict, field: str) -> dict:
    return seal({key: item for key, item in value.items() if key != field}, field)


def _inputs() -> dict:
    parent = build_authored_synthetic_packet()
    manifest = derive_dependency_manifest(parent)
    impact = build_observation_impact_policy()
    registry = build_observation_alias_registry(manifest["practice_binding_digest"])
    policy = build_live_source_observation_policy(
        manifest["practice_binding_digest"],
        alias_registry_digest=registry["alias_registry_digest"],
        impact_policy_digest=impact["impact_policy_digest"],
    )
    binding = build_live_source_observer_binding(policy, registry, impact)
    source = build_authored_synthetic_source_input(manifest["practice_binding_digest"])
    activation = build_synthetic_observation_classification_activation(
        policy, binding, fixture_digest=canonical_sha256(source)
    )
    prior = build_observation_prior_coordinate(
        practice_binding_digest=manifest["practice_binding_digest"],
        policy=policy,
        binding=binding,
        alias_registry=registry,
        impact_policy=impact,
    )
    return {
        "source": source,
        "policy": policy,
        "binding": binding,
        "registry": registry,
        "impact": impact,
        "activation": activation,
        "prior": prior,
    }


def _activate(values: dict) -> None:
    values["activation"] = build_synthetic_observation_classification_activation(
        values["policy"],
        values["binding"],
        fixture_digest=canonical_sha256(values["source"]),
    )


def _coordinate_trusted_contracts(values: dict) -> None:
    practice = values["registry"]["practice_binding_digest"]
    values["policy"] = build_live_source_observation_policy(
        practice,
        alias_registry_digest=values["registry"]["alias_registry_digest"],
        impact_policy_digest=values["impact"]["impact_policy_digest"],
    )
    values["binding"] = build_live_source_observer_binding(
        values["policy"], values["registry"], values["impact"]
    )
    _activate(values)
    values["prior"] = build_observation_prior_coordinate(
        practice_binding_digest=practice,
        policy=values["policy"],
        binding=values["binding"],
        alias_registry=values["registry"],
        impact_policy=values["impact"],
    )


def _admit(values: dict, **kwargs):
    return admit_synthetic_committed_change(
        values["source"],
        values["policy"],
        values["binding"],
        values["registry"],
        values["impact"],
        values["prior"],
        values.get("activation"),
        observed_at=kwargs.get("observed_at", "2026-08-06T03:00:11Z"),
        expires_at=kwargs.get("expires_at", "2026-08-06T03:02:00Z"),
        hmac_key=kwargs.get("hmac_key", KEY),
    )


def _decision(values: dict, expected: str) -> dict:
    observation, decision = _admit(values)
    assert observation is None
    assert decision["decision"] == expected
    assert decision["ordinary_temporal_signal_emitted"] is False
    assert decision["signal_digest"] is None
    assert decision["checkpoint_advanced"] is False
    assert decision["durable_handoff_implemented"] is False
    return decision


def test_nominal_packet_releases_and_uses_exact_normalization_profile() -> None:
    packet = build_authored_synthetic_observation_to_signal_packet()
    validate_observation_to_signal_packet(packet)

    assert packet["result"] == RESULT
    assert packet["evidence_label"] == EVIDENCE_LABEL
    assert packet["proofreader_trace"]["release_decision"] == "RELEASE"
    assert packet["policy"]["enabled_by_default"] is False
    assert packet["policy"]["enabled"] is False
    assert packet["observer_binding"]["source_system_id"] == SOURCE_SYSTEM_ID
    assert packet["observation"]["event_schema_version"] == (
        "diary.appointment_rescheduled.v1"
    )
    assert packet["temporal_signal"]["event_schema_version"] == (
        "emr4.diary.appointment_rescheduled.v1"
    )
    assert packet["temporal_signal"]["aggregate_class"] == "APPOINTMENT"
    assert packet["temporal_signal"]["affected_frame_types"] == list(
        MANDATORY_FRAME_FLOOR
    )


def test_positive_admission_binds_one_reconstructed_signal_digest() -> None:
    values = _inputs()
    observation, admission = _admit(values)
    assert observation is not None
    assert admission["decision"] == "ADMIT_SIGNAL"
    assert admission["ordinary_temporal_signal_emitted"] is True
    assert admission["conservative_impact_frame_types"] == list(MANDATORY_FRAME_FLOOR)
    signal, trace = map_observation_to_temporal_signal(
        observation, admission, values["registry"], values["impact"]
    )
    assert admission["signal_digest"] == signal["signal_digest"]
    assert trace["source_event_schema_version"] == ("diary.appointment_rescheduled.v1")
    assert trace["temporal_event_schema_version"] == (
        "emr4.diary.appointment_rescheduled.v1"
    )
    assert trace["impact_floor_preserved"] is True
    assert trace["source_selector_used"] is False


def test_activation_mode_and_observation_evidence_are_distinct_exact_fields() -> None:
    values = _inputs()
    assert values["activation"]["activation_mode"] == ACTIVATION_MODE
    assert values["source"]["evidence_mode"] == "AUTHORED_SYNTHETIC"
    values["source"]["evidence_mode"] = "LIVE"
    _activate(values)
    decision = _decision(values, "OBSERVER_DISABLED")
    assert decision["reason_codes"] == ["SYNTHETIC_ACTIVATION_REQUIRED"]


@pytest.mark.parametrize("activation_state", ["missing", "expired", "substituted"])
def test_disabled_policy_requires_exact_current_synthetic_activation(
    activation_state: str,
) -> None:
    values = _inputs()
    if activation_state == "missing":
        values["activation"] = None
    elif activation_state == "expired":
        values["activation"]["expires_at"] = "2026-08-06T03:00:11Z"
        values["activation"] = _reseal(values["activation"], "activation_digest")
    else:
        values["activation"]["binding_digest"] = "sha256:" + "1" * 64
        values["activation"] = _reseal(values["activation"], "activation_digest")
    _decision(values, "OBSERVER_DISABLED")


def test_hmac_identity_binds_all_frozen_scope_coordinates() -> None:
    values = _inputs()
    policy = values["policy"]
    binding = values["binding"]
    base = {
        "practice_binding_digest": policy["practice_binding_digest"],
        "source_system_id": SOURCE_SYSTEM_ID,
        "source_contract_id": SOURCE_CONTRACT_ID,
        "source_contract_digest": policy["source_contract_digest"],
        "observer_id": binding["observer_id"],
        "observer_generation": binding["observer_generation"],
        "hmac_key": KEY,
    }
    original = derive_observation_id(RAW_ID, **base)
    variants = [
        {**base, "practice_binding_digest": "sha256:" + "2" * 64},
        {**base, "source_system_id": "AUTHORED_SYNTHETIC_SOURCE_HARNESS_TWO"},
        {
            **base,
            "source_contract_id": "emr4.synthetic_committed_change_control_metadata.v2",
        },
        {**base, "source_contract_digest": "sha256:" + "3" * 64},
        {**base, "observer_id": "synthetic:observer:002"},
        {**base, "observer_generation": 2},
    ]
    assert all(
        derive_observation_id(RAW_ID, **variant) != original for variant in variants
    )


def test_raw_event_id_and_hmac_key_never_cross_output_boundary() -> None:
    packet = build_authored_synthetic_observation_to_signal_packet()
    serialized = json.dumps(packet, sort_keys=True)
    assert RAW_ID not in serialized
    assert KEY.decode("ascii") not in serialized
    assert packet["proofreader_trace"]["raw_source_event_id_released"] is False
    assert packet["proofreader_trace"]["hmac_key_released"] is False


def test_unknown_source_field_fails_before_hashing_or_classification() -> None:
    values = _inputs()
    values["source"]["selector_digest"] = "sha256:" + "4" * 64
    with pytest.raises(
        ObservationToSignalViolation, match="source_input_shape_invalid"
    ):
        _admit(values)


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("transaction_position", True, "transaction_position_invalid"),
        ("aggregate_revision", 0, "aggregate_revision_invalid"),
        ("aggregate_alias", "not-an-alias", "aggregate_alias_invalid"),
        (
            "source_transaction_committed_at",
            "2026-08-06T03:00:10+00:00",
            "timestamp_not_canonical_utc",
        ),
    ],
)
def test_malformed_typed_source_coordinates_fail_closed(
    field: str, value: object, error: str
) -> None:
    values = _inputs()
    values["source"][field] = value
    with pytest.raises(ObservationToSignalViolation, match=error):
        _admit(values)


@pytest.mark.parametrize("raw_id", [None, 1, True, {}, []])
def test_malformed_raw_event_identity_has_closed_domain_error(raw_id: object) -> None:
    values = _inputs()
    values["source"]["raw_source_event_id"] = raw_id
    with pytest.raises(ObservationToSignalViolation, match="raw_event_id_invalid"):
        _admit(values)


@pytest.mark.parametrize(
    ("contract", "field", "value"),
    [
        ("registry", "command_authority", True),
        ("registry", "read_only", False),
        ("impact", "command_authority", True),
        ("impact", "read_only", False),
    ],
)
def test_coordinated_resealed_authority_widening_never_admits(
    contract: str, field: str, value: object
) -> None:
    values = _inputs()
    digest_field = (
        "alias_registry_digest" if contract == "registry" else "impact_policy_digest"
    )
    values[contract][field] = value
    values[contract] = _reseal(values[contract], digest_field)
    _coordinate_trusted_contracts(values)
    with pytest.raises(ObservationToSignalViolation, match="contract_not_exact"):
        _admit(values)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema_version", "emr4.substituted.v1"),
        ("policy_id", "synthetic:substituted-policy:001"),
        ("policy_version", 2),
        ("allowed_sensitivities", ["PUBLIC"]),
        ("required_authentication_kinds", ["SUBSTITUTED"]),
        ("continuity_mode", "BEST_EFFORT"),
        ("source_contract_digest", "sha256:" + "6" * 64),
    ],
)
def test_coordinated_resealed_policy_substitution_is_structurally_rejected(
    field: str, value: object
) -> None:
    values = _inputs()
    values["policy"][field] = value
    values["policy"] = _reseal(values["policy"], "policy_digest")
    values["binding"] = build_live_source_observer_binding(
        values["policy"], values["registry"], values["impact"]
    )
    _activate(values)
    values["prior"] = build_observation_prior_coordinate(
        practice_binding_digest=values["policy"]["practice_binding_digest"],
        policy=values["policy"],
        binding=values["binding"],
        alias_registry=values["registry"],
        impact_policy=values["impact"],
    )
    with pytest.raises(ObservationToSignalViolation, match="policy_contract_not_exact"):
        _admit(values)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema_version", "emr4.substituted.v1"),
        ("binding_id", "synthetic:substituted-binding:001"),
        ("integration_principal_digest", "sha256:" + "7" * 64),
        ("authentication_kind", "SUBSTITUTED"),
        ("allowed_event_types", []),
        ("read_authority", True),
        ("provider_authority", True),
        ("command_authority", True),
        ("persistence_authority", True),
    ],
)
def test_resealed_binding_substitution_is_structurally_rejected(
    field: str, value: object
) -> None:
    values = _inputs()
    values["binding"][field] = value
    values["binding"] = _reseal(values["binding"], "binding_digest")
    _activate(values)
    values["prior"] = build_observation_prior_coordinate(
        practice_binding_digest=values["policy"]["practice_binding_digest"],
        policy=values["policy"],
        binding=values["binding"],
        alias_registry=values["registry"],
        impact_policy=values["impact"],
    )
    with pytest.raises(ObservationToSignalViolation):
        _admit(values)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema_version", "emr4.substituted.v1"),
        ("activation_id", "synthetic:substituted-activation:001"),
        ("plan_version", "2026-08-06.substituted"),
    ],
)
def test_resealed_activation_identity_substitution_keeps_observer_disabled(
    field: str, value: object
) -> None:
    values = _inputs()
    values["activation"][field] = value
    values["activation"] = _reseal(values["activation"], "activation_digest")
    _decision(values, "OBSERVER_DISABLED")


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("schema_version", "emr4.substituted.v1", "prior_coordinate_schema_invalid"),
        ("baseline_established", 1, "prior_baseline_established_invalid"),
        ("aggregate_revisions", {}, "prior_aggregate_revision_shape_invalid"),
        ("observer_generation", True, "prior_observer_generation_invalid"),
        ("observer_id", 7, "prior_observer_id_invalid"),
    ],
)
def test_malformed_prior_coordinate_types_fail_structurally(
    field: str, value: object, error: str
) -> None:
    values = _inputs()
    values["prior"][field] = value
    values["prior"] = _reseal(values["prior"], "coordinate_digest")
    with pytest.raises(ObservationToSignalViolation, match=error):
        _admit(values)


def test_foreign_scope_precedes_expiry() -> None:
    values = _inputs()
    values["source"]["practice_binding_digest"] = "sha256:" + "5" * 64
    values["binding"]["revoked"] = True
    values["binding"] = _reseal(values["binding"], "binding_digest")
    # Activation is deliberately rebuilt for the changed fixture and binding.
    _activate(values)
    # Prior binding is trusted and therefore rebuilt for the changed binding.
    values["prior"] = build_observation_prior_coordinate(
        practice_binding_digest=values["policy"]["practice_binding_digest"],
        policy=values["policy"],
        binding=values["binding"],
        alias_registry=values["registry"],
        impact_policy=values["impact"],
    )
    _decision(values, "BLOCK_FOREIGN_SCOPE")


def test_wrong_source_schema_is_blocked_and_not_silently_relabelled() -> None:
    values = _inputs()
    values["source"]["event_schema_version"] = "emr4.diary.appointment_rescheduled.v1"
    _activate(values)
    _decision(values, "BLOCK_SCHEMA_OR_POLICY")


@pytest.mark.parametrize("mode", ["expired", "revoked"])
def test_expired_or_revoked_binding_is_blocked(mode: str) -> None:
    values = _inputs()
    if mode == "expired":
        values["binding"]["expires_at"] = "2026-08-06T03:00:11Z"
    else:
        values["binding"]["revoked"] = True
    values["binding"] = _reseal(values["binding"], "binding_digest")
    _activate(values)
    values["prior"] = build_observation_prior_coordinate(
        practice_binding_digest=values["policy"]["practice_binding_digest"],
        policy=values["policy"],
        binding=values["binding"],
        alias_registry=values["registry"],
        impact_policy=values["impact"],
    )
    _decision(values, "BLOCK_EXPIRED_OR_REVOKED")


def test_exact_seen_observation_is_suppressed_as_duplicate() -> None:
    values = _inputs()
    digest = derive_observation_id(
        RAW_ID,
        practice_binding_digest=values["policy"]["practice_binding_digest"],
        source_system_id=SOURCE_SYSTEM_ID,
        source_contract_id=SOURCE_CONTRACT_ID,
        source_contract_digest=values["policy"]["source_contract_digest"],
        observer_id=values["binding"]["observer_id"],
        observer_generation=values["binding"]["observer_generation"],
        hmac_key=KEY,
    )
    values["prior"]["seen_observation_ids"] = [digest]
    values["prior"] = _reseal(values["prior"], "coordinate_digest")
    _decision(values, "SUPPRESS_DUPLICATE")


def test_older_position_is_suppressed_as_replay_before_gap_reasoning() -> None:
    values = _inputs()
    values["source"]["expected_predecessor_position"] = 99
    values["source"]["transaction_position"] = 100
    _activate(values)
    _decision(values, "SUPPRESS_REPLAY")


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        ({"baseline_established": False}, "BASELINE_NOT_ESTABLISHED"),
        ({"restart_uncertain": True}, "RESTART_UNCERTAINTY"),
        ({"overflow_detected": True}, "PRIOR_OVERFLOW_UNCERTAINTY"),
    ],
)
def test_prior_uncertainty_requires_admission_only_full_invalidation(
    mutation: dict, reason: str
) -> None:
    values = _inputs()
    values["prior"].update(mutation)
    values["prior"] = _reseal(values["prior"], "coordinate_digest")
    decision = _decision(values, "FULL_INVALIDATION_REQUIRED")
    assert reason in decision["reason_codes"]
    _assert_full_invalidation_shape(decision)


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("expected_predecessor_position", 99, "EXPECTED_PREDECESSOR_MISMATCH"),
        ("transaction_position", 102, "TRANSACTION_POSITION_GAP"),
        ("aggregate_revision", 13, "AGGREGATE_REVISION_GAP"),
        ("transaction_position", MAX_SAFE_INTEGER + 1, "POSITION_OR_REVISION_OVERFLOW"),
    ],
)
def test_continuity_uncertainty_has_exact_full_invalidation_shape(
    field: str, value: int, reason: str
) -> None:
    values = _inputs()
    values["source"][field] = value
    _activate(values)
    decision = _decision(values, "FULL_INVALIDATION_REQUIRED")
    assert reason in decision["reason_codes"]
    _assert_full_invalidation_shape(decision)


def _assert_full_invalidation_shape(decision: dict) -> None:
    assert decision["conservative_impact_frame_types"] == list(MANDATORY_FRAME_FLOOR)
    assert decision["ordinary_temporal_signal_emitted"] is False
    assert decision["signal_digest"] is None
    assert decision["checkpoint_advanced"] is False
    assert decision["durable_handoff_implemented"] is False
    for field in (
        "returns_data",
        "read_authority",
        "provider_authority",
        "command_authority",
        "persistence_authority",
    ):
        assert decision[field] is False


def test_unresolved_backend_alias_requires_full_invalidation_not_irrelevance() -> None:
    values = _inputs()
    values["source"]["aggregate_alias"] = "syn/v1/aggregate/ffffffffffffffff"
    values["prior"]["aggregate_revisions"] = [
        {
            "aggregate_alias": values["source"]["aggregate_alias"],
            "aggregate_revision": 11,
        }
    ]
    values["prior"] = _reseal(values["prior"], "coordinate_digest")
    _activate(values)
    decision = _decision(values, "FULL_INVALIDATION_REQUIRED")
    assert decision["reason_codes"] == ["ALIAS_OR_IMPACT_UNRESOLVED"]
    _assert_full_invalidation_shape(decision)


def test_non_admit_decision_cannot_be_mapped_to_temporal_signal() -> None:
    packet = build_authored_synthetic_observation_to_signal_packet()
    admission = deepcopy(packet["admission_decision"])
    admission["decision"] = "FULL_INVALIDATION_REQUIRED"
    admission["ordinary_temporal_signal_emitted"] = False
    admission["signal_digest"] = None
    admission = _reseal(admission, "admission_digest")
    with pytest.raises(ObservationToSignalViolation, match="only_admit_signal_may_map"):
        map_observation_to_temporal_signal(
            packet["observation"],
            admission,
            packet["alias_registry"],
            packet["impact_policy"],
        )


def test_public_mapping_rejects_coordinated_resealed_registry_widening() -> None:
    values = _inputs()
    observation, admission = _admit(values)
    assert observation is not None
    values["registry"]["command_authority"] = True
    values["registry"] = _reseal(values["registry"], "alias_registry_digest")
    observation["alias_registry_digest"] = values["registry"]["alias_registry_digest"]
    observation = _reseal(observation, "observation_digest")
    admission["alias_registry_digest"] = values["registry"]["alias_registry_digest"]
    admission["observation_digest"] = observation["observation_digest"]
    admission = _reseal(admission, "admission_digest")
    with pytest.raises(
        ObservationToSignalViolation, match="alias_registry_contract_not_exact"
    ):
        map_observation_to_temporal_signal(
            observation, admission, values["registry"], values["impact"]
        )


def test_public_mapping_rejects_coordinated_resealed_observation_links() -> None:
    values = _inputs()
    observation, admission = _admit(values)
    assert observation is not None
    observation["policy_digest"] = "sha256:" + "8" * 64
    observation = _reseal(observation, "observation_digest")
    admission["policy_digest"] = observation["policy_digest"]
    admission["observation_digest"] = observation["observation_digest"]
    admission = _reseal(admission, "admission_digest")
    with pytest.raises(
        ObservationToSignalViolation, match="observation_contract_not_exact"
    ):
        map_observation_to_temporal_signal(
            observation, admission, values["registry"], values["impact"]
        )


def test_public_mapping_rejects_resealed_alias_resolution_substitution() -> None:
    values = _inputs()
    observation, admission = _admit(values)
    assert observation is not None
    values["registry"]["entries"][0]["aggregate_ref"] = (
        "synthetic:appointment:substituted"
    )
    values["registry"] = _reseal(values["registry"], "alias_registry_digest")
    with pytest.raises(
        ObservationToSignalViolation, match="alias_registry_contract_not_exact"
    ):
        map_observation_to_temporal_signal(
            observation, admission, values["registry"], values["impact"]
        )


def test_public_mapping_rejects_resealed_impact_route_substitution() -> None:
    values = _inputs()
    observation, admission = _admit(values)
    assert observation is not None
    values["impact"]["routes"][0]["temporal_event_schema_version"] = (
        "emr4.substituted.v1"
    )
    values["impact"] = _reseal(values["impact"], "impact_policy_digest")
    with pytest.raises(
        ObservationToSignalViolation, match="impact_policy_contract_not_exact"
    ):
        map_observation_to_temporal_signal(
            observation, admission, values["registry"], values["impact"]
        )


def test_temporal_handoff_retires_without_mutating_old_frame_bytes_or_reading() -> None:
    packet = build_authored_synthetic_observation_to_signal_packet()
    assert packet["temporal_invalidation_decision"]["decision"] == (
        "REASSEMBLY_REQUIRED"
    )
    assert packet["temporal_frame_set_state"]["state"] == "REASSEMBLY_REQUIRED"
    assert packet["old_frame_set_bytes_unchanged"] is True
    assert packet["temporal_reassembly_requirement"]["execution_enabled"] is False
    assert packet["temporal_reassembly_requirement"]["returns_data"] is False
    assert packet["temporal_trace"]["source_read_executed"] is False


def test_all_runtime_authority_and_effect_flags_are_false() -> None:
    packet = build_authored_synthetic_observation_to_signal_packet()
    false_fields = {
        "source_connection",
        "credential_acquisition",
        "source_read_executed",
        "fresh_read_executed",
        "listener_mounted",
        "runtime_state_mounted",
        "filesystem_effects",
        "network_effects",
        "database_effects",
        "subprocess_effects",
        "checkpoint_persisted",
        "provider_called",
        "command_executed",
        "returns_data",
        "read_authority",
        "provider_authority",
        "command_authority",
        "persistence_authority",
    }
    assert all(packet[field] is False for field in false_fields)
    assert packet["read_only"] is True


@pytest.mark.parametrize(
    ("path", "field", "value", "digest_field"),
    [
        ("policy", "enabled", True, "policy_digest"),
        ("observer_binding", "read_authority", True, "binding_digest"),
        ("alias_registry", "backend_issued_only", False, "alias_registry_digest"),
        ("impact_policy", "source_may_supply_impact", True, "impact_policy_digest"),
        ("observation", "aggregate_revision", 13, "observation_digest"),
        ("temporal_signal", "command_authority", True, "signal_digest"),
    ],
)
def test_self_consistently_resealed_substitution_is_blocked(
    path: str, field: str, value: object, digest_field: str
) -> None:
    packet = build_authored_synthetic_observation_to_signal_packet()
    packet[path][field] = value
    packet[path] = _reseal(packet[path], digest_field)
    proof = proofread_observation_to_signal_packet(packet)
    assert proof["release_decision"] == "BLOCK"


def test_recursively_unknown_packet_field_is_blocked() -> None:
    packet = build_authored_synthetic_observation_to_signal_packet()
    packet["observation"]["callback"] = "run-read"
    packet["observation"] = _reseal(packet["observation"], "observation_digest")
    assert proofread_observation_to_signal_packet(packet)["release_decision"] == (
        "BLOCK"
    )
    with pytest.raises(ObservationToSignalViolation, match="closed_keys_mismatch"):
        validate_observation_to_signal_packet(packet)


def test_proofreader_blocks_expiry() -> None:
    packet = build_authored_synthetic_observation_to_signal_packet()
    proof = proofread_observation_to_signal_packet(
        packet, checked_at=packet["observation"]["expires_at"]
    )
    assert proof["release_decision"] == "BLOCK"
    assert "PACKET_EXPIRED" in proof["reason_codes"]


def test_closed_decision_and_reason_enums_are_exact() -> None:
    assert ADMISSION_DECISIONS == {
        "ADMIT_SIGNAL",
        "SUPPRESS_DUPLICATE",
        "SUPPRESS_REPLAY",
        "BLOCK_FOREIGN_SCOPE",
        "BLOCK_SCHEMA_OR_POLICY",
        "BLOCK_EXPIRED_OR_REVOKED",
        "FULL_INVALIDATION_REQUIRED",
        "OBSERVER_DISABLED",
    }
    packet = build_authored_synthetic_observation_to_signal_packet()
    assert set(packet["admission_decision"]["reason_codes"]).issubset(
        ADMISSION_REASON_CODES
    )


def test_pure_module_has_no_runtime_product_or_side_effect_surface() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    modules = set()
    calls = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".", 1)[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr)
    assert not modules.intersection(
        {
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
    )
    assert not calls.intersection(
        {
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
    )


def test_generated_closed_schema_example_and_evidence_reproduce_exactly() -> None:
    packet, schema, evidence = build_acceptance_evidence()
    assert packet == _json(CONTINUITY_DIR / "authored-synthetic-example.json")
    assert schema == _json(CONTINUITY_DIR / "contract.schema.json")
    assert evidence == _json(CONTINUITY_DIR / "provider-free-acceptance-evidence.json")
    assert not list(Draft202012Validator(schema).iter_errors(packet))
    assert evidence["passed"] is True
    assert (
        evidence["case_count"] == evidence["passed_case_count"] == len(ACCEPTANCE_CASES)
    )
    assert set(evidence["authority_and_side_effect_counts"].values()) == {0}
    assert set(evidence["static_surface_counts"].values()) == {0}


def test_evidence_artifact_hashes_match_direct_bytes_and_canonical_schema() -> None:
    evidence = _json(CONTINUITY_DIR / "provider-free-acceptance-evidence.json")
    root = CONTINUITY_DIR.parents[2]
    direct = {
        "pure_rehearsal_module": root
        / "scripts"
        / "raisa_provider_free_unmounted_authored_synthetic_observation_to_temporal_signal_rehearsal.py",
        "acceptance_generator": root
        / "scripts"
        / "raisa_provider_free_unmounted_authored_synthetic_observation_to_temporal_signal_rehearsal_acceptance.py",
        "accepted_temporal_module": root
        / "scripts"
        / "raisa_provider_free_practice_context_fabric_patient_free_temporal_weave.py",
        "frozen_plan": root
        / "docs"
        / "raisa-provider-free-unmounted-authored-synthetic-observation-to-temporal-signal-rehearsal-plan.md",
        "frozen_design": root
        / "docs"
        / "raisa-provider-free-unmounted-authored-synthetic-observation-to-temporal-signal-rehearsal-design.md",
        "frozen_threat_delta": root
        / "docs"
        / "security"
        / "raisa-provider-free-unmounted-authored-synthetic-observation-to-temporal-signal-rehearsal-threat-model-delta.md",
    }
    for name, path in direct.items():
        assert evidence["artifact_hashes"][name] == (
            "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        )
    schema_path = CONTINUITY_DIR / "contract.schema.json"
    assert evidence["artifact_hashes"]["contract_schema"] == (
        "sha256:" + hashlib.sha256(schema_path.read_bytes()).hexdigest()
    )


def test_owned_artifacts_are_repository_local_and_exclude_branding() -> None:
    paths = [
        MODULE_PATH,
        CONTINUITY_DIR / "contract.schema.json",
        CONTINUITY_DIR / "authored-synthetic-example.json",
        CONTINUITY_DIR / "provider-free-acceptance-evidence.json",
        Path(__file__),
    ]
    root = Path(__file__).resolve().parents[1]
    for path in paths:
        assert path.is_file()
        assert root in path.parents
        assert not path.is_relative_to(root / "docs" / "branding")
        text = path.read_text(encoding="utf-8")
        assert "C:" + "\\Users\\" not in text
        assert "C:" + "/Users/" not in text
