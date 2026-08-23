"""Pure, unmounted evaluator for canonical check-in environment evidence.

The evaluator consumes only already-normalized in-memory readings and an
explicit evaluation time. It never reads a clock or ambient state and its
satisfied result is not an admission or command capability.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Literal

from app.services.appointment_check_in_environment_manifest import (
    MANIFEST_SCHEMA_VERSION,
    MANIFEST_SLOT_IDS,
    ManifestBreakGlass,
    ManifestEnvironment,
    ManifestNormalizationResult,
    ManifestRotationEvidence,
    ManifestRuntimeRole,
    ManifestSecretReference,
    NormalizedCheckInEnvironmentManifest,
)
from app.services.appointment_check_in_operational_evidence import (
    EVIDENCE_INPUT_SCHEMA_VERSION,
    BreakGlassEvidenceInput,
    CheckInOperationalEvidenceInputs,
    OperationalEvidenceInputNormalizationResult,
    RoleAttestationInput,
    RotationCustodyAttestationInput,
)


EVIDENCE_GATE_READING_SCHEMA_VERSION = (
    "emr4.check-in-environment-evidence-gate-reading.v1"
)

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_FULL_GIT_OBJECT = re.compile(r"^[0-9a-f]{40}$")
_MANIFEST_ID = re.compile(r"^check-in-env-manifest:[a-z0-9][a-z0-9._-]{2,95}$")
_ENVIRONMENT_ID = re.compile(r"^env:[a-z0-9][a-z0-9._-]{2,95}$")
_PRACTICE_REFERENCE = re.compile(r"^practice-ref:[a-z0-9][a-z0-9._/-]{2,127}$")
_EVIDENCE_REFERENCE = re.compile(r"^evidence-ref:[a-z0-9][a-z0-9._/-]{2,127}$")
_SECRET_REFERENCE = re.compile(r"^secret-ref:[a-z0-9][a-z0-9._/-]{2,127}$")
_POLICY_REFERENCE = re.compile(r"^policy-ref:[a-z0-9][a-z0-9._/-]{2,127}$")
_DATABASE_ROLE = re.compile(r"^[a-z][a-z0-9_]{2,62}$")
_PROVIDER_NAMESPACE = re.compile(r"^[a-z][a-z0-9._-]{2,63}$")
_KEY_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{2,95}$")
_VERSION = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")

EvidenceGateOutcome = Literal["denied", "satisfied"]
EvidenceGateReason = Literal[
    "manifest_absent",
    "manifest_invalid",
    "manifest_stale",
    "manifest_ambiguous",
    "environment_mismatch",
    "role_binding_missing",
    "role_evidence_invalid",
    "secret_reference_invalid",
    "rotation_evidence_invalid",
    "break_glass_not_inactive",
    "evidence_gate_satisfied",
]


@dataclass(frozen=True, slots=True)
class EnvironmentEvidenceGateReading:
    schema_version: str
    outcome: EvidenceGateOutcome
    reason_code: EvidenceGateReason
    environment_identifier: str | None
    admission_snapshot_generation: int | None
    manifest_digest: str | None


def _parse_normalized_time(value: object) -> datetime | None:
    if type(value) is not str or not value.endswith("Z"):
        return None
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except (OverflowError, ValueError):
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def _exact_aware_time(value: object) -> datetime | None:
    if type(value) is not datetime or value.tzinfo is None:
        return None
    try:
        if value.utcoffset() is None:
            return None
        return value.astimezone(timezone.utc)
    except (OverflowError, ValueError):
        return None


def _positive_integer(value: object) -> bool:
    return type(value) is int and value >= 1


def _matches(value: object, pattern: re.Pattern[str]) -> bool:
    return type(value) is str and pattern.fullmatch(value) is not None


def _manifest_result_is_internally_valid(value: object) -> bool:
    if type(value) is not ManifestNormalizationResult:
        return False
    if (
        value.outcome != "normalized"
        or value.reason_code != "manifest_normalized"
        or not _matches(value.manifest_digest, _SHA256)
        or type(value.manifest) is not NormalizedCheckInEnvironmentManifest
    ):
        return False

    manifest = value.manifest
    if (
        manifest.schema_version != MANIFEST_SCHEMA_VERSION
        or not _matches(manifest.manifest_id, _MANIFEST_ID)
        or type(manifest.environment) is not ManifestEnvironment
        or manifest.environment.environment_class
        not in {"development", "test", "staging", "production"}
        or not _matches(manifest.environment.identifier, _ENVIRONMENT_ID)
        or not _positive_integer(manifest.admission_snapshot_generation)
        or not _matches(manifest.authority_git_object, _FULL_GIT_OBJECT)
        or not _matches(manifest.practice_scope_reference, _PRACTICE_REFERENCE)
        or type(manifest.runtime_role) is not ManifestRuntimeRole
        or type(manifest.secret_references) is not tuple
        or len(manifest.secret_references) != len(MANIFEST_SLOT_IDS)
        or type(manifest.rotation_evidence) is not tuple
        or len(manifest.rotation_evidence) != len(MANIFEST_SLOT_IDS)
        or type(manifest.break_glass) is not ManifestBreakGlass
    ):
        return False

    role = manifest.runtime_role
    if (
        role.logical_role_id != "appointment_check_in_ordinary_runtime_v1"
        or not _matches(role.database_role_identifier, _DATABASE_ROLE)
        or role.credential_secret_slot_id != MANIFEST_SLOT_IDS[0]
        or type(role.non_owner_required) is not bool
        or role.non_owner_required is not True
        or type(role.nobypassrls_required) is not bool
        or role.nobypassrls_required is not True
        or type(role.product_relation_ownership_allowed) is not bool
        or role.product_relation_ownership_allowed is not False
        or not _matches(role.tenant_attestation_reference, _EVIDENCE_REFERENCE)
    ):
        return False

    issued = _parse_normalized_time(manifest.issued_at)
    expires = _parse_normalized_time(manifest.expires_at)
    if issued is None or expires is None or expires <= issued:
        return False

    secrets = manifest.secret_references
    rotations = manifest.rotation_evidence
    if any(type(row) is not ManifestSecretReference for row in secrets) or any(
        type(row) is not ManifestRotationEvidence for row in rotations
    ):
        return False
    if (
        tuple(row.slot_id for row in secrets) != MANIFEST_SLOT_IDS
        or tuple(row.slot_id for row in rotations) != MANIFEST_SLOT_IDS
        or len({row.provider_namespace for row in secrets}) != len(secrets)
        or len({row.secret_reference for row in secrets}) != len(secrets)
        or len({row.key_id for row in secrets}) != len(secrets)
    ):
        return False

    for secret, rotation in zip(secrets, rotations, strict=True):
        observed = _parse_normalized_time(rotation.observed_at)
        fresh = _parse_normalized_time(rotation.fresh_until)
        if (
            not _matches(secret.provider_namespace, _PROVIDER_NAMESPACE)
            or not _matches(secret.secret_reference, _SECRET_REFERENCE)
            or not _matches(secret.key_id, _KEY_ID)
            or not _matches(secret.version, _VERSION)
            or not _matches(secret.rotation_policy_reference, _POLICY_REFERENCE)
            or not _matches(
                secret.rotation_evidence_reference, _EVIDENCE_REFERENCE
            )
            or secret.slot_id != rotation.slot_id
            or secret.key_id != rotation.key_id
            or secret.version != rotation.version
            or secret.rotation_evidence_reference != rotation.evidence_reference
            or not _matches(rotation.evidence_reference, _EVIDENCE_REFERENCE)
            or rotation.environment_identifier != manifest.environment.identifier
            or rotation.admission_snapshot_generation
            != manifest.admission_snapshot_generation
            or rotation.authority_git_object != manifest.authority_git_object
            or not _matches(rotation.authority_git_object, _FULL_GIT_OBJECT)
            or not _matches(rotation.artifact_sha256, _SHA256)
            or not _matches(rotation.key_id, _KEY_ID)
            or not _matches(rotation.version, _VERSION)
            or not _positive_integer(rotation.rotation_sequence)
            or not _matches(
                rotation.independent_verifier_reference, _EVIDENCE_REFERENCE
            )
            or observed is None
            or fresh is None
            or fresh <= observed
        ):
            return False

    break_glass = manifest.break_glass
    return (
        break_glass.mode == "deny_only"
        and break_glass.state in {"inactive", "engaged_deny", "retired"}
        and _matches(break_glass.evidence_reference, _EVIDENCE_REFERENCE)
        and type(break_glass.bypass_allowed) is bool
        and break_glass.bypass_allowed is False
        and type(break_glass.secret_injection_allowed) is bool
        and break_glass.secret_injection_allowed is False
        and type(break_glass.automatic_clear_allowed) is bool
        and break_glass.automatic_clear_allowed is False
    )


def _reading(
    reason: EvidenceGateReason,
    selected: ManifestNormalizationResult | None = None,
) -> EnvironmentEvidenceGateReading:
    manifest = selected.manifest if selected is not None else None
    satisfied = reason == "evidence_gate_satisfied"
    return EnvironmentEvidenceGateReading(
        schema_version=EVIDENCE_GATE_READING_SCHEMA_VERSION,
        outcome="satisfied" if satisfied else "denied",
        reason_code=reason,
        environment_identifier=(
            manifest.environment.identifier if manifest is not None else None
        ),
        admission_snapshot_generation=(
            manifest.admission_snapshot_generation if manifest is not None else None
        ),
        manifest_digest=(selected.manifest_digest if selected is not None else None),
    )


def _in_current_window(observed_at: object, fresh_until: object, now: datetime) -> bool:
    observed = _parse_normalized_time(observed_at)
    fresh = _parse_normalized_time(fresh_until)
    return observed is not None and fresh is not None and observed <= now < fresh


def _evidence_envelope(
    value: object,
) -> tuple[
    CheckInOperationalEvidenceInputs,
    RoleAttestationInput,
    tuple[RotationCustodyAttestationInput, ...],
    BreakGlassEvidenceInput,
] | EvidenceGateReason:
    if (
        type(value) is not OperationalEvidenceInputNormalizationResult
        or value.outcome != "normalized"
        or value.reason_code != "evidence_inputs_normalized"
        or type(value.evidence_inputs) is not CheckInOperationalEvidenceInputs
        or value.evidence_inputs.schema_version != EVIDENCE_INPUT_SCHEMA_VERSION
        or type(value.evidence_inputs.role_attestation) is not RoleAttestationInput
    ):
        return "role_evidence_invalid"
    inputs = value.evidence_inputs
    rotations = inputs.rotation_custody_attestations
    if (
        type(rotations) is not tuple
        or len(rotations) != len(MANIFEST_SLOT_IDS)
        or any(type(row) is not RotationCustodyAttestationInput for row in rotations)
    ):
        return "rotation_evidence_invalid"
    if type(inputs.break_glass_evidence) is not BreakGlassEvidenceInput:
        return "break_glass_not_inactive"
    return inputs, inputs.role_attestation, rotations, inputs.break_glass_evidence


def _same_environment_binding(
    manifest: NormalizedCheckInEnvironmentManifest,
    role: RoleAttestationInput,
    rotations: tuple[RotationCustodyAttestationInput, ...],
    break_glass: BreakGlassEvidenceInput,
) -> bool:
    expected = (
        manifest.environment.identifier,
        manifest.admission_snapshot_generation,
        manifest.authority_git_object,
    )
    records = (role, *rotations, break_glass)
    return all(
        (
            record.environment_identifier,
            record.admission_snapshot_generation,
            record.authority_git_object,
        )
        == expected
        for record in records
    )


def _role_binding_matches(
    manifest: NormalizedCheckInEnvironmentManifest,
    role: RoleAttestationInput,
) -> bool:
    expected = manifest.runtime_role
    return (
        role.evidence_reference == expected.tenant_attestation_reference
        and role.logical_role_id == expected.logical_role_id
        and role.database_role_identifier == expected.database_role_identifier
        and role.credential_secret_slot_id == expected.credential_secret_slot_id
    )


def _role_evidence_is_valid(
    role: RoleAttestationInput,
    all_evidence_references: tuple[str, ...],
    all_artifact_digests: tuple[str, ...],
    now: datetime,
) -> bool:
    return (
        role.ownership_observation == "non_owner"
        and role.rls_bypass_observation == "nobypassrls"
        and role.product_relation_ownership_observation == "absent"
        and role.cross_tenant_probe_observation == "denied"
        and _matches(role.artifact_sha256, _SHA256)
        and _matches(role.evidence_reference, _EVIDENCE_REFERENCE)
        and _matches(role.independent_verifier_reference, _EVIDENCE_REFERENCE)
        and role.independent_verifier_reference not in all_evidence_references
        and all_artifact_digests.count(role.artifact_sha256) == 1
        and _in_current_window(role.observed_at, role.fresh_until, now)
    )


def _secret_references_are_valid(
    manifest: NormalizedCheckInEnvironmentManifest,
    rotations: tuple[RotationCustodyAttestationInput, ...],
) -> bool:
    secrets = manifest.secret_references
    manifest_rotations = manifest.rotation_evidence
    if (
        tuple(row.slot_id for row in rotations) != MANIFEST_SLOT_IDS
        or len({row.secret_reference for row in secrets}) != len(MANIFEST_SLOT_IDS)
        or len({row.key_id for row in secrets}) != len(MANIFEST_SLOT_IDS)
    ):
        return False
    return all(
        operational.slot_id == secret.slot_id == declared.slot_id
        and operational.evidence_reference
        == secret.rotation_evidence_reference
        == declared.evidence_reference
        and operational.key_id == secret.key_id == declared.key_id
        and operational.version == secret.version == declared.version
        for secret, declared, operational in zip(
            secrets, manifest_rotations, rotations, strict=True
        )
    )


def _rotation_evidence_is_valid(
    manifest: NormalizedCheckInEnvironmentManifest,
    rotations: tuple[RotationCustodyAttestationInput, ...],
    all_evidence_references: tuple[str, ...],
    all_artifact_digests: tuple[str, ...],
    now: datetime,
) -> bool:
    if (
        len(set(row.evidence_reference for row in rotations)) != len(rotations)
        or len(set(row.artifact_sha256 for row in rotations)) != len(rotations)
    ):
        return False
    for declared, observed in zip(manifest.rotation_evidence, rotations, strict=True):
        if (
            observed.artifact_sha256 != declared.artifact_sha256
            or observed.rotation_sequence != declared.rotation_sequence
            or observed.observed_at != declared.observed_at
            or observed.fresh_until != declared.fresh_until
            or observed.independent_verifier_reference
            != declared.independent_verifier_reference
            or not _matches(observed.artifact_sha256, _SHA256)
            or not _matches(
                observed.independent_verifier_reference, _EVIDENCE_REFERENCE
            )
            or observed.independent_verifier_reference in all_evidence_references
            or all_artifact_digests.count(observed.artifact_sha256) != 1
            or not _in_current_window(
                observed.observed_at, observed.fresh_until, now
            )
        ):
            return False
    return True


def _break_glass_is_inactive(
    manifest: NormalizedCheckInEnvironmentManifest,
    evidence: BreakGlassEvidenceInput,
    all_evidence_references: tuple[str, ...],
    all_artifact_digests: tuple[str, ...],
    now: datetime,
) -> bool:
    declared = manifest.break_glass
    return (
        declared.mode == "deny_only"
        and evidence.mode == "deny_only"
        and declared.state == "inactive"
        and evidence.state == "inactive"
        and evidence.evidence_reference == declared.evidence_reference
        and _matches(evidence.artifact_sha256, _SHA256)
        and _matches(evidence.independent_verifier_reference, _EVIDENCE_REFERENCE)
        and evidence.independent_verifier_reference not in all_evidence_references
        and all_artifact_digests.count(evidence.artifact_sha256) == 1
        and _in_current_window(evidence.observed_at, evidence.fresh_until, now)
    )


def _evaluate_check_in_environment_evidence_gate(
    manifest_results: object,
    operational_evidence_result: object,
    *,
    evaluation_time: object,
) -> EnvironmentEvidenceGateReading:
    """Evaluate normalized evidence and return a capability-free reading."""

    if type(manifest_results) is not tuple:
        return _reading("manifest_invalid")
    if not manifest_results:
        return _reading("manifest_absent")
    if any(not _manifest_result_is_internally_valid(item) for item in manifest_results):
        return _reading("manifest_invalid")
    if len(manifest_results) != 1:
        return _reading("manifest_ambiguous")

    selected = manifest_results[0]
    assert type(selected) is ManifestNormalizationResult
    assert selected.manifest is not None
    manifest = selected.manifest

    now = _exact_aware_time(evaluation_time)
    if now is None:
        return _reading("manifest_invalid")
    issued = _parse_normalized_time(manifest.issued_at)
    expires = _parse_normalized_time(manifest.expires_at)
    assert issued is not None and expires is not None
    if not issued <= now < expires:
        return _reading("manifest_stale", selected)

    envelope = _evidence_envelope(operational_evidence_result)
    if isinstance(envelope, str):
        return _reading(envelope, selected)
    _inputs, role, rotations, break_glass = envelope

    if not _same_environment_binding(manifest, role, rotations, break_glass):
        return _reading("environment_mismatch", selected)
    if not _role_binding_matches(manifest, role):
        return _reading("role_binding_missing", selected)

    evidence_references = (
        role.evidence_reference,
        *(row.evidence_reference for row in rotations),
        break_glass.evidence_reference,
    )
    artifact_digests = (
        role.artifact_sha256,
        *(row.artifact_sha256 for row in rotations),
        break_glass.artifact_sha256,
    )
    if not _role_evidence_is_valid(
        role, evidence_references, artifact_digests, now
    ):
        return _reading("role_evidence_invalid", selected)
    if not _secret_references_are_valid(manifest, rotations):
        return _reading("secret_reference_invalid", selected)
    if len(set(evidence_references)) != len(evidence_references):
        return _reading("rotation_evidence_invalid", selected)
    if not _rotation_evidence_is_valid(
        manifest, rotations, evidence_references, artifact_digests, now
    ):
        return _reading("rotation_evidence_invalid", selected)
    if not _break_glass_is_inactive(
        manifest, break_glass, evidence_references, artifact_digests, now
    ):
        return _reading("break_glass_not_inactive", selected)
    return _reading("evidence_gate_satisfied", selected)


def evaluate_check_in_environment_evidence_gate(
    manifest_results: object,
    operational_evidence_result: object,
    *,
    evaluation_time: object,
) -> EnvironmentEvidenceGateReading:
    """Evaluate normalized evidence and fail closed for hostile objects."""

    try:
        return _evaluate_check_in_environment_evidence_gate(
            manifest_results,
            operational_evidence_result,
            evaluation_time=evaluation_time,
        )
    except Exception:
        return _reading("manifest_invalid")
