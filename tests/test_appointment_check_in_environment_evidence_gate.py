"""Focused tests for the pure check-in environment evidence-gate evaluator."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone, tzinfo
import inspect
from typing import Any, Callable

import pytest
import yaml

import app.services.appointment_check_in_environment_evidence_gate as gate_module
from app.services.appointment_check_in_environment_evidence_gate import (
    EVIDENCE_GATE_READING_SCHEMA_VERSION,
    EnvironmentEvidenceGateReading,
    evaluate_check_in_environment_evidence_gate,
)
from app.services.appointment_check_in_environment_manifest import (
    MANIFEST_SCHEMA_VERSION,
    MANIFEST_SLOT_IDS,
    ManifestNormalizationResult,
    normalize_check_in_environment_manifest,
)
from app.services.appointment_check_in_operational_evidence import (
    EVIDENCE_INPUT_SCHEMA_VERSION,
    OperationalEvidenceInputNormalizationResult,
    normalize_check_in_operational_evidence_inputs,
)


GIT_OBJECT = "a" * 40
EVALUATION_TIME = datetime(2026, 8, 25, 0, 0, tzinfo=timezone.utc)


class ExplodingTimezone(tzinfo):
    def utcoffset(self, value: datetime | None) -> None:
        raise RuntimeError("caller-controlled timezone failure")

    def dst(self, value: datetime | None) -> None:
        return None


def canonical_manifest() -> dict[str, Any]:
    secret_references = []
    rotation_evidence = []
    for index, slot_id in enumerate(MANIFEST_SLOT_IDS, start=1):
        evidence_reference = f"evidence-ref:rotation/{index}"
        secret_references.append(
            {
                "slot_id": slot_id,
                "provider_namespace": f"namespace-{index}",
                "secret_reference": f"secret-ref:check-in/{index}",
                "key_id": f"key-{index}",
                "version": f"v{index}",
                "rotation_policy_reference": f"policy-ref:rotation/{index}",
                "rotation_evidence_reference": evidence_reference,
            }
        )
        rotation_evidence.append(
            {
                "slot_id": slot_id,
                "evidence_reference": evidence_reference,
                "artifact_sha256": str(index) * 64,
                "authority_git_object": GIT_OBJECT,
                "environment_identifier": "env:authored-reference",
                "admission_snapshot_generation": 7,
                "key_id": f"key-{index}",
                "version": f"v{index}",
                "rotation_sequence": index,
                "observed_at": f"2026-08-2{index}T00:00:00+10:00",
                "fresh_until": f"2026-09-2{index}T00:00:00+10:00",
                "independent_verifier_reference": f"evidence-ref:verifier/{index}",
            }
        )
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "manifest_id": "check-in-env-manifest:authored-reference",
        "environment": {"class": "test", "identifier": "env:authored-reference"},
        "admission_snapshot_generation": 7,
        "authority_git_object": GIT_OBJECT,
        "practice_scope_reference": "practice-ref:authored/reference",
        "runtime_role": {
            "logical_role_id": "appointment_check_in_ordinary_runtime_v1",
            "database_role_identifier": "check_in_runtime",
            "credential_secret_slot_id": MANIFEST_SLOT_IDS[0],
            "non_owner_required": True,
            "nobypassrls_required": True,
            "product_relation_ownership_allowed": False,
            "tenant_attestation_reference": "evidence-ref:role/attestation",
        },
        "secret_references": secret_references,
        "rotation_evidence": rotation_evidence,
        "break_glass": {
            "mode": "deny_only",
            "state": "inactive",
            "evidence_reference": "evidence-ref:break-glass/state",
            "bypass_allowed": False,
            "secret_injection_allowed": False,
            "automatic_clear_allowed": False,
        },
        "issued_at": "2026-08-20T00:00:00+10:00",
        "expires_at": "2026-10-20T00:00:00+10:00",
    }


def canonical_evidence() -> dict[str, Any]:
    rotations = []
    for index, slot_id in enumerate(MANIFEST_SLOT_IDS, start=1):
        rotations.append(
            {
                "slot_id": slot_id,
                "evidence_reference": f"evidence-ref:rotation/{index}",
                "artifact_sha256": str(index) * 64,
                "authority_git_object": GIT_OBJECT,
                "environment_identifier": "env:authored-reference",
                "admission_snapshot_generation": 7,
                "key_id": f"key-{index}",
                "version": f"v{index}",
                "rotation_sequence": index,
                "observed_at": f"2026-08-2{index}T00:00:00+10:00",
                "fresh_until": f"2026-09-2{index}T00:00:00+10:00",
                "independent_verifier_reference": f"evidence-ref:verifier/{index}",
            }
        )
    return {
        "schema_version": EVIDENCE_INPUT_SCHEMA_VERSION,
        "role_attestation": {
            "evidence_reference": "evidence-ref:role/attestation",
            "artifact_sha256": "4" * 64,
            "authority_git_object": GIT_OBJECT,
            "environment_identifier": "env:authored-reference",
            "admission_snapshot_generation": 7,
            "logical_role_id": "appointment_check_in_ordinary_runtime_v1",
            "database_role_identifier": "check_in_runtime",
            "credential_secret_slot_id": MANIFEST_SLOT_IDS[0],
            "ownership_observation": "non_owner",
            "rls_bypass_observation": "nobypassrls",
            "product_relation_ownership_observation": "absent",
            "cross_tenant_probe_observation": "denied",
            "observed_at": "2026-08-20T00:00:00+10:00",
            "fresh_until": "2026-09-20T00:00:00+10:00",
            "independent_verifier_reference": "evidence-ref:verifier/role",
        },
        "rotation_custody_attestations": rotations,
        "break_glass_evidence": {
            "mode": "deny_only",
            "state": "inactive",
            "evidence_reference": "evidence-ref:break-glass/state",
            "artifact_sha256": "5" * 64,
            "authority_git_object": GIT_OBJECT,
            "environment_identifier": "env:authored-reference",
            "admission_snapshot_generation": 7,
            "observed_at": "2026-08-20T00:00:00+10:00",
            "fresh_until": "2026-09-20T00:00:00+10:00",
            "independent_verifier_reference": "evidence-ref:verifier/break-glass",
        },
    }


def normalized_manifest(
    value: dict[str, Any] | None = None,
) -> ManifestNormalizationResult:
    payload = yaml.safe_dump(
        canonical_manifest() if value is None else value,
        allow_unicode=True,
        sort_keys=False,
    ).encode("utf-8")
    result = normalize_check_in_environment_manifest(payload)
    assert result.outcome == "normalized"
    return result


def normalized_evidence(
    value: dict[str, Any] | None = None,
) -> OperationalEvidenceInputNormalizationResult:
    result = normalize_check_in_operational_evidence_inputs(
        canonical_evidence() if value is None else value
    )
    assert result.outcome == "normalized"
    return result


def reason(
    manifests: object,
    evidence: object,
    evaluation_time: object = EVALUATION_TIME,
) -> str:
    return evaluate_check_in_environment_evidence_gate(
        manifests, evidence, evaluation_time=evaluation_time
    ).reason_code


def test_satisfied_reading_is_exact_frozen_and_capability_free() -> None:
    manifest = normalized_manifest()

    reading = evaluate_check_in_environment_evidence_gate(
        (manifest,), normalized_evidence(), evaluation_time=EVALUATION_TIME
    )

    assert reading == EnvironmentEvidenceGateReading(
        schema_version=EVIDENCE_GATE_READING_SCHEMA_VERSION,
        outcome="satisfied",
        reason_code="evidence_gate_satisfied",
        environment_identifier="env:authored-reference",
        admission_snapshot_generation=7,
        manifest_digest=manifest.manifest_digest,
    )
    assert set(reading.__dataclass_fields__) == {
        "schema_version",
        "outcome",
        "reason_code",
        "environment_identifier",
        "admission_snapshot_generation",
        "manifest_digest",
    }
    with pytest.raises(FrozenInstanceError):
        reading.outcome = "denied"  # type: ignore[misc]
    assert not any(
        callable(getattr(reading, name, None)) for name in ("admit", "execute")
    )


def test_empty_manifest_population_denies_without_selecting_data() -> None:
    reading = evaluate_check_in_environment_evidence_gate(
        (), None, evaluation_time=object()
    )
    assert reading.reason_code == "manifest_absent"
    assert reading.outcome == "denied"
    assert reading.environment_identifier is None
    assert reading.admission_snapshot_generation is None
    assert reading.manifest_digest is None


@pytest.mark.parametrize(
    "manifests",
    [
        [],
        (object(),),
        (
            ManifestNormalizationResult(
                outcome="denied",
                reason_code="manifest_shape_invalid",
                manifest_digest=None,
                manifest=None,
            ),
        ),
    ],
)
def test_invalid_manifest_envelopes_deny(manifests: object) -> None:
    assert reason(manifests, normalized_evidence()) == "manifest_invalid"


@pytest.mark.parametrize("evaluation_time", [None, "2026-08-25T00:00:00Z", datetime(2026, 8, 25)])
def test_invalid_explicit_time_denies_as_manifest_invalid(
    evaluation_time: object,
) -> None:
    assert (
        reason((normalized_manifest(),), normalized_evidence(), evaluation_time)
        == "manifest_invalid"
    )


def test_hostile_timezone_object_fails_closed_without_escaping() -> None:
    hostile_time = datetime(2026, 8, 25, tzinfo=ExplodingTimezone())
    assert (
        reason((normalized_manifest(),), normalized_evidence(), hostile_time)
        == "manifest_invalid"
    )


def test_multiple_valid_manifests_deny_without_selection() -> None:
    manifest = normalized_manifest()
    reading = evaluate_check_in_environment_evidence_gate(
        (manifest, manifest), normalized_evidence(), evaluation_time=EVALUATION_TIME
    )
    assert reading.reason_code == "manifest_ambiguous"
    assert reading.environment_identifier is None
    assert reading.manifest_digest is None


@pytest.mark.parametrize(
    "evaluation_time",
    [
        datetime(2026, 8, 19, 13, 59, 59, tzinfo=timezone.utc),
        datetime(2026, 10, 19, 14, 0, tzinfo=timezone.utc),
    ],
)
def test_manifest_half_open_freshness_window_denies_outside(
    evaluation_time: datetime,
) -> None:
    assert (
        reason((normalized_manifest(),), normalized_evidence(), evaluation_time)
        == "manifest_stale"
    )


def test_manifest_boundary_and_offset_equivalence_are_deterministic() -> None:
    manifest = normalized_manifest()
    issued_boundary = datetime(2026, 8, 19, 14, 0, tzinfo=timezone.utc)
    offset_same_instant = datetime.fromisoformat("2026-08-25T10:00:00+10:00")
    assert reason((manifest,), normalized_evidence(), issued_boundary) == (
        "rotation_evidence_invalid"
    )
    assert reason((manifest,), normalized_evidence(), offset_same_instant) == (
        "evidence_gate_satisfied"
    )


@pytest.mark.parametrize(
    ("record", "field", "value"),
    [
        ("role_attestation", "environment_identifier", "env:wrong"),
        ("role_attestation", "admission_snapshot_generation", 8),
        ("role_attestation", "authority_git_object", "b" * 40),
        ("rotation_custody_attestations", "environment_identifier", "env:wrong"),
        ("break_glass_evidence", "admission_snapshot_generation", 8),
    ],
)
def test_any_environment_generation_or_authority_mismatch_denies_first(
    record: str, field: str, value: object
) -> None:
    evidence = canonical_evidence()
    if record == "rotation_custody_attestations":
        evidence[record][1][field] = value
    else:
        evidence[record][field] = value
    assert reason((normalized_manifest(),), normalized_evidence(evidence)) == (
        "environment_mismatch"
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("evidence_reference", "evidence-ref:role/wrong"),
        ("logical_role_id", "appointment_check_in_other_runtime_v1"),
        ("database_role_identifier", "other_runtime"),
        ("credential_secret_slot_id", MANIFEST_SLOT_IDS[1]),
    ],
)
def test_missing_exact_role_binding_denies(field: str, value: str) -> None:
    evidence = canonical_evidence()
    evidence["role_attestation"][field] = value
    assert reason((normalized_manifest(),), normalized_evidence(evidence)) == (
        "role_binding_missing"
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("ownership_observation", "owner"),
        ("ownership_observation", "unknown"),
        ("rls_bypass_observation", "bypassrls"),
        ("rls_bypass_observation", "unknown"),
        ("product_relation_ownership_observation", "present"),
        ("product_relation_ownership_observation", "unknown"),
        ("cross_tenant_probe_observation", "allowed"),
        ("cross_tenant_probe_observation", "not_observed"),
        ("independent_verifier_reference", "evidence-ref:role/attestation"),
        ("fresh_until", "2026-08-24T00:00:00Z"),
        ("observed_at", "2026-08-26T00:00:00Z"),
    ],
)
def test_hostile_or_noncurrent_role_evidence_denies(field: str, value: str) -> None:
    evidence = canonical_evidence()
    evidence["role_attestation"][field] = value
    assert reason((normalized_manifest(),), normalized_evidence(evidence)) == (
        "role_evidence_invalid"
    )


@pytest.mark.parametrize("field", ["evidence_reference", "key_id", "version"])
def test_secret_reference_binding_mismatch_denies(field: str) -> None:
    evidence = canonical_evidence()
    evidence["rotation_custody_attestations"][1][field] = {
        "evidence_reference": "evidence-ref:rotation/other",
        "key_id": "other-key",
        "version": "v-other",
    }[field]
    assert reason((normalized_manifest(),), normalized_evidence(evidence)) == (
        "secret_reference_invalid"
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("artifact_sha256", "6" * 64),
        ("rotation_sequence", 99),
        ("fresh_until", "2026-08-24T00:00:00Z"),
        ("observed_at", "2026-08-26T00:00:00Z"),
        ("independent_verifier_reference", "evidence-ref:rotation/2"),
    ],
)
def test_invalid_rotation_evidence_denies(field: str, value: object) -> None:
    evidence = canonical_evidence()
    evidence["rotation_custody_attestations"][1][field] = value
    assert reason((normalized_manifest(),), normalized_evidence(evidence)) == (
        "rotation_evidence_invalid"
    )


@pytest.mark.parametrize("field", ["evidence_reference", "artifact_sha256"])
def test_duplicate_evidence_or_artifact_denies(field: str) -> None:
    evidence = canonical_evidence()
    evidence["rotation_custody_attestations"][1][field] = evidence[
        "rotation_custody_attestations"
    ][0][field]
    expected = (
        "secret_reference_invalid"
        if field == "evidence_reference"
        else "rotation_evidence_invalid"
    )
    assert reason((normalized_manifest(),), normalized_evidence(evidence)) == expected


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("state", "engaged_deny"),
        ("state", "retired"),
        ("evidence_reference", "evidence-ref:break-glass/wrong"),
        ("independent_verifier_reference", "evidence-ref:break-glass/state"),
        ("fresh_until", "2026-08-24T00:00:00Z"),
        ("observed_at", "2026-08-26T00:00:00Z"),
    ],
)
def test_break_glass_is_strictly_deny_only_and_current(
    field: str, value: str
) -> None:
    manifest_value = canonical_manifest()
    evidence = canonical_evidence()
    evidence["break_glass_evidence"][field] = value
    if field == "state":
        manifest_value["break_glass"]["state"] = value
    assert reason((normalized_manifest(manifest_value),), normalized_evidence(evidence)) == (
        "break_glass_not_inactive"
    )


def test_reason_precedence_is_fail_closed() -> None:
    stale_time = datetime(2027, 1, 1, tzinfo=timezone.utc)
    evidence = canonical_evidence()
    evidence["role_attestation"]["environment_identifier"] = "env:wrong"
    evidence["role_attestation"]["ownership_observation"] = "owner"
    evidence["rotation_custody_attestations"][0]["key_id"] = "other-key"
    assert reason((normalized_manifest(),), normalized_evidence(evidence), stale_time) == (
        "manifest_stale"
    )
    assert reason((normalized_manifest(),), normalized_evidence(evidence)) == (
        "environment_mismatch"
    )
    evidence["role_attestation"]["environment_identifier"] = "env:authored-reference"
    evidence["role_attestation"]["logical_role_id"] = "other_role"
    assert reason((normalized_manifest(),), normalized_evidence(evidence)) == (
        "role_binding_missing"
    )
    evidence["role_attestation"]["logical_role_id"] = (
        "appointment_check_in_ordinary_runtime_v1"
    )
    assert reason((normalized_manifest(),), normalized_evidence(evidence)) == (
        "role_evidence_invalid"
    )


def test_missing_or_denied_operational_evidence_maps_to_role_evidence_invalid() -> None:
    denied = normalize_check_in_operational_evidence_inputs({})
    assert denied.outcome == "denied"
    assert reason((normalized_manifest(),), None) == "role_evidence_invalid"
    assert reason((normalized_manifest(),), denied) == "role_evidence_invalid"


def test_manually_forged_normalized_manifest_result_denies() -> None:
    original = normalized_manifest()
    assert original.manifest is not None
    forged = replace(
        original,
        manifest=replace(original.manifest, authority_git_object="abc1234"),
    )
    assert reason((forged,), normalized_evidence()) == "manifest_invalid"


def test_inputs_are_not_mutated_and_reading_is_deterministic() -> None:
    manifests = (normalized_manifest(),)
    evidence = normalized_evidence()
    before = deepcopy((manifests, evidence))
    first = evaluate_check_in_environment_evidence_gate(
        manifests, evidence, evaluation_time=EVALUATION_TIME
    )
    second = evaluate_check_in_environment_evidence_gate(
        manifests, evidence, evaluation_time=EVALUATION_TIME
    )
    assert first == second
    assert (manifests, evidence) == before


def test_module_has_no_ambient_or_effect_capability() -> None:
    source = inspect.getsource(gate_module)
    forbidden_tokens = (
        "datetime.now",
        "datetime.utcnow",
        "Path(",
        "open(",
        "os.environ",
        "getenv(",
        "yaml",
        "sqlalchemy",
        "requests",
        "httpx",
        "subprocess",
        "app.config",
        "app.database",
        "app.api",
        "admit(",
        "execute(",
    )
    assert not any(token in source for token in forbidden_tokens)
    assert set(gate_module.__dict__) >= {
        "evaluate_check_in_environment_evidence_gate",
        "EnvironmentEvidenceGateReading",
    }


@pytest.mark.parametrize(
    "mutator",
    [
        lambda value: value["role_attestation"].update(
            {"artifact_sha256": value["rotation_custody_attestations"][0]["artifact_sha256"]}
        ),
        lambda value: value["break_glass_evidence"].update(
            {"artifact_sha256": value["rotation_custody_attestations"][2]["artifact_sha256"]}
        ),
        lambda value: value["rotation_custody_attestations"][0].update(
            {"independent_verifier_reference": "evidence-ref:break-glass/state"}
        ),
    ],
)
def test_cross_record_artifact_or_verifier_reuse_denies(
    mutator: Callable[[dict[str, Any]], None],
) -> None:
    evidence = canonical_evidence()
    mutator(evidence)
    assert reason((normalized_manifest(),), normalized_evidence(evidence)) in {
        "role_evidence_invalid",
        "rotation_evidence_invalid",
        "break_glass_not_inactive",
    }
