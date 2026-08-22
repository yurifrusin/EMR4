"""Pure, unmounted normalizer for the canonical check-in environment manifest.

The public function accepts explicit bytes only. It must never read ambient
configuration, resolve a reference, evaluate current freshness, or grant
admission/command authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


MANIFEST_SCHEMA_VERSION = "emr4.check-in-ordinary-environment-manifest.v1"
MANIFEST_MAX_BYTES = 32_768
MANIFEST_SLOT_IDS = (
    "database_connection_credential",
    "application_token_signing_key",
    "admission_snapshot_verification_key",
)

ManifestEnvironmentClass = Literal["development", "test", "staging", "production"]
ManifestNormalizationOutcome = Literal["normalized", "denied"]
ManifestNormalizationReason = Literal[
    "manifest_input_type_invalid",
    "manifest_size_invalid",
    "manifest_encoding_invalid",
    "manifest_bytes_non_canonical",
    "manifest_alias_or_tag_forbidden",
    "manifest_duplicate_key",
    "manifest_yaml_structure_invalid",
    "manifest_forbidden_field",
    "manifest_shape_invalid",
    "manifest_git_object_invalid",
    "manifest_binding_invalid",
    "manifest_normalized",
]


@dataclass(frozen=True, slots=True)
class ManifestEnvironment:
    environment_class: ManifestEnvironmentClass
    identifier: str


@dataclass(frozen=True, slots=True)
class ManifestRuntimeRole:
    logical_role_id: str
    database_role_identifier: str
    credential_secret_slot_id: str
    non_owner_required: bool
    nobypassrls_required: bool
    product_relation_ownership_allowed: bool
    tenant_attestation_reference: str


@dataclass(frozen=True, slots=True)
class ManifestSecretReference:
    slot_id: str
    provider_namespace: str
    secret_reference: str
    key_id: str
    version: str
    rotation_policy_reference: str
    rotation_evidence_reference: str


@dataclass(frozen=True, slots=True)
class ManifestRotationEvidence:
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
class ManifestBreakGlass:
    mode: str
    state: Literal["inactive", "engaged_deny", "retired"]
    evidence_reference: str
    bypass_allowed: bool
    secret_injection_allowed: bool
    automatic_clear_allowed: bool


@dataclass(frozen=True, slots=True)
class NormalizedCheckInEnvironmentManifest:
    schema_version: str
    manifest_id: str
    environment: ManifestEnvironment
    admission_snapshot_generation: int
    authority_git_object: str
    practice_scope_reference: str
    runtime_role: ManifestRuntimeRole
    secret_references: tuple[ManifestSecretReference, ...]
    rotation_evidence: tuple[ManifestRotationEvidence, ...]
    break_glass: ManifestBreakGlass
    issued_at: str
    expires_at: str


@dataclass(frozen=True, slots=True)
class ManifestNormalizationResult:
    outcome: ManifestNormalizationOutcome
    reason_code: ManifestNormalizationReason
    manifest_digest: str | None
    manifest: NormalizedCheckInEnvironmentManifest | None


def normalize_check_in_environment_manifest(
    payload: bytes,
) -> ManifestNormalizationResult:
    """Normalize explicit manifest bytes or return a deterministic denial.

    Native Harness implementation ownership begins below this contract. The
    implementation must satisfy the frozen plan without changing public types.
    """
    raise NotImplementedError("closed manifest normalizer implementation pending")
