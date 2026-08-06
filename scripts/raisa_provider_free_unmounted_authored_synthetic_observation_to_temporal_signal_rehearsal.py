"""Pure unmounted authored-synthetic observation-to-temporal-signal rehearsal.

This module is deliberately a deterministic contract library.  It opens no
source, listener, database, network, provider, command, checkpoint, or runtime
surface.  Source-shaped metadata is untrusted; trusted policy and registry
objects alone determine whether one accepted temporal signal may be built.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import hmac
import re
from typing import Any

from scripts.raisa_provider_free_practice_context_fabric_bureau_memory_contract import (
    ContractViolation,
    canonical_sha256,
    seal,
    verify_seal,
)
from scripts.raisa_provider_free_practice_context_fabric_current_operational_weave import (
    build_authored_synthetic_packet,
)
from scripts.raisa_provider_free_practice_context_fabric_patient_free_temporal_weave import (
    derive_dependency_manifest,
    derive_watch_lease,
    make_signal,
    process_signals,
)


SCHEMA_VERSION = (
    "emr4.practice_context_fabric_observation_to_temporal_signal_rehearsal.v1"
)
SOURCE_CONTRACT_ID = "emr4.synthetic_committed_change_control_metadata.v1"
SOURCE_SYSTEM_ID = "AUTHORED_SYNTHETIC_SOURCE_HARNESS"
EVIDENCE_LABEL = "provider_free_authored_synthetic_unmounted_observation_to_temporal_signal_rehearsal"
DATA_CLASS = "authored_synthetic_payload_free_control_metadata"
RESULT = (
    "raisa_provider_free_unmounted_authored_synthetic_observation_to_temporal_"
    "signal_rehearsal_pass"
)
MAX_SAFE_INTEGER = 9_007_199_254_740_991
OBSERVATION_ID_DOMAIN = b"emr4:observation-id:v1\x00"

EVENT_TYPE = "diary.appointment_rescheduled"
SOURCE_EVENT_SCHEMA_VERSION = "diary.appointment_rescheduled.v1"
TEMPORAL_EVENT_SCHEMA_VERSION = "emr4.diary.appointment_rescheduled.v1"
AGGREGATE_CLASS = "APPOINTMENT"
MANDATORY_FRAME_FLOOR = (
    "current_diary_projection",
    "current_waiting_room_projection",
)
SENSITIVITY = "PATIENT_FREE_CONTROL_METADATA"
ACTIVATION_MODE = "AUTHORED_SYNTHETIC_REHEARSAL"
SYNTHETIC_EVIDENCE_MODE = "AUTHORED_SYNTHETIC"

ADMISSION_DECISIONS = frozenset(
    {
        "ADMIT_SIGNAL",
        "SUPPRESS_DUPLICATE",
        "SUPPRESS_REPLAY",
        "BLOCK_FOREIGN_SCOPE",
        "BLOCK_SCHEMA_OR_POLICY",
        "BLOCK_EXPIRED_OR_REVOKED",
        "FULL_INVALIDATION_REQUIRED",
        "OBSERVER_DISABLED",
    }
)
ADMISSION_REASON_CODES = frozenset(
    {
        "ADMISSION_CHECKS_PASSED",
        "EXACT_OBSERVATION_DUPLICATE",
        "TRANSACTION_POSITION_REPLAY",
        "FOREIGN_PRACTICE_OR_SOURCE",
        "SCHEMA_POLICY_OR_CONTRACT_MISMATCH",
        "BINDING_EXPIRED_OR_REVOKED",
        "BASELINE_NOT_ESTABLISHED",
        "EXPECTED_PREDECESSOR_MISMATCH",
        "TRANSACTION_POSITION_GAP",
        "AGGREGATE_REVISION_GAP",
        "POSITION_OR_REVISION_OVERFLOW",
        "STREAM_OR_OBSERVER_GENERATION_MISMATCH",
        "RESTART_UNCERTAINTY",
        "PRIOR_OVERFLOW_UNCERTAINTY",
        "ALIAS_OR_IMPACT_UNRESOLVED",
        "SYNTHETIC_ACTIVATION_REQUIRED",
    }
)

_DIGEST_RE = re.compile(r"sha256:[0-9a-f]{64}\Z")
_ALIAS_RE = re.compile(
    r"syn/v1/(aggregate|stream|location|practitioner)/[a-z0-9]{16,32}\Z"
)
_RAW_EVENT_ID_RE = re.compile(r"evt_[a-z0-9]{32}\Z")
_OBSERVER_ID_RE = re.compile(r"synthetic:observer:[a-z0-9-]{1,32}\Z")
_SOURCE_SYSTEM_RE = re.compile(r"[A-Z][A-Z0-9_]{2,63}\Z")
_SOURCE_CONTRACT_RE = re.compile(r"emr4\.[a-z0-9_.-]{3,96}\Z")
_UTC_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z\Z")

SOURCE_INPUT_KEYS = {
    "schema_version",
    "source_system_id",
    "source_contract_id",
    "practice_binding_digest",
    "event_type",
    "event_schema_version",
    "aggregate_class",
    "raw_source_event_id",
    "aggregate_alias",
    "stream_alias",
    "aggregate_revision",
    "expected_predecessor_position",
    "transaction_position",
    "source_transaction_committed_at",
    "committed",
    "evidence_mode",
}
PRIOR_COORDINATE_KEYS = {
    "schema_version",
    "practice_binding_digest",
    "source_system_id",
    "source_contract_id",
    "source_contract_digest",
    "observer_id",
    "observer_generation",
    "policy_digest",
    "binding_digest",
    "alias_registry_digest",
    "impact_policy_digest",
    "stream_alias",
    "baseline_established",
    "last_transaction_position",
    "aggregate_revisions",
    "seen_observation_ids",
    "restart_uncertain",
    "overflow_detected",
    "checkpoint_persisted",
    "runtime_checkpoint",
    "coordinate_digest",
}
POLICY_KEYS = {
    "schema_version",
    "policy_id",
    "policy_version",
    "practice_binding_digest",
    "source_system_id",
    "source_contract_id",
    "source_contract_digest",
    "allowed_event_types",
    "allowed_event_schema_versions",
    "allowed_aggregate_classes",
    "allowed_sensitivities",
    "required_authentication_kinds",
    "maximum_events_per_minute",
    "maximum_batch_size",
    "maximum_clock_skew_seconds",
    "continuity_mode",
    "alias_registry_digest",
    "impact_policy_id",
    "impact_policy_digest",
    "issued_at",
    "expires_at",
    "enabled_by_default",
    "enabled",
    "payload_allowed",
    "persistence_authority",
    "policy_digest",
}
BINDING_KEYS = {
    "schema_version",
    "binding_id",
    "observer_id",
    "observer_generation",
    "integration_principal_digest",
    "authentication_kind",
    "practice_binding_digest",
    "source_system_id",
    "source_contract_id",
    "source_contract_digest",
    "policy_version",
    "policy_digest",
    "allowed_event_types",
    "allowed_event_schema_versions",
    "allowed_aggregate_classes",
    "alias_registry_digest",
    "impact_policy_digest",
    "issued_at",
    "not_before",
    "expires_at",
    "revoked",
    "returns_data",
    "read_authority",
    "provider_authority",
    "command_authority",
    "persistence_authority",
    "binding_digest",
}
REGISTRY_KEYS = {
    "schema_version",
    "registry_id",
    "registry_version",
    "practice_binding_digest",
    "source_system_id",
    "source_contract_id",
    "aggregate_class",
    "entries",
    "stream_entries",
    "backend_issued_only",
    "read_only",
    "command_authority",
    "alias_registry_digest",
}
IMPACT_POLICY_KEYS = {
    "schema_version",
    "impact_policy_id",
    "impact_policy_version",
    "routes",
    "source_may_supply_impact",
    "unknown_impact_decision",
    "read_only",
    "command_authority",
    "impact_policy_digest",
}
ACTIVATION_KEYS = {
    "schema_version",
    "activation_id",
    "plan_version",
    "policy_digest",
    "binding_digest",
    "fixture_digest",
    "activation_mode",
    "evidence_mode",
    "not_before",
    "expires_at",
    "source_connection",
    "credential_acquisition",
    "cursor_persistence",
    "returns_data",
    "read_authority",
    "provider_authority",
    "command_authority",
    "persistence_authority",
    "activation_digest",
}


class ObservationToSignalViolation(ContractViolation):
    """Raised when the pure observation membrane fails closed."""


def _instant(value: str) -> datetime:
    if not isinstance(value, str) or not _UTC_RE.fullmatch(value):
        raise ObservationToSignalViolation("timestamp_not_canonical_utc")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ObservationToSignalViolation("timestamp_invalid") from error
    return parsed.astimezone(timezone.utc)


def _expect_exact_keys(value: Any, expected: set[str], code: str) -> None:
    if not isinstance(value, dict) or set(value) != expected:
        raise ObservationToSignalViolation(code)


def _expect_digest(value: Any, code: str) -> None:
    if not isinstance(value, str) or not _DIGEST_RE.fullmatch(value):
        raise ObservationToSignalViolation(code)


def _expect_alias(value: Any, kind: str, code: str) -> None:
    if (
        not isinstance(value, str)
        or len(value) > 96
        or not _ALIAS_RE.fullmatch(value)
        or not value.startswith(f"syn/v1/{kind}/")
    ):
        raise ObservationToSignalViolation(code)


def _expect_positive_integer(
    value: Any, code: str, *, allow_overflow: bool = False
) -> None:
    if type(value) is not int or value < 1:
        raise ObservationToSignalViolation(code)
    if not allow_overflow and value > MAX_SAFE_INTEGER:
        raise ObservationToSignalViolation(code)


def _verify(value: dict[str, Any], field: str) -> None:
    try:
        verify_seal(value, field)
    except ContractViolation as error:
        raise ObservationToSignalViolation(f"{field}_invalid") from error


def _validate_closed_typed(supplied: Any, trusted: Any, *, path: str = "$") -> None:
    if type(supplied) is not type(trusted):
        raise ObservationToSignalViolation(f"closed_type_mismatch:{path}")
    if isinstance(trusted, dict):
        if set(supplied) != set(trusted):
            raise ObservationToSignalViolation(f"closed_keys_mismatch:{path}")
        for key in sorted(trusted):
            _validate_closed_typed(supplied[key], trusted[key], path=f"{path}.{key}")
    elif isinstance(trusted, list):
        if len(supplied) != len(trusted):
            raise ObservationToSignalViolation(f"closed_list_length_mismatch:{path}")
        for index, item in enumerate(trusted):
            _validate_closed_typed(supplied[index], item, path=f"{path}[{index}]")


def derive_observation_id(
    raw_source_event_id: str,
    *,
    practice_binding_digest: str,
    source_system_id: str,
    source_contract_id: str,
    source_contract_digest: str,
    observer_id: str,
    observer_generation: int,
    hmac_key: bytes,
) -> str:
    """Return a domain-separated keyed digest and never retain the raw id/key."""

    if not isinstance(raw_source_event_id, str) or not _RAW_EVENT_ID_RE.fullmatch(
        raw_source_event_id
    ):
        raise ObservationToSignalViolation("raw_event_id_invalid")
    if not isinstance(source_contract_id, str) or not _SOURCE_CONTRACT_RE.fullmatch(
        source_contract_id
    ):
        raise ObservationToSignalViolation("source_contract_not_admitted")
    if not isinstance(source_system_id, str) or not _SOURCE_SYSTEM_RE.fullmatch(
        source_system_id
    ):
        raise ObservationToSignalViolation("source_system_not_admitted")
    _expect_digest(practice_binding_digest, "practice_binding_digest_invalid")
    _expect_digest(source_contract_digest, "source_contract_digest_invalid")
    if not isinstance(observer_id, str) or not _OBSERVER_ID_RE.fullmatch(observer_id):
        raise ObservationToSignalViolation("observer_id_not_admitted")
    _expect_positive_integer(observer_generation, "observer_generation_invalid")
    if not isinstance(hmac_key, bytes) or len(hmac_key) < 32:
        raise ObservationToSignalViolation("hmac_key_too_short")
    message = (
        OBSERVATION_ID_DOMAIN
        + practice_binding_digest.encode("ascii")
        + b"\x00"
        + source_system_id.encode("ascii")
        + b"\x00"
        + source_contract_id.encode("ascii")
        + b"\x00"
        + source_contract_digest.encode("ascii")
        + b"\x00"
        + observer_id.encode("ascii")
        + b"\x00"
        + str(observer_generation).encode("ascii")
        + b"\x00"
        + raw_source_event_id.encode("ascii")
    )
    return "sha256:" + hmac.new(hmac_key, message, hashlib.sha256).hexdigest()


def build_live_source_observation_policy(
    practice_binding_digest: str,
    *,
    alias_registry_digest: str,
    impact_policy_digest: str,
) -> dict[str, Any]:
    _expect_digest(practice_binding_digest, "practice_binding_digest_invalid")
    _expect_digest(alias_registry_digest, "alias_registry_digest_invalid")
    _expect_digest(impact_policy_digest, "impact_policy_digest_invalid")
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "policy_id": "synthetic:live-source-observation-policy:001",
            "policy_version": 1,
            "practice_binding_digest": practice_binding_digest,
            "source_system_id": SOURCE_SYSTEM_ID,
            "source_contract_id": SOURCE_CONTRACT_ID,
            "source_contract_digest": canonical_sha256(
                {
                    "source_contract_id": SOURCE_CONTRACT_ID,
                    "source_event_type": EVENT_TYPE,
                    "source_event_schema": SOURCE_EVENT_SCHEMA_VERSION,
                    "temporal_event_schema": TEMPORAL_EVENT_SCHEMA_VERSION,
                    "aggregate_class": AGGREGATE_CLASS,
                }
            ),
            "allowed_event_types": [EVENT_TYPE],
            "allowed_event_schema_versions": [SOURCE_EVENT_SCHEMA_VERSION],
            "allowed_aggregate_classes": [AGGREGATE_CLASS],
            "allowed_sensitivities": [SENSITIVITY],
            "required_authentication_kinds": ["SYNTHETIC_INTEGRATION_PRINCIPAL"],
            "maximum_events_per_minute": 20,
            "maximum_batch_size": 1,
            "maximum_clock_skew_seconds": 120,
            "continuity_mode": "MONOTONIC_POSITION_AND_AGGREGATE_REVISION",
            "alias_registry_digest": alias_registry_digest,
            "impact_policy_id": "synthetic:observation-impact-policy:001",
            "impact_policy_digest": impact_policy_digest,
            "issued_at": "2026-08-06T03:00:00Z",
            "expires_at": "2026-08-06T03:02:00Z",
            "enabled_by_default": False,
            "enabled": False,
            "payload_allowed": False,
            "persistence_authority": False,
        },
        "policy_digest",
    )


def build_observation_impact_policy() -> dict[str, Any]:
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "impact_policy_id": "synthetic:observation-impact-policy:001",
            "impact_policy_version": 1,
            "routes": [
                {
                    "event_type": EVENT_TYPE,
                    "source_event_schema_version": SOURCE_EVENT_SCHEMA_VERSION,
                    "temporal_event_schema_version": TEMPORAL_EVENT_SCHEMA_VERSION,
                    "aggregate_class": AGGREGATE_CLASS,
                    "mandatory_frame_type_floor": list(MANDATORY_FRAME_FLOOR),
                    "bounded_full_invalidation_frame_types": list(
                        MANDATORY_FRAME_FLOOR
                    ),
                }
            ],
            "source_may_supply_impact": False,
            "unknown_impact_decision": "FULL_INVALIDATION_REQUIRED",
            "read_only": True,
            "command_authority": False,
        },
        "impact_policy_digest",
    )


def build_observation_alias_registry(
    practice_binding_digest: str,
) -> dict[str, Any]:
    _expect_digest(practice_binding_digest, "practice_binding_digest_invalid")
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "registry_id": "synthetic:observation-alias-registry:001",
            "registry_version": 1,
            "practice_binding_digest": practice_binding_digest,
            "source_system_id": SOURCE_SYSTEM_ID,
            "source_contract_id": SOURCE_CONTRACT_ID,
            "aggregate_class": AGGREGATE_CLASS,
            "entries": [
                {
                    "aggregate_alias": "syn/v1/aggregate/a0b1c2d3e4f5a6b7",
                    "aggregate_ref": "synthetic:appointment:one",
                    "location_aliases": ["syn/v1/location/b0c1d2e3f4a5b6c7"],
                    "location_refs": ["synthetic:location:brisbane-one"],
                    "practitioner_aliases": ["syn/v1/practitioner/c0d1e2f3a4b5c6d7"],
                    "practitioner_refs": ["synthetic:practitioner:one"],
                    "additional_frame_types": [],
                }
            ],
            "stream_entries": [
                {
                    "stream_alias": "syn/v1/stream/d0e1f2a3b4c5d6e7",
                    "stream_ref": "synthetic:practice-event-stream:001",
                }
            ],
            "backend_issued_only": True,
            "read_only": True,
            "command_authority": False,
        },
        "alias_registry_digest",
    )


def build_live_source_observer_binding(
    policy: dict[str, Any],
    alias_registry: dict[str, Any],
    impact_policy: dict[str, Any],
) -> dict[str, Any]:
    _verify(policy, "policy_digest")
    _verify(alias_registry, "alias_registry_digest")
    _verify(impact_policy, "impact_policy_digest")
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "binding_id": "synthetic:live-source-observer-binding:001",
            "observer_id": "synthetic:observer:001",
            "observer_generation": 1,
            "integration_principal_digest": canonical_sha256(
                {"principal": "synthetic:integration-principal:observation-001"}
            ),
            "authentication_kind": "SYNTHETIC_INTEGRATION_PRINCIPAL",
            "practice_binding_digest": policy["practice_binding_digest"],
            "source_system_id": policy["source_system_id"],
            "source_contract_id": policy["source_contract_id"],
            "source_contract_digest": policy["source_contract_digest"],
            "policy_version": policy["policy_version"],
            "policy_digest": policy["policy_digest"],
            "allowed_event_types": policy["allowed_event_types"],
            "allowed_event_schema_versions": policy["allowed_event_schema_versions"],
            "allowed_aggregate_classes": policy["allowed_aggregate_classes"],
            "alias_registry_digest": alias_registry["alias_registry_digest"],
            "impact_policy_digest": impact_policy["impact_policy_digest"],
            "issued_at": "2026-08-06T03:00:00Z",
            "not_before": "2026-08-06T03:00:00Z",
            "expires_at": "2026-08-06T03:02:00Z",
            "revoked": False,
            "returns_data": False,
            "read_authority": False,
            "provider_authority": False,
            "command_authority": False,
            "persistence_authority": False,
        },
        "binding_digest",
    )


def build_synthetic_observation_classification_activation(
    policy: dict[str, Any],
    binding: dict[str, Any],
    *,
    fixture_digest: str,
) -> dict[str, Any]:
    _expect_digest(fixture_digest, "fixture_digest_invalid")
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "activation_id": "synthetic:observation-classification-activation:001",
            "plan_version": "2026-08-06.frozen.v1",
            "policy_digest": policy["policy_digest"],
            "binding_digest": binding["binding_digest"],
            "fixture_digest": fixture_digest,
            "activation_mode": ACTIVATION_MODE,
            "evidence_mode": SYNTHETIC_EVIDENCE_MODE,
            "not_before": "2026-08-06T03:00:00Z",
            "expires_at": "2026-08-06T03:02:00Z",
            "source_connection": False,
            "credential_acquisition": False,
            "cursor_persistence": False,
            "returns_data": False,
            "read_authority": False,
            "provider_authority": False,
            "command_authority": False,
            "persistence_authority": False,
        },
        "activation_digest",
    )


def build_authored_synthetic_source_input(
    practice_binding_digest: str,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "source_system_id": SOURCE_SYSTEM_ID,
        "source_contract_id": SOURCE_CONTRACT_ID,
        "practice_binding_digest": practice_binding_digest,
        "event_type": EVENT_TYPE,
        "event_schema_version": SOURCE_EVENT_SCHEMA_VERSION,
        "aggregate_class": AGGREGATE_CLASS,
        "raw_source_event_id": "evt_0123456789abcdef0123456789abcdef",
        "aggregate_alias": "syn/v1/aggregate/a0b1c2d3e4f5a6b7",
        "stream_alias": "syn/v1/stream/d0e1f2a3b4c5d6e7",
        "aggregate_revision": 12,
        "expected_predecessor_position": 100,
        "transaction_position": 101,
        "source_transaction_committed_at": "2026-08-06T03:00:10Z",
        "committed": True,
        "evidence_mode": SYNTHETIC_EVIDENCE_MODE,
    }


def build_observation_prior_coordinate(
    *,
    practice_binding_digest: str,
    policy: dict[str, Any],
    binding: dict[str, Any],
    alias_registry: dict[str, Any],
    impact_policy: dict[str, Any],
) -> dict[str, Any]:
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "practice_binding_digest": practice_binding_digest,
            "source_system_id": SOURCE_SYSTEM_ID,
            "source_contract_id": SOURCE_CONTRACT_ID,
            "source_contract_digest": policy["source_contract_digest"],
            "observer_id": binding["observer_id"],
            "observer_generation": binding["observer_generation"],
            "policy_digest": policy["policy_digest"],
            "binding_digest": binding["binding_digest"],
            "alias_registry_digest": alias_registry["alias_registry_digest"],
            "impact_policy_digest": impact_policy["impact_policy_digest"],
            "stream_alias": "syn/v1/stream/d0e1f2a3b4c5d6e7",
            "baseline_established": True,
            "last_transaction_position": 100,
            "aggregate_revisions": [
                {
                    "aggregate_alias": "syn/v1/aggregate/a0b1c2d3e4f5a6b7",
                    "aggregate_revision": 11,
                }
            ],
            "seen_observation_ids": ["sha256:" + "0" * 64],
            "restart_uncertain": False,
            "overflow_detected": False,
            "checkpoint_persisted": False,
            "runtime_checkpoint": False,
        },
        "coordinate_digest",
    )


def _validate_source_input(value: dict[str, Any]) -> None:
    _expect_exact_keys(value, SOURCE_INPUT_KEYS, "source_input_shape_invalid")
    if value["schema_version"] != SCHEMA_VERSION:
        raise ObservationToSignalViolation("source_input_schema_invalid")
    _expect_digest(value["practice_binding_digest"], "practice_binding_digest_invalid")
    if not _RAW_EVENT_ID_RE.fullmatch(value["raw_source_event_id"]):
        raise ObservationToSignalViolation("raw_event_id_invalid")
    _expect_alias(value["aggregate_alias"], "aggregate", "aggregate_alias_invalid")
    _expect_alias(value["stream_alias"], "stream", "stream_alias_invalid")
    _expect_positive_integer(
        value["aggregate_revision"], "aggregate_revision_invalid", allow_overflow=True
    )
    _expect_positive_integer(
        value["expected_predecessor_position"],
        "predecessor_position_invalid",
        allow_overflow=True,
    )
    _expect_positive_integer(
        value["transaction_position"],
        "transaction_position_invalid",
        allow_overflow=True,
    )
    _instant(value["source_transaction_committed_at"])
    if value["committed"] is not True:
        raise ObservationToSignalViolation("uncommitted_input_forbidden")


def _validate_trusted_contracts(
    policy: dict[str, Any],
    binding: dict[str, Any],
    alias_registry: dict[str, Any],
    impact_policy: dict[str, Any],
) -> None:
    _expect_exact_keys(policy, POLICY_KEYS, "policy_shape_invalid")
    _expect_exact_keys(binding, BINDING_KEYS, "binding_shape_invalid")
    _expect_exact_keys(alias_registry, REGISTRY_KEYS, "alias_registry_shape_invalid")
    _expect_exact_keys(impact_policy, IMPACT_POLICY_KEYS, "impact_policy_shape_invalid")
    for value, field in (
        (policy, "policy_digest"),
        (binding, "binding_digest"),
        (alias_registry, "alias_registry_digest"),
        (impact_policy, "impact_policy_digest"),
    ):
        _verify(value, field)
    for field in (
        "policy_version",
        "maximum_events_per_minute",
        "maximum_batch_size",
        "maximum_clock_skew_seconds",
    ):
        _expect_positive_integer(policy[field], f"policy_{field}_invalid")
    _expect_positive_integer(
        binding["observer_generation"], "binding_observer_generation_invalid"
    )
    for value in (
        policy["issued_at"],
        policy["expires_at"],
        binding["issued_at"],
        binding["not_before"],
        binding["expires_at"],
    ):
        _instant(value)
    if not (
        policy["enabled_by_default"] is False
        and policy["enabled"] is False
        and policy["payload_allowed"] is False
        and policy["persistence_authority"] is False
    ):
        raise ObservationToSignalViolation("policy_default_off_ceiling_invalid")
    for field in (
        "returns_data",
        "read_authority",
        "provider_authority",
        "command_authority",
        "persistence_authority",
    ):
        if binding[field] is not False:
            raise ObservationToSignalViolation("binding_authority_ceiling_invalid")
    if binding["policy_digest"] != policy["policy_digest"]:
        raise ObservationToSignalViolation("binding_policy_mismatch")
    if not (
        binding["alias_registry_digest"]
        == alias_registry["alias_registry_digest"]
        == policy["alias_registry_digest"]
    ):
        raise ObservationToSignalViolation("alias_registry_binding_mismatch")
    if not (
        binding["impact_policy_digest"]
        == impact_policy["impact_policy_digest"]
        == policy["impact_policy_digest"]
    ):
        raise ObservationToSignalViolation("impact_policy_binding_mismatch")
    if impact_policy["source_may_supply_impact"] is not False:
        raise ObservationToSignalViolation("source_impact_authority_forbidden")
    if impact_policy["unknown_impact_decision"] != "FULL_INVALIDATION_REQUIRED":
        raise ObservationToSignalViolation("unknown_impact_must_fail_closed")
    if not (
        policy["source_system_id"] == SOURCE_SYSTEM_ID
        and policy["source_contract_id"] == SOURCE_CONTRACT_ID
        and policy["allowed_event_types"] == [EVENT_TYPE]
        and policy["allowed_event_schema_versions"] == [SOURCE_EVENT_SCHEMA_VERSION]
        and policy["allowed_aggregate_classes"] == [AGGREGATE_CLASS]
        and binding["authentication_kind"] == "SYNTHETIC_INTEGRATION_PRINCIPAL"
        and binding["observer_id"] == "synthetic:observer:001"
        and alias_registry["practice_binding_digest"]
        == policy["practice_binding_digest"]
        and alias_registry["source_system_id"] == SOURCE_SYSTEM_ID
        and alias_registry["source_contract_id"] == SOURCE_CONTRACT_ID
        and alias_registry["aggregate_class"] == AGGREGATE_CLASS
        and alias_registry["backend_issued_only"] is True
    ):
        raise ObservationToSignalViolation("trusted_scope_contract_invalid")
    if len(impact_policy["routes"]) != 1:
        raise ObservationToSignalViolation("impact_route_not_exact")
    route = impact_policy["routes"][0]
    _expect_exact_keys(
        route,
        {
            "event_type",
            "source_event_schema_version",
            "temporal_event_schema_version",
            "aggregate_class",
            "mandatory_frame_type_floor",
            "bounded_full_invalidation_frame_types",
        },
        "impact_route_shape_invalid",
    )
    if not (
        route["event_type"] == EVENT_TYPE
        and route["source_event_schema_version"] == SOURCE_EVENT_SCHEMA_VERSION
        and route["temporal_event_schema_version"] == TEMPORAL_EVENT_SCHEMA_VERSION
        and route["aggregate_class"] == AGGREGATE_CLASS
        and route["mandatory_frame_type_floor"] == list(MANDATORY_FRAME_FLOOR)
        and route["bounded_full_invalidation_frame_types"]
        == list(MANDATORY_FRAME_FLOOR)
    ):
        raise ObservationToSignalViolation("impact_route_not_exact")
    if (
        len(alias_registry["entries"]) != 1
        or len(alias_registry["stream_entries"]) != 1
    ):
        raise ObservationToSignalViolation("alias_registry_entries_not_exact")
    _expect_exact_keys(
        alias_registry["entries"][0],
        {
            "aggregate_alias",
            "aggregate_ref",
            "location_aliases",
            "location_refs",
            "practitioner_aliases",
            "practitioner_refs",
            "additional_frame_types",
        },
        "aggregate_alias_entry_shape_invalid",
    )
    _expect_exact_keys(
        alias_registry["stream_entries"][0],
        {"stream_alias", "stream_ref"},
        "stream_alias_entry_shape_invalid",
    )
    entry = alias_registry["entries"][0]
    stream = alias_registry["stream_entries"][0]
    _expect_alias(
        entry["aggregate_alias"], "aggregate", "registry_aggregate_alias_invalid"
    )
    _expect_alias(stream["stream_alias"], "stream", "registry_stream_alias_invalid")
    for alias in entry["location_aliases"]:
        _expect_alias(alias, "location", "registry_location_alias_invalid")
    for alias in entry["practitioner_aliases"]:
        _expect_alias(alias, "practitioner", "registry_practitioner_alias_invalid")
    if not (
        entry["aggregate_ref"] == "synthetic:appointment:one"
        and entry["location_refs"] == ["synthetic:location:brisbane-one"]
        and entry["practitioner_refs"] == ["synthetic:practitioner:one"]
        and entry["additional_frame_types"] == []
        and stream["stream_ref"] == "synthetic:practice-event-stream:001"
    ):
        raise ObservationToSignalViolation("alias_registry_resolution_not_exact")


def _validate_prior_coordinate(
    coordinate: dict[str, Any],
    policy: dict[str, Any],
    binding: dict[str, Any],
    alias_registry: dict[str, Any],
    impact_policy: dict[str, Any],
) -> None:
    _expect_exact_keys(
        coordinate, PRIOR_COORDINATE_KEYS, "prior_coordinate_shape_invalid"
    )
    _verify(coordinate, "coordinate_digest")
    for field in (
        "practice_binding_digest",
        "source_contract_digest",
        "policy_digest",
        "binding_digest",
        "alias_registry_digest",
        "impact_policy_digest",
    ):
        _expect_digest(coordinate[field], f"prior_{field}_invalid")
    _expect_positive_integer(
        coordinate["observer_generation"], "prior_observer_generation_invalid"
    )
    _expect_positive_integer(
        coordinate["last_transaction_position"],
        "prior_transaction_position_invalid",
    )
    _expect_alias(coordinate["stream_alias"], "stream", "prior_stream_alias_invalid")
    if not (
        coordinate["practice_binding_digest"]
        == policy["practice_binding_digest"]
        == binding["practice_binding_digest"]
        == alias_registry["practice_binding_digest"]
        and coordinate["source_system_id"]
        == policy["source_system_id"]
        == binding["source_system_id"]
        == alias_registry["source_system_id"]
        and coordinate["source_contract_id"]
        == policy["source_contract_id"]
        == binding["source_contract_id"]
        == alias_registry["source_contract_id"]
        and coordinate["source_contract_digest"]
        == policy["source_contract_digest"]
        == binding["source_contract_digest"]
        and coordinate["policy_digest"] == policy["policy_digest"]
        and coordinate["binding_digest"] == binding["binding_digest"]
        and coordinate["alias_registry_digest"]
        == alias_registry["alias_registry_digest"]
        and coordinate["impact_policy_digest"] == impact_policy["impact_policy_digest"]
    ):
        raise ObservationToSignalViolation("prior_coordinate_binding_mismatch")
    if len(coordinate["aggregate_revisions"]) != 1:
        raise ObservationToSignalViolation("prior_aggregate_revision_shape_invalid")
    aggregate = coordinate["aggregate_revisions"][0]
    _expect_exact_keys(
        aggregate,
        {"aggregate_alias", "aggregate_revision"},
        "prior_aggregate_revision_shape_invalid",
    )
    _expect_alias(
        aggregate["aggregate_alias"], "aggregate", "prior_aggregate_alias_invalid"
    )
    _expect_positive_integer(
        aggregate["aggregate_revision"], "prior_aggregate_revision_invalid"
    )
    if not isinstance(coordinate["seen_observation_ids"], list):
        raise ObservationToSignalViolation("prior_seen_observation_ids_invalid")
    for digest in coordinate["seen_observation_ids"]:
        _expect_digest(digest, "prior_seen_observation_id_invalid")
    for field in ("restart_uncertain", "overflow_detected"):
        if type(coordinate[field]) is not bool:
            raise ObservationToSignalViolation(f"prior_{field}_invalid")
    for field in ("checkpoint_persisted", "runtime_checkpoint"):
        if coordinate[field] is not False:
            raise ObservationToSignalViolation(f"prior_{field}_must_be_false")


def _activation_current_and_exact(
    activation: dict[str, Any] | None,
    *,
    source_input: dict[str, Any],
    policy: dict[str, Any],
    binding: dict[str, Any],
    observed_at: str,
) -> bool:
    if activation is None:
        return False
    try:
        _expect_exact_keys(
            activation, ACTIVATION_KEYS, "synthetic_activation_shape_invalid"
        )
        _verify(activation, "activation_digest")
        exact_false_fields = (
            "source_connection",
            "credential_acquisition",
            "cursor_persistence",
            "returns_data",
            "read_authority",
            "provider_authority",
            "command_authority",
            "persistence_authority",
        )
        return (
            activation["activation_mode"] == ACTIVATION_MODE
            and activation["evidence_mode"] == SYNTHETIC_EVIDENCE_MODE
            and source_input["evidence_mode"] == SYNTHETIC_EVIDENCE_MODE
            and activation["policy_digest"] == policy["policy_digest"]
            and activation["binding_digest"] == binding["binding_digest"]
            and activation["fixture_digest"] == canonical_sha256(source_input)
            and _instant(activation["not_before"])
            <= _instant(observed_at)
            < _instant(activation["expires_at"])
            and all(activation[field] is False for field in exact_false_fields)
        )
    except (KeyError, TypeError, ObservationToSignalViolation):
        return False


def _route_for(
    source_input: dict[str, Any], impact_policy: dict[str, Any]
) -> dict[str, Any] | None:
    matches = [
        route
        for route in impact_policy["routes"]
        if route["event_type"] == source_input["event_type"]
        and route["source_event_schema_version"] == source_input["event_schema_version"]
        and route["aggregate_class"] == source_input["aggregate_class"]
    ]
    return matches[0] if len(matches) == 1 else None


def _resolve_aliases(
    source_input: dict[str, Any], alias_registry: dict[str, Any]
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    aggregate_matches = [
        item
        for item in alias_registry["entries"]
        if item["aggregate_alias"] == source_input["aggregate_alias"]
    ]
    stream_matches = [
        item
        for item in alias_registry["stream_entries"]
        if item["stream_alias"] == source_input["stream_alias"]
    ]
    if len(aggregate_matches) != 1 or len(stream_matches) != 1:
        return None, None
    return aggregate_matches[0], stream_matches[0]


def _decision(
    decision: str,
    reason_codes: list[str],
    *,
    policy: dict[str, Any],
    binding: dict[str, Any],
    previous_coordinate: dict[str, Any],
    source_input_digest: str,
    observation: dict[str, Any] | None,
    conservative_impact_frame_types: list[str] | None = None,
    signal_digest: str | None = None,
) -> dict[str, Any]:
    if decision not in ADMISSION_DECISIONS or not set(reason_codes).issubset(
        ADMISSION_REASON_CODES
    ):
        raise ObservationToSignalViolation("admission_decision_not_closed")
    impact = sorted(set(conservative_impact_frame_types or []))
    if decision == "ADMIT_SIGNAL":
        _expect_digest(signal_digest, "admitted_signal_digest_invalid")
        if impact != list(MANDATORY_FRAME_FLOOR):
            raise ObservationToSignalViolation("admitted_impact_floor_not_exact")
    elif signal_digest is not None:
        raise ObservationToSignalViolation("non_admit_signal_digest_forbidden")
    if decision == "FULL_INVALIDATION_REQUIRED" and impact != list(
        MANDATORY_FRAME_FLOOR
    ):
        raise ObservationToSignalViolation("full_invalidation_impact_not_exact")
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "decision": decision,
            "reason_codes": sorted(set(reason_codes)),
            "observation_digest": (
                observation["observation_digest"] if observation is not None else None
            ),
            "policy_digest": policy["policy_digest"],
            "binding_digest": binding["binding_digest"],
            "alias_registry_digest": policy["alias_registry_digest"],
            "impact_policy_digest": policy["impact_policy_digest"],
            "prior_coordinate_digest": previous_coordinate["coordinate_digest"],
            "conservative_impact_frame_types": impact,
            "signal_digest": signal_digest,
            "ordinary_temporal_signal_emitted": decision == "ADMIT_SIGNAL",
            "checkpoint_advanced": False,
            "durable_handoff_implemented": False,
            "authority_renewed": False,
            "returns_data": False,
            "read_authority": False,
            "provider_authority": False,
            "command_authority": False,
            "persistence_authority": False,
        },
        "admission_digest",
    )


def admit_synthetic_committed_change(
    source_input: dict[str, Any],
    policy: dict[str, Any],
    binding: dict[str, Any],
    alias_registry: dict[str, Any],
    impact_policy: dict[str, Any],
    previous_coordinate: dict[str, Any],
    activation: dict[str, Any] | None,
    *,
    observed_at: str,
    expires_at: str,
    hmac_key: bytes,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Validate and admit one input without opening or advancing any source."""

    _validate_source_input(source_input)
    _validate_trusted_contracts(policy, binding, alias_registry, impact_policy)
    _validate_prior_coordinate(
        previous_coordinate, policy, binding, alias_registry, impact_policy
    )
    now = _instant(observed_at)
    expiry = _instant(expires_at)
    if expiry <= now:
        raise ObservationToSignalViolation("observation_expiry_invalid")
    source_input_digest = canonical_sha256(source_input)
    route = _route_for(source_input, impact_policy)
    bounded_full = (
        route["bounded_full_invalidation_frame_types"]
        if route is not None
        else sorted(
            {
                frame
                for item in impact_policy["routes"]
                for frame in item["bounded_full_invalidation_frame_types"]
            }
        )
    )

    if not _activation_current_and_exact(
        activation,
        source_input=source_input,
        policy=policy,
        binding=binding,
        observed_at=observed_at,
    ):
        return None, _decision(
            "OBSERVER_DISABLED",
            ["SYNTHETIC_ACTIVATION_REQUIRED"],
            policy=policy,
            binding=binding,
            previous_coordinate=previous_coordinate,
            source_input_digest=source_input_digest,
            observation=None,
        )

    exact_scope = (
        source_input["practice_binding_digest"]
        == policy["practice_binding_digest"]
        == binding["practice_binding_digest"]
        == alias_registry["practice_binding_digest"]
        and source_input["source_system_id"]
        == policy["source_system_id"]
        == binding["source_system_id"]
        == alias_registry["source_system_id"]
    )
    if not exact_scope:
        return None, _decision(
            "BLOCK_FOREIGN_SCOPE",
            ["FOREIGN_PRACTICE_OR_SOURCE"],
            policy=policy,
            binding=binding,
            previous_coordinate=previous_coordinate,
            source_input_digest=source_input_digest,
            observation=None,
        )

    exact_contract = (
        source_input["source_contract_id"]
        == policy["source_contract_id"]
        == binding["source_contract_id"]
        == alias_registry["source_contract_id"]
        and source_input["event_type"] in policy["allowed_event_types"]
        and source_input["event_type"] in binding["allowed_event_types"]
        and source_input["event_schema_version"]
        in policy["allowed_event_schema_versions"]
        and source_input["event_schema_version"]
        in binding["allowed_event_schema_versions"]
        and source_input["aggregate_class"] in policy["allowed_aggregate_classes"]
        and source_input["aggregate_class"] in binding["allowed_aggregate_classes"]
        and source_input["evidence_mode"] == SYNTHETIC_EVIDENCE_MODE
    )
    if not exact_contract:
        return None, _decision(
            "BLOCK_SCHEMA_OR_POLICY",
            ["SCHEMA_POLICY_OR_CONTRACT_MISMATCH"],
            policy=policy,
            binding=binding,
            previous_coordinate=previous_coordinate,
            source_input_digest=source_input_digest,
            observation=None,
        )

    skew = abs(
        (
            now - _instant(source_input["source_transaction_committed_at"])
        ).total_seconds()
    )
    if skew > policy["maximum_clock_skew_seconds"]:
        return None, _decision(
            "BLOCK_SCHEMA_OR_POLICY",
            ["SCHEMA_POLICY_OR_CONTRACT_MISMATCH"],
            policy=policy,
            binding=binding,
            previous_coordinate=previous_coordinate,
            source_input_digest=source_input_digest,
            observation=None,
        )

    if (
        binding["revoked"] is True
        or now < _instant(binding["not_before"])
        or now >= _instant(binding["expires_at"])
        or now >= _instant(policy["expires_at"])
    ):
        return None, _decision(
            "BLOCK_EXPIRED_OR_REVOKED",
            ["BINDING_EXPIRED_OR_REVOKED"],
            policy=policy,
            binding=binding,
            previous_coordinate=previous_coordinate,
            source_input_digest=source_input_digest,
            observation=None,
        )

    observation_id = derive_observation_id(
        source_input["raw_source_event_id"],
        practice_binding_digest=source_input["practice_binding_digest"],
        source_system_id=source_input["source_system_id"],
        source_contract_id=source_input["source_contract_id"],
        source_contract_digest=policy["source_contract_digest"],
        observer_id=binding["observer_id"],
        observer_generation=binding["observer_generation"],
        hmac_key=hmac_key,
    )
    if observation_id in previous_coordinate["seen_observation_ids"]:
        return None, _decision(
            "SUPPRESS_DUPLICATE",
            ["EXACT_OBSERVATION_DUPLICATE"],
            policy=policy,
            binding=binding,
            previous_coordinate=previous_coordinate,
            source_input_digest=source_input_digest,
            observation=None,
        )
    if (
        source_input["transaction_position"]
        <= previous_coordinate["last_transaction_position"]
    ):
        return None, _decision(
            "SUPPRESS_REPLAY",
            ["TRANSACTION_POSITION_REPLAY"],
            policy=policy,
            binding=binding,
            previous_coordinate=previous_coordinate,
            source_input_digest=source_input_digest,
            observation=None,
        )
    if any(
        source_input[field] > MAX_SAFE_INTEGER
        for field in (
            "aggregate_revision",
            "expected_predecessor_position",
            "transaction_position",
        )
    ):
        return None, _decision(
            "FULL_INVALIDATION_REQUIRED",
            ["POSITION_OR_REVISION_OVERFLOW"],
            policy=policy,
            binding=binding,
            previous_coordinate=previous_coordinate,
            source_input_digest=source_input_digest,
            observation=None,
            conservative_impact_frame_types=bounded_full,
        )
    prior_uncertainty_reasons = []
    if (
        previous_coordinate["observer_id"] != binding["observer_id"]
        or previous_coordinate["observer_generation"] != binding["observer_generation"]
        or previous_coordinate["stream_alias"] != source_input["stream_alias"]
    ):
        prior_uncertainty_reasons.append("STREAM_OR_OBSERVER_GENERATION_MISMATCH")
    if previous_coordinate["restart_uncertain"] is True:
        prior_uncertainty_reasons.append("RESTART_UNCERTAINTY")
    if previous_coordinate["overflow_detected"] is True:
        prior_uncertainty_reasons.append("PRIOR_OVERFLOW_UNCERTAINTY")
    if prior_uncertainty_reasons:
        return None, _decision(
            "FULL_INVALIDATION_REQUIRED",
            prior_uncertainty_reasons,
            policy=policy,
            binding=binding,
            previous_coordinate=previous_coordinate,
            source_input_digest=source_input_digest,
            observation=None,
            conservative_impact_frame_types=bounded_full,
        )
    if previous_coordinate["baseline_established"] is not True:
        return None, _decision(
            "FULL_INVALIDATION_REQUIRED",
            ["BASELINE_NOT_ESTABLISHED"],
            policy=policy,
            binding=binding,
            previous_coordinate=previous_coordinate,
            source_input_digest=source_input_digest,
            observation=None,
            conservative_impact_frame_types=bounded_full,
        )
    if (
        source_input["expected_predecessor_position"]
        != previous_coordinate["last_transaction_position"]
    ):
        return None, _decision(
            "FULL_INVALIDATION_REQUIRED",
            ["EXPECTED_PREDECESSOR_MISMATCH"],
            policy=policy,
            binding=binding,
            previous_coordinate=previous_coordinate,
            source_input_digest=source_input_digest,
            observation=None,
            conservative_impact_frame_types=bounded_full,
        )
    if (
        source_input["transaction_position"]
        != previous_coordinate["last_transaction_position"] + 1
    ):
        return None, _decision(
            "FULL_INVALIDATION_REQUIRED",
            ["TRANSACTION_POSITION_GAP"],
            policy=policy,
            binding=binding,
            previous_coordinate=previous_coordinate,
            source_input_digest=source_input_digest,
            observation=None,
            conservative_impact_frame_types=bounded_full,
        )
    prior_revisions = {
        item["aggregate_alias"]: item["aggregate_revision"]
        for item in previous_coordinate["aggregate_revisions"]
    }
    if source_input["aggregate_alias"] not in prior_revisions:
        return None, _decision(
            "FULL_INVALIDATION_REQUIRED",
            ["ALIAS_OR_IMPACT_UNRESOLVED"],
            policy=policy,
            binding=binding,
            previous_coordinate=previous_coordinate,
            source_input_digest=source_input_digest,
            observation=None,
            conservative_impact_frame_types=bounded_full,
        )
    if (
        source_input["aggregate_revision"]
        != prior_revisions[source_input["aggregate_alias"]] + 1
    ):
        return None, _decision(
            "FULL_INVALIDATION_REQUIRED",
            ["AGGREGATE_REVISION_GAP"],
            policy=policy,
            binding=binding,
            previous_coordinate=previous_coordinate,
            source_input_digest=source_input_digest,
            observation=None,
            conservative_impact_frame_types=bounded_full,
        )

    aggregate_entry, stream_entry = _resolve_aliases(source_input, alias_registry)
    if route is None or aggregate_entry is None or stream_entry is None:
        return None, _decision(
            "FULL_INVALIDATION_REQUIRED",
            ["ALIAS_OR_IMPACT_UNRESOLVED"],
            policy=policy,
            binding=binding,
            previous_coordinate=previous_coordinate,
            source_input_digest=source_input_digest,
            observation=None,
            conservative_impact_frame_types=bounded_full,
        )
    observation = seal(
        {
            "schema_version": SCHEMA_VERSION,
            "observation_id": observation_id,
            "event_type": source_input["event_type"],
            "event_schema_version": source_input["event_schema_version"],
            "source_system_id": source_input["source_system_id"],
            "source_contract_id": source_input["source_contract_id"],
            "source_contract_digest": policy["source_contract_digest"],
            "observer_id": binding["observer_id"],
            "observer_generation": binding["observer_generation"],
            "practice_binding_digest": source_input["practice_binding_digest"],
            "aggregate_class": source_input["aggregate_class"],
            "aggregate_alias": source_input["aggregate_alias"],
            "aggregate_revision": source_input["aggregate_revision"],
            "stream_alias": source_input["stream_alias"],
            "expected_predecessor_position": source_input[
                "expected_predecessor_position"
            ],
            "transaction_position": source_input["transaction_position"],
            "committed": True,
            "evidence_mode": SYNTHETIC_EVIDENCE_MODE,
            "source_transaction_committed_at": source_input[
                "source_transaction_committed_at"
            ],
            "observed_at": observed_at,
            "expires_at": expires_at,
            "sensitivity": SENSITIVITY,
            "binding_digest": binding["binding_digest"],
            "policy_digest": policy["policy_digest"],
            "alias_registry_digest": alias_registry["alias_registry_digest"],
            "impact_policy_digest": impact_policy["impact_policy_digest"],
        },
        "observation_digest",
    )
    floor = sorted(set(route["mandatory_frame_type_floor"]))
    if floor != list(MANDATORY_FRAME_FLOOR):
        raise ObservationToSignalViolation("mandatory_impact_floor_not_exact")
    affected_frames = sorted(
        set(floor).union(aggregate_entry["additional_frame_types"])
    )
    reconstructed_signal = make_signal(
        signal_id=observation["observation_id"],
        event_type=observation["event_type"],
        aggregate_ref=aggregate_entry["aggregate_ref"],
        aggregate_revision=observation["aggregate_revision"],
        previous_transaction_position=observation["expected_predecessor_position"],
        transaction_position=observation["transaction_position"],
        location_refs=aggregate_entry["location_refs"],
        practitioner_refs=aggregate_entry["practitioner_refs"],
        frame_types=affected_frames,
        practice_binding_digest=observation["practice_binding_digest"],
        occurred_at=observation["source_transaction_committed_at"],
        received_at=observation["observed_at"],
        expires_at=observation["expires_at"],
        baseline_established=False,
    )
    if (
        reconstructed_signal["event_schema_version"]
        != route["temporal_event_schema_version"]
    ):
        raise ObservationToSignalViolation("temporal_schema_mapping_mismatch")
    decision = _decision(
        "ADMIT_SIGNAL",
        ["ADMISSION_CHECKS_PASSED"],
        policy=policy,
        binding=binding,
        previous_coordinate=previous_coordinate,
        source_input_digest=source_input_digest,
        observation=observation,
        conservative_impact_frame_types=floor,
        signal_digest=reconstructed_signal["signal_digest"],
    )
    return observation, decision


