"""Pure typed inputs for canonical check-in operational evidence.

This unmounted module normalizes explicitly supplied authored-reference data.
It does not retrieve or verify evidence, compare a manifest, evaluate current
freshness, resolve a secret, or grant admission or command authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Literal


EVIDENCE_INPUT_SCHEMA_VERSION = "emr4.check-in-operational-evidence-inputs.v1"
EVIDENCE_SLOT_IDS = (
    "database_connection_credential",
    "application_token_signing_key",
    "admission_snapshot_verification_key",
)

_TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "role_attestation",
        "rotation_custody_attestations",
        "break_glass_evidence",
    }
)
_ROLE_FIELDS = frozenset(
    {
        "evidence_reference",
        "artifact_sha256",
        "authority_git_object",
        "environment_identifier",
        "admission_snapshot_generation",
        "logical_role_id",
        "database_role_identifier",
        "credential_secret_slot_id",
        "ownership_observation",
        "rls_bypass_observation",
        "product_relation_ownership_observation",
        "cross_tenant_probe_observation",
        "observed_at",
        "fresh_until",
        "independent_verifier_reference",
    }
)
_ROTATION_FIELDS = frozenset(
    {
        "slot_id",
        "evidence_reference",
        "artifact_sha256",
        "authority_git_object",
        "environment_identifier",
        "admission_snapshot_generation",
        "key_id",
        "version",
        "rotation_sequence",
        "observed_at",
        "fresh_until",
        "independent_verifier_reference",
    }
)
_BREAK_GLASS_FIELDS = frozenset(
    {
        "mode",
        "state",
        "evidence_reference",
        "artifact_sha256",
        "authority_git_object",
        "environment_identifier",
        "admission_snapshot_generation",
        "observed_at",
        "fresh_until",
        "independent_verifier_reference",
    }
)
_FORBIDDEN_FIELD_NAMES = frozenset(
    {
        "value",
        "secret_value",
        "password",
        "token",
        "private_key",
        "database_url",
        "connection_url",
        "environment_value",
        "secret_material_sha256",
        "secret_fingerprint",
        "secret_manager_endpoint",
        "secret_resolution_result",
        "resolved_secret",
    }
)
_OWNERSHIP_OBSERVATIONS = frozenset({"non_owner", "owner", "unknown"})
_RLS_BYPASS_OBSERVATIONS = frozenset({"nobypassrls", "bypassrls", "unknown"})
_PRODUCT_OWNERSHIP_OBSERVATIONS = frozenset({"absent", "present", "unknown"})
_CROSS_TENANT_OBSERVATIONS = frozenset({"denied", "allowed", "not_observed"})
_BREAK_GLASS_STATES = frozenset({"inactive", "engaged_deny", "retired"})

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_FULL_GIT_OBJECT = re.compile(r"^[0-9a-f]{40}$")
_ENVIRONMENT_ID = re.compile(r"^env:[a-z0-9][a-z0-9._-]{2,95}$")
_EVIDENCE_REFERENCE = re.compile(r"^evidence-ref:[a-z0-9][a-z0-9._/-]{2,127}$")
_LOGICAL_ROLE_ID = re.compile(r"^[a-z][a-z0-9_]{2,95}$")
_DATABASE_ROLE = re.compile(r"^[a-z][a-z0-9_]{2,62}$")
_KEY_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{2,95}$")
_VERSION = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
_RFC3339 = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})$"
)

RoleOwnershipObservation = Literal["non_owner", "owner", "unknown"]
RoleRlsBypassObservation = Literal["nobypassrls", "bypassrls", "unknown"]
ProductRelationOwnershipObservation = Literal["absent", "present", "unknown"]
CrossTenantProbeObservation = Literal["denied", "allowed", "not_observed"]
BreakGlassEvidenceState = Literal["inactive", "engaged_deny", "retired"]
OperationalEvidenceInputOutcome = Literal["normalized", "denied"]
OperationalEvidenceInputReason = Literal[
    "evidence_input_type_invalid",
    "evidence_forbidden_field",
    "evidence_boolean_claim_forbidden",
    "evidence_shape_invalid",
    "evidence_git_object_invalid",
    "evidence_time_invalid",
    "evidence_inputs_normalized",
]


@dataclass(frozen=True, slots=True)
class RoleAttestationInput:
    evidence_reference: str
    artifact_sha256: str
    authority_git_object: str
    environment_identifier: str
    admission_snapshot_generation: int
    logical_role_id: str
    database_role_identifier: str
    credential_secret_slot_id: str
    ownership_observation: RoleOwnershipObservation
    rls_bypass_observation: RoleRlsBypassObservation
    product_relation_ownership_observation: ProductRelationOwnershipObservation
    cross_tenant_probe_observation: CrossTenantProbeObservation
    observed_at: str
    fresh_until: str
    independent_verifier_reference: str


@dataclass(frozen=True, slots=True)
class RotationCustodyAttestationInput:
    slot_id: str
    evidence_reference: str
    artifact_sha256: str
    authority_git_object: str
    environment_identifier: str
    admission_snapshot_generation: int
    key_id: str
    version: str
    rotation_sequence: int
    observed_at: str
    fresh_until: str
    independent_verifier_reference: str


@dataclass(frozen=True, slots=True)
class BreakGlassEvidenceInput:
    mode: Literal["deny_only"]
    state: BreakGlassEvidenceState
    evidence_reference: str
    artifact_sha256: str
    authority_git_object: str
    environment_identifier: str
    admission_snapshot_generation: int
    observed_at: str
    fresh_until: str
    independent_verifier_reference: str


@dataclass(frozen=True, slots=True)
class CheckInOperationalEvidenceInputs:
    schema_version: str
    role_attestation: RoleAttestationInput
    rotation_custody_attestations: tuple[RotationCustodyAttestationInput, ...]
    break_glass_evidence: BreakGlassEvidenceInput


@dataclass(frozen=True, slots=True)
class OperationalEvidenceInputNormalizationResult:
    outcome: OperationalEvidenceInputOutcome
    reason_code: OperationalEvidenceInputReason
    evidence_inputs: CheckInOperationalEvidenceInputs | None


def _denied(
    reason: OperationalEvidenceInputReason,
) -> OperationalEvidenceInputNormalizationResult:
    return OperationalEvidenceInputNormalizationResult(
        outcome="denied",
        reason_code=reason,
        evidence_inputs=None,
    )


def _normalized_field_name(value: str) -> str:
    return value.casefold().replace("-", "_")


def _has_forbidden_field(value: object) -> bool:
    if type(value) is dict:
        for key, child in value.items():
            if type(key) is str and _normalized_field_name(key) in _FORBIDDEN_FIELD_NAMES:
                return True
            if _has_forbidden_field(child):
                return True
    elif type(value) is list:
        return any(_has_forbidden_field(child) for child in value)
    return False


def _has_boolean(value: object) -> bool:
    if type(value) is bool:
        return True
    if type(value) is dict:
        return any(_has_boolean(child) for child in value.values())
    if type(value) is list:
        return any(_has_boolean(child) for child in value)
    return False


def _is_record(value: object, fields: frozenset[str]) -> bool:
    return (
        type(value) is dict
        and all(type(key) is str for key in value)
        and set(value) == fields
    )


def _is_text(value: object, pattern: re.Pattern[str]) -> bool:
    return type(value) is str and pattern.fullmatch(value) is not None


def _is_choice(value: object, choices: frozenset[str] | tuple[str, ...]) -> bool:
    return type(value) is str and value in choices


def _is_positive_integer(value: object) -> bool:
    return type(value) is int and value >= 1


def _normalize_timestamp(value: object) -> tuple[str, datetime] | None:
    if type(value) is not str or _RFC3339.fullmatch(value) is None:
        return None
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            return None
        utc_value = parsed.astimezone(timezone.utc)
    except (OverflowError, ValueError):
        return None
    normalized = utc_value.isoformat().replace("+00:00", "Z")
    return normalized, utc_value


def _normalize_window(record: dict[str, object]) -> tuple[str, str] | None:
    observed = _normalize_timestamp(record["observed_at"])
    fresh = _normalize_timestamp(record["fresh_until"])
    if observed is None or fresh is None or fresh[1] <= observed[1]:
        return None
    return observed[0], fresh[0]


def _role_shape_is_valid(role: dict[str, object]) -> bool:
    return (
        _is_text(role["evidence_reference"], _EVIDENCE_REFERENCE)
        and _is_text(role["artifact_sha256"], _SHA256)
        and type(role["authority_git_object"]) is str
        and _is_text(role["environment_identifier"], _ENVIRONMENT_ID)
        and _is_positive_integer(role["admission_snapshot_generation"])
        and _is_text(role["logical_role_id"], _LOGICAL_ROLE_ID)
        and _is_text(role["database_role_identifier"], _DATABASE_ROLE)
        and _is_choice(role["credential_secret_slot_id"], EVIDENCE_SLOT_IDS)
        and _is_choice(role["ownership_observation"], _OWNERSHIP_OBSERVATIONS)
        and _is_choice(role["rls_bypass_observation"], _RLS_BYPASS_OBSERVATIONS)
        and _is_choice(
            role["product_relation_ownership_observation"],
            _PRODUCT_OWNERSHIP_OBSERVATIONS,
        )
        and _is_choice(
            role["cross_tenant_probe_observation"], _CROSS_TENANT_OBSERVATIONS
        )
        and type(role["observed_at"]) is str
        and type(role["fresh_until"]) is str
        and _is_text(role["independent_verifier_reference"], _EVIDENCE_REFERENCE)
    )


def _rotation_shape_is_valid(rotation: dict[str, object], slot_id: str) -> bool:
    return (
        type(rotation["slot_id"]) is str
        and rotation["slot_id"] == slot_id
        and _is_text(rotation["evidence_reference"], _EVIDENCE_REFERENCE)
        and _is_text(rotation["artifact_sha256"], _SHA256)
        and type(rotation["authority_git_object"]) is str
        and _is_text(rotation["environment_identifier"], _ENVIRONMENT_ID)
        and _is_positive_integer(rotation["admission_snapshot_generation"])
        and _is_text(rotation["key_id"], _KEY_ID)
        and _is_text(rotation["version"], _VERSION)
        and _is_positive_integer(rotation["rotation_sequence"])
        and type(rotation["observed_at"]) is str
        and type(rotation["fresh_until"]) is str
        and _is_text(rotation["independent_verifier_reference"], _EVIDENCE_REFERENCE)
    )


def _break_glass_shape_is_valid(evidence: dict[str, object]) -> bool:
    return (
        type(evidence["mode"]) is str
        and evidence["mode"] == "deny_only"
        and _is_choice(evidence["state"], _BREAK_GLASS_STATES)
        and _is_text(evidence["evidence_reference"], _EVIDENCE_REFERENCE)
        and _is_text(evidence["artifact_sha256"], _SHA256)
        and type(evidence["authority_git_object"]) is str
        and _is_text(evidence["environment_identifier"], _ENVIRONMENT_ID)
        and _is_positive_integer(evidence["admission_snapshot_generation"])
        and type(evidence["observed_at"]) is str
        and type(evidence["fresh_until"]) is str
        and _is_text(evidence["independent_verifier_reference"], _EVIDENCE_REFERENCE)
    )


def normalize_check_in_operational_evidence_inputs(
    payload: object,
) -> OperationalEvidenceInputNormalizationResult:
    """Normalize a closed evidence-input object without evaluating its facts."""

    if type(payload) is not dict:
        return _denied("evidence_input_type_invalid")
    if _has_forbidden_field(payload):
        return _denied("evidence_forbidden_field")
    if _has_boolean(payload):
        return _denied("evidence_boolean_claim_forbidden")
    if not _is_record(payload, _TOP_LEVEL_FIELDS):
        return _denied("evidence_shape_invalid")

    role_value = payload["role_attestation"]
    rotations_value = payload["rotation_custody_attestations"]
    break_glass_value = payload["break_glass_evidence"]
    if (
        type(payload["schema_version"]) is not str
        or payload["schema_version"] != EVIDENCE_INPUT_SCHEMA_VERSION
        or not _is_record(role_value, _ROLE_FIELDS)
        or type(rotations_value) is not list
        or len(rotations_value) != len(EVIDENCE_SLOT_IDS)
        or not _is_record(break_glass_value, _BREAK_GLASS_FIELDS)
    ):
        return _denied("evidence_shape_invalid")

    role = role_value
    break_glass = break_glass_value
    if not _role_shape_is_valid(role) or not _break_glass_shape_is_valid(break_glass):
        return _denied("evidence_shape_invalid")

    rotations: list[dict[str, object]] = []
    for value, slot_id in zip(rotations_value, EVIDENCE_SLOT_IDS, strict=True):
        if not _is_record(value, _ROTATION_FIELDS):
            return _denied("evidence_shape_invalid")
        rotation = value
        if not _rotation_shape_is_valid(rotation, slot_id):
            return _denied("evidence_shape_invalid")
        rotations.append(rotation)

    git_objects = [
        role["authority_git_object"],
        *(rotation["authority_git_object"] for rotation in rotations),
        break_glass["authority_git_object"],
    ]
    if any(
        type(value) is not str or _FULL_GIT_OBJECT.fullmatch(value) is None
        for value in git_objects
    ):
        return _denied("evidence_git_object_invalid")

    role_window = _normalize_window(role)
    rotation_windows = [_normalize_window(rotation) for rotation in rotations]
    break_glass_window = _normalize_window(break_glass)
    if (
        role_window is None
        or any(window is None for window in rotation_windows)
        or break_glass_window is None
    ):
        return _denied("evidence_time_invalid")

    normalized_rotations = tuple(
        RotationCustodyAttestationInput(
            slot_id=str(rotation["slot_id"]),
            evidence_reference=str(rotation["evidence_reference"]),
            artifact_sha256=str(rotation["artifact_sha256"]),
            authority_git_object=str(rotation["authority_git_object"]),
            environment_identifier=str(rotation["environment_identifier"]),
            admission_snapshot_generation=int(rotation["admission_snapshot_generation"]),
            key_id=str(rotation["key_id"]),
            version=str(rotation["version"]),
            rotation_sequence=int(rotation["rotation_sequence"]),
            observed_at=window[0],
            fresh_until=window[1],
            independent_verifier_reference=str(rotation["independent_verifier_reference"]),
        )
        for rotation, window in zip(rotations, rotation_windows, strict=True)
        if window is not None
    )
    result = CheckInOperationalEvidenceInputs(
        schema_version=EVIDENCE_INPUT_SCHEMA_VERSION,
        role_attestation=RoleAttestationInput(
            evidence_reference=str(role["evidence_reference"]),
            artifact_sha256=str(role["artifact_sha256"]),
            authority_git_object=str(role["authority_git_object"]),
            environment_identifier=str(role["environment_identifier"]),
            admission_snapshot_generation=int(role["admission_snapshot_generation"]),
            logical_role_id=str(role["logical_role_id"]),
            database_role_identifier=str(role["database_role_identifier"]),
            credential_secret_slot_id=str(role["credential_secret_slot_id"]),
            ownership_observation=role["ownership_observation"],
            rls_bypass_observation=role["rls_bypass_observation"],
            product_relation_ownership_observation=role[
                "product_relation_ownership_observation"
            ],
            cross_tenant_probe_observation=role["cross_tenant_probe_observation"],
            observed_at=role_window[0],
            fresh_until=role_window[1],
            independent_verifier_reference=str(role["independent_verifier_reference"]),
        ),
        rotation_custody_attestations=normalized_rotations,
        break_glass_evidence=BreakGlassEvidenceInput(
            mode="deny_only",
            state=break_glass["state"],
            evidence_reference=str(break_glass["evidence_reference"]),
            artifact_sha256=str(break_glass["artifact_sha256"]),
            authority_git_object=str(break_glass["authority_git_object"]),
            environment_identifier=str(break_glass["environment_identifier"]),
            admission_snapshot_generation=int(
                break_glass["admission_snapshot_generation"]
            ),
            observed_at=break_glass_window[0],
            fresh_until=break_glass_window[1],
            independent_verifier_reference=str(
                break_glass["independent_verifier_reference"]
            ),
        ),
    )
    return OperationalEvidenceInputNormalizationResult(
        outcome="normalized",
        reason_code="evidence_inputs_normalized",
        evidence_inputs=result,
    )
