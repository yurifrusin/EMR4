"""Focused tests for the pure check-in environment-manifest normalizer."""

from __future__ import annotations

import hashlib
import inspect
from typing import Any

import pytest
import yaml

import app.services.appointment_check_in_environment_manifest as manifest_module
from app.services.appointment_check_in_environment_manifest import (
    MANIFEST_MAX_BYTES,
    MANIFEST_SCHEMA_VERSION,
    MANIFEST_SLOT_IDS,
    ManifestNormalizationResult,
    normalize_check_in_environment_manifest,
)


GIT_OBJECT = "a" * 40
ARTIFACT_SHA256 = "b" * 64


def canonical_manifest() -> dict[str, Any]:
    secret_references = []
    rotation_evidence = []
    for index, slot_id in enumerate(MANIFEST_SLOT_IDS, start=1):
        key_id = f"key-{index}"
        version = f"v{index}"
        evidence_reference = f"evidence-ref:rotation/{index}"
        secret_references.append(
            {
                "slot_id": slot_id,
                "provider_namespace": f"namespace-{index}",
                "secret_reference": f"secret-ref:check-in/{index}",
                "key_id": key_id,
                "version": version,
                "rotation_policy_reference": f"policy-ref:rotation/{index}",
                "rotation_evidence_reference": evidence_reference,
            }
        )
        rotation_evidence.append(
            {
                "slot_id": slot_id,
                "evidence_reference": evidence_reference,
                "artifact_sha256": ARTIFACT_SHA256,
                "authority_git_object": GIT_OBJECT,
                "environment_identifier": "env:test-practice",
                "admission_snapshot_generation": 7,
                "key_id": key_id,
                "version": version,
                "rotation_sequence": index,
                "observed_at": f"2026-08-2{index}T00:00:00+10:00",
                "fresh_until": f"2026-09-2{index}T00:00:00+10:00",
                "independent_verifier_reference": f"evidence-ref:verifier/{index}",
            }
        )
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "manifest_id": "check-in-env-manifest:test-practice",
        "environment": {"class": "test", "identifier": "env:test-practice"},
        "admission_snapshot_generation": 7,
        "authority_git_object": GIT_OBJECT,
        "practice_scope_reference": "practice-ref:test/practice",
        "runtime_role": {
            "logical_role_id": "appointment_check_in_ordinary_runtime_v1",
            "database_role_identifier": "check_in_runtime",
            "credential_secret_slot_id": MANIFEST_SLOT_IDS[0],
            "non_owner_required": True,
            "nobypassrls_required": True,
            "product_relation_ownership_allowed": False,
            "tenant_attestation_reference": "evidence-ref:tenant/test-practice",
        },
        "secret_references": secret_references,
        "rotation_evidence": rotation_evidence,
        "break_glass": {
            "mode": "deny_only",
            "state": "inactive",
            "evidence_reference": "evidence-ref:break-glass/inactive",
            "bypass_allowed": False,
            "secret_injection_allowed": False,
            "automatic_clear_allowed": False,
        },
        "issued_at": "2026-08-20T00:00:00+10:00",
        "expires_at": "2026-10-20T00:00:00+10:00",
    }


def manifest_bytes(value: dict[str, Any] | None = None) -> bytes:
    return yaml.safe_dump(
        canonical_manifest() if value is None else value,
        allow_unicode=True,
        sort_keys=False,
    ).encode("utf-8")


def reason(payload: object) -> str:
    return normalize_check_in_environment_manifest(payload).reason_code  # type: ignore[arg-type]


def test_manifest_normalizer_public_contract_is_frozen() -> None:
    assert MANIFEST_SCHEMA_VERSION == "emr4.check-in-ordinary-environment-manifest.v1"
    assert MANIFEST_MAX_BYTES == 32_768
    assert MANIFEST_SLOT_IDS == (
        "database_connection_credential",
        "application_token_signing_key",
        "admission_snapshot_verification_key",
    )
    assert set(ManifestNormalizationResult.__dataclass_fields__) == {
        "outcome",
        "reason_code",
        "manifest_digest",
        "manifest",
    }