def map_observation_to_temporal_signal(
    observation: dict[str, Any],
    admission: dict[str, Any],
    alias_registry: dict[str, Any],
    impact_policy: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Construct one accepted signal from backend-owned impact and aliases."""

    _verify(observation, "observation_digest")
    _verify(admission, "admission_digest")
    _verify(alias_registry, "alias_registry_digest")
    _verify(impact_policy, "impact_policy_digest")
    if (
        admission["decision"] != "ADMIT_SIGNAL"
        or admission["ordinary_temporal_signal_emitted"] is not True
    ):
        raise ObservationToSignalViolation("only_admit_signal_may_map")
    source_shape = {
        "event_type": observation["event_type"],
        "event_schema_version": observation["event_schema_version"],
        "aggregate_class": observation["aggregate_class"],
        "aggregate_alias": observation["aggregate_alias"],
        "stream_alias": observation["stream_alias"],
    }
    route = _route_for(source_shape, impact_policy)
    aggregate_entry, stream_entry = _resolve_aliases(source_shape, alias_registry)
    if route is None or aggregate_entry is None or stream_entry is None:
        raise ObservationToSignalViolation("trusted_impact_or_alias_unresolved")
    floor = sorted(set(route["mandatory_frame_type_floor"]))
    if floor != list(MANDATORY_FRAME_FLOOR):
        raise ObservationToSignalViolation("mandatory_impact_floor_not_exact")
    affected_frames = sorted(
        set(floor).union(aggregate_entry["additional_frame_types"])
    )
    signal = make_signal(
        signal_id=observation["observation_id"],
        event_type=observation["event_type"],
        aggregate_ref=aggregate_entry["aggregate_ref"],
        aggregate_revision=observation["aggregate_revision"],
        previous_transaction_position=observation["expected_predecessor_position"],
        transaction_position=observation["transaction_position"],
        location_refs=aggregate_entry["location_refs"],
        practitioner_refs=aggregate_entry["practitioner_refs"],
        frame_types=affected_frames,
        practice_binding_digest=observation["practice_binding_digest"],
        occurred_at=observation["source_transaction_committed_at"],
        received_at=observation["observed_at"],
        expires_at=observation["expires_at"],
        baseline_established=False,
    )
    if signal["event_schema_version"] != route["temporal_event_schema_version"]:
        raise ObservationToSignalViolation("temporal_schema_mapping_mismatch")
    if not hmac.compare_digest(signal["signal_digest"], admission["signal_digest"]):
        raise ObservationToSignalViolation("admission_signal_digest_mismatch")
    trace = seal(
        {
            "schema_version": SCHEMA_VERSION,
            "observation_id": observation["observation_id"],
            "observation_digest": observation["observation_digest"],
            "admission_digest": admission["admission_digest"],
            "signal_id": signal["signal_id"],
            "signal_digest": signal["signal_digest"],
            "practice_binding_digest": observation["practice_binding_digest"],
            "event_type": observation["event_type"],
            "source_event_schema_version": observation["event_schema_version"],
            "temporal_event_schema_version": signal["event_schema_version"],
            "observer_id": observation["observer_id"],
            "observer_generation": observation["observer_generation"],
            "aggregate_class": observation["aggregate_class"],
            "aggregate_alias": observation["aggregate_alias"],
            "resolved_aggregate_ref_digest": canonical_sha256(
                {"aggregate_ref": aggregate_entry["aggregate_ref"]}
            ),
            "aggregate_revision": observation["aggregate_revision"],
            "stream_alias": observation["stream_alias"],
            "resolved_stream_ref_digest": canonical_sha256(
                {"stream_ref": stream_entry["stream_ref"]}
            ),
            "expected_predecessor_position": observation[
                "expected_predecessor_position"
            ],
            "transaction_position": observation["transaction_position"],
            "source_transaction_committed_at": observation[
                "source_transaction_committed_at"
            ],
            "observed_at": observation["observed_at"],
            "expires_at": observation["expires_at"],
            "sensitivity": observation["sensitivity"],
            "binding_digest": observation["binding_digest"],
            "policy_digest": observation["policy_digest"],
            "alias_registry_digest": observation["alias_registry_digest"],
            "impact_policy_digest": observation["impact_policy_digest"],
            "mandatory_frame_type_floor": floor,
            "resolved_frame_types": affected_frames,
            "impact_floor_preserved": set(floor).issubset(affected_frames),
            "source_selector_used": False,
            "source_payload_used_as_truth": False,
            "checkpoint_persisted": False,
            "source_read_executed": False,
            "fresh_read_executed": False,
            "provider_called": False,
            "command_executed": False,
            "returns_data": False,
            "read_authority": False,
            "provider_authority": False,
            "command_authority": False,
            "persistence_authority": False,
        },
        "trace_digest",
    )
    return signal, trace


def build_observation_continuity_requirement() -> dict[str, Any]:
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "requirement_id": "synthetic:observation-continuity-requirement:001",
            "required_future_mechanisms": [
                "ATOMIC_DECISION_INVALIDATION_CHECKPOINT_PERSISTENCE",
                "AUTHENTICATED_INTEGRATION_PRINCIPAL",
                "DURABLE_CLASSIFIED_CHECKPOINT",
                "MONOTONIC_TRANSACTION_OR_OUTBOX_POSITION",
                "RESTART_GAP_OVERFLOW_RETENTION_HANDLING",
                "STABLE_EVENT_IDENTITY_AND_AGGREGATE_REVISION",
            ],
            "runtime_implemented": False,
            "source_connection": False,
            "credential_acquisition": False,
            "cursor_observed": False,
            "cursor_advanced": False,
            "checkpoint_persisted": False,
            "decision_persisted": False,
            "invalidation_persisted": False,
            "listener_mounted": False,
            "returns_data": False,
            "read_authority": False,
            "provider_authority": False,
            "command_authority": False,
            "persistence_authority": False,
            "no_loss_claimed": False,
        },
        "continuity_requirement_digest",
    )


def _build_packet_without_proofreader() -> dict[str, Any]:
    parent = build_authored_synthetic_packet()
    manifest = derive_dependency_manifest(parent)
    lease = derive_watch_lease(parent, manifest)
    impact_policy = build_observation_impact_policy()
    alias_registry = build_observation_alias_registry(
        manifest["practice_binding_digest"]
    )
    policy = build_live_source_observation_policy(
        manifest["practice_binding_digest"],
        alias_registry_digest=alias_registry["alias_registry_digest"],
        impact_policy_digest=impact_policy["impact_policy_digest"],
    )
    binding = build_live_source_observer_binding(policy, alias_registry, impact_policy)
    source_input = build_authored_synthetic_source_input(
        manifest["practice_binding_digest"]
    )
    activation = build_synthetic_observation_classification_activation(
        policy,
        binding,
        fixture_digest=canonical_sha256(source_input),
    )
    previous = build_observation_prior_coordinate(
        practice_binding_digest=manifest["practice_binding_digest"],
        policy=policy,
        binding=binding,
        alias_registry=alias_registry,
        impact_policy=impact_policy,
    )
    observation, admission = admit_synthetic_committed_change(
        source_input,
        policy,
        binding,
        alias_registry,
        impact_policy,
        previous,
        activation,
        observed_at="2026-08-06T03:00:11Z",
        expires_at="2026-08-06T03:02:00Z",
        hmac_key=b"authored-synthetic-observation-key-0001",
    )
    if observation is None or admission["decision"] != "ADMIT_SIGNAL":
        raise ObservationToSignalViolation("canonical_observation_not_admitted")
    signal, mapping_trace = map_observation_to_temporal_signal(
        observation, admission, alias_registry, impact_policy
    )
    state, requirement, checkpoint, temporal_decisions, transitions, temporal_trace = (
        process_signals(
            parent,
            manifest,
            lease,
            [signal],
            observed_at="2026-08-06T03:01:00Z",
        )
    )
    if requirement is None:
        raise ObservationToSignalViolation("temporal_requirement_missing")
    packet = {
        "schema_version": SCHEMA_VERSION,
        "result": RESULT,
        "evidence_label": EVIDENCE_LABEL,
        "data_class": DATA_CLASS,
        "policy": policy,
        "observer_binding": binding,
        "alias_registry": alias_registry,
        "impact_policy": impact_policy,
        "synthetic_activation": activation,
        "observation_prior_coordinate": previous,
        "observation": observation,
        "admission_decision": admission,
        "temporal_signal": signal,
        "observation_to_signal_trace": mapping_trace,
        "observation_continuity_requirement": build_observation_continuity_requirement(),
        "temporal_manifest_digest": manifest["manifest_digest"],
        "temporal_lease_digest": lease["lease_digest"],
        "temporal_invalidation_decision": temporal_decisions[0],
        "temporal_frame_set_state": state,
        "temporal_reassembly_requirement": requirement,
        "temporal_checkpoint_ephemeral": checkpoint,
        "temporal_transition": transitions[0],
        "temporal_trace": temporal_trace,
        "old_frame_set_bytes_unchanged": temporal_trace["parent_frame_set_unchanged"],
        "source_connection": False,
        "credential_acquisition": False,
        "source_read_executed": False,
        "fresh_read_executed": False,
        "listener_mounted": False,
        "runtime_state_mounted": False,
        "filesystem_effects": False,
        "network_effects": False,
        "database_effects": False,
        "subprocess_effects": False,
        "checkpoint_persisted": False,
        "provider_called": False,
        "command_executed": False,
        "returns_data": False,
        "read_authority": False,
        "provider_authority": False,
        "command_authority": False,
        "persistence_authority": False,
        "read_only": True,
    }
    return packet


def validate_observation_to_signal_packet(packet: dict[str, Any]) -> None:
    expected = _build_packet_without_proofreader()
    candidate = {
        key: value for key, value in packet.items() if key != "proofreader_trace"
    }
    _validate_closed_typed(candidate, expected)
    seal_fields = (
        ("policy", "policy_digest"),
        ("observer_binding", "binding_digest"),
        ("alias_registry", "alias_registry_digest"),
        ("impact_policy", "impact_policy_digest"),
        ("synthetic_activation", "activation_digest"),
        ("observation_prior_coordinate", "coordinate_digest"),
        ("observation", "observation_digest"),
        ("admission_decision", "admission_digest"),
        ("temporal_signal", "signal_digest"),
        ("observation_to_signal_trace", "trace_digest"),
        ("observation_continuity_requirement", "continuity_requirement_digest"),
        ("temporal_invalidation_decision", "decision_digest"),
        ("temporal_frame_set_state", "state_digest"),
        ("temporal_reassembly_requirement", "requirement_digest"),
        ("temporal_checkpoint_ephemeral", "checkpoint_digest"),
        ("temporal_transition", "transition_digest"),
        ("temporal_trace", "temporal_trace_digest"),
    )
    for key, digest_field in seal_fields:
        _verify(candidate[key], digest_field)
    if (
        not hmac.compare_digest(canonical_sha256(candidate), canonical_sha256(expected))
        or candidate != expected
    ):
        raise ObservationToSignalViolation("packet_not_canonical_reconstruction")
    if candidate["admission_decision"]["decision"] != "ADMIT_SIGNAL":
        raise ObservationToSignalViolation("positive_packet_not_admitted")
    if candidate["temporal_invalidation_decision"]["decision"] != "REASSEMBLY_REQUIRED":
        raise ObservationToSignalViolation("temporal_handoff_not_classified")
    if candidate["temporal_frame_set_state"]["state"] != "REASSEMBLY_REQUIRED":
        raise ObservationToSignalViolation("old_frame_set_not_retired")
    if candidate["temporal_reassembly_requirement"]["execution_enabled"] is not False:
        raise ObservationToSignalViolation("temporal_requirement_not_inert")


def proofread_observation_to_signal_packet(
    packet: dict[str, Any], *, checked_at: str = "2026-08-06T03:01:01Z"
) -> dict[str, Any]:
    reasons: list[str] = []
    candidate = {
        key: value for key, value in packet.items() if key != "proofreader_trace"
    }
    try:
        validate_observation_to_signal_packet(candidate)
        if _instant(checked_at) >= _instant(candidate["observation"]["expires_at"]):
            reasons.append("PACKET_EXPIRED")
        serialized = repr(candidate)
        if "evt_0123456789abcdef0123456789abcdef" in serialized:
            reasons.append("RAW_EVENT_ID_LEAK")
        if "authored-synthetic-observation-key-0001" in serialized:
            reasons.append("HMAC_KEY_LEAK")
        false_fields = (
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
        )
        if any(candidate[field] is not False for field in false_fields):
            reasons.append("AUTHORITY_OR_EFFECT_WIDENED")
    except (KeyError, TypeError, ValueError, ObservationToSignalViolation) as error:
        reasons.append(f"PACKET_INVALID:{type(error).__name__}")
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "packet_digest": canonical_sha256(candidate),
            "checked_at": checked_at,
            "reason_codes": sorted(set(reasons)) if reasons else ["ALL_CHECKS_PASSED"],
            "release_decision": "BLOCK" if reasons else "RELEASE",
            "raw_source_event_id_released": False,
            "hmac_key_released": False,
            "source_payload_used_as_truth": False,
            "checkpoint_persisted": False,
            "source_read_executed": False,
            "provider_called": False,
            "command_executed": False,
            "returns_data": False,
            "read_authority": False,
            "provider_authority": False,
            "command_authority": False,
            "persistence_authority": False,
        },
        "proofreader_trace_digest",
    )


def build_authored_synthetic_observation_to_signal_packet() -> dict[str, Any]:
    packet = _build_packet_without_proofreader()
    packet["proofreader_trace"] = proofread_observation_to_signal_packet(packet)
    if packet["proofreader_trace"]["release_decision"] != "RELEASE":
        raise ObservationToSignalViolation("canonical_packet_not_released")
    return packet


__all__ = [
    "ACTIVATION_MODE",
    "ADMISSION_DECISIONS",
    "ADMISSION_REASON_CODES",
    "DATA_CLASS",
    "EVIDENCE_LABEL",
    "MAX_SAFE_INTEGER",
    "ObservationToSignalViolation",
    "RESULT",
    "SCHEMA_VERSION",
    "SOURCE_CONTRACT_ID",
    "SOURCE_SYSTEM_ID",
    "admit_synthetic_committed_change",
    "build_authored_synthetic_observation_to_signal_packet",
    "build_authored_synthetic_source_input",
    "build_live_source_observation_policy",
    "build_live_source_observer_binding",
    "build_observation_alias_registry",
    "build_observation_continuity_requirement",
    "build_observation_impact_policy",
    "build_observation_prior_coordinate",
    "build_synthetic_observation_classification_activation",
    "derive_observation_id",
    "map_observation_to_temporal_signal",
    "proofread_observation_to_signal_packet",
    "validate_observation_to_signal_packet",
]
