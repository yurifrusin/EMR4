"""Focused tests for canonical check-in typed operational-evidence inputs."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import FrozenInstanceError
import inspect
from typing import Any

import pytest

import app.services.appointment_check_in_operational_evidence as evidence_module
from app.services.appointment_check_in_operational_evidence import (
    EVIDENCE_INPUT_SCHEMA_VERSION,
    EVIDENCE_SLOT_IDS,
    OperationalEvidenceInputNormalizationResult,
    normalize_check_in_operational_evidence_inputs,
)


GIT_OBJECT = "a" * 40
ARTIFACT_SHA256 = "b" * 64


def canonical_inputs() -> dict[str, Any]:
    rotations = []
    for index, slot_id in enumerate(EVIDENCE_SLOT_IDS, start=1):
        rotations.append(
            {
                "slot_id": slot_id,
                "evidence_reference": f"evidence-ref:rotation/{index}",
                "artifact_sha256": ARTIFACT_SHA256,
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
            "artifact_sha256": ARTIFACT_SHA256,
            "authority_git_object": GIT_OBJECT,
            "environment_identifier": "env:authored-reference",
            "admission_snapshot_generation": 7,
            "logical_role_id": "appointment_check_in_ordinary_runtime_v1",
            "database_role_identifier": "check_in_runtime",
            "credential_secret_slot_id": EVIDENCE_SLOT_IDS[0],
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
            "artifact_sha256": ARTIFACT_SHA256,
            "authority_git_object": GIT_OBJECT,
            "environment_identifier": "env:authored-reference",
            "admission_snapshot_generation": 7,
            "observed_at": "2026-08-20T00:00:00+10:00",
            "fresh_until": "2026-09-20T00:00:00+10:00",
            "independent_verifier_reference": "evidence-ref:verifier/break-glass",
        },
    }


def reason(payload: object) -> str:
    return normalize_check_in_operational_evidence_inputs(payload).reason_code


def test_public_contract_and_complete_frozen_readback_are_exact() -> None:
    payload = canonical_inputs()

    result = normalize_check_in_operational_evidence_inputs(payload)

    assert EVIDENCE_INPUT_SCHEMA_VERSION == "emr4.check-in-operational-evidence-inputs.v1"
    assert EVIDENCE_SLOT_IDS == (
        "database_connection_credential",
        "application_token_signing_key",
        "admission_snapshot_verification_key",
    )
    assert set(OperationalEvidenceInputNormalizationResult.__dataclass_fields__) == {
        "outcome",
        "reason_code",
        "evidence_inputs",
    }
    assert result.outcome == "normalized"
    assert result.reason_code == "evidence_inputs_normalized"
    assert result.evidence_inputs is not None
    assert result.evidence_inputs.schema_version == EVIDENCE_INPUT_SCHEMA_VERSION
    assert result.evidence_inputs.role_attestation.observed_at == "2026-08-19T14:00:00Z"
    assert result.evidence_inputs.role_attestation.fresh_until == "2026-09-19T14:00:00Z"
    assert tuple(
        row.slot_id for row in result.evidence_inputs.rotation_custody_attestations
    ) == EVIDENCE_SLOT_IDS
    assert result.evidence_inputs.rotation_custody_attestations[2].fresh_until == (
        "2026-09-22T14:00:00Z"
    )
    with pytest.raises(FrozenInstanceError):
        result.evidence_inputs.role_attestation.environment_identifier = "env:changed"  # type: ignore[misc]


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
    ],
)
def test_hostile_role_observations_remain_typed_for_later_evaluator(
    field: str, value: str
) -> None:
    payload = canonical_inputs()
    payload["role_attestation"][field] = value

    result = normalize_check_in_operational_evidence_inputs(payload)

    assert result.outcome == "normalized"
    assert result.evidence_inputs is not None
    assert getattr(result.evidence_inputs.role_attestation, field) == value


@pytest.mark.parametrize("state", ["inactive", "engaged_deny", "retired"])
def test_every_deny_only_break_glass_state_is_typed_not_evaluated(state: str) -> None:
    payload = canonical_inputs()
    payload["break_glass_evidence"]["state"] = state

    result = normalize_check_in_operational_evidence_inputs(payload)

    assert result.outcome == "normalized"
    assert result.evidence_inputs is not None
    assert result.evidence_inputs.break_glass_evidence.state == state


def test_cross_binding_self_verifier_and_staleness_are_deferred() -> None:
    payload = canonical_inputs()
    payload["role_attestation"]["environment_identifier"] = "env:other-reference"
    payload["role_attestation"]["admission_snapshot_generation"] = 99
    payload["role_attestation"]["authority_git_object"] = "c" * 40
    payload["role_attestation"]["credential_secret_slot_id"] = EVIDENCE_SLOT_IDS[1]
    payload["role_attestation"]["independent_verifier_reference"] = payload[
        "role_attestation"
    ]["evidence_reference"]
    payload["rotation_custody_attestations"][0]["key_id"] = "different-key"
    payload["rotation_custody_attestations"][0]["fresh_until"] = (
        "2026-08-22T00:00:00+10:00"
    )
    payload["break_glass_evidence"]["independent_verifier_reference"] = payload[
        "break_glass_evidence"
    ]["evidence_reference"]

    result = normalize_check_in_operational_evidence_inputs(payload)

    assert result.outcome == "normalized"
    assert result.evidence_inputs is not None
    assert result.evidence_inputs.role_attestation.environment_identifier == (
        "env:other-reference"
    )


@pytest.mark.parametrize(
    "payload",
    [None, "value", [], (), object()],
)
def test_exact_builtin_dict_input_is_required(payload: object) -> None:
    assert reason(payload) == "evidence_input_type_invalid"


def test_dict_subclass_is_not_an_implicit_input_surface() -> None:
    class DictSubclass(dict[str, object]):
        pass

    assert reason(DictSubclass(canonical_inputs())) == "evidence_input_type_invalid"


@pytest.mark.parametrize(
    "field",
    [
        "value",
        "secret-value",
        "Password",
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
    ],
)
def test_secret_or_resolution_fields_are_recursively_denied(field: str) -> None:
    payload = canonical_inputs()
    payload["rotation_custody_attestations"][1]["nested"] = {field: "not-a-secret"}
    assert reason(payload) == "evidence_forbidden_field"


@pytest.mark.parametrize("value", [True, False])
def test_any_boolean_claim_is_denied_before_shape(value: bool) -> None:
    payload = canonical_inputs()
    payload["role_attestation"]["verified"] = value
    assert reason(payload) == "evidence_boolean_claim_forbidden"


def test_forbidden_field_precedes_boolean_claim() -> None:
    payload = canonical_inputs()
    payload["role_attestation"]["secret_value"] = True
    assert reason(payload) == "evidence_forbidden_field"


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.update({"unknown": "field"}),
        lambda value: value.pop("role_attestation"),
        lambda value: value.update({"schema_version": "wrong"}),
        lambda value: value.update({"rotation_custody_attestations": tuple()}),
        lambda value: value["role_attestation"].update(
            {"ownership_observation": "verified"}
        ),
        lambda value: value["break_glass_evidence"].update({"mode": "bypass"}),
    ],
)
def test_unknown_missing_and_nonclosed_shapes_deny(mutation: Any) -> None:
    payload = canonical_inputs()
    mutation(payload)
    assert reason(payload) == "evidence_shape_invalid"


@pytest.mark.parametrize(
    ("record", "field"),
    [
        ("role_attestation", "ownership_observation"),
        ("role_attestation", "credential_secret_slot_id"),
        ("break_glass_evidence", "state"),
    ],
)
def test_unhashable_choice_values_deny_without_exception(record: str, field: str) -> None:
    payload = canonical_inputs()
    payload[record][field] = []
    assert reason(payload) == "evidence_shape_invalid"


def test_rotation_rows_are_exactly_three_and_ordered() -> None:
    payload = canonical_inputs()
    payload["rotation_custody_attestations"].reverse()
    assert reason(payload) == "evidence_shape_invalid"

    payload = canonical_inputs()
    payload["rotation_custody_attestations"].pop()
    assert reason(payload) == "evidence_shape_invalid"


@pytest.mark.parametrize("git_object", ["a" * 7, "A" * 40, "g" * 40, "a" * 41])
def test_every_git_object_requires_full_lowercase_oid(git_object: str) -> None:
    payload = canonical_inputs()
    payload["rotation_custody_attestations"][1]["authority_git_object"] = git_object
    assert reason(payload) == "evidence_git_object_invalid"


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value["role_attestation"].update(
            {"observed_at": "2026-08-20T00:00:00"}
        ),
        lambda value: value["role_attestation"].update(
            {"observed_at": "not-a-time"}
        ),
        lambda value: value["role_attestation"].update(
            {"fresh_until": value["role_attestation"]["observed_at"]}
        ),
        lambda value: value["rotation_custody_attestations"][0].update(
            {"fresh_until": "2026-08-19T00:00:00+10:00"}
        ),
    ],
)
def test_invalid_or_nonincreasing_evidence_windows_deny(mutation: Any) -> None:
    payload = canonical_inputs()
    mutation(payload)
    assert reason(payload) == "evidence_time_invalid"


def test_shape_denial_precedes_git_and_time_denial() -> None:
    payload = canonical_inputs()
    payload["role_attestation"]["logical_role_id"] = "INVALID"
    payload["role_attestation"]["authority_git_object"] = "short"
    payload["role_attestation"]["observed_at"] = "not-a-time"
    assert reason(payload) == "evidence_shape_invalid"


def test_git_denial_precedes_time_denial() -> None:
    payload = canonical_inputs()
    payload["role_attestation"]["authority_git_object"] = "short"
    payload["role_attestation"]["observed_at"] = "not-a-time"
    assert reason(payload) == "evidence_git_object_invalid"


def test_deterministic_normalization_does_not_mutate_input() -> None:
    payload = canonical_inputs()
    before = deepcopy(payload)
    first = normalize_check_in_operational_evidence_inputs(payload)
    second = normalize_check_in_operational_evidence_inputs(payload)

    assert first == second
    assert payload == before


def test_source_has_no_ambient_evaluator_or_effect_dependencies() -> None:
    source = inspect.getsource(evidence_module)
    for forbidden in (
        "import os",
        "from os",
        "pathlib",
        "open(",
        "import yaml",
        "requests",
        "httpx",
        "sqlalchemy",
        "app.api",
        "app.core.config",
        "datetime.now",
        "datetime.utcnow",
        "getenv",
        "os.environ",
        "resolve_secret",
        "execute_check_in",
        "evidence_gate_satisfied",
    ):
        assert forbidden not in source