def test_canonical_manifest_normalizes_complete_frozen_reading_and_exact_digest() -> None:
    payload = manifest_bytes()

    result = normalize_check_in_environment_manifest(payload)

    assert result.outcome == "normalized"
    assert result.reason_code == "manifest_normalized"
    assert result.manifest_digest == hashlib.sha256(payload).hexdigest()
    assert result.manifest is not None
    assert result.manifest.schema_version == MANIFEST_SCHEMA_VERSION
    assert result.manifest.environment.environment_class == "test"
    assert result.manifest.environment.identifier == "env:test-practice"
    assert result.manifest.runtime_role.database_role_identifier == "check_in_runtime"
    assert tuple(row.slot_id for row in result.manifest.secret_references) == MANIFEST_SLOT_IDS
    assert tuple(row.slot_id for row in result.manifest.rotation_evidence) == MANIFEST_SLOT_IDS
    assert result.manifest.rotation_evidence[0].observed_at == "2026-08-20T14:00:00Z"
    assert result.manifest.rotation_evidence[2].fresh_until == "2026-09-22T14:00:00Z"
    assert result.manifest.issued_at == "2026-08-19T14:00:00Z"
    assert result.manifest.expires_at == "2026-10-19T14:00:00Z"
    assert result.manifest.break_glass.bypass_allowed is False


@pytest.mark.parametrize("payload", [None, "value", bytearray(b"x\n"), memoryview(b"x\n")])
def test_exact_bytes_are_required(payload: object) -> None:
    assert reason(payload) == "manifest_input_type_invalid"


@pytest.mark.parametrize(
    "payload",
    [b"", b"a" * MANIFEST_MAX_BYTES + b"\n"],
    ids=["empty", "over-maximum"],
)
def test_size_denial_precedes_content(payload: bytes) -> None:
    assert reason(payload) == "manifest_size_invalid"


def test_invalid_utf8_is_denied_before_byte_canonicality() -> None:
    assert reason(b"\xff\r\n") == "manifest_encoding_invalid"


@pytest.mark.parametrize(
    "payload",
    [
        b"\xef\xbb\xbfkey: value\n",
        b"key: \x00\n",
        b"key: value\r\n",
        b"key:\tvalue\n",
        b"key: value",
        b"key: value\n\n",
    ],
)
def test_noncanonical_bytes_are_denied(payload: bytes) -> None:
    assert reason(payload) == "manifest_bytes_non_canonical"


@pytest.mark.parametrize(
    "payload",
    [
        b"first: &anchor value\nsecond: other\n",
        b"first: value\nsecond: *anchor\n",
        b"first: !!str value\n",
        b"base: {first: value}\nmerged: {<<: {first: value}}\n",
    ],
)
def test_anchors_aliases_tags_and_merge_keys_share_closed_denial(payload: bytes) -> None:
    assert reason(payload) == "manifest_alias_or_tag_forbidden"


def test_duplicate_key_denial_is_recursive() -> None:
    payload = b"outer:\n  repeated: one\n  repeated: two\n"
    assert reason(payload) == "manifest_duplicate_key"


@pytest.mark.parametrize(
    "payload",
    [
        b"- not\n- a\n- mapping\n",
        b"---\nfirst: one\n---\nsecond: two\n",
        b"value: [unterminated\n",
        b"number: 1.5\n",
        b"? [sequence, key]\n: invalid\n",
    ],
)
def test_yaml_structure_and_scalar_domain_are_closed(payload: bytes) -> None:
    assert reason(payload) == "manifest_yaml_structure_invalid"


@pytest.mark.parametrize(
    "field",
    [
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
    ],
)
def test_every_forbidden_secret_field_name_is_denied_before_shape(field: str) -> None:
    value = canonical_manifest()
    value["runtime_role"][field.upper().replace("_", "-")] = "forbidden"
    assert reason(manifest_bytes(value)) == "manifest_forbidden_field"


@pytest.mark.parametrize(
    "mutator",
    [
        lambda value: value.update({"unexpected": "field"}),
        lambda value: value.pop("manifest_id"),
        lambda value: value["environment"].update({"class": "live"}),
        lambda value: value["runtime_role"].update({"non_owner_required": 1}),
        lambda value: value["secret_references"][0].update({"version": "UPPER"}),
        lambda value: value["rotation_evidence"][0].update({"artifact_sha256": "x"}),
        lambda value: value.update({"issued_at": "not-a-time"}),
    ],
)
def test_unknown_missing_and_invalid_shape_are_denied(mutator: Any) -> None:
    value = canonical_manifest()
    mutator(value)
    assert reason(manifest_bytes(value)) == "manifest_shape_invalid"


