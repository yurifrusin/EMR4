"""Pure, unmounted normalizer for the canonical check-in environment manifest.

The public function accepts explicit bytes only. It must never read ambient
configuration, resolve a reference, evaluate current freshness, or grant
admission/command authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import re
from typing import Any, Literal

import yaml
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode
from yaml.tokens import AliasToken, AnchorToken, TagToken


MANIFEST_SCHEMA_VERSION = "emr4.check-in-ordinary-environment-manifest.v1"
MANIFEST_MAX_BYTES = 32_768
MANIFEST_SLOT_IDS = (
    "database_connection_credential",
    "application_token_signing_key",
    "admission_snapshot_verification_key",
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
    }
)
_TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "manifest_id",
        "environment",
        "admission_snapshot_generation",
        "authority_git_object",
        "practice_scope_reference",
        "runtime_role",
        "secret_references",
        "rotation_evidence",
        "break_glass",
        "issued_at",
        "expires_at",
    }
)
_ENVIRONMENT_FIELDS = frozenset({"class", "identifier"})
_RUNTIME_ROLE_FIELDS = frozenset(
    {
        "logical_role_id",
        "database_role_identifier",
        "credential_secret_slot_id",
        "non_owner_required",
        "nobypassrls_required",
        "product_relation_ownership_allowed",
        "tenant_attestation_reference",
    }
)
_SECRET_REFERENCE_FIELDS = frozenset(
    {
        "slot_id",
        "provider_namespace",
        "secret_reference",
        "key_id",
        "version",
        "rotation_policy_reference",
        "rotation_evidence_reference",
    }
)
_ROTATION_EVIDENCE_FIELDS = frozenset(
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
        "bypass_allowed",
        "secret_injection_allowed",
        "automatic_clear_allowed",
    }
)
_ENVIRONMENT_CLASSES = frozenset({"development", "test", "staging", "production"})
_BREAK_GLASS_STATES = frozenset({"inactive", "engaged_deny", "retired"})
_FULL_GIT_OBJECT = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_MANIFEST_ID = re.compile(r"^check-in-env-manifest:[a-z0-9][a-z0-9._-]{2,95}$")
_ENVIRONMENT_ID = re.compile(r"^env:[a-z0-9][a-z0-9._-]{2,95}$")
_PRACTICE_REFERENCE = re.compile(r"^practice-ref:[a-z0-9][a-z0-9._/-]{2,127}$")
_EVIDENCE_REFERENCE = re.compile(r"^evidence-ref:[a-z0-9][a-z0-9._/-]{2,127}$")
_POLICY_REFERENCE = re.compile(r"^policy-ref:[a-z0-9][a-z0-9._/-]{2,127}$")
_SECRET_REFERENCE = re.compile(r"^secret-ref:[a-z0-9][a-z0-9._/-]{2,127}$")
_DATABASE_ROLE = re.compile(r"^[a-z][a-z0-9_]{2,62}$")
_PROVIDER_NAMESPACE = re.compile(r"^[a-z][a-z0-9._-]{2,63}$")
_KEY_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{2,95}$")
_VERSION = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
_RFC3339 = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)


class _ManifestLoader(yaml.SafeLoader):
    """Local loader whose scalars stay inside the frozen JSON-shaped domain."""


_ManifestLoader.yaml_implicit_resolvers = {
    key: [
        (tag, expression)
        for tag, expression in resolvers
        if tag != "tag:yaml.org,2002:timestamp"
    ]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


class _AliasOrTagForbidden(ValueError):
    pass


class _DuplicateKey(ValueError):
    pass


class _YamlStructureInvalid(ValueError):
    pass

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


def _denied(reason: ManifestNormalizationReason) -> ManifestNormalizationResult:
    return ManifestNormalizationResult(
        outcome="denied",
        reason_code=reason,
        manifest_digest=None,
        manifest=None,
    )


def _validate_yaml_node(node: Node) -> None:
    if isinstance(node, MappingNode):
        for key_node, _value_node in node.value:
            if isinstance(key_node, ScalarNode) and key_node.value == "<<":
                raise _AliasOrTagForbidden
        keys: set[str] = set()
        for key_node, value_node in node.value:
            if not isinstance(key_node, ScalarNode) or key_node.tag != "tag:yaml.org,2002:str":
                raise _YamlStructureInvalid
            if key_node.value in keys:
                raise _DuplicateKey
            keys.add(key_node.value)
            _validate_yaml_node(value_node)
        return
    if isinstance(node, SequenceNode):
        for child in node.value:
            _validate_yaml_node(child)
        return
    if not isinstance(node, ScalarNode) or node.tag not in {
        "tag:yaml.org,2002:str",
        "tag:yaml.org,2002:int",
        "tag:yaml.org,2002:bool",
        "tag:yaml.org,2002:null",
    }:
        raise _YamlStructureInvalid


def _load_yaml(text: str) -> tuple[dict[str, Any] | None, ManifestNormalizationReason | None]:
    try:
        for token in yaml.scan(text, Loader=_ManifestLoader):
            if isinstance(token, (AliasToken, AnchorToken, TagToken)):
                raise _AliasOrTagForbidden
        nodes = list(yaml.compose_all(text, Loader=_ManifestLoader))
        if len(nodes) != 1 or not isinstance(nodes[0], MappingNode):
            raise _YamlStructureInvalid
        _validate_yaml_node(nodes[0])
        value = yaml.load(text, Loader=_ManifestLoader)
        if not isinstance(value, dict):
            raise _YamlStructureInvalid
        return value, None
    except _AliasOrTagForbidden:
        return None, "manifest_alias_or_tag_forbidden"
    except _DuplicateKey:
        return None, "manifest_duplicate_key"
    except (
        _YamlStructureInvalid,
        yaml.YAMLError,
        RecursionError,
        ValueError,
        TypeError,
    ):
        return None, "manifest_yaml_structure_invalid"


def _contains_forbidden_field(value: Any) -> bool:
    pending = [value]
    while pending:
        current = pending.pop()
        if isinstance(current, dict):
            for key, child in current.items():
                if (
                    isinstance(key, str)
                    and key.casefold().replace("-", "_") in _FORBIDDEN_FIELD_NAMES
                ):
                    return True
                pending.append(child)
        elif isinstance(current, list):
            pending.extend(current)
    return False


def _exact_fields(value: Any, expected: frozenset[str]) -> bool:
    return isinstance(value, dict) and set(value) == expected


def _string_matches(value: Any, pattern: re.Pattern[str]) -> bool:
    return isinstance(value, str) and pattern.fullmatch(value) is not None


def _positive_integer(value: Any) -> bool:
    return type(value) is int and value >= 1


def _parse_timestamp(value: Any) -> tuple[datetime, str] | None:
    if not isinstance(value, str) or _RFC3339.fullmatch(value) is None:
        return None
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    normalized = parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return parsed, normalized


def _shape_is_valid(value: dict[str, Any]) -> bool:
    if not _exact_fields(value, _TOP_LEVEL_FIELDS):
        return False
    environment = value["environment"]
    runtime_role = value["runtime_role"]
    secret_references = value["secret_references"]
    rotation_evidence = value["rotation_evidence"]
    break_glass = value["break_glass"]
    if (
        value["schema_version"] != MANIFEST_SCHEMA_VERSION
        or not _string_matches(value["manifest_id"], _MANIFEST_ID)
        or not _exact_fields(environment, _ENVIRONMENT_FIELDS)
        or not isinstance(environment["class"], str)
        or environment["class"] not in _ENVIRONMENT_CLASSES
        or not _string_matches(environment["identifier"], _ENVIRONMENT_ID)
        or not _positive_integer(value["admission_snapshot_generation"])
        or not isinstance(value["authority_git_object"], str)
        or not _string_matches(value["practice_scope_reference"], _PRACTICE_REFERENCE)
        or not _exact_fields(runtime_role, _RUNTIME_ROLE_FIELDS)
        or runtime_role["logical_role_id"] != "appointment_check_in_ordinary_runtime_v1"
        or not _string_matches(runtime_role["database_role_identifier"], _DATABASE_ROLE)
        or runtime_role["credential_secret_slot_id"] != MANIFEST_SLOT_IDS[0]
        or type(runtime_role["non_owner_required"]) is not bool
        or runtime_role["non_owner_required"] is not True
        or type(runtime_role["nobypassrls_required"]) is not bool
        or runtime_role["nobypassrls_required"] is not True
        or type(runtime_role["product_relation_ownership_allowed"]) is not bool
        or runtime_role["product_relation_ownership_allowed"] is not False
        or not _string_matches(
            runtime_role["tenant_attestation_reference"], _EVIDENCE_REFERENCE
        )
        or not isinstance(secret_references, list)
        or len(secret_references) != 3
        or not isinstance(rotation_evidence, list)
        or len(rotation_evidence) != 3
        or not _exact_fields(break_glass, _BREAK_GLASS_FIELDS)
        or break_glass["mode"] != "deny_only"
        or not isinstance(break_glass["state"], str)
        or break_glass["state"] not in _BREAK_GLASS_STATES
        or not _string_matches(break_glass["evidence_reference"], _EVIDENCE_REFERENCE)
        or type(break_glass["bypass_allowed"]) is not bool
        or break_glass["bypass_allowed"] is not False
        or type(break_glass["secret_injection_allowed"]) is not bool
        or break_glass["secret_injection_allowed"] is not False
        or type(break_glass["automatic_clear_allowed"]) is not bool
        or break_glass["automatic_clear_allowed"] is not False
        or _parse_timestamp(value["issued_at"]) is None
        or _parse_timestamp(value["expires_at"]) is None
    ):
        return False
    for row in secret_references:
        if (
            not _exact_fields(row, _SECRET_REFERENCE_FIELDS)
            or not isinstance(row["slot_id"], str)
            or not _string_matches(row["provider_namespace"], _PROVIDER_NAMESPACE)
            or not _string_matches(row["secret_reference"], _SECRET_REFERENCE)
            or not _string_matches(row["key_id"], _KEY_ID)
            or not _string_matches(row["version"], _VERSION)
            or not _string_matches(row["rotation_policy_reference"], _POLICY_REFERENCE)
            or not _string_matches(row["rotation_evidence_reference"], _EVIDENCE_REFERENCE)
        ):
            return False
    for row in rotation_evidence:
        if (
            not _exact_fields(row, _ROTATION_EVIDENCE_FIELDS)
            or not isinstance(row["slot_id"], str)
            or not _string_matches(row["evidence_reference"], _EVIDENCE_REFERENCE)
            or not _string_matches(row["artifact_sha256"], _SHA256)
            or not isinstance(row["authority_git_object"], str)
            or not _string_matches(row["environment_identifier"], _ENVIRONMENT_ID)
            or not _positive_integer(row["admission_snapshot_generation"])
            or not _string_matches(row["key_id"], _KEY_ID)
            or not _string_matches(row["version"], _VERSION)
            or not _positive_integer(row["rotation_sequence"])
            or _parse_timestamp(row["observed_at"]) is None
            or _parse_timestamp(row["fresh_until"]) is None
            or not _string_matches(
                row["independent_verifier_reference"], _EVIDENCE_REFERENCE
            )
        ):
            return False
    return True


def _git_objects_are_valid(value: dict[str, Any]) -> bool:
    return _FULL_GIT_OBJECT.fullmatch(value["authority_git_object"]) is not None and all(
        _FULL_GIT_OBJECT.fullmatch(row["authority_git_object"]) is not None
        for row in value["rotation_evidence"]
    )


def _bindings_are_valid(value: dict[str, Any]) -> bool:
    secret_references = value["secret_references"]
    rotation_evidence = value["rotation_evidence"]
    if (
        tuple(row["slot_id"] for row in secret_references) != MANIFEST_SLOT_IDS
        or tuple(row["slot_id"] for row in rotation_evidence) != MANIFEST_SLOT_IDS
        or len({row["provider_namespace"] for row in secret_references}) != 3
        or len({row["secret_reference"] for row in secret_references}) != 3
        or len({row["key_id"] for row in secret_references}) != 3
    ):
        return False
    for secret, rotation in zip(secret_references, rotation_evidence, strict=True):
        if (
            rotation["slot_id"] != secret["slot_id"]
            or rotation["key_id"] != secret["key_id"]
            or rotation["version"] != secret["version"]
            or rotation["evidence_reference"] != secret["rotation_evidence_reference"]
            or rotation["environment_identifier"] != value["environment"]["identifier"]
            or rotation["admission_snapshot_generation"]
            != value["admission_snapshot_generation"]
            or rotation["authority_git_object"] != value["authority_git_object"]
        ):
            return False
        observed = _parse_timestamp(rotation["observed_at"])
        fresh = _parse_timestamp(rotation["fresh_until"])
        if observed is None or fresh is None or fresh[0] <= observed[0]:
            return False
    issued = _parse_timestamp(value["issued_at"])
    expires = _parse_timestamp(value["expires_at"])
    return issued is not None and expires is not None and expires[0] > issued[0]


def _normalized_manifest(value: dict[str, Any]) -> NormalizedCheckInEnvironmentManifest:
    issued = _parse_timestamp(value["issued_at"])
    expires = _parse_timestamp(value["expires_at"])
    assert issued is not None and expires is not None
    return NormalizedCheckInEnvironmentManifest(
        schema_version=value["schema_version"],
        manifest_id=value["manifest_id"],
        environment=ManifestEnvironment(
            environment_class=value["environment"]["class"],
            identifier=value["environment"]["identifier"],
        ),
        admission_snapshot_generation=value["admission_snapshot_generation"],
        authority_git_object=value["authority_git_object"],
        practice_scope_reference=value["practice_scope_reference"],
        runtime_role=ManifestRuntimeRole(**value["runtime_role"]),
        secret_references=tuple(
            ManifestSecretReference(**row) for row in value["secret_references"]
        ),
        rotation_evidence=tuple(
            ManifestRotationEvidence(
                **{
                    **row,
                    "observed_at": _parse_timestamp(row["observed_at"])[1],
                    "fresh_until": _parse_timestamp(row["fresh_until"])[1],
                }
            )
            for row in value["rotation_evidence"]
        ),
        break_glass=ManifestBreakGlass(**value["break_glass"]),
        issued_at=issued[1],
        expires_at=expires[1],
    )


def normalize_check_in_environment_manifest(
    payload: bytes,
) -> ManifestNormalizationResult:
    """Normalize explicit manifest bytes or return a deterministic denial."""
    if type(payload) is not bytes:
        return _denied("manifest_input_type_invalid")
    if not 1 <= len(payload) <= MANIFEST_MAX_BYTES:
        return _denied("manifest_size_invalid")
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return _denied("manifest_encoding_invalid")
    if (
        payload.startswith(b"\xef\xbb\xbf")
        or b"\x00" in payload
        or b"\r" in payload
        or b"\t" in payload
        or not payload.endswith(b"\n")
        or payload.endswith(b"\n\n")
    ):
        return _denied("manifest_bytes_non_canonical")
    value, denial = _load_yaml(text)
    if denial is not None or value is None:
        return _denied(denial or "manifest_yaml_structure_invalid")
    if _contains_forbidden_field(value):
        return _denied("manifest_forbidden_field")
    if not _shape_is_valid(value):
        return _denied("manifest_shape_invalid")
    if not _git_objects_are_valid(value):
        return _denied("manifest_git_object_invalid")
    if not _bindings_are_valid(value):
        return _denied("manifest_binding_invalid")
    return ManifestNormalizationResult(
        outcome="normalized",
        reason_code="manifest_normalized",
        manifest_digest=hashlib.sha256(payload).hexdigest(),
        manifest=_normalized_manifest(value),
    )