@pytest.mark.parametrize(
    ("location", "git_object"),
    [
        ("top", "abc1234"),
        ("top", "A" * 40),
        ("rotation", "abc1234"),
        ("rotation", "A" * 40),
    ],
)
def test_only_full_lowercase_git_objects_are_accepted(location: str, git_object: str) -> None:
    value = canonical_manifest()
    if location == "top":
        value["authority_git_object"] = git_object
    else:
        value["rotation_evidence"][1]["authority_git_object"] = git_object
    assert reason(manifest_bytes(value)) == "manifest_git_object_invalid"


@pytest.mark.parametrize(
    "mutator",
    [
        lambda value: value["secret_references"].reverse(),
        lambda value: value["rotation_evidence"].reverse(),
        lambda value: value["secret_references"][1].update(
            {"provider_namespace": value["secret_references"][0]["provider_namespace"]}
        ),
        lambda value: value["secret_references"][1].update(
            {"secret_reference": value["secret_references"][0]["secret_reference"]}
        ),
        lambda value: value["secret_references"][1].update(
            {"key_id": value["secret_references"][0]["key_id"]}
        ),
        lambda value: value["rotation_evidence"][1].update({"key_id": "different-key"}),
        lambda value: value["rotation_evidence"][1].update(
            {"evidence_reference": "evidence-ref:different/rotation"}
        ),
        lambda value: value["rotation_evidence"][1].update(
            {"environment_identifier": "env:different"}
        ),
        lambda value: value["rotation_evidence"][1].update(
            {"admission_snapshot_generation": 8}
        ),
        lambda value: value["rotation_evidence"][1].update(
            {"authority_git_object": "c" * 40}
        ),
        lambda value: value["rotation_evidence"][0].update(
            {"fresh_until": value["rotation_evidence"][0]["observed_at"]}
        ),
        lambda value: value.update({"expires_at": value["issued_at"]}),
    ],
)
def test_order_distinctness_cross_field_and_time_bindings_are_denied(mutator: Any) -> None:
    value = canonical_manifest()
    mutator(value)
    assert reason(manifest_bytes(value)) == "manifest_binding_invalid"


def test_denial_precedence_does_not_release_digest_or_manifest() -> None:
    value = canonical_manifest()
    value["authority_git_object"] = "short"
    value["PASSWORD"] = "forbidden"

    result = normalize_check_in_environment_manifest(manifest_bytes(value))

    assert result.reason_code == "manifest_forbidden_field"
    assert result.outcome == "denied"
    assert result.manifest_digest is None
    assert result.manifest is None


def test_normalization_is_deterministic_and_does_not_mutate_input() -> None:
    payload = manifest_bytes()
    original = bytes(payload)

    first = normalize_check_in_environment_manifest(payload)
    second = normalize_check_in_environment_manifest(payload)

    assert first == second
    assert payload == original


@pytest.mark.parametrize(
    "payload",
    [
        b"{}\n",
        b"null\n",
        b"timestamp: 2026-08-23T00:00:00Z\n",
        b"set: !!set {one: null}\n",
        b"broken: {one: two\n",
        b"value: " + (b"[" * 1_100) + (b"]" * 1_100) + b"\n",
    ],
)
def test_caller_controlled_yaml_never_raises(payload: bytes) -> None:
    result = normalize_check_in_environment_manifest(payload)
    assert result.outcome == "denied"


@pytest.mark.parametrize(
    ("path", "malformed"),
    [
        (("environment", "class"), ["development"]),
        (("break_glass", "state"), {"unexpected": "inactive"}),
    ],
)
def test_unhashable_enum_values_fail_closed(
    path: tuple[str, str], malformed: object
) -> None:
    value = canonical_manifest()
    value[path[0]][path[1]] = malformed

    assert reason(manifest_bytes(value)) == "manifest_shape_invalid"


def test_source_has_no_ambient_or_forbidden_capability() -> None:
    source = inspect.getsource(manifest_module)
    forbidden = (
        "import os",
        "from os",
        "pathlib",
        "open(",
        "getenv",
        "os.environ",
        "dotenv",
        "sqlalchemy",
        "requests",
        "httpx",
        "socket",
        "datetime.now",
        "datetime.utcnow",
        "time.time",
        "FastAPI",
        "APIRouter",
    )
    assert not [token for token in forbidden if token in source]
    assert "yaml.SafeLoader" in source
    assert "yaml.unsafe_load" not in source
    assert "yaml.full_load" not in source
